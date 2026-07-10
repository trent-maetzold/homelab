from modelparams.clients.base import BaseClient
from modelparams.schemas.app import BifrostParameterModel, BifrostPricingModel


class ModelsDevClient(BaseClient):
    """Client that translates models.dev catalog data into Bifrost datasheet format."""

    def to_datasheet(self) -> dict[str, BifrostPricingModel]:
        """Fetch models.dev catalog and return Bifrost pricing entries."""
        ...

    def to_datasheet_model_parameters(self) -> dict[str, BifrostParameterModel]:
        """Fetch models.dev catalog and return Bifrost model-parameter entries."""
        ...
