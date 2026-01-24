import typing
from pydantic_settings import BaseSettings
from pydantic import Field
import pydantic_settings


class AppSettings(BaseSettings):
    app_name: str = Field(default="Backend", description="Application name")
    app_description: str = Field(
        default="Backend", description="Application description"
    )

    https_enabled: bool = Field(default=True, description="Enable HTTPS")


app_settings = AppSettings()


class PostgresSettings(BaseSettings):
    model_config = pydantic_settings.SettingsConfigDict(env_prefix="postgres_")

    host: str = Field(default="localhost", description="Database host")
    port: int = Field(default=5432, description="Database port")
    user: str = Field(default="app", description="Database user")
    password: str = Field(default="passwd", description="Database password")
    app_db: str = Field(default="postgres", description="Database name")

    @property
    def sync_app_database_url(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.app_db}"

    @property
    def async_app_database_url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.app_db}"

postgres_settings = PostgresSettings()


class RedisSettings(BaseSettings):
    model_config = pydantic_settings.SettingsConfigDict(env_prefix="redis_")

    host: str = Field(default="localhost", description="Redis host")
    port: int = Field(default=6379, description="Redis port")
    db: int = Field(default=0, description="Redis database")
    queue_name: str = Field(default="CHANGE_ME", description="Redis queue name")

    @property
    def dsn(self) -> str:
        return f"redis://{self.host}:{self.port}/{self.db}"


redis_settings = RedisSettings()


class SentrySettings(BaseSettings):
    model_config = pydantic_settings.SettingsConfigDict(env_prefix="sentry_")

    enabled: bool = Field(default=False, description="Enable Sentry")
    dsn: str | None = Field(default=None, description="Sentry DSN")


sentry_settings = SentrySettings()


class LoggingSettings(BaseSettings):
    model_config = pydantic_settings.SettingsConfigDict(env_prefix="logging_")

    level: typing.Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO", description="Logging level"
    )


logging_settings = LoggingSettings()


class JWTSettings(BaseSettings):
    model_config = pydantic_settings.SettingsConfigDict(env_prefix="jwt_")

    secret_key: str = Field(
        default="change-me-in-production", description="JWT secret key"
    )
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(
        default=60 * 24 * 7, description="Access token expiration in minutes"
    )


jwt_settings = JWTSettings()

