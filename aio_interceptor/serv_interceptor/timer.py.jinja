from time import time
from typing import Callable, Awaitable
from pyloggerhelper import log
import grpc


class TimerInterceptor(grpc.aio.ServerInterceptor):

    async def intercept_service(self,
                                continuation: Callable[[grpc.HandlerCallDetails], Awaitable[grpc.RpcMethodHandler]],
                                handler_call_details: grpc.HandlerCallDetails) -> grpc.RpcMethodHandler:
        start = time()
        ctx = await continuation(handler_call_details)
        log.info("query cost", cost=time() - start, method=handler_call_details.method)
        return ctx
