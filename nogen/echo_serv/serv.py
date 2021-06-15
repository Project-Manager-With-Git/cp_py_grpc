import os
import asyncio
import warnings
from pathlib import Path
from concurrent import futures
from typing import Any, Dict, Tuple, Union, List
import grpc
from grpc_health.v1 import health
from grpc_health.v1 import _async as health_async
from grpc_health.v1 import health_pb2
from grpc_health.v1 import health_pb2_grpc
from grpc_channelz.v1 import channelz
from grpc_reflection.v1alpha import reflection
from schema_entry import EntryPoint
from .pb import rpc_protos, rpc_services
from .handdler import Handdler


_COMPRESSION_OPTIONS = {
    "none": grpc.Compression.NoCompression,
    "deflate": grpc.Compression.Deflate,
    "gzip": grpc.Compression.Gzip,
}


class Serv(EntryPoint):
    """grpc的服务端启动入口."""
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "required": ["address", "log_level"],
        "properties": {
            "app_version": {
                "type": "string",
                "title": "v",
                "description": "应用版本"
            },
            "app_name": {
                "type": "string",
                "title": "n",
                "description": "应用名"
            },
            "address": {
                "type": "string",
                "title": "a",
                "description": "服务启动地址",
                "default": "0.0.0.0:5000"
            },
            "log_level": {
                "type": "string",
                "title": "l",
                "description": "log等级",
                "enum": ["DEBUG", "INFO", "WARN", "ERROR"],
                "default": "DEBUG"
            },
            "max_threads": {
                "type": "integer",
                "title": "t",
                "description": "单进程最大线程数",
                "default": 1000
            },
            "maximum_concurrent_rpcs": {
                "type": "integer",
                "title": "m",
                "description": "最大每秒接受并发数",
                "default": 50
            },
            "use_channelz": {
                "type": "boolean",
                "description": "是否使用channelz协助优化",
                "default": False
            },
            "server_cert_path": {
                "type": "string",
                "description": "使用TLS时服务端的证书位置",
            },
            "server_key_path": {
                "type": "string",
                "description": "使用TLS时服务端证书的私钥位置",
            },
            "grpc_mode": {
                "type": "string",
                "description": "grpc的执行模式,分为`latency`(高响应),`blend`(均衡),`throughput`(高吞吐)",
                "enum": ["latency", "blend", "throughput"]
            },
            "max_rec_msg_size": {
                "type": "integer",
                "description": "允许接收的最大消息长度",
                "default": 1024 * 1024
            },
            "max_send_msg_size": {
                "type": "integer",
                "description": "允许发送的最大消息长度",
                "default": 1024 * 1024
            },
            "max_concurrent_streams": {
                "type": "integer",
                "description": "单连接最大并发量",
                "default": 100
            },
            "max_connection_idle": {
                "type": "integer",
                "description": "客户端连接的最大空闲时长(s)",
            },
            "max_connection_age": {
                "type": "integer",
                "description": "如果连接存活超过n则发送goaway",
            },
            "max_connection_age_grace": {
                "type": "integer",
                "description": "强制关闭连接之前允许等待的rpc在n秒内完成",
            },
            "keepalive_time": {
                "type": "integer",
                "description": "空闲连接每隔n秒ping一次客户端已确保连接存活",
            },
            "keepalive_timeout": {
                "type": "integer",
                "description": "ping时长超过n则认为连接已死",
            },
            "keepalive_enforement_permit_without_stream": {
                "type": "boolean",
                "description": "即使没有活动流也允许ping",
            },
            "compression": {
                "type": "string",
                "title": "z",
                "description": "使用哪种方式压缩发送的消息",
                "enum": ["deflate", "gzip"],
            },
            "rpc_options": {
                "type": "array",
                "title": "o",
                "description": "grpc服务端的其他配置项",
                "items": {
                    "type": "string"
                }
            },
        }
    }

    def make_opts(self, config: Dict[str, Any]) -> List[Tuple[str, Union[int]]]:
        """构造grpc服务端的选项配置.

        Args:
            as_worker (bool): 服务是否是多线程中作为worker的

        Returns:
            List[Tuple[str, Union[int]]]: 配置项
        """
        _opt = {
            'grpc.so_reuseport': 0
        }
        # grpc运行模式
        grpc_mode = config.get("grpc_mode")
        if grpc_mode:
            _opt.update({"grpc.optimization_target": grpc_mode})

        # 吞吐量
        max_rec_msg_size = config.get("max_rec_msg_size")
        if max_rec_msg_size:
            _opt.update({"grpc.max_receive_message_length": max_rec_msg_size})
        max_send_msg_size = config.get("max_send_msg_size")
        if max_send_msg_size:
            _opt.update({"grpc.max_send_message_length": max_send_msg_size})

        initial_window_size = config.get("initial_window_size")
        if initial_window_size:
            _opt.update({"grpc.http2.lookahead_bytes": initial_window_size})

        # 多路复用
        max_concurrent_streams = config.get("max_concurrent_streams")
        if max_concurrent_streams:
            _opt.update({"grpc.max_concurrent_streams": max_concurrent_streams})
        # keepalive
        max_connection_idle = config.get("max_connection_idle")
        if max_connection_idle:
            _opt.update({"grpc.max_connection_idle_ms": max_connection_idle * 1000})
        max_connection_age = config.get("max_connection_age")
        if max_connection_age:
            _opt.update({"grpc.max_connection_age_ms": max_connection_age * 1000})
        max_connection_age_grace = config.get("max_connection_age_grace")
        if max_connection_age_grace:
            _opt.update({"grpc.max_connection_age_grace_ms": max_connection_age_grace * 1000})
        keepalive_time = config.get("keepalive_time")
        if keepalive_time:
            _opt.update({"grpc.keepalive_time_ms": keepalive_time * 1000})
        keepalive_timeout = config.get("keepalive_timeout")
        if keepalive_timeout:
            _opt.update({"grpc.keepalive_timeout_ms": keepalive_timeout * 1000})
        keepalive_enforement_permit_without_stream = config.get("keepalive_enforement_permit_without_stream")
        if keepalive_enforement_permit_without_stream:
            _opt.update({"grpc.keepalive_permit_without_calls": 1 if keepalive_enforement_permit_without_stream else 0})
        # 其他配置
        rpc_options = config.get("rpc_options")
        if rpc_options:
            _opt.update({
                pair[0]: int(pair[1]) if pair[1].isdigit() else pair[1]
                for opt in rpc_options if len(pair := opt.split(":")) == 2
            })
        return [(k, v) for k, v in _opt.items()]

    async def run_singal_serv(self, config: Dict[str, Any]) -> None:
        opts = self.make_opts(config)
        grpc_serv = grpc.aio.server(
            futures.ThreadPoolExecutor(max_workers=config.get("max_threads", 1000)),
            compression=_COMPRESSION_OPTIONS.get(self.config.get("compression"), grpc.Compression.NoCompression),
            options=opts,
            maximum_concurrent_rpcs=config.get("maximum_concurrent_rpcs", 50)
        )
        handdler = Handdler(config)
        rpc_services.add_ECHOServicer_to_server(handdler, grpc_serv)

        # 健康检查
        health_servicer = health_async.HealthServicer()
        health_pb2_grpc.add_HealthServicer_to_server(health_servicer, grpc_serv)

        # 反射
        services = tuple(
            service.full_name
            for service in rpc_protos.DESCRIPTOR.services_by_name.values()
        ) + (
            reflection.SERVICE_NAME,
            health.SERVICE_NAME
        )
        reflection.enable_server_reflection(services, grpc_serv)

        # channelz
        if self.config.get("use_channelz"):
            channelz.add_channelz_servicer(grpc_serv)
        # 绑定端口
        pid = os.getpid()
        addr = config["address"]
        if self.config.get("server_cert_path") and self.config.get("server_key_path"):
            server_cert_p = Path(self.config["server_cert_path"])
            server_key_p = Path(self.config["server_key_path"])
            try:
                with open(server_cert_p, 'rb') as f:
                    server_cert = f.read()
                with open(server_key_p, 'rb') as f:
                    server_key = f.read()
                server_credentials = grpc.ssl_server_credentials(((
                    server_key,
                    server_cert,
                ),))
                grpc_serv.add_secure_port(addr, server_credentials)
            except Exception as e:
                warnings.warn(f"tls load error:{str(e)}")
                grpc_serv.add_insecure_port(addr)
        else:
            grpc_serv.add_insecure_port(addr)

        warnings.warn(f"grpc @process:{pid} start @{addr}")
        await grpc_serv.start()
        # 设置服务为健康
        overall_server_health = ""
        for service in services + (overall_server_health,):
            await health_servicer.set(service, health_pb2.HealthCheckResponse.SERVING)
        try:
            await grpc_serv.wait_for_termination()
        except KeyboardInterrupt:
            await grpc_serv.stop(0)


    def do_main(self) -> None:
        """服务程序入口."""
        config = self.config
        if config.get("uvloop"):
            try:
                import uvloop
                uvloop.install()
                warnings.warn("grpc try to use uvloop")
            except Exception:
                warnings.warn("import uvloop error")
            else:
                warnings.warn("grpc using uvloop")
        try:
            asyncio.run(self.run_singal_serv(config=config))
        except KeyboardInterrupt:
            warnings.warn("grpc stoped")
        except Exception as e:
            raise e
