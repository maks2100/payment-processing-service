import logging
from functools import lru_cache

from pydantic import BaseModel, Field, PostgresDsn, SecretStr, computed_field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.core.enums import Environment


class SettingsBase(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        str_strip_whitespace=True,
        validate_assignment=True,
        env_nested_delimiter="__",
    )


class DatabaseSettings(BaseModel):
    host: str
    port: int = 5432
    user: str
    password: SecretStr
    database: str

    pool_size: int = 5
    pool_max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600
    pool_pre_ping: bool = True

    def _build_url(self, driver: str) -> PostgresDsn:
        return PostgresDsn.build(
            scheme=f"postgresql+{driver}",
            username=self.user,
            password=self.password.get_secret_value(),
            host=self.host,
            port=self.port,
            path=self.database,
        )

    @computed_field(return_type=PostgresDsn)
    @property
    def async_url(self) -> PostgresDsn:
        return self._build_url(driver="asyncpg")


class Settings(SettingsBase):
    environment: Environment = Environment.PRODUCTION
    app_name: str = "Payment Processing Service"
    app_version: str = "VERSION NOT SET"

    api_prefix: str = "/api/v1"
    app_root_path: str = ""

    cors_allow_origins: list[str] = Field(default_factory=list)
    cors_allow_credentials: bool = False
    cors_allow_methods: list[str] = ["GET", "POST", "PATCH", "DELETE", "OPTIONS"]
    cors_allow_headers: list[str] = ["Authorization", "Content-Type"]

    trusted_hosts: list[str] = Field(default_factory=list)

    db: DatabaseSettings

    @property
    def debug(self) -> bool:
        return self.environment == Environment.LOCAL

    @property
    def docs_enabled(self) -> bool:
        return self.environment != Environment.PRODUCTION

    @property
    def log_level(self) -> int:
        if self.environment == Environment.LOCAL:
            return logging.DEBUG
        if self.environment == Environment.DEV:
            return logging.INFO
        return logging.WARNING

    @model_validator(mode="before")
    @classmethod
    def set_environment_defaults(cls, data: dict) -> dict:
        if data.get("environment") == Environment.LOCAL:
            data["cors_allow_origins"] = ["*"]
            data["trusted_hosts"] = ["*"]
        return data

    @model_validator(mode="after")
    def validate_production_safety(self) -> "Settings":
        if self.environment != Environment.LOCAL:
            if not self.cors_allow_origins:
                msg = "cors_allow_origins is required for non-local environments"
                raise ValueError(msg)
            if not self.trusted_hosts:
                msg = "trusted_hosts is required for non-local environments"
                raise ValueError(msg)
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
