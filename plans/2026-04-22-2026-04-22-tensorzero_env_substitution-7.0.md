# TensorZero OpenCode & OpenRouter Configuration Plan

## Version: 7.0
## Date: 2026-04-22

---

## Objective

Configure TensorZero with 8 OpenCode Go models using dual providers (OpenCode primary, OpenRouter fallback), with environment variable substitution for API base URL and API keys.

---

## Environment Variable Configuration

### Required Environment Variables

| Variable | Purpose | Example Value |
|----------|---------|---------------|
| `OPENCODE_GO_API_BASE` | OpenCode Go API base URL | `https://opencode.ai/zen/go/v1/` |
| `OPENCODE_API_KEY` | OpenCode API key (shared for zen/go) | `sk-opencode-...` |
| `OPENROUTER_API_KEY` | OpenRouter API key | `sk-or-...` |

---

## Implementation Plan

### Task 1: Update Docker Compose Configuration

- [ ] **Task 1a: Update `stacks/tensorzero/compose.yaml`**
  
  Add environment variables to the gateway service:
  ```yaml
  gateway:
    # ... existing config
    environment:
      - TENSORZERO_POSTGRES_URL=postgresql://tensorzero:${CLICKHOUSE_PASSWORD}@postgres:5432/tensorzero
      - TENSORZERO_CLICKHOUSE_URL=http://clickhouse:8123/tensorzero
      - OPENCODE_GO_API_BASE=${OPENCODE_GO_API_BASE}
      - OPENCODE_API_KEY=${OPENCODE_API_KEY}
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
    volumes:
      - ./config:/app/config:ro
    command: --config-file /app/config/**/*.toml
  ```

### Task 2: Create Model Configuration Files in `config/models/`

- [ ] **Task 2a: Create `config/models/glm.toml`**
  
  ```toml
  [models.glm-5-1]
  routing = ["opencode", "openrouter"]
  
  [models.glm-5-1.providers.opencode]
  type = "openai"
  api_base = "env::OPENCODE_GO_API_BASE"
  api_key_location = "env::OPENCODE_API_KEY"
  model_name = "glm-5.1"
  
  [models.glm-5-1.providers.openrouter]
  type = "openrouter"
  api_key_location = "env::OPENROUTER_API_KEY"
  model_name = "thudm/glm-5.1"
  
  [models.glm-5]
  routing = ["opencode", "openrouter"]
  
  [models.glm-5.providers.opencode]
  type = "openai"
  api_base = "env::OPENCODE_GO_API_BASE"
  api_key_location = "env::OPENCODE_API_KEY"
  model_name = "glm-5"
  
  [models.glm-5.providers.openrouter]
  type = "openrouter"
  api_key_location = "env::OPENROUTER_API_KEY"
  model_name = "thudm/glm-5"
  ```

- [ ] **Task 2b: Create `config/models/kimi.toml`**
  
  ```toml
  [models.kimi-k2-5]
  routing = ["opencode", "openrouter"]
  
  [models.kimi-k2-5.providers.opencode]
  type = "openai"
  api_base = "env::OPENCODE_GO_API_BASE"
  api_key_location = "env::OPENCODE_API_KEY"
  model_name = "kimi-k2.5"
  
  [models.kimi-k2-5.providers.openrouter]
  type = "openrouter"
  api_key_location = "env::OPENROUTER_API_KEY"
  model_name = "moonshot/kimi-k2.5"
  
  [models.kimi-k2-6]
  routing = ["opencode", "openrouter"]
  
  [models.kimi-k2-6.providers.opencode]
  type = "openai"
  api_base = "env::OPENCODE_GO_API_BASE"
  api_key_location = "env::OPENCODE_API_KEY"
  model_name = "kimi-k2.6"
  
  [models.kimi-k2-6.providers.openrouter]
  type = "openrouter"
  api_key_location = "env::OPENROUTER_API_KEY"
  model_name = "moonshot/kimi-k2.6"
  ```

- [ ] **Task 2c: Create `config/models/mimo.toml`**
  
  ```toml
  [models.mimo-v2-pro]
  routing = ["opencode", "openrouter"]
  
  [models.mimo-v2-pro.providers.opencode]
  type = "openai"
  api_base = "env::OPENCODE_GO_API_BASE"
  api_key_location = "env::OPENCODE_API_KEY"
  model_name = "mimo-v2-pro"
  
  [models.mimo-v2-pro.providers.openrouter]
  type = "openrouter"
  api_key_location = "env::OPENROUTER_API_KEY"
  model_name = "xiaomi/mimo-v2-pro"
  
  [models.mimo-v2-omni]
  routing = ["opencode", "openrouter"]
  
  [models.mimo-v2-omni.providers.opencode]
  type = "openai"
  api_base = "env::OPENCODE_GO_API_BASE"
  api_key_location = "env::OPENCODE_API_KEY"
  model_name = "mimo-v2-omni"
  
  [models.mimo-v2-omni.providers.openrouter]
  type = "openrouter"
  api_key_location = "env::OPENROUTER_API_KEY"
  model_name = "xiaomi/mimo-v2-omni"
  ```

- [ ] **Task 2d: Create `config/models/minimax.toml`**
  
  ```toml
  [models.minimax-m2-7]
  routing = ["opencode", "openrouter"]
  
  [models.minimax-m2-7.providers.opencode]
  type = "openai"
  api_base = "env::OPENCODE_GO_API_BASE"
  api_key_location = "env::OPENCODE_API_KEY"
  model_name = "minimax-m2.7"
  
  [models.minimax-m2-7.providers.openrouter]
  type = "openrouter"
  api_key_location = "env::OPENROUTER_API_KEY"
  model_name = "minimax/minimax-m2.7"
  
  [models.minimax-m2-5]
  routing = ["opencode", "openrouter"]
  
  [models.minimax-m2-5.providers.opencode]
  type = "openai"
  api_base = "env::OPENCODE_GO_API_BASE"
  api_key_location = "env::OPENCODE_API_KEY"
  model_name = "minimax-m2.5"
  
  [models.minimax-m2-5.providers.openrouter]
  type = "openrouter"
  api_key_location = "env::OPENROUTER_API_KEY"
  model_name = "minimax/minimax-m2.5"
  ```

### Task 3: Create Main `tensorzero.toml`

- [ ] **Task 3a: Create `config/tensorzero.toml`**
  
  Minimal main config:
  ```toml
  # Gateway configuration
  [gateway]
  ```
  
  Or if empty is not allowed:
  ```toml
  # TensorZero Gateway Configuration
  # Models loaded from config/models/*.toml
  ```

### Task 4: Update `.env` File Documentation

- [ ] **Task 4a: Document required environment variables**
  
  Add to `.env` or `.env.example`:
  ```bash
  # OpenCode Configuration
  OPENCODE_GO_API_BASE=https://opencode.ai/zen/go/v1/
  OPENCODE_API_KEY=your_opencode_api_key_here
  
  # OpenRouter Configuration
  OPENROUTER_API_KEY=your_openrouter_api_key_here
  ```

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

**Note**: MiniMax models use `/messages` endpoint instead of `/chat/completions`. The execution agent should test if the standard `api_base` works or if special handling is needed.

---

## Verification Criteria

- [ ] All 8 models configured with `env::` substitution for API base and keys
- [ ] Docker compose includes all three environment variables
- [ ] Config files loaded via glob pattern
- [ ] `docker compose config` validates without errors
- [ ] TensorZero gateway starts successfully
- [ ] Test inference works for each model via OpenCode
- [ ] Fallback to OpenRouter works when OpenCode fails

---

## Environment Variable Substitution Pattern

Using `env::VARIABLE_NAME` syntax throughout the configuration:

```toml
[models.example.providers.opencode]
type = "openai"
api_base = "env::OPENCODE_GO_API_BASE"
api_key_location = "env::OPENCODE_API_KEY"
model_name = "model-id"

[models.example.providers.openrouter]
type = "openrouter"
api_key_location = "env::OPENROUTER_API_KEY"
model_name = "openrouter/model-id"
```
