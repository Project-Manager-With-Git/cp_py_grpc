import os
import warnings
from typing import Any, Dict

import grpc
from .pb import rpc_protos, rpc_services


class Handdler(rpc_services.ECHOServicer):
    def __init__(self, config: Dict[str, Any]):
        super().__init__()
        self.config = config
        self.pid = os.getpid()

    async def Square(self, request: Any, context: grpc.aio.ServicerContext) -> Any:
        warnings.warn(f"pid:{self.pid}")
        return rpc_protos.Message(Message=request.Message**2)

    async def RangeSquare(self, request: Any, context: Any) -> Any:
        warnings.warn(f"pid:{self.pid}")
        for i in range(int(request.Message + 1)):
            yield rpc_protos.Message(Message=i**2)

    async def SumSquare(self, request_iterator: Any, context: Any) -> Any:
        warnings.warn(f"pid:{self.pid}")
        result = 0
        async for i in request_iterator:
            result += i.Message**2
        return rpc_protos.Message(Message=result)

    async def StreamrangeSquare(self, request_iterator: Any, context: Any) -> Any:
        warnings.warn(f"pid:{self.pid}")
        result = []
        async for i in request_iterator:
            result.append(i.Message**2)
        for j in result:
            yield rpc_protos.Message(Message=j)
