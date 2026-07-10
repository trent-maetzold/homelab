from abc import ABC, abstractmethod

from modelparams.schemas.app import BifrostParameterModel, BifrostPricingModel


class BaseClient(ABC):
    @abstractmethod
    def to_datasheet(self) -> dict[str, BifrostPricingModel]: ...

    @abstractmethod
    def to_datasheet_model_parameters(self) -> dict[str, BifrostParameterModel]: ...
