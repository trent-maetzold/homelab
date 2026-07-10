from enum import StrEnum

from pydantic_settings import BaseSettings, SettingsConfigDict

_SOURCE_URLS = {
    "models.dev": "https://models.dev/api.json",
    "getbifrost.ai": "https://getbifrost.ai",
}


class Source(StrEnum):
    """Model data source provider."""

    MODELS_DEV = "models.dev"
    GETBIFROST_AI = "getbifrost.ai"

    @property
    def url(self) -> str:
        """Return the API base URL for this data source."""
        return _SOURCE_URLS[self.value]


class Settings(BaseSettings):
    """Application settings, prefixed with BIFROST_MODEL_PARAMS_."""

    source: Source = Source.MODELS_DEV

    pricing_url: str = "https://getbifrost.ai/datasheet"
    url: str = "https://getbifrost.ai/datasheet/model-parameters"

    model_config = SettingsConfigDict(env_prefix="bifrost_model_params")
