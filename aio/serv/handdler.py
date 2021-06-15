from typing import Any, Dict
import grpc
from echo_pb.echo_pb2_grpc import ECHOServicer
from echo_pb.echo_pb2 import Message


class Handdler(ECHOServicer):
    def __init__(self, config: Dict[str, Any]):
        super().__init__()
        self.config = config

    async def Square(self, request: Any, context: grpc.aio.ServicerContext) -> Any:
        return Message(Message=request.Message**2)

    async def RangeSquare(self, request: Any, context: Any) -> Any:
        for i in range(int(request.Message + 1)):
            yield Message(Message=i**2)

    async def SumSquare(self, request_iterator: Any, context: Any) -> Any:
        result = 0
        async for i in request_iterator:
            result += i.Message**2
        return Message(Message=result)

    async def StreamrangeSquare(self, request_iterator: Any, context: Any) -> Any:
        result = []
        async for i in request_iterator:
            result.append(i.Message**2)
        for j in result:
            yield Message(Message=j)
