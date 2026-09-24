from redis.asyncio import Redis

from .configs import SysConfig

redis_client = Redis(
    host="localhost" if SysConfig.DEBUG else SysConfig.REDIS,
    port=6379,
    db=0,
    decode_responses=True,
)


async def invalidar_cache(chave_origem: str):
    async for key in redis_client.scan_iter(f"{chave_origem}:*"):
        await redis_client.delete(key)
