from fastapi import FastAPI, Query

from modelparams.schemas.bifrost import (
    BifrostMode,
    BifrostModelParametersDatasheet,
    BifrostPricingDatasheet,
)

app = FastAPI(
    title="Bifrost Model Parameters",
    description="Translates model metadata from models.dev into Bifrost's datasheet format.",
)


@app.get(
    "/datasheet",
    response_model=BifrostPricingDatasheet,
    summary="Fetch model pricing datasheet",
)
async def get_datasheet(
    provider: str | None = Query(
        default=None, description="Filter by provider identifier"
    ),
    mode: BifrostMode | None = Query(default=None, description="Filter by model mode"),
) -> BifrostPricingDatasheet:
    """Return a pricing datasheet in the Bifrost `pricing_url` format.

    Maps 1:1 to `GET https://getbifrost.ai/datasheet`, translating models.dev
    catalog data into Bifrost pricing entries keyed by model route ID.
    """
    ...


@app.get(
    "/datasheet/model-parameters",
    response_model=BifrostModelParametersDatasheet,
    summary="Fetch model parameter definitions",
)
async def get_datasheet_model_parameters(
    provider: str | None = Query(
        default=None, description="Filter by provider identifier"
    ),
    mode: BifrostMode | None = Query(default=None, description="Filter by model mode"),
) -> BifrostModelParametersDatasheet:
    """Return model parameter definitions in the Bifrost `model_parameters_url` format.

    Maps 1:1 to `GET https://getbifrost.ai/datasheet/model-parameters`, translating
    models.dev catalog data into Bifrost parameter entries keyed by model route ID.
    """
    ...
