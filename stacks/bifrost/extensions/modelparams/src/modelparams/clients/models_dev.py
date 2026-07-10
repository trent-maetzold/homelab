from modelparams.clients.base import BaseClient
from modelparams.schemas.bifrost import (
    BifrostModelParametersDatasheet,
    BifrostPricingDatasheet,
)
from modelparams.schemas.clients.models_dev import ModelsDevCatalog


class ModelsDevClient(BaseClient):
    """Client that translates models.dev catalog data into Bifrost datasheet format."""

    def from_api(self) -> ModelsDevCatalog: ...

    def to_datasheet(self) -> BifrostPricingDatasheet:
        """Fetch models.dev catalog and return Bifrost pricing entries."""
        ...

    def to_datasheet_model_parameters(self) -> BifrostModelParametersDatasheet:
        """Fetch models.dev catalog and return Bifrost model-parameter entries."""
        ...
