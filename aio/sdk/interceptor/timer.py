from time import time
import asyncio
from typing import Callable, Union, AsyncIterable, Any, Iterable
import grpc
from pyloggerhelper import log


class UnaryUnaryTimerInterceptor(grpc.aio.UnaryUnaryClientInterceptor):

    async def intercept_unary_unary(self,
                                    continuation: Callable[[grpc.aio._interceptor.ClientCallDetails, grpc.aio._typing.RequestType], grpc.aio._call.UnaryUnaryCall],
                                    client_call_details: grpc.aio._interceptor.ClientCallDetails,
                                    request: grpc.aio._typing.RequestType) -> Union[grpc.aio._call.UnaryUnaryCall, grpc.aio._typing.ResponseType]:
        start = time()
        call = await continuation(client_call_details, request)
        call.add_done_callback(lambda f: log.info("unary_unary query cost", cost=time() - start, method=client_call_details.method))
        return call


class UnaryStreamTimerInterceptor(grpc.aio.UnaryStreamClientInterceptor):

    async def intercept_unary_stream(self,
                                     continuation: Callable[[grpc.aio._interceptor.ClientCallDetails, grpc.aio._typing.RequestType], grpc.aio._call.UnaryStreamCall],
                                     client_call_details: grpc.aio._interceptor.ClientCallDetails,
                                     request: grpc.aio._typing.RequestType) -> Union[AsyncIterable[Any], grpc.aio._call.UnaryStreamCall]:
        try:
            start = time()
            call = await continuation(client_call_details, request)
            call.add_done_callback(lambda f: log.info("unary_stream query cost", cost=time() - start, method=client_call_details.method))
        except Exception as e:
            print("********")
            print(e)
            raise e
        else:
            return call


class StreamUnaryTimerInterceptor(grpc.aio.StreamUnaryClientInterceptor):

    async def intercept_stream_unary(self,
                                     continuation: Callable[[grpc.aio._interceptor.ClientCallDetails, grpc.aio._typing.RequestIterableType], grpc.aio._call.StreamUnaryCall],
                                     client_call_details: grpc.aio._interceptor.ClientCallDetails,
                                     request_iterator: grpc.aio._typing.RequestIterableType) -> grpc.aio._call.StreamUnaryCall:
        start = time()
        call = await continuation(client_call_details, request_iterator)
        call.add_done_callback(lambda f: log.info("stream_unary query cost", cost=time() - start, method=client_call_details.method))
        return call


class StreamStreamTimerInterceptor(grpc.aio.StreamStreamClientInterceptor):
    async def intercept_stream_stream(self,
                                      continuation: Callable[[grpc.aio._interceptor.ClientCallDetails, grpc.aio._typing.RequestIterableType], grpc.aio._call.StreamStreamCall],
                                      client_call_details: grpc.aio._interceptor.ClientCallDetails,
                                      request_iterator: grpc.aio._typing.RequestIterableType) -> Union[AsyncIterable[Any], grpc.aio._call.StreamStreamCall]:
        start = time()
        call = await continuation(client_call_details, request_iterator)
        call.add_done_callback(lambda f: log.info("stream_stream query cost", cost=time() - start, method=client_call_details.method))
        return call
