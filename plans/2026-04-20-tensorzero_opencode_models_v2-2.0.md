# Add OpenCode Go Models to TensorZero Configuration (Updated)

## Objective

Add all OpenCode Go models to the `stacks/tensorzero/config/tensorzero.toml` configuration file using TWO providers:
1. **OpenRouter** - for models available through OpenRouter
2. **OpenCode** - as an OpenAI-compatible custom provider for OpenCode-specific models

## Research Findings

### TensorZero Provider Support
TensorZero supports the following provider types:
- `openrouter` - Native OpenRouter integration
- `openai` - OpenAI API
- `openai-compatible` - For custom providers with OpenAI-compatible APIs

Since OpenCode is not a native TensorZero provider, it must be configured as an **OpenAI-compatible** provider.

### OpenCode API
OpenCode provides an OpenAI-compatible API endpoint. Configuration requires:
- Base URL: `https://api.opencode.ai/v1` (or similar)
- API Key: Already configured as `OPENCODE_API_KEY` environment variable

## Models Configuration

### Provider 1: OpenRouter Models

| Model Display Name | TensorZero Model Name | OpenRouter Model ID |
|-------------------|----------------------|---------------------|
| GLM-5.1 | `glm-5.1` | `thudm/glm-5.1` |
| GLM-5 | `glm-5` | `thudm/glm-5` |
| Kimi K2.5 | `kimi-k2.5` | `moonshot/kimi-k2.5` |
| Kimi K2.6 | `kimi-k2.6` | `moonshot/kimi-k2.6` |
| MiMo-V2-Pro | `mimo-v2-pro` | `xiaomi/mimo-v2-pro` |
| MiMo-V2-Omni | `mimo-v2-omni` | `xiaomi/mimo-v2-omni` |
| Qwen3.5 Plus | `qwen3.5-plus` | `alibaba/qwen3.5-plus` |
| Qwen3.6 Plus | `qwen3.6-plus` | `alibaba/qwen3.6-plus` |
| MiniMax M2.7 | `minimax-m2.7` | `minimax/minimax-m2.7` |
| MiniMax M2.5 | `minimax-m2.5` | `minimax/minimax-m2.5` |

### Provider 2: OpenCode Models (OpenAI-Compatible)

OpenCode-specific models need to be identified. The user mentioned "all the opencode go models" which suggests OpenCode has its own model offerings beyond just being a proxy.

**Note for Execution Agent:** Verify OpenCode's specific model names from their API documentation. Common patterns might be:
- `opencode-go`
- `opencode-go-v1`
- Or other model identifiers specific to OpenCode

## Implementation Plan

- [ ] **Task 1: Create tensorzero.toml with OpenRouter models**
  - Write TOML configuration for all 10 OpenRouter models listed above
  - Use `type = "openrouter"` for each provider

- [ ] **Task 2: Add OpenCode provider configuration**
  - Configure OpenCode as an OpenAI-compatible provider
  - Add OpenCode-specific models
  - Use `type = "openai-compatible"` with appropriate base URL

- [ ] **Task 3: Configure OpenCode provider credentials**
  - Ensure `OPENCODE_API_KEY` environment variable is properly referenced
  - Verify the API key location configuration

- [ ] **Task 4: Validate TOML syntax**
  - Validate the complete configuration file
  - Check for any parsing errors

- [ ] **Task 5: Commit and push changes**
  - Stage and commit the updated configuration
  - Push to remote repository

## Configuration File Content

### OpenRouter Models Configuration

```toml
# OpenRouter Models

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

### OpenCode Provider Configuration

```toml
# OpenCode Provider (OpenAI-Compatible)
# Base URL and models to be confirmed from OpenCode API documentation

[models.opencode-go]
routing = ["opencode"]

[models.opencode-go.providers.opencode]
type = "openai-compatible"
model_name = "opencode-go"  # Verify actual model name from OpenCode API
api_base = "https://api.opencode.ai/v1"  # Verify actual base URL
```

## Environment Variables

Ensure these are set in `.env`:
- `OPENROUTER_API_KEY` - Already configured
- `OPENCODE_API_KEY` - Already configured

## Verification Criteria

- [ ] All 10 OpenRouter models are configured with correct model IDs
- [ ] OpenCode provider is configured as OpenAI-compatible
- [ ] OpenCode models are defined and routed correctly
- [ ] API keys are properly referenced via environment variables
- [ ] TOML file is valid and parses correctly
- [ ] Configuration is committed and pushed

## Notes for Execution Agent

1. **OpenCode API Details**: Verify the exact base URL and available models from OpenCode's API documentation at https://opencode.ai or their developer docs

2. **OpenAI-Compatible Provider**: In TensorZero, use:
   ```toml
   type = "openai-compatible"
   api_base = "https://api.opencode.ai/v1"
   ```

3. **Model Name Mapping**: Confirm the exact model identifiers OpenCode uses (e.g., `opencode-go`, `opencode-go-latest`, etc.)

4. **Authentication**: The `OPENCODE_API_KEY` environment variable should be picked up automatically by TensorZero

5. **Testing**: After deployment, test both OpenRouter and OpenCode models to ensure connectivity

## Potential Risks and Mitigations

1. **OpenCode API compatibility**: If OpenCode's API isn't fully OpenAI-compatible, some features may not work
2. **Model availability**: Verify all model IDs exist on both platforms
3. **Rate limits**: Different providers have different rate limits - monitor accordingly

## References

- TensorZero OpenAI-Compatible Provider: https://www.tensorzero.com/docs/integrations/model-providers/openai-compatible
- TensorZero OpenRouter Provider: https://www.tensorzero.com/docs/integrations/model-providers/openrouter
- OpenCode API Documentation: https://opencode.ai/docs (verify actual URL)