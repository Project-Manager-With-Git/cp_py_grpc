import asyncio
from google.protobuf.json_format import MessageToDict
from .sdk import client, Client
from echo_pb.echo_pb2 import Message


async def _cli_exp(url: str = "localhost:5000") -> None:
    # req-res
    async with client.initialize_from_url(url) as conn:
        res = await conn.Square(Message(Message=2.0))
        print(MessageToDict(res))
    # req-stream
    async with Client(url=url) as conn:
        res_stream = conn.RangeSquare(Message(Message=4.0))
        async for res in res_stream:
            print(MessageToDict(res))
    # stream-res
    client.initialize_from_url(url)
    async with client:
        res = await client.SumSquare((Message(Message=float(i)) for i in range(4)))
        print(MessageToDict(res))
    # stream-stream
    async with client:
        res_stream = client.StreamrangeSquare((Message(Message=float(i)) for i in range(4)))
        async for res in res_stream:
            print(MessageToDict(res))


def main(url: str = "localhost:5000") -> None:
    asyncio.run(_cli_exp(url))


if __name__ == "__main__":
    main()
