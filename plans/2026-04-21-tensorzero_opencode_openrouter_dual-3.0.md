# Add OpenCode Go Models with OpenRouter Fallback

## Objective

Configure all 10 OpenCode Go models in TensorZero with **dual provider support**:
- **Primary**: OpenCode (direct API)
- **Fallback**: OpenRouter (if OpenCode fails)

## API Endpoints

### OpenCode Endpoints
- **Standard models** (8 models): `https://opencode.ai/zen/go/v1/chat/completions`
- **MiniMax models** (2 models): `https://opencode.ai/zen/go/v1/messages`

### OpenRouter Endpoint
- All models: `https://openrouter.ai/api/v1` (native OpenRouter provider)

## Provider Strategy

Since OpenCode has two different API endpoints, we need **two OpenCode provider configurations**:

1. `opencode-chat` - For standard chat completions endpoint
2. `opencode-messages` - For MiniMax messages endpoint

Both will fallback to `openrouter`.

## Model Mapping

| Model | TensorZero Name | OpenCode Provider | OpenRouter Model ID |
|-------|----------------|-------------------|---------------------|
| GLM-5.1 | `glm-5.1` | opencode-chat | `thudm/glm-5.1` |
| GLM-5 | `glm-5` | opencode-chat | `thudm/glm-5` |
| Kimi K2.5 | `kimi-k2.5` | opencode-chat | `moonshot/kimi-k2.5` |
| Kimi K2.6 | `kimi-k2.6` | opencode-chat | `moonshot/kimi-k2.6` |
| MiMo-V2-Pro | `mimo-v2-pro` | opencode-chat | `xiaomi/mimo-v2-pro` |
| MiMo-V2-Omni | `mimo-v2-omni` | opencode-chat | `xiaomi/mimo-v2-omni` |
| Qwen3.5 Plus | `qwen3.5-plus` | opencode-chat | `alibaba/qwen3.5-plus` |
| Qwen3.6 Plus | `qwen3.6-plus` | opencode-chat | `alibaba/qwen3.6-plus` |
| MiniMax M2.7 | `minimax-m2.7` | opencode-messages | `minimax/minimax-m2.7` |
| MiniMax M2.5 | `minimax-m2.5` | opencode-messages | `minimax/minimax-m2.5` |

## Implementation Plan

- [ ] **Task 1: Configure OpenCode providers (2 variants)**
  - Create `opencode-chat` provider with `api_base = "https://opencode.ai/zen/go/v1"`
  - Create `opencode-messages` provider with same base but for MiniMax models
  - Use `type = "openai-compatible"` for both

- [ ] **Task 2: Configure OpenRouter provider**
  - Standard OpenRouter configuration with `type = "openrouter"`

- [ ] **Task 3: Configure all 10 models with dual routing**
  - Each model has `routing = ["opencode-chat", "openrouter"]` or `routing = ["opencode-messages", "openrouter"]`
  - Define provider configs under each model

- [ ] **Task 4: Handle MiniMax endpoint difference**
  - For MiniMax models, use provider name `opencode-messages` 
  - May need `extra_body` to modify endpoint path from `/chat/completions` to `/messages`
  - OR configure separate provider with appropriate endpoint

- [ ] **Task 5: Validate and test**
  - Validate TOML syntax
  - Ensure all API keys are properly referenced

- [ ] **Task 6: Commit and push**

## Configuration File Content

```toml
# ============================================
# OpenCode Go Models with OpenRouter Fallback
# ============================================

# OpenCode Provider for Standard Chat Endpoint
# Used by: GLM, Kimi, MiMo, Qwen models
[models.glm-5.1]
routing = ["opencode-chat", "openrouter"]

[models.glm-5.1.providers.opencode-chat]
type = "openai-compatible"
model_name = "glm-5.1"
api_base = "https://opencode.ai/zen/go/v1"

[models.glm-5.1.providers.openrouter]
type = "openrouter"
model_name = "thudm/glm-5.1"

[models.glm-5]
routing = ["opencode-chat", "openrouter"]

[models.glm-5.providers.opencode-chat]
type = "openai-compatible"
model_name = "glm-5"
api_base = "https://opencode.ai/zen/go/v1"

[models.glm-5.providers.openrouter]
type = "openrouter"
model_name = "thudm/glm-5"

[models.kimi-k2.5]
routing = ["opencode-chat", "openrouter"]

[models.kimi-k2.5.providers.opencode-chat]
type = "openai-compatible"
model_name = "kimi-k2.5"
api_base = "https://opencode.ai/zen/go/v1"

[models.kimi-k2.5.providers.openrouter]
type = "openrouter"
model_name = "moonshot/kimi-k2.5"

[models.kimi-k2.6]
routing = ["opencode-chat", "openrouter"]

[models.kimi-k2.6.providers.opencode-chat]
type = "openai-compatible"
model_name = "kimi-k2.6"
api_base = "https://opencode.ai/zen/go/v1"

[models.kimi-k2.6.providers.openrouter]
type = "openrouter"
model_name = "moonshot/kimi-k2.6"

[models.mimo-v2-pro]
routing = ["opencode-chat", "openrouter"]

[models.mimo-v2-pro.providers.opencode-chat]
type = "openai-compatible"
model_name = "mimo-v2-pro"
api_base = "https://opencode.ai/zen/go/v1"

[models.mimo-v2-pro.providers.openrouter]
type = "openrouter"
model_name = "xiaomi/mimo-v2-pro"

[models.mimo-v2-omni]
routing = ["opencode-chat", "openrouter"]

[models.mimo-v2-omni.providers.opencode-chat]
type = "openai-compatible"
model_name = "mimo-v2-omni"
api_base = "https://opencode.ai/zen/go/v1"

[models.mimo-v2-omni.providers.openrouter]
type = "openrouter"
model_name = "xiaomi/mimo-v2-omni"

[models.qwen3.5-plus]
routing = ["opencode-chat", "openrouter"]

[models.qwen3.5-plus.providers.opencode-chat]
type = "openai-compatible"
model_name = "qwen3.5-plus"
api_base = "https://opencode.ai/zen/go/v1"

[models.qwen3.5-plus.providers.openrouter]
type = "openrouter"
model_name = "alibaba/qwen3.5-plus"

[models.qwen3.6-plus]
routing = ["opencode-chat", "openrouter"]

[models.qwen3.6-plus.providers.opencode-chat]
type = "openai-compatible"
model_name = "qwen3.6-plus"
api_base = "https://opencode.ai/zen/go/v1"

[models.qwen3.6-plus.providers.openrouter]
type = "openrouter"
model_name = "alibaba/qwen3.6-plus"

# ============================================
# MiniMax Models (use /messages endpoint)
# ============================================

[models.minimax-m2.7]
routing = ["opencode-messages", "openrouter"]

[models.minimax-m2.7.providers.opencode-messages]
type = "openai-compatible"
model_name = "minimax-m2.7"
api_base = "https://opencode.ai/zen/go/v1"
# NOTE: This provider needs to use /messages instead of /chat/completions
# May require extra_body or custom provider configuration

[models.minimax-m2.7.providers.openrouter]
type = "openrouter"
model_name = "minimax/minimax-m2.7"

[models.minimax-m2.5]
routing = ["opencode-messages", "openrouter"]

[models.minimax-m2.5.providers.opencode-messages]
type = "openai-compatible"
model_name = "minimax-m2.5"
api_base = "https://opencode.ai/zen/go/v1"
# NOTE: This provider needs to use /messages instead of /chat/completions

[models.minimax-m2.5.providers.openrouter]
type = "openrouter"
model_name = "minimax/minimax-m2.5"
```

## MiniMax Endpoint Handling

The MiniMax models use `/messages` endpoint instead of `/chat/completions`. Options:

1. **Use `extra_body` to modify request** (if TensorZero supports endpoint override)
2. **Configure a custom provider** that maps to the correct endpoint
3. **Use extra_headers** if the API expects a different content-type or path

**For Execution Agent**: Research TensorZero's `extra_body` or `extra_headers` capabilities to modify the endpoint path for MiniMax models, or check if `api_base` can include the full path.

## Environment Variables Required

```bash
OPENROUTER_API_KEY=your_openrouter_key
OPENCODE_API_KEY=your_opencode_key
```

Both already configured in compose.yaml.

## Verification Criteria

- [ ] All 10 models configured with dual routing (OpenCode primary, OpenRouter fallback)
- [ ] 8 models use `opencode-chat` provider with standard endpoint
- [ ] 2 MiniMax models use `opencode-messages` provider with `/messages` endpoint
- [ ] OpenRouter fallback configured for all models
- [ ] TOML syntax is valid
- [ ] API keys properly referenced
- [ ] File committed and pushed

## Notes for Execution Agent

1. **MiniMax Endpoint**: The key challenge is making MiniMax models use `/messages` instead of `/chat/completions`. Research:
   - Can `api_base` be set to `"https://opencode.ai/zen/go/v1/messages"` directly?
   - Does TensorZero's `extra_body` support changing the endpoint path?
   - Or is there a provider-level configuration for the endpoint path?

2. **Provider Naming**: I used `opencode-chat` and `opencode-messages` as provider names to distinguish the two endpoint types.

3. **Fallback Behavior**: TensorZero will try OpenCode first, and if it fails (network error, rate limit, etc.), it will automatically fallback to OpenRouter.

4. **Model Names**: Confirm exact model identifiers OpenCode expects in the `model_name` field of requests.

## References

- OpenCode API Docs: https://opencode.ai/
- TensorZero OpenAI-Compatible Provider: https://www.tensorzero.com/docs/integrations/model-providers/openai-compatible
- TensorZero Routing/Fallbacks: https://www.tensorzero.com/docs/gateway/guides/retries-fallbacks