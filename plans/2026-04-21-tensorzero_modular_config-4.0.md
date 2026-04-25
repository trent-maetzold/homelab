# Modular OpenCode/OpenRouter Configuration (Updated)

## Objective

Configure 8 OpenCode Go models (excluding Qwen models) with dual provider support using **modular TOML files**:
- **OpenCode** as primary provider
- **OpenRouter** as fallback

## Excluded Models

Qwen models are **skipped** until Alibaba provider type is added to TensorZero:
- ~~Qwen3.5 Plus~~
- ~~Qwen3.6 Plus~~

## Remaining Models (8 Total)

| Model | Provider Type | OpenCode Endpoint |
|-------|---------------|-------------------|
| GLM-5.1 | opencode-chat | /chat/completions |
| GLM-5 | opencode-chat | /chat/completions |
| Kimi K2.5 | opencode-chat | /chat/completions |
| Kimi K2.6 | opencode-chat | /chat/completions |
| MiMo-V2-Pro | opencode-chat | /chat/completions |
| MiMo-V2-Omni | opencode-chat | /chat/completions |
| MiniMax M2.7 | opencode-messages | /messages |
| MiniMax M2.5 | opencode-messages | /messages |

## Modular File Structure

```
stacks/tensorzero/config/
├── tensorzero.toml          # Main config (sources other files)
├── opencode.toml            # OpenCode provider configs
├── openrouter.toml          # OpenRouter provider configs
└── models/                  # Model definitions
    ├── glm.toml
    ├── kimi.toml
    ├── mimo.toml
    └── minimax.toml
```

## Implementation Plan

- [ ] **Task 1: Create OpenCode provider configuration** (`opencode.toml`)
  - Define `opencode-chat` provider for standard endpoint
  - Define `opencode-messages` provider for MiniMax endpoint
  - Use `type = "openai-compatible"`
  - Set `api_base = "https://opencode.ai/zen/go/v1"`

- [ ] **Task 2: Create OpenRouter provider configuration** (`openrouter.toml`)
  - Standard OpenRouter provider configuration
  - Use `type = "openrouter"`

- [ ] **Task 3: Create model definition files**
  - `models/glm.toml` - GLM-5.1 and GLM-5 with dual routing
  - `models/kimi.toml` - Kimi K2.5 and K2.6 with dual routing
  - `models/mimo.toml` - MiMo-V2-Pro and MiMo-V2-Omni with dual routing
  - `models/minimax.toml` - MiniMax M2.7 and M2.5 with dual routing (special endpoint)

- [ ] **Task 4: Create main tensorzero.toml with includes**
  - Use TOML's `__requires__` or similar include mechanism if supported
  - OR list all model files to be loaded
  - Source provider configs first, then model configs

- [ ] **Task 5: Handle MiniMax /messages endpoint**
  - Configure `opencode-messages` provider
  - May need `extra_body` to modify endpoint from `/chat/completions` to `/messages`
  - OR configure `api_base` with full path if TensorZero supports it

- [ ] **Task 6: Validate and commit**
  - Validate all TOML files
  - Ensure proper sourcing/including
  - Commit all files

## File Contents

### opencode.toml
```toml
# OpenCode Provider Configurations

[provider_types.opencode-chat]
type = "openai-compatible"
api_base = "https://opencode.ai/zen/go/v1"

[provider_types.opencode-messages]
type = "openai-compatible"
api_base = "https://opencode.ai/zen/go/v1"
# Note: MiniMax models use /messages endpoint
# May require extra_body configuration
```

### openrouter.toml
```toml
# OpenRouter Provider Configuration

[provider_types.openrouter]
type = "openrouter"
```

### models/glm.toml
```toml
# GLM Models - OpenCode (primary) + OpenRouter (fallback)

[models.glm-5.1]
routing = ["opencode-chat", "openrouter"]

[models.glm-5.1.providers.opencode-chat]
type = "openai-compatible"
model_name = "glm-5.1"

[models.glm-5.1.providers.openrouter]
type = "openrouter"
model_name = "thudm/glm-5.1"

[models.glm-5]
routing = ["opencode-chat", "openrouter"]

[models.glm-5.providers.opencode-chat]
type = "openai-compatible"
model_name = "glm-5"

[models.glm-5.providers.openrouter]
type = "openrouter"
model_name = "thudm/glm-5"
```

### models/kimi.toml
```toml
# Kimi Models - OpenCode (primary) + OpenRouter (fallback)

[models.kimi-k2.5]
routing = ["opencode-chat", "openrouter"]

[models.kimi-k2.5.providers.opencode-chat]
type = "openai-compatible"
model_name = "kimi-k2.5"

[models.kimi-k2.5.providers.openrouter]
type = "openrouter"
model_name = "moonshot/kimi-k2.5"

[models.kimi-k2.6]
routing = ["opencode-chat", "openrouter"]

[models.kimi-k2.6.providers.opencode-chat]
type = "openai-compatible"
model_name = "kimi-k2.6"

[models.kimi-k2.6.providers.openrouter]
type = "openrouter"
model_name = "moonshot/kimi-k2.6"
```

### models/mimo.toml
```toml
# MiMo Models - OpenCode (primary) + OpenRouter (fallback)

[models.mimo-v2-pro]
routing = ["opencode-chat", "openrouter"]

[models.mimo-v2-pro.providers.opencode-chat]
type = "openai-compatible"
model_name = "mimo-v2-pro"

[models.mimo-v2-pro.providers.openrouter]
type = "openrouter"
model_name = "xiaomi/mimo-v2-pro"

[models.mimo-v2-omni]
routing = ["opencode-chat", "openrouter"]

[models.mimo-v2-omni.providers.opencode-chat]
type = "openai-compatible"
model_name = "mimo-v2-omni"

[models.mimo-v2-omni.providers.openrouter]
type = "openrouter"
model_name = "xiaomi/mimo-v2-omni"
```

### models/minimax.toml
```toml
# MiniMax Models - OpenCode /messages endpoint (primary) + OpenRouter (fallback)

[models.minimax-m2.7]
routing = ["opencode-messages", "openrouter"]

[models.minimax-m2.7.providers.opencode-messages]
type = "openai-compatible"
model_name = "minimax-m2.7"
# Uses /messages endpoint instead of /chat/completions

[models.minimax-m2.7.providers.openrouter]
type = "openrouter"
model_name = "minimax/minimax-m2.7"

[models.minimax-m2.5]
routing = ["opencode-messages", "openrouter"]

[models.minimax-m2.5.providers.opencode-messages]
type = "openai-compatible"
model_name = "minimax-m2.5"
# Uses /messages endpoint instead of /chat/completions

[models.minimax-m2.5.providers.openrouter]
type = "openrouter"
model_name = "minimax/minimax-m2.5"
```

### tensorzero.toml (Main Config)
```toml
# TensorZero Main Configuration
# Sources provider and model configurations

# Provider Configurations
# __requires__ = ["opencode.toml", "openrouter.toml"]
# OR inline includes if supported

# Model Configurations  
# __requires__ = [
#   "models/glm.toml",
#   "models/kimi.toml",
#   "models/mimo.toml",
#   "models/minimax.toml"
# ]

# Note: Qwen models excluded until Alibaba provider is available
```

## TensorZero Include/Sourcing Mechanism

**Critical for Execution Agent**: Research how TensorZero handles multiple config files:

1. **Option A**: TensorZero supports `__requires__` or similar TOML extension
2. **Option B**: Mount all config files and TensorZero auto-discovers them
3. **Option C**: Use Docker Compose to concatenate files before startup
4. **Option D**: TensorZero has a specific multi-file configuration mechanism

**Check TensorZero documentation** for:
- Configuration file organization
- Multiple file support
- Include/import mechanisms

## Alternative: Single File with Sections

If TensorZero doesn't support includes, use single file with clear sections:

```toml
# ============================================
# Providers
# ============================================

# ... provider configs ...

# ============================================
# Models - GLM
# ============================================

# ... GLM models ...

# ============================================
# Models - Kimi
# ============================================
```

## Verification Criteria

- [ ] 8 models configured (excluded: Qwen3.5 Plus, Qwen3.6 Plus)
- [ ] OpenCode as primary, OpenRouter as fallback for all models
- [ ] MiniMax models use `opencode-messages` provider
- [ ] All other models use `opencode-chat` provider
- [ ] Modular file structure created (or single organized file)
- [ ] TOML syntax valid for all files
- [ ] All files committed and pushed

## Notes for Execution Agent

1. **File Existence**: User mentioned they "added toml files for both providers" but they may not be visible yet. Check for:
   - `opencode.toml`
   - `openrouter.toml`
   - Existing files to build upon

2. **Include Mechanism**: Critical to verify how TensorZero loads multiple config files. The compose.yaml mounts:
   ```yaml
   - ./config/tensorzero.toml:/app/config/tensorzero.toml:ro
   - ./config/functions:/app/config/functions:ro
   ```
   May need to adjust mount or use directory mount instead.

3. **MiniMax Endpoint**: The `/messages` vs `/chat/completions` difference is the main technical challenge. Options:
   - Check if `api_base` can include path: `"https://opencode.ai/zen/go/v1/messages"`
   - Use `extra_body` to override endpoint
   - Check OpenCode docs for query param or header to switch endpoints

4. **Qwen Exclusion**: Explicitly skip these models - do not include in any config file

## Environment Variables

Already configured in compose.yaml:
- `OPENROUTER_API_KEY`
- `OPENCODE_API_KEY`