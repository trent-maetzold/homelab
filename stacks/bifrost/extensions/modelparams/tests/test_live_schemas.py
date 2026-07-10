import pytest
import httpx2
from pydantic import ValidationError

pytestmark = pytest.mark.integration


def test_models_dev_schema():
    """models.dev/api.json parses cleanly against ModelCatalog."""
    r = httpx2.get("https://models.dev/api.json", follow_redirects=True, timeout=30)
    r.raise_for_status()

    try:
        from modelparams.schemas.clients.models_dev import ModelsDevCatalog

        catalog = ModelsDevCatalog.model_validate_json(r.text)
    except ValidationError as e:
        pytest.fail(f"ModelsDevCatalog validation failed:\n{e}")

    # Sanity-check a few known entries
    assert len(catalog.root) > 0, "catalog has no providers"
    # Spot-check a provider has models
    sample_providers = list(catalog.root.values())
    non_empty = [p for p in sample_providers if p.models]
    assert non_empty, "no provider has any models"
    sample_model = list(non_empty[0].models.values())[0]
    # Core fields should be present on most models
    assert sample_model.id is not None
    assert sample_model.name is not None


def test_bifrost_pricing_schema():
    """Bifrost /datasheet entries all parse cleanly against PricingModel."""
    r = httpx2.get("https://getbifrost.ai/datasheet", follow_redirects=True, timeout=30)
    r.raise_for_status()
    raw = r.json()

    from modelparams.schemas.bifrost import PricingModel

    errors = []
    for key, entry in raw.items():
        try:
            PricingModel.model_validate(entry)
        except ValidationError as e:
            errors.append((key, str(e)))

    if errors:
        lines = "\n".join(f"  {k}: {v}" for k, v in errors[:5])
        pytest.fail(f"{len(errors)} entries failed validation:\n{lines}")

    assert len(raw) > 0, "datasheet is empty"


def test_bifrost_parameters_schema():
    """Bifrost /datasheet/model-parameters entries parse against ParameterModel."""
    r = httpx2.get(
        "https://getbifrost.ai/datasheet/model-parameters",
        follow_redirects=True,
        timeout=30,
    )
    r.raise_for_status()
    raw = r.json()

    from modelparams.schemas.bifrost import ParameterModel

    errors = []
    for key, entry in raw.items():
        try:
            ParameterModel.model_validate(entry)
        except ValidationError as e:
            errors.append((key, str(e)))

    if errors:
        lines = "\n".join(f"  {k}: {v}" for k, v in errors[:5])
        pytest.fail(f"{len(errors)} entries failed validation:\n{lines}")

    assert len(raw) > 0, "parameters datasheet is empty"
