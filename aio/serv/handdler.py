from typing import Any, Dict
import grpc
from pyloggerhelper import log
from echo_pb.echo_pb2_grpc import ECHOServicer
from echo_pb.echo_pb2 import Message


class Handdler(ECHOServicer):
    def __init__(self, config: Dict[str, Any]):
        super().__init__()
        self.config = config

    async def Square(self, request: grpc.aio._typing.RequestType, context: grpc.aio.ServicerContext) -> grpc.aio._typing.ResponseType:
        header = context.invocation_metadata()
        log.info("get header", header=header)
        await context.send_initial_metadata((("c", "3"), ("d", "4")))
        context.set_trailing_metadata((
            ('checksum-bin', b'I agree'),
            ('retry', 'false'),
        ))
        return Message(Message=request.Message**2)

    async def RangeSquare(self, request: grpc.aio._typing.RequestType, context: grpc.aio.ServicerContext) -> grpc.aio._typing.ResponseIterableType:
        for i in range(int(request.Message + 1)):
            yield Message(Message=i**2)

    async def SumSquare(self, request_iterator: grpc.aio._typing.RequestIterableType, context: grpc.aio.ServicerContext) -> grpc.aio._typing.ResponseType:
        result = 0
        async for i in request_iterator:
            result += i.Message**2
        return Message(Message=result)

    async def StreamrangeSquare(self, request_iterator: grpc.aio._typing.RequestIterableType, context: grpc.aio.ServicerContext) -> grpc.aio._typing.ResponseIterableType:
        header = context.invocation_metadata()
        log.info("get header", header=header)
        await context.send_initial_metadata((("c", "3"), ("d", "4")))
        context.set_trailing_metadata((
            ('checksum-bin', b'I agree'),
            ('retry', 'false'),
        ))
        result = []
        async for i in request_iterator:
            result.append(i.Message**2)
        for j in result:
            yield Message(Message=j)
