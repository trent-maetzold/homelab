# TensorZero OpenCode & OpenRouter Configuration Plan

## Version: 5.0
## Date: 2026-04-21

---

## Objective

Configure TensorZero with 8 OpenCode Go models (excluding Qwen models) using dual providers:
- **OpenCode** as primary provider (OpenAI-compatible custom provider)
- **OpenRouter** as fallback provider

---

## Key Findings from TensorZero Documentation

### 1. Multi-File Configuration Support

TensorZero supports splitting configuration across multiple TOML files using glob patterns:

```bash
# Load all TOML files in config directory
--config-file path/to/**/*.toml
```

Under the hood, TensorZero concatenates the configuration files with special handling for paths. Models declared in one file can be used in variants declared in another.

### 2. OpenAI-Compatible Provider Configuration

The `type = "openai"` provider supports custom `api_base` for OpenAI-compatible APIs:

```toml
[models.model_name.providers.provider_name]
type = "openai"
api_base = "https://custom-api.com/v1/"  # Custom endpoint
api_key_location = "env::CUSTOM_API_KEY"
model_name = "model-id"
```

**Critical Finding**: The `api_base` for OpenAI provider specifies the base URL only (e.g., `https://api.openai.com/v1/`), and TensorZero appends the endpoint path based on `api_type`:
- `api_type = "chat_completions"` (default) → appends `/chat/completions`
- `api_type = "responses"` → appends `/responses`

### 3. OpenRouter Provider

OpenRouter is a native provider type:

```toml
[models.model_name.providers.openrouter]
type = "openrouter"
model_name = "openrouter/model-id"
```

---

## Configuration Strategy

### Challenge: MiniMax `/messages` Endpoint

OpenCode Go uses:
- Standard models: `https://opencode.ai/zen/go/v1/chat/completions`
- MiniMax models: `https://opencode.ai/zen/go/v1/messages`

The MiniMax models use `/messages` instead of `/chat/completions`, which may require special handling.

### Solution Approach

**Option A** (Recommended): Try using `type = "openai"` with full path in `api_base`:
```toml
api_base = "https://opencode.ai/zen/go/v1/chat/completions"
```

**Option B**: If Option A doesn't work, try:
```toml
api_base = "https://opencode.ai/zen/go/v1/"
```

**Option C**: For MiniMax specifically, if the endpoint path causes issues:
```toml
api_base = "https://opencode.ai/zen/go/v1/messages"
```

The execution agent should test these configurations.

---

## Implementation Plan

### File Structure

```
stacks/tensorzero/config/
├── tensorzero.toml          # Main config (empty or minimal)
├── providers/
│   ├── opencode.toml        # OpenCode provider definitions
│   └── openrouter.toml      # OpenRouter provider definitions
└── models/
    ├── glm.toml             # GLM-5.1, GLM-5
    ├── kimi.toml            # Kimi K2.5, Kimi K2.6
    ├── mimo.toml            # MiMo-V2-Pro, MiMo-V2-Omni
    └── minimax.toml         # MiniMax M2.7, MiniMax M2.5
```

### Task 1: Create Provider Configuration Files

- [ ] **Task 1a: Create `config/providers/opencode.toml`**
  - Define OpenCode provider configuration for standard endpoint (`/chat/completions`)
  - Configure `api_base = "https://opencode.ai/zen/go/v1/"`
  - Set `api_key_location = "env::OPENCODE_API_KEY"`
  
- [ ] **Task 1b: Create `config/providers/openrouter.toml`**
  - Define OpenRouter provider configuration
  - Set `api_key_location = "env::OPENROUTER_API_KEY"`

### Task 2: Create Model Configuration Files

- [ ] **Task 2a: Create `config/models/glm.toml`**
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
  ```

- [ ] **Task 2b: Create `config/models/glm-5.toml`** (or combine with glm.toml)
  - Same structure for GLM-5
  - OpenRouter model name: `thudm/glm-5`

- [ ] **Task 2c: Create `config/models/kimi.toml`**
  - Kimi K2.5: OpenRouter model name `moonshot/kimi-k2.5`
  - Kimi K2.6: OpenRouter model name `moonshot/kimi-k2.6`

- [ ] **Task 2d: Create `config/models/mimo.toml`**
  - MiMo-V2-Pro: OpenRouter model name `xiaomi/mimo-v2-pro`
  - MiMo-V2-Omni: OpenRouter model name `xiaomi/mimo-v2-omni`

- [ ] **Task 2e: Create `config/models/minimax.toml`**
  - MiniMax M2.7: OpenRouter model name `minimax/minimax-m2.7`
  - MiniMax M2.5: OpenRouter model name `minimax/minimax-m2.5`
  - **Note**: Test if special endpoint handling is needed for MiniMax

### Task 3: Update Docker Compose Configuration

- [ ] **Task 3a: Update `stacks/tensorzero/compose.yaml`**
  - Change config volume mount from single file to config directory:
    ```yaml
    volumes:
      - ./config:/app/config:ro
    ```
  - Update command to use glob pattern:
    ```yaml
    command: --config-file /app/config/**/*.toml
    ```

### Task 4: Verify Environment Variables

- [ ] **Task 4a: Confirm `.env` contains required API keys**
  - `OPENCODE_API_KEY`
  - `OPENROUTER_API_KEY`

---

## Verification Criteria

- [ ] All 8 models configured with dual providers (OpenCode primary, OpenRouter fallback)
- [ ] `docker compose config` validates without errors
- [ ] TensorZero gateway starts successfully
- [ ] Test inference for each model works via OpenCode
- [ ] Fallback to OpenRouter works when OpenCode fails

---

## Potential Risks and Mitigations

1. **MiniMax Endpoint Path Issue**
   - Risk: MiniMax uses `/messages` instead of `/chat/completions`
   - Mitigation: Test `api_base` with full path; if that fails, research if `extra_body` can override endpoint

2. **Configuration File Loading**
   - Risk: Glob pattern may not work as expected in Docker
   - Mitigation: Verify TensorZero version supports glob patterns; test with explicit file list if needed

3. **Model Name Mapping**
   - Risk: OpenCode model names may differ from OpenRouter
   - Mitigation: Verify exact model identifiers with both providers

---

## Model Summary (8 Models)

| Model | OpenCode Model Name | OpenRouter Model Name |
|-------|--------------------|----------------------|
| GLM-5.1 | `glm-5.1` | `thudm/glm-5.1` |
| GLM-5 | `glm-5` | `thudm/glm-5` |
| Kimi K2.5 | `kimi-k2.5` | `moonshot/kimi-k2.5` |
| Kimi K2.6 | `kimi-k2.6` | `moonshot/kimi-k2.6` |
| MiMo-V2-Pro | `mimo-v2-pro` | `xiaomi/mimo-v2-pro` |
| MiMo-V2-Omni | `mimo-v2-omni` | `xiaomi/mimo-v2-omni` |
| MiniMax M2.7 | `minimax-m2.7` | `minimax/minimax-m2.7` |
| MiniMax M2.5 | `minimax-m2.5` | `minimax/minimax-m2.5` |

**Excluded**: Qwen3.5 Plus, Qwen3.6 Plus (awaiting TensorZero Alibaba provider support)
