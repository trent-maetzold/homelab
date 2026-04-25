# Add OpenCode Go Models to TensorZero Configuration

## Objective

Add all OpenCode Go models to the `stacks/tensorzero/config/tensorzero.toml` configuration file, using OpenRouter as the provider since these models are available through OpenRouter.

## Current State

- `stacks/tensorzero/config/tensorzero.toml` is currently empty
- TensorZero gateway is already configured with `OPENROUTER_API_KEY` environment variable
- TensorZero supports OpenRouter as a provider type

## Models to Add

Based on the user's requirements, the following models need to be configured:

| Model Display Name | Provider Source | TensorZero Model Name | OpenRouter Model ID |
|-------------------|-----------------|----------------------|---------------------|
| GLM-5.1 | DeepInfra, Z.ai | `glm-5.1` | `thudm/glm-5.1` |
| GLM-5 | DeepInfra, Z.ai | `glm-5` | `thudm/glm-5` |
| Kimi K2.5 | Moonshot AI | `kimi-k2.5` | `moonshot/kimi-k2.5` |
| Kimi K2.6 | Moonshot AI | `kimi-k2.6` | `moonshot/kimi-k2.6` |
| MiMo-V2-Pro | Xiaomi MiMo | `mimo-v2-pro` | `xiaomi/mimo-v2-pro` |
| MiMo-V2-Omni | Xiaomi MiMo | `mimo-v2-omni` | `xiaomi/mimo-v2-omni` |
| Qwen3.5 Plus | Alibaba Cloud | `qwen3.5-plus` | `alibaba/qwen3.5-plus` |
| Qwen3.6 Plus | Alibaba Cloud | `qwen3.6-plus` | `alibaba/qwen3.6-plus` |
| MiniMax M2.7 | MiniMax | `minimax-m2.7` | `minimax/minimax-m2.7` |
| MiniMax M2.5 | MiniMax | `minimax-m2.5` | `minimax/minimax-m2.5` |

## TensorZero Configuration Format

Each model in TensorZero is defined using the following TOML structure:

```toml
[models.model_name]
routing = ["provider_name"]

[models.model_name.providers.provider_name]
type = "openrouter"
model_name = "openrouter/model-id"
```

## Implementation Plan

- [ ] **Task 1: Create tensorzero.toml with all OpenCode Go models**
  - Write complete TOML configuration to `stacks/tensorzero/config/tensorzero.toml`
  - Configure all 10 models listed above
  - Use OpenRouter as the provider type for each model
  - Follow TensorZero naming conventions (kebab-case for model names)
  - Use appropriate OpenRouter model IDs

- [ ] **Task 2: Validate TOML syntax**
  - Ensure the configuration file is valid TOML
  - Verify no syntax errors that would prevent TensorZero from parsing

- [ ] **Task 3: Commit and push changes**
  - Stage the new configuration file
  - Commit with descriptive message
  - Push to the remote repository

## Configuration File Content

The following content should be written to `stacks/tensorzero/config/tensorzero.toml`:

```toml
# OpenCode Go Models Configuration
# All models configured to use OpenRouter provider

[models.glm-5.1]
routing = ["openrouter"]

[models.glm-5.1.providers.openrouter]
type = "openrouter"
model_name = "thudm/glm-5.1"

[models.glm-5]
routing = ["openrouter"]

[models.glm-5.providers.openrouter]
type = "openrouter"
model_name = "thudm/glm-5"

[models.kimi-k2.5]
routing = ["openrouter"]

[models.kimi-k2.5.providers.openrouter]
type = "openrouter"
model_name = "moonshot/kimi-k2.5"

[models.kimi-k2.6]
routing = ["openrouter"]

[models.kimi-k2.6.providers.openrouter]
type = "openrouter"
model_name = "moonshot/kimi-k2.6"

[models.mimo-v2-pro]
routing = ["openrouter"]

[models.mimo-v2-pro.providers.openrouter]
type = "openrouter"
model_name = "xiaomi/mimo-v2-pro"

[models.mimo-v2-omni]
routing = ["openrouter"]

[models.mimo-v2-omni.providers.openrouter]
type = "openrouter"
model_name = "xiaomi/mimo-v2-omni"

[models.qwen3.5-plus]
routing = ["openrouter"]

[models.qwen3.5-plus.providers.openrouter]
type = "openrouter"
model_name = "alibaba/qwen3.5-plus"

[models.qwen3.6-plus]
routing = ["openrouter"]

[models.qwen3.6-plus.providers.openrouter]
type = "openrouter"
model_name = "alibaba/qwen3.6-plus"

[models.minimax-m2.7]
routing = ["openrouter"]

[models.minimax-m2.7.providers.openrouter]
type = "openrouter"
model_name = "minimax/minimax-m2.7"

[models.minimax-m2.5]
routing = ["openrouter"]

[models.minimax-m2.5.providers.openrouter]
type = "openrouter"
model_name = "minimax/minimax-m2.5"
```

## Verification Criteria

- [ ] `stacks/tensorzero/config/tensorzero.toml` exists and is valid TOML
- [ ] All 10 OpenCode Go models are defined
- [ ] Each model uses `type = "openrouter"` in its provider configuration
- [ ] Model names use kebab-case convention
- [ ] OpenRouter model IDs follow the `provider/model-name` format
- [ ] File is committed and pushed to the repository

## Notes for Execution Agent

1. The `tensorzero.toml` file is currently empty (0 bytes)
2. Use `toml` validation tool or Python's `toml` module to verify syntax after writing
3. The OpenRouter API key is already configured in the environment (`OPENROUTER_API_KEY`)
4. No changes needed to `compose.yaml` - configuration is read from the mounted `tensorzero.toml`
5. After deployment, models will be accessible via TensorZero gateway using their model names (e.g., `glm-5.1`, `kimi-k2.5`, etc.)

## Potential Risks and Mitigations

1. **Invalid TOML syntax**: Use a TOML validator after writing the file
2. **OpenRouter model ID changes**: Verify model IDs are current on OpenRouter's website
3. **Model availability**: Some models may not be available immediately on OpenRouter - monitor for 404 errors

## References

- TensorZero Configuration Reference: https://www.tensorzero.com/docs/gateway/configuration-reference
- OpenRouter Models: https://openrouter.ai/models
- TensorZero OpenRouter Integration: https://www.tensorzero.com/docs/integrations/model-providers/openrouter