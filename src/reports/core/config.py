from pydantic_settings import BaseSettings
from pydantic import SecretStr


class Settings(BaseSettings):
    APP_PORT: int

    RABBITMQ_HOST: str
    RABBITMQ_PORT: int
    RABBITMQ_USER: SecretStr
    RABBITMQ_PASSWORD: SecretStr
    RABBITMQ_EXCHANGE: str
    RABBITMQ_ROUTING_KEY_TO_GENERATION: str
    RABBITMQ_ROUTING_KEY_GENERATED: str

    MINIO_HOST: str
    MINIO_PORT: int
    MINIO_ROOT_USER: SecretStr
    MINIO_ROOT_PASSWORD: SecretStr
    MINIO_BUCKET_NAME: str

    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_USER: SecretStr
    POSTGRES_PASSWORD: SecretStr
    MIN_POOL_SIZE: int = 5
    MAX_POOL_SIZE: int = 10

    OSM_TILE_URL: str
    OSM_ATTRIBUTION: str
    LEAFLET_JS_URL: str
    LEAFLET_JS_INTEGRITY: str
    LEAFLET_JS_CROSSORIGIN: str
    LEAFLET_CSS_URL: str
    LEAFLET_CSS_INTEGRITY: str
    LEAFLET_CSS_CROSSORIGIN: str

    @property
    def rabbit_url(self) -> str:
        return (
            f"amqp://{self.RABBITMQ_USER.get_secret_value()}:{self.RABBITMQ_PASSWORD.get_secret_value()}"
            f"@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}/"
        )

    @property
    def minio_url(self) -> str:
        return f"http://{self.MINIO_HOST}:{self.MINIO_PORT}"

    @property
    def postgres_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER.get_secret_value()}:{self.POSTGRES_PASSWORD.get_secret_value()}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings()


