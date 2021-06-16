from time import time
from typing import Any
import grpc
from pyloggerhelper import log


class TimerInterceptor(grpc.UnaryUnaryClientInterceptor,
                       grpc.UnaryStreamClientInterceptor,
                       grpc.StreamUnaryClientInterceptor,
                       grpc.StreamStreamClientInterceptor):

    def intercept_unary_unary(self,
                              continuation: Any,
                              client_call_details: grpc.ClientCallDetails,
                              request: Any) -> Any:
        start = time()
        response = continuation(client_call_details, request)
        end = time()
        log.info("unary_unary query cost", cost=end - start, method=client_call_details.method)
        return response

    def intercept_unary_stream(self,
                               continuation: Any,
                               client_call_details: grpc.ClientCallDetails,
                               request: Any) -> Any:
        start = time()
        call = continuation(client_call_details, request)
        call.add_done_callback(lambda f: log.info("unary_stream query cost", cost=time() - start, method=client_call_details.method))
        return call

    def intercept_stream_unary(self,
                               continuation: Any,
                               client_call_details: grpc.ClientCallDetails,
                               request_iterator: Any) -> Any:
        start = time()
        response = continuation(client_call_details, request_iterator)
        end = time()
        log.info("stream_unary query cost", cost=end - start, method=client_call_details.method)
        return response

    def intercept_stream_stream(self,
                                continuation: Any,
                                client_call_details: grpc.ClientCallDetails,
                                request_iterator: Any) -> Any:
        start = time()
        call = continuation(client_call_details, request_iterator)
        call.add_done_callback(lambda f: log.info("stream_stream query cost", cost=time() - start, method=client_call_details.method))
        return call
