import httpx2

from modelparams.clients.base import BaseClient
from modelparams.config import Settings
from modelparams.schemas.getbifrost_ai import (
    BifrostMode,
    BifrostModelParametersDatasheet,
    BifrostPricingDatasheet,
    ParameterModel,
    PricingModel,
)

settings = Settings()


class GetBifrostAiClient(BaseClient):
    """Passthrough client that fetches Bifrost-format data from getbifrost.ai."""

    def to_pricing_datasheet(
        self, provider: str | None = None, mode: BifrostMode | None = None
    ) -> BifrostPricingDatasheet:
        """Fetch pricing datasheet from getbifrost.ai and validate through PricingModel."""
        r = httpx2.get(settings.pricing_url, follow_redirects=True, timeout=30)
        r.raise_for_status()
        raw = r.json()
        entries: dict[str, PricingModel] = {}

        for key, entry in raw.items():
            parsed = PricingModel.model_validate(entry)
            if provider is not None and parsed.provider != provider:
                continue
            if mode is not None and parsed.mode != mode:
                continue
            entries[key] = parsed

        return BifrostPricingDatasheet(root=entries)

    def to_model_parameters_datasheet(
        self, provider: str | None = None, mode: BifrostMode | None = None
    ) -> BifrostModelParametersDatasheet:
        """Fetch parameter datasheet from getbifrost.ai and validate through ParameterModel."""
        r = httpx2.get(settings.url, follow_redirects=True, timeout=30)
        r.raise_for_status()
        raw = r.json()
        entries: dict[str, ParameterModel] = {}

        for key, entry in raw.items():
            parsed = ParameterModel.model_validate(entry)
            if provider is not None and parsed.provider != provider:
                continue
            if mode is not None and parsed.mode != mode:
                continue
            entries[key] = parsed

        return BifrostModelParametersDatasheet(root=entries)
