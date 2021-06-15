import asyncio
from google.protobuf.json_format import MessageToDict
from .sdk import sdk, Client
from .pb import rpc_protos


async def _cli_exp(url: str = "localhost:5000") -> None:
    # req-res
    async with sdk.initialize_from_url(url) as conn:
        res = await conn.Square(rpc_protos.Message(Message=2.0))
        print(MessageToDict(res))
    # req-stream
    async with Client(url=url) as conn:
        res_stream = conn.RangeSquare(rpc_protos.Message(Message=4.0))
        async for res in res_stream:
            print(MessageToDict(res))
    # stream-res
    sdk.initialize_from_url(url)
    async with sdk:
        res = await sdk.SumSquare((rpc_protos.Message(Message=float(i)) for i in range(4)))
        print(MessageToDict(res))
    # stream-stream
    async with sdk:
        res_stream = sdk.StreamrangeSquare((rpc_protos.Message(Message=float(i)) for i in range(4)))
        async for res in res_stream:
            print(MessageToDict(res))


def main(url: str = "localhost:5000") -> None:
    asyncio.run(_cli_exp(url))


if __name__ == "__main__":
    main()
