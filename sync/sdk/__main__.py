from google.protobuf.json_format import MessageToDict
from pyloggerhelper import log
from .sdk import sdk, Client
from echo_pb.echo_pb2 import Message


def main(url: str = "localhost:5000") -> None:
    log.initialize_for_app(app_name="sdk", log_level="DEBUG")
    # req-res
    with sdk.initialize_from_url(url) as conn:
        res, call = conn.Square.with_call(Message(Message=2.0), metadata=(("a", "1"), ("b", "2")))
        header = call.initial_metadata()
        trailing = call.trailing_metadata()
        log.info("Square get result", res=MessageToDict(res), header=header, trailing=trailing)
    # req-stream
    with Client(url=url) as conn:
        res_stream = conn.RangeSquare(Message(Message=4.0))
        for res in res_stream:
            log.info("RangeSquare get msg", res=MessageToDict(res))
    # stream-res
    sdk.initialize_from_url(url)
    with sdk:
        res = sdk.SumSquare((Message(Message=float(i)) for i in range(4)))
        log.info("SumSquare get result", res=MessageToDict(res))
    # stream-stream
    with sdk:
        res_stream = sdk.StreamrangeSquare((Message(Message=float(i)) for i in range(4)), metadata=(("a", "1"), ("b", "2")))
        header = res_stream.initial_metadata()
        for res in res_stream:
            log.info("StreamrangeSquare get msg", res=MessageToDict(res))
        trailing = res_stream.trailing_metadata()
        log.info("StreamrangeSquare done", header=header, trailing=trailing)


if __name__ == "__main__":
    main()
