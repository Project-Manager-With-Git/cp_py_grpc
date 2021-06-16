from time import time
from typing import Callable, Union, AsyncIterable, Any, Iterable
import grpc
from pyloggerhelper import log


class TimerInterceptor(grpc.aio.UnaryUnaryClientInterceptor,
                       grpc.aio.UnaryStreamClientInterceptor,
                       grpc.aio.StreamUnaryClientInterceptor,
                       grpc.aio.StreamStreamClientInterceptor):

    async def intercept_unary_unary(self,
                                    continuation: Callable[[grpc.aio._interceptor.ClientCallDetails, grpc.aio._typing.RequestType], grpc.aio._call.UnaryUnaryCall],
                                    client_call_details: grpc.aio._interceptor.ClientCallDetails,
                                    request: grpc.aio._typing.RequestType) -> Union[grpc.aio._call.UnaryUnaryCall, grpc.aio._typing.ResponseType]:
        start = time()
        response = await continuation(client_call_details, request)
        end = time()
        log.info("unary_unary query cost", cost=end - start, method=client_call_details.method)
        return response

    async def intercept_unary_stream(self,
                                     continuation: Callable[[grpc.aio._interceptor.ClientCallDetails, grpc.aio._typing.RequestType], grpc.aio._call.UnaryStreamCall],
                                     client_call_details: grpc.aio._interceptor.ClientCallDetails,
                                     request: grpc.aio._typing.RequestType) -> Union[AsyncIterable[Any], grpc.aio._call.UnaryStreamCall]:
        start = time()
        async for res in continuation(client_call_details, request):
            yield res
        end = time()
        log.info("unary_stream query cost", cost=end - start, method=client_call_details.method)

    async def intercept_stream_unary(self,
                                     continuation: Callable[[grpc.aio._interceptor.ClientCallDetails, grpc.aio._typing.RequestIterableType], grpc.aio._call.StreamUnaryCall],
                                     client_call_details: grpc.aio._interceptor.ClientCallDetails,
                                     request_iterator: grpc.aio._typing.RequestIterableType) -> grpc.aio._call.StreamUnaryCall:
        start = time()
        response = await continuation(client_call_details, request_iterator)
        end = time()
        log.info("stream_unary query cost", cost=end - start, method=client_call_details.method)
        return response

    async def intercept_stream_stream(self,
                                      continuation: Callable[[grpc.aio._interceptor.ClientCallDetails, grpc.aio._typing.RequestIterableType], grpc.aio._call.StreamStreamCall],
                                      client_call_details: grpc.aio._interceptor.ClientCallDetails,
                                      request_iterator: grpc.aio._typing.RequestIterableType) -> Union[AsyncIterable[Any], grpc.aio._call.StreamStreamCall]:
        log.info("stream_stream query intercept", method=client_call_details.method)
        async for res in continuation(client_call_details, request_iterator):
            log.info("stream_stream query get", method=client_call_details.method)
            yield res
