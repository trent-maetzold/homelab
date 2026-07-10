from abc import ABC, abstractmethod

from modelparams.schemas.app import (
    BifrostParameterModels,
    BifrostPricingModels,
)


class BaseClient(ABC):
    """Abstract client for translating provider model data into Bifrost datasheet format."""

    @abstractmethod
    def to_datasheet(self) -> BifrostPricingModels:
        """Translate provider model catalog into Bifrost pricing datasheet format."""
        ...

    @abstractmethod
    def to_datasheet_model_parameters(self) -> BifrostParameterModels:
        """Translate provider model catalog into Bifrost model-parameters format."""
        ...
