from modelparams.config import Settings, Source

from .base import BaseClient
from .getbifrost_ai import GetBifrostAiClient
from .models_dev import ModelsDevClient

_settings = Settings()
_CLIENTS = {
    Source.MODELS_DEV: ModelsDevClient,
    Source.GETBIFROST_AI: GetBifrostAiClient,
}


def get_client() -> BaseClient:
    return _CLIENTS[_settings.source]()
