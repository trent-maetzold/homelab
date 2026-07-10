import json
from pathlib import Path

import httpx2
import pytest

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
    from modelparams.clients.models_dev import ModelsDevClient

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

    def test_to_datasheet_returns_pricing(self, client):
        """to_datasheet() returns BifrostPricingDatasheet with entries."""
        datasheet = client.to_datasheet()
        assert isinstance(datasheet, BifrostPricingDatasheet)
        assert len(datasheet.root) > 0

        # Check a sample entry has required fields
        sample = next(iter(datasheet.root.values()))
        assert sample.provider is not None
        assert sample.base_model is not None
        assert sample.mode is not None

    def test_to_datasheet_model_parameters_returns_params(self, client):
        """to_datasheet_model_parameters() returns BifrostModelParametersDatasheet."""
        datasheet = client.to_datasheet_model_parameters()
        assert isinstance(datasheet, BifrostModelParametersDatasheet)
        assert len(datasheet.root) > 0

        sample = next(iter(datasheet.root.values()))
        assert sample.provider is not None
        assert sample.base_model is not None

    def test_cached_catalog_reused(self, client):
        """Second call without re-fetching still returns results."""
        # First call fetches
        _ = client.from_api()
        # Second call should use cache, not re-fetch
        datasheet = client.to_datasheet()
        assert isinstance(datasheet, BifrostPricingDatasheet)
        assert len(datasheet.root) > 0
