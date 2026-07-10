from abc import ABC, abstractmethod

from modelparams.schemas.app import BifrostParameterModel, BifrostPricingModel


class BaseClient(ABC):
    """Abstract client for translating provider model data into Bifrost datasheet format."""

    @abstractmethod
    def to_datasheet(self) -> dict[str, BifrostPricingModel]:
        """Translate provider model catalog into Bifrost pricing datasheet format."""
        ...

    @abstractmethod
    def to_datasheet_model_parameters(self) -> dict[str, BifrostParameterModel]:
        """Translate provider model catalog into Bifrost model-parameters format."""
        ...
