from modelparams.clients.base import BaseClient
from modelparams.schemas.app import BifrostParameterModel, BifrostPricingModel


class ModelsDevClient(BaseClient):
    def to_datasheet(self) -> dict[str, BifrostPricingModel]: ...

    def to_datasheet_model_parameters(self) -> dict[str, BifrostParameterModel]: ...
