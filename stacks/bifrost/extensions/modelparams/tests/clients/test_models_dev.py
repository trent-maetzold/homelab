import json
from pathlib import Path

import httpx2
import pytest

from modelparams.clients.models_dev import ModelsDevClient
from modelparams.schemas.bifrost import (
    BifrostModelParametersDatasheet,
    BifrostPricingDatasheet,
)
from modelparams.schemas.clients.models_dev import ModelsDevCatalog

FIXTURE = Path(__file__).parent / "fixtures" / "models_dev_subset.json"


@pytest.fixture
def mock_models_dev(mocker):
    """Patch httpx2.get to return the fixture data."""
    raw = FIXTURE.read_text()
    response = httpx2.Response(200, content=raw)
    response._request = httpx2.Request("GET", "https://models.dev/api.json")

    mocker.patch.object(httpx2, "get", return_value=response)


@pytest.fixture
def client(mock_models_dev):
    return ModelsDevClient()


class TestModelsDevClient:
    """ModelsDevClient returns correctly typed Pydantic models."""

    def test_from_api_returns_catalog(self, client):
        """from_api() returns a ModelsDevCatalog with expected providers."""
        catalog = client.from_api()
        assert isinstance(catalog, ModelsDevCatalog)
        assert len(catalog.root) == 3
        assert "openai" in catalog.root
        assert "anthropic" in catalog.root
        assert "google" in catalog.root

    def test_to_pricing_datasheet_returns_pricing(self, client):
        """to_pricing_datasheet() returns BifrostPricingDatasheet with entries."""
        datasheet = client.to_pricing_datasheet()
        assert isinstance(datasheet, BifrostPricingDatasheet)
        assert len(datasheet.root) > 0

        sample = next(iter(datasheet.root.values()))
        assert sample.provider is not None
        assert sample.base_model is not None
        assert sample.mode is not None

    def test_to_model_parameters_datasheet_returns_params(self, client):
        """to_model_parameters_datasheet() returns BifrostModelParametersDatasheet."""
        datasheet = client.to_model_parameters_datasheet()
        assert isinstance(datasheet, BifrostModelParametersDatasheet)
        assert len(datasheet.root) > 0

        sample = next(iter(datasheet.root.values()))
        assert sample.provider is not None
        assert sample.base_model is not None

    def test_filter_by_provider(self, client):
        """Filtering by provider returns only that provider's models."""
        ds = client.to_pricing_datasheet(provider="openai")
        assert all(m.provider == "openai" for m in ds.root.values())
        assert len(ds.root) > 0

    def test_filter_by_mode(self, client):
        """Filtering by mode returns only matching entries."""
        ds = client.to_pricing_datasheet(mode="chat")
        if ds.root:
            sample = next(iter(ds.root.values()))
            assert sample.mode == "chat"

    def test_filter_unknown_provider_returns_empty(self, client):
        """Filtering by unknown provider returns empty datasheet."""
        ds = client.to_pricing_datasheet(provider="nonexistent")
        assert len(ds.root) == 0

    def test_cached_catalog_reused(self, client):
        """Second call without re-fetching still returns results."""
        _ = client.from_api()
        datasheet = client.to_pricing_datasheet()
        assert isinstance(datasheet, BifrostPricingDatasheet)
        assert len(datasheet.root) > 0
