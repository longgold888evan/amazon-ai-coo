from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"
    log_level: str = "INFO"
    database_url: str | None = None

    amazon_ads_client_id: str | None = None
    amazon_ads_client_secret: str | None = None
    amazon_ads_refresh_token: str | None = None
    amazon_ads_profile_id: str | None = None

    sp_api_client_id: str | None = None
    sp_api_client_secret: str | None = None
    sp_api_refresh_token: str | None = None
    sp_api_marketplace_id: str | None = None

    sellersprite_base_url: str | None = None
    sellersprite_api_key: str | None = None
    openai_api_key: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
