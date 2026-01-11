from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    app_name: str = ""
    app_env: str = ""
    db_url: str = ""
    access_token_key: str = ""
    refresh_token_key: str = ""
    access_token_expire_time: str = ""
    refresh_token_expire_time: str = ""
    db_dev: str = ""
    imagekit_private_key: str = ""
    imagekit_url_endpoint: str = ""
    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def getAppConfig():
    return AppConfig()
