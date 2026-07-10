import json

import pytest
from fastapi.testclient import TestClient
from pydantic import TypeAdapter

from modelparams.main import app
from modelparams.schema import (
    BifrostMode,
    BifrostParameterModel,
    BifrostPricingModel,
    Parameter,
    ParameterArray,
    ParameterArrayType,
    ParameterRange,
    ParameterType,
)

client = TestClient(app)

pricing_adapter = TypeAdapter(dict[str, BifrostPricingModel])
params_adapter = TypeAdapter(dict[str, BifrostParameterModel])


class TestPricingSchema:
    """BifrostPricingModel construction and serialization."""

    def test_minimal_model(self):
        """A BifrostPricingModel can be created with only core fields."""
        model = BifrostPricingModel(
            provider="openai",
            base_model="gpt-4",
            mode=BifrostMode.chat,
            input_cost_per_token=0.00001,
            output_cost_per_token=0.00003,
            max_tokens=8192,
            max_input_tokens=8192,
        )
        dumped = model.model_dump(mode="json", exclude_none=True)
        assert dumped["provider"] == "openai"
        assert dumped["base_model"] == "gpt-4"
        assert dumped["mode"] == "chat"
        assert dumped["input_cost_per_token"] == 0.00001
        assert dumped["output_cost_per_token"] == 0.00003
        assert dumped["max_tokens"] == 8192

        # Round-trip through TypeAdapter
        restored = pricing_adapter.validate_json(json.dumps({"gpt-4": dumped}))
        assert restored["gpt-4"].provider == "openai"
        assert restored["gpt-4"].mode == BifrostMode.chat

    def test_image_generation_model(self):
        """An image-generation model uses image-specific cost fields."""
        model = BifrostPricingModel(
            provider="bedrock",
            base_model="dall-e-3",
            mode=BifrostMode.image_generation,
            output_cost_per_image=0.040,
            max_input_tokens=1000,
        )
        dumped = model.model_dump(mode="json", exclude_none=True)
        assert dumped["output_cost_per_image"] == 0.040
        assert "input_cost_per_token" not in dumped


class TestParameterSchema:
    """BifrostParameterModel with nested Parameter objects."""

    def test_model_with_parameters(self):
        """A BifrostParameterModel serialises nested Parameter, Range, and Array."""
        model = BifrostParameterModel(
            provider="openai",
            base_model="gpt-4",
            mode=BifrostMode.chat,
            model_parameters=[
                Parameter(
                    id="temperature",
                    label="Temperature",
                    type=ParameterType.number,
                    range=ParameterRange(min=0.0, max=2.0, step=0.01),
                ),
                Parameter(
                    id="stop_sequences",
                    label="Stop Sequence",
                    type=ParameterType.array,
                    array=ParameterArray(
                        type=ParameterArrayType.text,
                        maxElements=4,
                        minElements=1,
                    ),
                ),
            ],
        )
        dumped = model.model_dump(mode="json", exclude_none=True)
        params = dumped["model_parameters"]
        assert params[0]["id"] == "temperature"
        assert params[0]["range"]["min"] == 0.0
        assert params[0]["range"]["max"] == 2.0
        assert params[0]["type"] == "number"

        assert params[1]["id"] == "stop_sequences"
        assert params[1]["type"] == "array"
        assert params[1]["array"]["maxElements"] == 4
        assert params[1]["array"]["minElements"] == 1

        # Round-trip
        restored = params_adapter.validate_json(json.dumps({"gpt-4": dumped}))
        assert len(restored["gpt-4"].model_parameters) == 2
        assert restored["gpt-4"].model_parameters[0].id == "temperature"

    def test_model_without_parameters(self):
        """BifrostParameterModel tolerates missing model_parameters."""
        model = BifrostParameterModel(
            provider="openai",
            base_model="gpt-4",
        )
        assert model.model_parameters is None


@pytest.mark.integration
class TestEndpointRegistration:
    """Endpoints are registered with the correct method, path, and parameters."""

    def test_datasheet_endpoint(self):
        """GET /datasheet accepts optional provider and mode query params."""
        openapi = app.openapi()
        path = openapi["paths"]["/datasheet"]["get"]
        assert path["summary"] == "Fetch model pricing datasheet"

        params = {p["name"]: p for p in path.get("parameters", [])}
        assert "provider" in params
        assert params["provider"]["in"] == "query"
        assert params["provider"]["required"] is False

        assert "mode" in params
        assert params["mode"]["in"] == "query"
        assert params["mode"]["required"] is False

        # Verify response schema references BifrostPricingModel
        resp_schema = json.dumps(path["responses"]["200"]["content"]["application/json"]["schema"])
        assert "BifrostPricingModel" in resp_schema

    def test_datasheet_model_parameters_endpoint(self):
        """GET /datasheet/model-parameters accepts optional provider and mode."""
        openapi = app.openapi()
        path = openapi["paths"]["/datasheet/model-parameters"]["get"]
        assert path["summary"] == "Fetch model parameter definitions"

        params = {p["name"]: p for p in path.get("parameters", [])}
        assert "provider" in params
        assert "mode" in params

        resp_schema = json.dumps(path["responses"]["200"]["content"]["application/json"]["schema"])
        assert "BifrostParameterModel" in resp_schema
