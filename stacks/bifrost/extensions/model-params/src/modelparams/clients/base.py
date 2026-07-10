from abc import ABC, abstractmethod

from modelparams.schemas.getbifrost_ai import (
    BifrostMode,
    BifrostModelParametersDatasheet,
    BifrostPricingDatasheet,
)


class BaseClient(ABC):
    """Abstract client for translating provider model data into Bifrost datasheet format."""

    @abstractmethod
    def to_pricing_datasheet(
        self, provider: str | None = None, mode: BifrostMode | None = None
    ) -> BifrostPricingDatasheet:
        """Translate provider model catalog into Bifrost pricing datasheet format."""
        ...

    @abstractmethod
    def to_model_parameters_datasheet(
        self, provider: str | None = None, mode: BifrostMode | None = None
    ) -> BifrostModelParametersDatasheet:
        """Translate provider model catalog into Bifrost model-parameters format."""
        ...
