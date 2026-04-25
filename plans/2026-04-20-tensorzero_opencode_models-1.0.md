# Add OpenCode Go Models to TensorZero Config

## Objective

Add all OpenCode Go models to the tensorzero.toml configuration file, using OpenRouter as the provider since these models are available through OpenRouter.

## Models to Add

| Model Name | Provider Source |
|------------|-----------------|
| GLM-5.1 | DeepInfra, Z.ai |
| GLM-5 | DeepInfra, Z.ai |
| Kimi K2.5 | Moonshot AI |
| Kimi K2.6 | Moonshot AI |
| MiMo-V2-Pro | Xiaomi MiMo |
| MiMo-V2-Omni | Xiaomi MiMo |
| Qwen3.5 Plus | Alibaba Cloud Model Studio |
| Qwen3.6 Plus | Alibaba Cloud Model Studio |
| MiniMax M2.7 | MiniMax |
| MiniMax M2.5 | MiniMax |

## Implementation Plan

- [ ] Create `stacks/tensorzero/config/tensorzero.toml` with model definitions
- [ ] Configure each model with OpenRouter provider type
- [ ] Map model names to OpenRouter model IDs (following OpenRouter's naming convention)
- [ ] Commit and push changes

## TensorZero Configuration Format

```toml
[models.model_name]
routing = ["openrouter"]

[models.model_name.providers.openrouter]
type = "openrouter"
model_name = "openrouter/model-id"
```

## OpenRouter Model IDs

Based on OpenRouter naming conventions:
- GLM models: `thudm/glm-5.1`, `thudm/glm-5`
- Kimi models: `moonshot/kimi-k2.5`, `moonshot/kimi-k2.6`
- MiMo models: `xiaomi/mimo-v2-pro`, `xiaomi/mimo-v2-omni`
- Qwen models: `alibaba/qwen3.5-plus`, `alibaba/qwen3.6-plus`
- MiniMax models: `minimax/minimax-m2.7`, `minimax/minimax-m2.5`

## Verification

- [ ] Config file is valid TOML
- [ ] All 10 models are defined
- [ ] Each model uses OpenRouter provider type
- [ ] Model names follow TensorZero conventions (kebab-case)