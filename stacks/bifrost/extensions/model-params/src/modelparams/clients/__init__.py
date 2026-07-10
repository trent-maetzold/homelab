from modelparams.config import Settings, Source

from .base import BaseClient
from .models_dev import ModelsDevClient

_settings = Settings()
_CLIENTS = {Source.MODELS_DEV: ModelsDevClient}


def get_client() -> BaseClient:
    return _CLIENTS[_settings.source]()
