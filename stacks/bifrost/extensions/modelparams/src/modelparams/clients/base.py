from abc import ABC, abstractmethod

from modelparams.schemas.bifrost import (
    BifrostModelParametersDatasheet,
    BifrostPricingDatasheet,
)


class BaseClient(ABC):
    """Abstract client for translating provider model data into Bifrost datasheet format."""

    @abstractmethod
    def to_datasheet(self) -> BifrostPricingDatasheet:
        """Translate provider model catalog into Bifrost pricing datasheet format."""
        ...

    @abstractmethod
    def to_datasheet_model_parameters(self) -> BifrostModelParametersDatasheet:
        """Translate provider model catalog into Bifrost model-parameters format."""
        ...
