# Homelab Steady State Roadmap

## Objective
Get infrastructure to a steady state where services are deployed, integrated, and secure. Execute incrementally in ~1-hour blocks. Prioritize force multipliers first, then high utility, then observability, then security hardening.

## Guiding Rules

1. **One thing at a time.** If a task tries to expand into five other tasks, stop and write it down for a future phase.
2. **Default to "good enough."** Perfect configuration is the enemy of running configuration.
3. **Auth first, then expose.** Nothing new gets a public route until Authentik protects it.
4. **Database migrations happen in Phase 4, not before.** The shared postgres works today; isolating it is important but not a force multiplier.
5. **If a stack is already defined, start it and move on.** Don't rebuild what exists.

---

## Phase 1: Foundation — Auth & AI Gateway (Force Multipliers)

> Goal: Authentik actually protects services. LiteLLM becomes the single API gateway for all AI traffic. This makes every subsequent AI step faster.

### Task 1.1: Traefik forwardAuth middleware for Authentik
- [ ] Create `stacks/traefik/config/dynamic/authentik.yaml` with a `forwardAuth` middleware pointing to `http://authentik:9000/outpost.goauthentik.io/auth/traefik`
- [ ] Create a catch-all `Chain` middleware that applies `forwardAuth` + `headers` so services can opt-in with one label
- [ ] Restart traefik and verify middleware appears in dashboard
- **Guardrail:** Do NOT apply the middleware to any service yet. Just verify it exists.
- **Done when:** Traefik dashboard shows the middleware and a test curl with no cookie returns 302 to `auth.trkm.io`.

### Task 1.2: Protect first services with Authentik
- [ ] In Authentik UI, create a Provider + Application for `OpenWebUI` (`chat.trkm.io`)
- [ ] Add traefik label to `stacks/openwebui/compose.yaml`: `traefik.http.routers.openwebui.middlewares: "authentik@file"` (or the chain name)
- [ ] Deploy and verify you can log in via Authentik and land in OpenWebUI
- [ ] Repeat for `TensorZero UI` (`t0.trkm.io`) and `Seerr` (`seerr.trkm.io`)
- **Guardrail:** Skip *arr apps, Plex, and anything that uses `network_mode: host` for now.
- **Done when:** Those three services require an Authentik login and redirect back correctly.

### Task 1.3: Deploy LiteLLM stack
- [ ] Create `stacks/litellm/compose.yaml` with: `litellm` service, dedicated `postgres`, optional `redis`
- [ ] Configure `config.yaml` with 2-3 existing providers: `openrouter`, `opencode-go`, and a local `ollama` placeholder
- [ ] Add traefik labels: `Host(`llm.trkm.io`)`
- [ ] Generate `LITELLM_MASTER_KEY` and `LITELLM_SALT_KEY` via `just gen-password`
- [ ] Start stack and verify `/health/readiness` responds
- **Guardrail:** Do NOT configure every model. Just enough to verify routing works.
- **Done when:** You can curl `llm.trkm.io/v1/models` with the master key and see model list.

### Task 1.4: Wire OpenWebUI to LiteLLM
- [ ] In OpenWebUI Admin Settings -> Connections, add an OpenAI API connection pointing to `http://litellm:4000` (or `https://llm.trkm.io/v1`)
- [ ] Use `LITELLM_MASTER_KEY` as the API key
- [ ] Send a test chat and verify LiteLLM logs show the request
- [ ] (Optional but fast) Disable OpenWebUI's direct model connections so all traffic flows through LiteLLM
- **Guardrail:** Do not theme OpenWebUI or configure custom pipelines yet.
- **Done when:** A chat message in OpenWebUI routes through LiteLLM and returns a response.

---

## Phase 2: Agent Stack — OpenClaw, ContextForge, MCP

> Goal: The "general agent" is actually working. OpenWebUI is the interface. MCP servers provide tool access.

### Task 2.1: Configure OpenClaw with LiteLLM backend
- [ ] Update `stacks/openclaw/config/openclaw.json` with a valid gateway config: model pointing to LiteLLM (`llm.trkm.io/v1`), API key, and at least one simple tool
- [ ] Remove or update the dynamic Traefik config `openclaw.yaml` — either delete it so the compose labels take over, or ensure both don't conflict
- [ ] Restart OpenClaw, verify `/healthz` passes
- **Guardrail:** Do not build custom tools yet. Just get the gateway talking to LiteLLM.
- **Done when:** You can curl OpenClaw directly and it proxies a chat completion through LiteLLM.

### Task 2.2: Integrate OpenClaw into OpenWebUI
- [ ] In OpenWebUI, add OpenClaw as an OpenAI-compatible API endpoint (or as a tool/function if OpenClaw exposes an OpenAI-compatible chat interface)
- [ ] If OpenClaw is not OpenAI-compatible, create a minimal OpenWebUI function/pipeline that forwards to OpenClaw
- [ ] Verify end-to-end: OpenWebUI message -> OpenClaw -> LiteLLM -> model response
- **Guardrail:** Do not build multi-agent workflows yet.
- **Done when:** Typing in OpenWebUI reaches OpenClaw and returns a response.

### Task 2.3: Secure ContextForge and enable first MCP server
- [ ] Set `AUTH_REQUIRED: "true"` in `stacks/contextforge/compose.yaml`
- [ ] Put ContextForge behind Authentik: add `traefik.http.routers.contextforge.middlewares: "authentik@file"`
- [ ] Configure the first MCP server in ContextForge: a simple `filesystem` or `shell` server scoped to a safe directory (e.g., read-only config dir)
- [ ] Verify ContextForge UI loads behind auth and the MCP server registers
- **Guardrail:** Do NOT add email/calendar/budget MCP servers yet.
- **Done when:** ContextForge requires login, and the MCP server appears in the gateway UI.

### Task 2.4: Connect ContextForge MCP to OpenClaw/OpenWebUI
- [ ] Configure OpenClaw to use ContextForge as an MCP client, OR configure OpenWebUI to use ContextForge's SSE endpoint as a tool source
- [ ] Test a simple tool call: "list files in /config" or similar
- **Guardrail:** If the integration is messy, document the blocker and move on — do not rewrite the integration layer.
- **Done when:** A message in OpenWebUI can trigger an MCP tool via ContextForge.

---

## Phase 3: High Utility Services

> Goal: Services you actually use daily are up, integrated, and protected.

### Task 3.1: Start and protect Seerr
- [ ] `cd stacks/seerr && docker compose up -d`
- [ ] Complete initial Seerr setup wizard (Plex login, *arr app connections)
- [ ] Add Authentik middleware to traefik labels in `stacks/seerr/compose.yaml`
- [ ] Verify requests redirect through Authentik
- **Guardrail:** Do NOT fix the bug you want to PR yet. Just get it running.
- **Done when:** `seerr.trkm.io` loads, requires auth, and can request a movie.

### Task 3.2: Deploy Tautulli
- [ ] Create `stacks/tautulli/compose.yaml` (linuxserver image, `TAUTULLI_PORT=8181`, volume for `/config`)
- [ ] Add traefik labels + Authentik middleware
- [ ] Configure Tautulli with Plex URL and token
- [ ] Verify basic dashboard loads
- **Guardrail:** Do not configure complex notification agents yet.
- **Done when:** `tautulli.trkm.io` loads behind auth and shows Plex activity.

### Task 3.3: Home Assistant quick wins
- [ ] Verify Home Assistant is running and accessible at `ha.trkm.io`
- [ ] Put it behind Authentik: add middleware label to `stacks/homeassistant/compose.yaml`
- [ ] Install HACS if not present (one-time setup)
- [ ] Add 2-3 useful integrations you actually need (not everything)
- **Guardrail:** Do not spend more than 30 minutes on automations.
- **Done when:** HA loads behind auth and has at least one working integration dashboard.

### Task 3.4: Wire AI agent to homelab status (first observability)
- [ ] Create a simple shell script or Python script that outputs: running container count, unhealthy containers, disk usage %, recent restarts
- [ ] Expose this as an MCP tool via ContextForge (filesystem read of the output, or a simple shell command)
- [ ] Verify the agent can answer "what's the status of my server?"
- **Guardrail:** Do not build a full metrics pipeline yet. This is a quick win.
- **Done when:** Asking the agent about server status returns current container/disk info.

---

## Phase 4: Data Isolation (Postgres Migration)

> Goal: Every service owns its database. The shared postgres init is retired.

### Task 4.1: Migrate Seerr to embedded postgres
- [ ] Add `db` service to `stacks/seerr/compose.yaml` (same pattern as authentik)
- [ ] Update `DB_HOST` env from `postgres` to `db`
- [ ] Remove `postgres` external network from seerr stack
- [ ] Stop seerr, backup DB from shared postgres, restore to embedded (or start fresh if data is trivial)
- [ ] Remove seerr init script from `stacks/postgres/init/`
- **Done when:** Seerr runs with its own DB and works.

### Task 4.2: Migrate Immich to embedded postgres
- [ ] Add `db` service to `stacks/immich/compose.yaml` using the same `ghcr.io/immich-app/postgres:18-vectorchord...` image
- [ ] Update `DB_HOSTNAME` to `db`, remove `postgres` external network
- [ ] Migrate data or start fresh
- [ ] Remove immich init script from shared postgres
- **Done when:** Immich runs with embedded DB and photo search works.

### Task 4.3: Migrate Baikal to embedded postgres
- [ ] Same pattern: add `db` service, update env, remove external network
- [ ] Migrate data (Baikal data is small)
- [ ] Remove baikal init script from shared postgres
- **Done when:** Baikal works with embedded DB.

### Task 4.4: Migrate ContextForge to embedded postgres
- [ ] Add `db` service, update `DATABASE_URL`, remove external `postgres` network
- [ ] Remove contextforge init script from shared postgres
- **Done when:** ContextForge works with embedded DB.

### Task 4.5: Migrate *arr apps to embedded postgres (batch)
- [ ] Create embedded `db` services in `stacks/radarr/`, `stacks/sonarr/`, `stacks/lidarr/`, `stacks/prowlarr/`
- [ ] For each: update `*_POSTGRES__HOST` to `db`, remove `postgres` external network
- [ ] Migrate data or start fresh (arr app configs can be re-imported quickly)
- [ ] Remove all arr init scripts from shared postgres
- **Guardrail:** Do one stack first (e.g., lidarr) to prove the pattern, then batch the rest.
- **Done when:** All *arr apps use embedded DBs and connect to indexers/trackers.

### Task 4.6: Retire shared postgres stack
- [ ] Verify nothing references the `postgres` external network anymore
- [ ] Back up all data from shared postgres volume
- [ ] Stop and remove `stacks/postgres/`
- [ ] Remove the `postgres` external network from Docker
- **Done when:** `docker network ls` shows no `postgres` network, and all services still work.

---

## Phase 5: External Access & Network Hardening

> Goal: Externally-exposed services go through Cloudflare Tunnel. Tailnet stays for admin access.

### Task 5.1: Deploy Cloudflare Tunnel
- [ ] Create `stacks/cloudflared/compose.yaml` using `cloudflare/cloudflared:latest`
- [ ] Generate tunnel token from Cloudflare Zero Trust dashboard
- [ ] Configure public hostnames for: `chat.trkm.io`, `auth.trkm.io`, `seerr.trkm.io` (and any other user-facing services)
- [ ] Start tunnel and verify external DNS resolves
- **Guardrail:** Do NOT expose traefik dashboard, *arr apps, Proxmox/Unraid, or admin panels.
- **Done when:** `chat.trkm.io` is reachable from the internet via Cloudflare.

### Task 5.2: Restrict Traefik to Cloudflare IPs (optional but fast)
- [ ] Add a simple IP allowlist middleware in Traefik for the externally routed services (Cloudflare IP ranges)
- [ ] Or configure cloudflared to enforce access policies in Zero Trust
- **Guardrail:** Don't build a full WAF. Just ensure direct IP access to 443 is less useful.
- **Done when:** Services behind the tunnel require going through Cloudflare.

### Task 5.3: Evaluate and configure DMZ (Unraid network)
- [ ] Document which services are externally exposed vs tailnet-only
- [ ] If Unraid VLAN/DMZ is easy to configure, move cloudflared + exposed services to an isolated bridge
- [ ] If it's complex, document it and move to Phase 8
- **Guardrail:** If Unraid networking is fiddly, skip and come back later.
- **Done when:** There is a written policy for what lives where, even if not fully implemented.

---

## Phase 6: Observability

> Goal: You can see what's happening with AI calls and infrastructure without SSHing in.

### Task 6.1: Deploy Langfuse
- [ ] Create `stacks/langfuse/compose.yaml` with `langfuse` web + worker + `postgres` + `redis`
- [ ] Add traefik labels + Authentik middleware
- [ ] Configure LiteLLM to send callbacks/traces to Langfuse (set `LANGFUSE_HOST`, `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY` in litellm env)
- [ ] Verify a chat in OpenWebUI creates a trace in Langfuse
- **Guardrail:** Do not customize Langfuse scoring or prompts yet.
- **Done when:** `langfuse.trkm.io` shows traces from OpenWebUI/LiteLLM chats.

### Task 6.2: Deploy SigNoz (all-in-one observability)
- [ ] Create `stacks/signoz/compose.yaml` using the SigNoz docker-compose minimal setup
- [ ] Add OpenTelemetry collector sidecar or configure Docker log driver to forward logs
- [ ] Put SigNoz behind Authentik
- [ ] Verify container logs and basic metrics appear
- **Guardrail:** Do not build custom dashboards. Use the built-in ones.
- **Done when:** `signoz.trkm.io` shows infrastructure logs and at least one APM trace.

### Task 6.3: Enhance agent homelab status tool
- [ ] Expand the Phase 3.4 status script to include: unhealthy container list, disk usage, memory usage, recent Docker events
- [ ] Schedule it to run every minute and write to a JSON file
- [ ] Add an MCP tool that reads this JSON so the agent always has fresh data
- **Guardrail:** Do not build a full metrics database. A JSON file is fine.
- **Done when:** The agent can answer "what's unhealthy?" and "how much disk is left?"

---

## Phase 7: Media Polish

> Goal: Kometa works correctly for kid profiles.

### Task 7.1: Fix Kometa collection visibility for restricted users
- [ ] Research the specific issue: Kometa `collection_filtering: user` + Plex restrictions causes collections to hide items
- [ ] Test configuration changes in `stacks/kometa/config/config.yml`: try `collection_mode: default` or adjust `mass_content_rating_update` to run before collection building
- [ ] Alternative: Use Kometa's `item_labels` or `plex_search` with rating filters instead of relying on Plex's user restrictions on collections
- [ ] Run Kometa manually with `--run` and verify a kid profile sees appropriate items inside collections
- **Guardrail:** If the fix requires a Kometa code change, document it for a PR but do not write the PR in this task.
- **Done when:** A Plex user restricted by rating can see age-appropriate items within collections.

---

## Phase 8: Security Hardening & Advanced Integrations

> Goal: Lock down remaining gaps and add advanced MCP integrations.

### Task 8.1: Lock down Tuwunel
- [ ] Disable open registration: `TUWUNEL_ALLOW_REGISTRATION: "false"` or require token
- [ ] Review `TUWUNEL_ALLOW_FEDERATION` and ACL if needed
- [ ] Put behind Authentik if Matrix clients support OIDC (or use a simple nginx basic auth layer)
- **Done when:** Random users cannot register on `matrix.trkm.io`.

### Task 8.2: Implement agent gates for server management
- [ ] Define the agent's authority boundary: read-only by default, write requires confirmation
- [ ] Implement a simple gate: destructive MCP tools (shell write, docker exec, config change) require a confirmation message/loop
- [ ] Document the gate behavior in `CLAUDE.md` or a new `AGENTS.md`
- **Guardrail:** Do not build a full RBAC system. Simple confirmation prompts are enough.
- **Done when:** The agent asks "Are you sure?" before running a shell command that modifies state.

### Task 8.3: Add MCP servers for secure services
- [ ] **Email:** Add an MCP server that interfaces with your email (IMAP/SMTP or Proton Bridge). Scope it to read-only or send-with-confirmation.
- [ ] **Calendar:** Add CalDAV MCP server pointing at Baikal (`dav.trkm.io`)
- [ ] **Budget:** Add YNAB MCP server using their API, or a simple read-only custom server
- [ ] Register all three in ContextForge
- **Guardrail:** Do not build a custom budget app. Use YNAB's API.
- **Done when:** The agent can answer "what's on my calendar?", "show my budget", and "check my email" via MCP tools.

---

## Current State Quick Reference

| Stack | Status | Needs Auth | Needs Own DB | Notes |
|-------|--------|-----------|--------------|-------|
| traefik | Running | N/A | N/A | Needs forwardAuth middleware |
| authentik | Running | N/A | Has own DB | Needs providers configured |
| openwebui | Running | Yes | Has own DB | Wire to LiteLLM |
| litellm | Missing | Yes | Needs stack | Deploy in Phase 1.3 |
| tensorzero | Running | Yes | Has own DB | UI behind auth |
| contextforge | Running | Yes (AUTH_REQUIRED=false) | Shared -> migrate | Secure then add MCP |
| openclaw | Running | Yes | N/A | Config is `{}`, needs setup |
| seerr | Defined | Yes | Shared -> migrate | Start and configure |
| tautulli | Missing | Yes | N/A | Create stack |
| homeassistant | Running | Yes | N/A | Add auth middleware |
| immich | Running | Yes | Shared -> migrate | Migrate DB |
| baikal | Running | Yes | Shared -> migrate | CalDAV server |
| plex | Running | N/A | N/A | Host net, hard to auth via traefik |
| radarr | Running | Uses External auth | Shared -> migrate | 3 instances |
| sonarr | Running | Uses External auth | Shared -> migrate | 3 instances |
| lidarr | Running | Uses External auth | Shared -> migrate | |
| prowlarr | Running | Uses External auth | Shared -> migrate | VPN-proxied |
| sabnzbd | Running | Yes | N/A | VPN-proxied |
| qbittorrent | Running | Yes | N/A | VPN-proxied |
| kometa | Running | Yes | N/A | Fix kid profile visibility |
| recyclarr | Running | N/A | N/A | No web UI |
| headscale | Running | Partial | N/A | Tailnet coord server |
| tuwunel | Running | No | N/A | Open registration — lock down |
| langfuse | Missing | Yes | Needs stack | Deploy in Phase 6.1 |
| signoz | Missing | Yes | Needs stack | Deploy in Phase 6.2 |
| cloudflared | Missing | N/A | N/A | Deploy in Phase 5.1 |

## What NOT To Do (Anti-Rabbit-Hole List)

- Do not migrate to Kubernetes.
- Do not replace Traefik with Caddy/Nginx unless it breaks.
- Do not rewrite OpenClaw or ContextForge.
- Do not build a custom budget app; use YNAB MCP.
- Do not configure complex Home Assistant automations until Phase 3 is done.
- Do not PR Seerr bug until media stack is steady.
- Do not set up Prometheus/Grafana if SigNoz gives you what you need.
- Do not expose *arr apps or admin panels to the internet.
