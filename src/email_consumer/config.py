from pydantic import BaseModel
from pydantic_settings import BaseSettings


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


class EmailSenderConfig(BaseModel):
    host: str
    port: int
    user: str
    password: str


class EmailSettings(BaseSettings):
    rabbit: RabbitConfig
    email: EmailSenderConfig

    class Config:
        env_file = "../.env"
        env_nested_delimiter = "__"


settings = EmailSettings()
