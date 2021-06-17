import asyncio
from google.protobuf.json_format import MessageToDict
from pyloggerhelper import log
from .sdk import sdk, Client
from echo_pb.echo_pb2 import Message


async def _cli_exp(url: str = "localhost:5000") -> None:
    log.initialize_for_app(app_name="sdk", log_level="DEBUG")
    # req-res
    async with sdk.initialize_from_url(url) as conn:
        ctx = conn.Square(Message(Message=2.0), metadata=(("a", "1"), ("b", "2")))
        header = await ctx.initial_metadata()
        res = await ctx
        trailing = await ctx.trailing_metadata()
        log.info("Square get result", res=MessageToDict(res), header=header, trailing=trailing)
    # req-stream
    async with Client(url=url) as conn:
        res_stream = conn.RangeSquare(Message(Message=4.0))
        async for res in res_stream:
            log.info("RangeSquare get msg", res=MessageToDict(res))
    # stream-res
    sdk.initialize_from_url(url)
    async with sdk:
        res = await sdk.SumSquare((Message(Message=float(i)) for i in range(4)))
        log.info("SumSquare get result", res=MessageToDict(res))
    # stream-stream
    async with sdk:
        res_stream = sdk.StreamrangeSquare((Message(Message=float(i)) for i in range(4)), metadata=(("a", "1"), ("b", "2")))
        header = await res_stream.initial_metadata()
        async for res in res_stream:
            log.info("StreamrangeSquare get msg", res=MessageToDict(res))
        trailing = await res_stream.trailing_metadata()
        log.info("StreamrangeSquare done", header=header, trailing=trailing)


def main(url: str = "ipv4:127.0.0.1:5001,127.0.0.1:5000") -> None:
    asyncio.run(_cli_exp(url))


if __name__ == "__main__":
    main()
