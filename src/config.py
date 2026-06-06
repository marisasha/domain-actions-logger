from pydantic_settings import BaseSettings
from pydantic import BaseModel


class RedisConfig(BaseModel):
    host: str
    port: int
    db: int


class CacheConfig(BaseModel):
    prefix: str
    expire_seconds: int


class RabbitConfig(BaseModel):
    host: str
    port: int
    user: str
    password: str
    vhost: str
    ssl: bool

    def get_rabbitmq_url(self):
        scheme = "amqps" if self.ssl else "amqp"
        return f"{scheme}://{self.user}:{self.password}@{self.host}:{self.port}/{self.vhost}"


class EmailConfig(BaseModel):
    host: str
    port: int
    user: str
    password: str


class Settings(BaseSettings):
    redis: RedisConfig
    cache: CacheConfig
    rabbit: RabbitConfig
    email: EmailConfig

    class Config:
        env_file = "../.env"
        env_nested_delimiter = "__"


settings = Settings()
