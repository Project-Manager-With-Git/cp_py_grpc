from google.protobuf.json_format import MessageToDict
from .sdk import sdk, Client

from .pb import rpc_protos


def main(url: str = "localhost:5000") -> None:
    # req-res
    with sdk.initialize_from_url(url) as conn:
        res, call = conn.Square.with_call(rpc_protos.Message(Message=2.0), metadata=(("a", "1"), ("b", "2")))
        print(call.initial_metadata())
        print(MessageToDict(res))
        print(call.trailing_metadata())
    # req-stream
    with Client(url=url) as conn:
        res_stream = conn.RangeSquare(rpc_protos.Message(Message=4.0))
        for res in res_stream:
            print(MessageToDict(res))
    # stream-res
    sdk.initialize_from_url(url)
    with sdk:
        res = sdk.SumSquare((rpc_protos.Message(Message=float(i)) for i in range(4)))
        print(MessageToDict(res))
    # stream-stream
    with sdk:
        res_stream = sdk.StreamrangeSquare((rpc_protos.Message(Message=float(i)) for i in range(4)), metadata=(("a", "1"), ("b", "2")))
        print(res_stream.initial_metadata())
        for res in res_stream:
            print(MessageToDict(res))
        print(res_stream.trailing_metadata())


if __name__ == "__main__":
    main()
