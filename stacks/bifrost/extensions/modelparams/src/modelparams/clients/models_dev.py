import httpx2

from modelparams.clients.base import BaseClient
from modelparams.schemas.bifrost import (
    BifrostMode,
    BifrostModelParametersDatasheet,
    BifrostPricingDatasheet,
    ParameterModel,
    PricingModel,
)
from modelparams.schemas.clients.models_dev import ModelsDevCatalog


_MODELS_DEV_URL = "https://models.dev/api.json"


class ModelsDevClient(BaseClient):
    """Client that translates models.dev catalog data into Bifrost datasheet format."""

    def __init__(self) -> None:
        self._catalog: ModelsDevCatalog | None = None

    def from_api(self) -> ModelsDevCatalog:
        """Fetch the models.dev catalog and parse it through ModelsDevCatalog."""
        r = httpx2.get(_MODELS_DEV_URL, follow_redirects=True, timeout=30)
        r.raise_for_status()
        self._catalog = ModelsDevCatalog.model_validate_json(r.text)
        return self._catalog

    def _ensure_catalog(self) -> ModelsDevCatalog:
        if self._catalog is not None:
            return self._catalog
        return self.from_api()

    @staticmethod
    def _infer_mode(model) -> BifrostMode:
        """Guess Bifrost mode from a model's modalities."""
        if model.modalities and model.modalities.input:
            has_image = any(m.value == "image" for m in model.modalities.input)
            if has_image:
                return BifrostMode.image_generation
        return BifrostMode.chat

    @staticmethod
    def _cost_per_token(cost_per_million: float | None) -> float | None:
        """Convert per-million-token cost to per-token cost."""
        if cost_per_million is None:
            return None
        return cost_per_million / 1_000_000

    def to_datasheet(self) -> BifrostPricingDatasheet:
        """Translate the models.dev catalog into Bifrost pricing datasheet format."""
        catalog = self._ensure_catalog()
        entries: dict[str, PricingModel] = {}

        for provider_id, provider in catalog.root.items():
            if not provider.models:
                continue
            for model_id, model in provider.models.items():
                cost = model.cost
                limit = model.limit
                mods = model.modalities

                entry = PricingModel(
                    provider=provider_id,
                    base_model=model_id,
                    mode=self._infer_mode(model),
                    input_cost_per_token=self._cost_per_token(cost.input if cost else None),
                    output_cost_per_token=self._cost_per_token(cost.output if cost else None),
                    cache_read_input_token_cost=self._cost_per_token(cost.cache_read if cost else None),
                    max_input_tokens=limit.context if limit else None,
                    max_output_tokens=limit.output if limit else None,
                    max_tokens=limit.output if limit else None,
                    supports_vision=bool(mods and any(m.value == "image" for m in mods.input)),
                    supports_function_calling=model.tool_call,
                    supports_system_messages=True,
                    supports_prompt_caching=bool(cost and cost.cache_read is not None),
                    supports_response_schema=model.structured_output,
                    supports_reasoning=model.reasoning,
                    supported_endpoints=["chat"],
                )
                entries[model_id] = entry

        return BifrostPricingDatasheet(root=entries)

    def to_datasheet_model_parameters(self) -> BifrostModelParametersDatasheet:
        """Translate the models.dev catalog into Bifrost model-parameters format."""
        catalog = self._ensure_catalog()
        entries: dict[str, ParameterModel] = {}

        for provider_id, provider in catalog.root.items():
            if not provider.models:
                continue
            for model_id, model in provider.models.items():
                cost = model.cost
                limit = model.limit
                mods = model.modalities

                entry = ParameterModel(
                    provider=provider_id,
                    base_model=model_id,
                    mode=self._infer_mode(model),
                    input_cost_per_token=self._cost_per_token(cost.input if cost else None),
                    output_cost_per_token=self._cost_per_token(cost.output if cost else None),
                    cache_read_input_token_cost=self._cost_per_token(cost.cache_read if cost else None),
                    max_input_tokens=limit.context if limit else None,
                    max_output_tokens=limit.output if limit else None,
                    max_tokens=limit.output if limit else None,
                    supports_vision=bool(mods and any(m.value == "image" for m in mods.input)),
                    supports_function_calling=model.tool_call,
                    supports_system_messages=True,
                    supports_prompt_caching=bool(cost and cost.cache_read is not None),
                    supports_response_schema=model.structured_output,
                    supports_reasoning=model.reasoning,
                    supported_endpoints=["chat"],
                    model_parameters=[],
                )
                entries[model_id] = entry

        return BifrostModelParametersDatasheet(root=entries)
