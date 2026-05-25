from pydantic_settings import BaseSettings
from pydantic import BaseModel


class RedisConfig(BaseModel):
    host: str = "redis"
    port: int = 6379
    db: int = 0

    class Config:
        env_prefix = "REDIS_"


class CacheConfig(BaseModel):
    prefix: str = "fastapi"
    expire_seconds: int = 300


class Settings(BaseSettings):

    redis: RedisConfig = RedisConfig()
    cache: CacheConfig = CacheConfig()

    class Config:
        env_file = "../.env"


settings = Settings()
print(f"🔍 Redis config: host={settings.redis.host}, port={settings.redis.port}")
