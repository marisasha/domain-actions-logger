from pydantic_settings import BaseSettings
from pydantic import BaseModel


class RedisConfig(BaseModel):
    host: str
    port: int
    db: int


class CacheConfig(BaseModel):
    prefix: str
    expire_seconds: int


class Settings(BaseSettings):
    redis: RedisConfig
    cache: CacheConfig

    class Config:
        env_file = "../.env"
        env_nested_delimiter = "__"


settings = Settings()
