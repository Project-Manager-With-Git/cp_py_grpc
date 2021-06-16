from typing import Any, Dict
import grpc
from pyloggerhelper import log
from echo_pb.echo_pb2_grpc import ECHOServicer
from echo_pb.echo_pb2 import Message


class Handdler(ECHOServicer):
    def __init__(self, config: Dict[str, Any]):
        super().__init__()
        self.config = config

    def Square(self, request: Any, context: grpc.ServicerContext) -> Any:
        header = context.invocation_metadata()
        log.info("get header", header=header)
        context.send_initial_metadata((("c", "3"), ("d", "4")))
        context.set_trailing_metadata((
            ('checksum-bin', b'I agree'),
            ('retry', 'false'),
        ))
        return Message(Message=request.Message**2)

    def RangeSquare(self, request: Any, context: grpc.ServicerContext) -> Any:
        for i in range(int(request.Message + 1)):
            yield Message(Message=i**2)

    def SumSquare(self, request_iterator: Any, context: grpc.ServicerContext) -> Any:
        result = 0
        for i in request_iterator:
            result += i.Message**2
        return Message(Message=result)

    def StreamrangeSquare(self, request_iterator: Any, context: grpc.ServicerContext) -> Any:
        header = context.invocation_metadata()
        log.info("get header", header=header)
        context.send_initial_metadata((("c", "3"), ("d", "4")))
        context.set_trailing_metadata((
            ('checksum-bin', b'I agree'),
            ('retry', 'false'),
        ))
        result = []
        for i in request_iterator:
            result.append(i.Message**2)
        for j in result:
            yield Message(Message=j)
