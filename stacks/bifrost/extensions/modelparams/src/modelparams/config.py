from enum import Enum

from pydantic_settings import BaseSettings, SettingsConfigDict


class Source(Enum):
    """Model data source provider."""

    MODELS_DEV = 1


class Settings(BaseSettings):
    """Application settings, prefixed with BIFROST_MODEL_PARAMS_."""

    source: Source = Source.MODELS_DEV

    model_config = SettingsConfigDict(env_prefix="bifrost_model_params")
