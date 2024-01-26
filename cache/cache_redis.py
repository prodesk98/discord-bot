import asyncio
from orjson import dumps

import redis.asyncio as aredis

from typing import Union

from config import env

client = aredis.Redis.from_url(env.REDIS_DSN)

async def aset(name: str, value: bytes, ex: int = 900) -> None:
    await client.set(name=name, value=value, ex=ex)

async def aget(name: str) -> Union[bytes, None]:
    return await client.get(name)

async def adel(*names: str) -> None:
    await client.delete(*names)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(aset("test:cooldown:1", dumps({"tst": 1})))
    print(loop.run_until_complete(aget("test:cooldown:1")))
