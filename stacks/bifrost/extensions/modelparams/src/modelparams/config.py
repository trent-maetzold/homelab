from enum import Enum

from pydantic_settings import BaseSettings, SettingsConfigDict


class Source(Enum):
    MODELS_DEV = 1


class Settings(BaseSettings):
    source: Source = Source.MODELS_DEV

    model_config = SettingsConfigDict(env_prefix="bifrost_model_params")
