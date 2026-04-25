# TensorZero OpenCode & OpenRouter Configuration Plan

## Version: 6.0
## Date: 2026-04-22

---

## Objective

Configure TensorZero with 8 OpenCode Go models using dual providers (OpenCode primary, OpenRouter fallback).

---

## Simplified Configuration Structure

Based on TensorZero's architecture, providers are defined inline within each model configuration - there's no separate provider abstraction.

### File Structure

```
stacks/tensorzero/config/
├── tensorzero.toml          # Main config file
└── models/                  # Model definitions
    ├── glm.toml
    ├── kimi.toml
    ├── mimo.toml
    └── minimax.toml
```

---

## Implementation Plan

### Task 1: Create Model Configuration Files in `config/models/`

- [ ] **Task 1a: Create `config/models/glm.toml`**
  
  ```toml
  [models.glm-5-1]
  routing = ["opencode", "openrouter"]
  
  [models.glm-5-1.providers.opencode]
  type = "openai"
  api_base = "https://opencode.ai/zen/go/v1/"
  api_key_location = "env::OPENCODE_API_KEY"
  model_name = "glm-5.1"
  
  [models.glm-5-1.providers.openrouter]
  type = "openrouter"
  model_name = "thudm/glm-5.1"
  
  [models.glm-5]
  routing = ["opencode", "openrouter"]
  
  [models.glm-5.providers.opencode]
  type = "openai"
  api_base = "https://opencode.ai/zen/go/v1/"
  api_key_location = "env::OPENCODE_API_KEY"
  model_name = "glm-5"
  
  [models.glm-5.providers.openrouter]
  type = "openrouter"
  model_name = "thudm/glm-5"
  ```

- [ ] **Task 1b: Create `config/models/kimi.toml`**
  
  ```toml
  [models.kimi-k2-5]
  routing = ["opencode", "openrouter"]
  
  [models.kimi-k2-5.providers.opencode]
  type = "openai"
  api_base = "https://opencode.ai/zen/go/v1/"
  api_key_location = "env::OPENCODE_API_KEY"
  model_name = "kimi-k2.5"
  
  [models.kimi-k2-5.providers.openrouter]
  type = "openrouter"
  model_name = "moonshot/kimi-k2.5"
  
  [models.kimi-k2-6]
  routing = ["opencode", "openrouter"]
  
  [models.kimi-k2-6.providers.opencode]
  type = "openai"
  api_base = "https://opencode.ai/zen/go/v1/"
  api_key_location = "env::OPENCODE_API_KEY"
  model_name = "kimi-k2.6"
  
  [models.kimi-k2-6.providers.openrouter]
  type = "openrouter"
  model_name = "moonshot/kimi-k2.6"
  ```

- [ ] **Task 1c: Create `config/models/mimo.toml`**
  
  ```toml
  [models.mimo-v2-pro]
  routing = ["opencode", "openrouter"]
  
  [models.mimo-v2-pro.providers.opencode]
  type = "openai"
  api_base = "https://opencode.ai/zen/go/v1/"
  api_key_location = "env::OPENCODE_API_KEY"
  model_name = "mimo-v2-pro"
  
  [models.mimo-v2-pro.providers.openrouter]
  type = "openrouter"
  model_name = "xiaomi/mimo-v2-pro"
  
  [models.mimo-v2-omni]
  routing = ["opencode", "openrouter"]
  
  [models.mimo-v2-omni.providers.opencode]
  type = "openai"
  api_base = "https://opencode.ai/zen/go/v1/"
  api_key_location = "env::OPENCODE_API_KEY"
  model_name = "mimo-v2-omni"
  
  [models.mimo-v2-omni.providers.openrouter]
  type = "openrouter"
  model_name = "xiaomi/mimo-v2-omni"
  ```

- [ ] **Task 1d: Create `config/models/minimax.toml`**
  
  ```toml
  [models.minimax-m2-7]
  routing = ["opencode", "openrouter"]
  
  [models.minimax-m2-7.providers.opencode]
  type = "openai"
  api_base = "https://opencode.ai/zen/go/v1/"
  api_key_location = "env::OPENCODE_API_KEY"
  model_name = "minimax-m2.7"
  
  [models.minimax-m2-7.providers.openrouter]
  type = "openrouter"
  model_name = "minimax/minimax-m2.7"
  
  [models.minimax-m2-5]
  routing = ["opencode", "openrouter"]
  
  [models.minimax-m2-5.providers.opencode]
  type = "openai"
  api_base = "https://opencode.ai/zen/go/v1/"
  api_key_location = "env::OPENCODE_API_KEY"
  model_name = "minimax-m2.5"
  
  [models.minimax-m2-5.providers.openrouter]
  type = "openrouter"
  model_name = "minimax/minimax-m2.5"
  ```

### Task 2: Create Main `tensorzero.toml`

- [ ] **Task 2a: Create `config/tensorzero.toml`**
  
  Minimal main config (models loaded from separate files):
  ```toml
  [gateway]
  # Gateway configuration if needed
  ```
  
  Or if all config is in models directory:
  ```toml
  # Empty or minimal gateway settings
  [gateway]
  ```

### Task 3: Update Docker Compose Configuration

- [ ] **Task 3a: Update `stacks/tensorzero/compose.yaml`**
  
  Mount config directory and use glob pattern:
  ```yaml
  gateway:
    # ... other config
    volumes:
      - ./config:/app/config:ro
    command: --config-file /app/config/**/*.toml
  ```

### Task 4: Verify Environment Variables

- [ ] **Task 4a: Confirm `.env` contains required API keys**
  - `OPENCODE_API_KEY`
  - `OPENROUTER_API_KEY`

---

## Model Summary (8 Models - Qwen Excluded)

| Model | TensorZero Name | OpenCode Model | OpenRouter Model |
|-------|-----------------|----------------|------------------|
| GLM-5.1 | `glm-5-1` | `glm-5.1` | `thudm/glm-5.1` |
| GLM-5 | `glm-5` | `glm-5` | `thudm/glm-5` |
| Kimi K2.5 | `kimi-k2-5` | `kimi-k2.5` | `moonshot/kimi-k2.5` |
| Kimi K2.6 | `kimi-k2-6` | `kimi-k2.6` | `moonshot/kimi-k2.6` |
| MiMo-V2-Pro | `mimo-v2-pro` | `mimo-v2-pro` | `xiaomi/mimo-v2-pro` |
| MiMo-V2-Omni | `mimo-v2-omni` | `mimo-v2-omni` | `xiaomi/mimo-v2-omni` |
| MiniMax M2.7 | `minimax-m2-7` | `minimax-m2.7` | `minimax/minimax-m2.7` |
| MiniMax M2.5 | `minimax-m2-5` | `minimax-m2.5` | `minimax/minimax-m2.5` |

**Note**: MiniMax models use `/messages` endpoint instead of `/chat/completions`. Execution agent should test if the standard `api_base` works or if special handling is needed.

---

## Verification Criteria

- [ ] All 8 models configured with OpenCode primary, OpenRouter fallback
- [ ] Config files loaded via glob pattern
- [ ] `docker compose config` validates without errors
- [ ] TensorZero gateway starts successfully
- [ ] Test inference works for each model

---

## Alternative Approaches

1. **Single File**: Could combine all models into one large `tensorzero.toml`, but modular approach is cleaner
2. **Per-Model Files**: Current approach - one file per model family (GLM, Kimi, etc.)
3. **Per-Provider Files**: Group by provider instead of model family - less clean for dual-provider setup
