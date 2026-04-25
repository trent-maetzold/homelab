# Homelab Steady State Roadmap — Granular Edition

## Objective
Get infrastructure to a steady state where services are deployed, integrated, and secure. Every task is designed to be ~1 hour. **Post-deploy configuration — the real time sink — is explicitly enumerated.**

## Rules

1. **One task, one hour.** If it doesn't fit, it gets split.
2. **Spin-up is not done.** "Deploy" means container is running *and* configured for actual use.
3. **If you hit a wall, document and escalate.** Do not debug for 3 hours. Write the blocker and move to the next task.
4. **Auth strategy:** Authentik for web apps. Apps with strong built-in auth (Plex, HA) stay on Tailnet and use their own auth. *Arr apps use Traefik forwardAuth + their `External` auth mode.
5. **Double-auth is a bug.** If a service asks you to log in after Authentik, stop and fix the integration.

---

## Phase 1: Foundation — Auth & AI Gateway

### Task 1.1: Traefik forwardAuth middleware for Authentik
**Pre-work:** Authentik stack is already running.

- [ ] Create `stacks/traefik/config/dynamic/authentik.yaml`
  - `forwardAuth` middleware pointing to `http://authentik:9000/outpost.goauthentik.io/auth/traefik`
  - `authResponseHeaders: X-Auth-User, X-Auth-Groups, X-Forwarded-User`
- [ ] Create a `chain` middleware named `authentik-chain` that applies `forwardAuth` + `headers`
- [ ] Add `traefik.http.routers.traefik.middlewares: "authentik@file"` to Traefik's own labels (so the dashboard is protected)
- [ ] Restart Traefik stack
- [ ] Verify: `curl -I http://traefik.trkm.io/dashboard/` returns `302` to `auth.trkm.io`
  - *Gotcha:* If you get a certificate error, use `-k` or test from inside the network
- [ ] Log in via Authentik and confirm Traefik dashboard loads
  - *Gotcha:* If the redirect loop happens, check that `trustForwardHeader` is set in the forwardAuth config
- **Done when:** Traefik dashboard requires Authentik login.

---

### Task 1.2: Authentik base setup (users, groups, 2FA)
**Pre-work:** Task 1.1 complete.

- [ ] Log in to `auth.trkm.io` as the bootstrap admin
- [ ] Create your personal user account (separate from admin)
- [ ] Enroll TOTP for your user
- [ ] Create a `family` group, add your user to it
- [ ] Create a `kids` group (even if empty for now)
- [ ] Verify 2FA works by logging out and back in
  - *Gotcha:* Save backup codes. If you lock yourself out, recovery requires DB access.
- [ ] Optional: Enroll a hardware key / WebAuthn if you have one
- **Done when:** You have a non-admin user with working 2FA.

---

### Task 1.3: Protect first web app — OpenWebUI
**Pre-work:** Tasks 1.1 and 1.2 complete.

- [ ] In Authentik, create a **Proxy Provider** for `chat.trkm.io`
  - External host: `https://chat.trkm.io`
  - Internal host: `http://openwebui:8080`
- [ ] Create an Application linking that provider
  - Bind to the `family` group
- [ ] In `stacks/openwebui/compose.yaml`, add label: `traefik.http.routers.openwebui.middlewares: "authentik-chain@file"`
- [ ] Restart OpenWebUI stack
- [ ] Verify: Unauthenticated request 302s to Authentik, login succeeds, OpenWebUI loads
  - *Gotcha:* OpenWebUI may show its own login screen after Authentik. If so:
    - In OpenWebUI Admin Settings -> Authentication, disable local login or set OAuth
    - OR: Accept double-auth for now and fix in Task 1.5
- [ ] Verify WebSockets work (send a test message)
  - *Gotcha:* Traefik needs `ws` upgrade headers. The `headers` middleware in the chain should handle this.
- **Done when:** `chat.trkm.io` requires Authentik and OpenWebUI is usable.

---

### Task 1.4: Protect TensorZero UI and Seerr
**Pre-work:** Task 1.3 complete (you know the pattern now).

- [ ] Repeat Task 1.3 pattern for `t0.trkm.io` (TensorZero UI)
  - Proxy Provider -> Application -> label -> restart -> test
- [ ] Repeat for `seerr.trkm.io`
  - *Gotcha:* Seerr has its own user system. After Authentik login, Seerr may ask you to "sign in with Plex" or create a local user.
  - Fix: In Seerr Settings -> General, set Authentication to `None` or `Proxy` if available. Otherwise, accept Plex login for now.
- **Done when:** Both services require Authentik and load successfully.

---

### Task 1.5: Fix double-auth on OpenWebUI (OAuth mode)
**Pre-work:** Task 1.3 complete.

- [ ] In Authentik, create an **OAuth2/OpenID Provider** (not Proxy)
  - Client type: Confidential
  - Redirect URIs: `https://chat.trkm.io/oauth/oidc/callback`
  - Scopes: `openid`, `profile`, `email`
- [ ] Create an Application for it
- [ ] In OpenWebUI Admin Settings -> Authentication:
  - Enable OAuth
  - Provider URL: `https://auth.trkm.io/application/o/openwebui/.well-known/openid-configuration`
  - Client ID/Secret from Authentik
  - Scope: `openid email profile`
- [ ] Remove the `authentik-chain` middleware from OpenWebUI's Traefik labels (or keep it as a second layer)
  - *Decision:* If OpenWebUI OAuth works well, you can drop the Traefik middleware for OpenWebUI. If not, keep both.
- [ ] Test: Log out of everything. Visit `chat.trkm.io`. You should land on Authentik, then back in OpenWebUI as a logged-in user.
- *Gotcha:* If OpenWebUI creates a new user instead of matching your existing one, check the `email` claim mapping.
- **Done when:** OpenWebUI login flows through Authentik OAuth without a second login screen.

---

### Task 1.6: Deploy LiteLLM stack
**Pre-work:** None. New stack.

- [ ] Create `stacks/litellm/compose.yaml`:
  - `litellm` service (image: `ghcr.io/berriai/litellm:main-latest`)
  - `db` service (postgres:18)
  - `cache` service (valkey)
  - `proxy` network + internal `net`
  - Traefik labels for `llm.trkm.io`
- [ ] Create `stacks/litellm/config/config.yaml`:
  - Model `gpt-4o` -> `openrouter` provider
  - Model `claude-sonnet` -> `openrouter` provider
  - Model `ollama/llama3` -> local Ollama placeholder (even if Ollama isn't up yet)
  - `general_settings`: `master_key` from env
- [ ] Add `.env` entries: `LITELLM_MASTER_KEY`, `LITELLM_SALT_KEY`, `POSTGRES_PASSWORD`
- [ ] Start stack: `docker compose up -d`
- [ ] Verify `/health/readiness` and `/v1/models`
  - *Gotcha:* If config fails to load, check `config.yaml` syntax in the logs. LiteLLM is picky about indentation.
- [ ] Create a test API key via LiteLLM UI or `/key/generate` endpoint
- **Done when:** `curl https://llm.trkm.io/v1/models -H "Authorization: Bearer $KEY"` returns a model list.

---

### Task 1.7: Wire OpenWebUI to LiteLLM
**Pre-work:** Tasks 1.5 and 1.6 complete.

- [ ] In OpenWebUI Admin Settings -> Connections:
  - Add OpenAI API connection
  - URL: `http://litellm:4000` (internal) or `https://llm.trkm.io/v1` (external)
  - Key: `LITELLM_MASTER_KEY`
  - Model IDs: match the names in `config.yaml` exactly
- [ ] Disable OpenWebUI's direct Ollama connection (if it exists) so all traffic routes through LiteLLM
- [ ] Send a test chat message
- [ ] Check LiteLLM logs: `docker logs litellm` should show the request
- [ ] Check that the response streams correctly
  - *Gotcha:* If OpenWebUI hangs, the model name in OpenWebUI might not match the name in LiteLLM config. They must match exactly.
- **Done when:** A chat in OpenWebUI hits LiteLLM and returns a response.

---

## Phase 2: Agent Stack — OpenClaw, ContextForge, MCP

### Task 2.1: Configure OpenClaw gateway
**Pre-work:** Task 1.7 complete.

- [ ] Write `stacks/openclaw/config/openclaw.json`:
  - `gateway` section with `token`
  - `llm` section pointing to `https://llm.trkm.io/v1` with `LITELLM_MASTER_KEY`
  - At least one simple tool definition (e.g., `time`, `echo`)
- [ ] Fix Traefik routing conflict:
  - Option A: Delete `stacks/traefik/config/dynamic/openclaw.yaml` and let compose labels handle it
  - Option B: Ensure the dynamic config doesn't conflict with compose labels
  - *Recommendation:* Delete the dynamic config. Compose labels are easier to maintain.
- [ ] Restart OpenClaw stack
- [ ] Verify `/healthz` returns 200
- [ ] Test a direct gateway request: `curl -H "Authorization: Bearer $TOKEN" https://claw.trkm.io/v1/chat/completions` with a simple body
  - *Gotcha:* If OpenClaw returns 500, check that it can reach LiteLLM. They share the `proxy` network, so `http://litellm:4000` should work internally.
- **Done when:** OpenClaw proxies a chat completion through LiteLLM successfully.

---

### Task 2.2: Integrate OpenClaw into OpenWebUI
**Pre-work:** Task 2.1 complete.

- [ ] In OpenWebUI, add a new "OpenAI API" connection pointing to OpenClaw:
  - URL: `http://openclaw:18789` (internal) or `https://claw.trkm.io` (external)
  - Key: `OPENCLAW_GATEWAY_TOKEN`
- [ ] If OpenClaw doesn't expose an OpenAI-compatible endpoint, check its docs for the correct API shape.
  - *Gotcha:* OpenClaw may use a custom protocol. If so, create a minimal OpenWebUI function in `~/.config/open-webui/functions/` that wraps OpenClaw.
  - Do not spend more than 20 minutes on this. If it's not straightforward, document the blocker.
- [ ] Send a test message in OpenWebUI using the OpenClaw model
- [ ] Verify OpenClaw logs show the request
- **Done when:** OpenWebUI -> OpenClaw -> LiteLLM -> Model works end-to-end.

---

### Task 2.3: Secure ContextForge
**Pre-work:** Task 1.2 complete.

- [ ] Change `AUTH_REQUIRED: "false"` to `"true"` in `stacks/contextforge/compose.yaml`
- [ ] Add `traefik.http.routers.contextforge.middlewares: "authentik-chain@file"`
- [ ] In Authentik, create Proxy Provider + Application for `api.trkm.io/mcp`
- [ ] Restart ContextForge
- [ ] Visit `api.trkm.io/mcp` and verify Authentik login is required
- [ ] Log in with the admin credentials configured in compose (`PLATFORM_ADMIN_EMAIL` / `PLATFORM_ADMIN_PASSWORD`)
  - *Gotcha:* ContextForge may have its own user DB separate from Authentik. The admin account is local. You may need to log in twice (Authentik + ContextForge local) unless you wire OIDC later.
  - *Decision:* For now, accept that ContextForge has local admin auth behind Authentik. Don't chase OIDC for ContextForge in this phase.
- [ ] Verify the UI loads and shows the gateway status
- **Done when:** ContextForge requires Authentik and the admin UI is accessible.

---

### Task 2.4: Add first MCP server to ContextForge
**Pre-work:** Task 2.3 complete.

- [ ] In ContextForge UI, navigate to MCP Servers -> Add Server
- [ ] Add `filesystem` MCP server:
  - Command: `npx -y @modelcontextprotocol/server-filesystem /mnt/cache/appdata/contextforge/shared`
  - Or use Docker-based MCP if ContextForge supports it
- [ ] Verify the server registers and shows as "connected"
- [ ] Test via ContextForge's built-in playground: "list files in the shared directory"
  - *Gotcha:* MCP servers run as subprocesses. If ContextForge can't find `npx`, install Node.js in the image or use a Docker sidecar.
- [ ] If filesystem MCP fails, try a simpler one: `time` or `fetch` (if available)
- **Done when:** ContextForge shows at least one connected MCP server and can execute a tool.

---

### Task 2.5: Connect ContextForge MCP to the agent
**Pre-work:** Tasks 2.2 and 2.4 complete.

- [ ] Configure OpenClaw to use ContextForge as an MCP client:
  - In `openclaw.json`, add an `mcp` section with ContextForge's SSE endpoint: `http://contextforge:4444/sse` or `https://api.trkm.io/mcp/sse`
- [ ] OR: Configure OpenWebUI to use ContextForge directly as a tool source (if OpenWebUI supports MCP)
- [ ] Test a tool-enabled message: "list files in /config"
  - *Gotcha:* If the agent says it doesn't have access to tools, the MCP connection isn't wired correctly.
- [ ] If this integration is non-trivial (no docs, custom protocol), document the exact blocker and move on.
- **Done when:** The agent can successfully invoke an MCP tool via ContextForge, OR a documented blocker exists in `TODO.md`.

---

## Phase 3: High Utility Services

### Task 3.1: Deploy and configure Seerr
**Pre-work:** Task 1.4 complete (Authentik app exists).

- [ ] `cd stacks/seerr && docker compose up -d`
- [ ] Visit `seerr.trkm.io`
  - *Gotcha:* If Seerr shows its own setup wizard before Authentik, you may need to temporarily bypass the Traefik middleware to complete setup, then re-enable it.
- [ ] Complete Seerr setup wizard:
  - Sign in with Plex (this creates the admin user)
  - Configure Radarr instances:
    - HD: `http://radarr_hd:7878/hd`, API key from env
    - UHD: `http://radarr_uhd:7878/uhd`
    - Anime: `http://radarr_anime:7878/anime`
  - Configure Sonarr instances (same pattern)
- [ ] In Seerr Settings -> Users, disable local sign-up if you want Authentik to be the gate
- [ ] Test: Request a movie. Verify it appears in Radarr.
  - *Gotcha:* If Radarr is on the `pvr` network and Seerr is on `proxy` + `postgres`, they may not share a network. Check if DNS resolution works: `docker exec seerr ping radarr_hd`
  - If it fails, add the `pvr` network to `stacks/seerr/compose.yaml`
- [ ] Re-enable Traefik Authentik middleware if you disabled it for setup
- [ ] Verify final flow: Authentik -> Seerr -> request -> Radarr
- **Done when:** You can request media through Seerr and it appears in the *arr app.

---

### Task 3.2: Deploy Tautulli
**Pre-work:** None. New stack.

- [ ] Create `stacks/tautulli/compose.yaml`:
  - Image: `lscr.io/linuxserver/tautulli:latest`
  - Volume: `/mnt/cache/appdata/tautulli/app/config:/config`
  - Port: `8181`
  - Traefik labels for `tautulli.trkm.io` + Authentik middleware
- [ ] Start stack
- [ ] Visit `tautulli.trkm.io`
  - Complete setup wizard
  - Plex URL: `http://plex:32400` (if on same network) or your Plex server URL
  - Plex token: get from Plex settings
- [ ] Verify dashboard shows current Plex activity
- [ ] Optional: Configure a simple notification agent (Discord/Email) — skip if it takes more than 10 minutes
- **Done when:** `tautulli.trkm.io` shows Plex activity behind Authentik.

---

### Task 3.3: Home Assistant — minimal viable setup
**Pre-work:** None. Stack exists.

- [ ] Verify Home Assistant is running at `ha.trkm.io`
  - *Decision:* Do NOT put Authentik in front of HA. HA has strong built-in auth and Zigbee/Z-Wave integrations that break behind proxies. Keep it on Tailnet (`ha.trkm.io` via Tailscale) with HA's own auth.
  - If you already added Authentik middleware in a previous task, remove it.
- [ ] Complete HA onboarding if not done:
  - Create owner account
  - Set home location
- [ ] Install HACS:
  - Follow HACS install script: `wget -O - https://get.hacs.xyz | bash -`
  - Restart HA container
  - Add HACS integration in UI
- [ ] Add 2-3 integrations you actually use:
  - Examples: MQTT, UniFi, ESPHome, Weather, or existing Zigbee dongle
  - *Guardrail:* Only add integrations for hardware you have plugged in.
- [ ] Verify dashboards show real data
- **Done when:** HA is accessible, has HACS, and at least one integration shows live data.

---

### Task 3.4: Build agent homelab status tool
**Pre-work:** Task 2.5 complete (agent can run tools).

- [ ] Create a simple script at `stacks/contextforge/tools/homelab_status.sh`:
  - Running container count
  - Unhealthy containers ( `docker ps --filter health=unhealthy` )
  - Disk usage for `/mnt/cache` and `/mnt/user`
  - Recent container restarts ( `docker events --since 24h --filter event=die` )
- [ ] Output as JSON to `/mnt/cache/appdata/contextforge/shared/status.json`
- [ ] Add a cron job or systemd timer to run it every 2 minutes
  - *Alternative:* Run it as a small sidecar container in the ContextForge stack
- [ ] In ContextForge, register a new MCP tool that reads this JSON file
- [ ] Test: Ask the agent "what's the status of my server?"
  - *Gotcha:* If the agent can't read the file, check permissions. The script and the container need to agree on the volume mount.
- **Done when:** The agent returns current container count, disk usage, and any unhealthy services.

---

## Phase 4: Database Isolation

### Task 4.1: Seerr — migrate to embedded DB
**Pre-work:** Task 3.1 complete (Seerr is configured and working).

- [ ] Stop Seerr: `docker compose down`
- [ ] Backup shared postgres DB: `docker exec postgres pg_dump -U postgres seerr > /tmp/seerr_backup.sql`
- [ ] Add `db` service to `stacks/seerr/compose.yaml` (copy pattern from authentik)
- [ ] Update `DB_HOST` from `postgres` to `db`
- [ ] Remove `postgres` external network from seerr stack
- [ ] Start Seerr stack (new DB will auto-create)
- [ ] Restore data: `docker exec -i seerr_db psql -U seerr -d seerr < /tmp/seerr_backup.sql`
  - *Gotcha:* If restore fails due to schema differences, start fresh. Seerr config (Radarr/Sonarr URLs) is in the app config dir, not the DB.
- [ ] Verify Seerr still works: browse, request a movie
- [ ] Remove seerr init script from `stacks/postgres/init/`
- **Done when:** Seerr runs with embedded DB and all configured *arr connections work.

---

### Task 4.2: Immich — migrate to embedded DB
**Pre-work:** Task 4.1 pattern proven.

- [ ] Stop Immich stack
- [ ] Backup shared postgres: `pg_dump -U postgres immich > /tmp/immich_backup.sql`
- [ ] Add `db` service using `ghcr.io/immich-app/postgres:18-vectorchord0.5.3-pgvector0.8.1`
- [ ] Update `DB_HOSTNAME` to `db`, remove `postgres` external network
- [ ] Start stack, restore DB
- [ ] Verify photo upload and search still work
- [ ] Remove immich init script from shared postgres
- **Done when:** Immich works with embedded DB.

---

### Task 4.3: Baikal — migrate to embedded DB
- [ ] Same pattern: add `db`, update env, migrate data, remove init script
- **Done when:** CalDAV/CardDAV clients still sync.

---

### Task 4.4: ContextForge — migrate to embedded DB
- [ ] Same pattern
- **Done when:** ContextForge UI loads and MCP servers register.

---

### Task 4.5: *arr apps — migrate to embedded DB
- [ ] Pick one stack first (e.g., `stacks/lidarr/`) to prove pattern
- [ ] Add `db` service, update `*_POSTGRES__HOST` to `db`, remove `postgres` external network
- [ ] For VPN-proxied apps (Prowlarr): the `db` service can live on the internal `net` or `pvr` network. It does NOT need to be VPN-proxied.
- [ ] Batch the rest once proven
- [ ] Remove all arr init scripts from shared postgres
- **Done when:** All *arr apps use embedded DB and connect to indexers.

---

### Task 4.6: Retire shared postgres stack
- [ ] Verify `docker network inspect postgres` shows zero connected containers
- [ ] Final backup of entire shared postgres volume
- [ ] `docker compose down` in `stacks/postgres/`
- [ ] Remove `postgres` network: `docker network rm postgres`
- [ ] Move `stacks/postgres/` to `stacks/_retired/postgres/` (don't delete, just archive)
- **Done when:** No `postgres` external network exists; all services still work.

---

## Phase 5: External Access

### Task 5.1: Deploy Cloudflare Tunnel
**Pre-work:** Phase 1 complete (auth works before exposing anything).

- [ ] In Cloudflare Zero Trust dashboard:
  - Create a new tunnel
  - Copy the tunnel token
- [ ] Create `stacks/cloudflared/compose.yaml`:
  - Image: `cloudflare/cloudflared:latest`
  - Command: `tunnel run --token $TUNNEL_TOKEN`
- [ ] Add `.env` entry: `CF_TUNNEL_TOKEN`
- [ ] In Zero Trust dashboard, configure public hostnames:
  - `chat.trkm.io` -> `http://traefik:80` (or `https://traefik:443` if internal TLS)
  - `auth.trkm.io` -> `http://traefik:80`
  - `seerr.trkm.io` -> `http://traefik:80`
  - Add others as needed
  - *Guardrail:* Do NOT expose: traefik dashboard, *arr apps, Proxmox/Unraid, Tautulli, Plex admin, OpenClaw direct (unless needed)
- [ ] Start tunnel
- [ ] From your phone (off WiFi), verify `chat.trkm.io` loads and Authentik login works
  - *Gotcha:* If you get a 404, the tunnel may not be routing to the right Traefik entrypoint. Check the tunnel's internal service URL.
- **Done when:** At least `chat.trkm.io` and `seerr.trkm.io` are reachable from the internet via Cloudflare.

---

### Task 5.2: Restrict Traefik to Cloudflare IPs
- [ ] Add a Traefik IP allowlist middleware for the `websecure` entrypoint
- [ ] Cloudflare publishes IP ranges at `https://www.cloudflare.com/ips-v4` and `ips-v6`
- [ ] OR: Configure Cloudflare Access policies in Zero Trust for extra auth layer
- **Done when:** Direct IP access to port 443 is blocked or less useful.

---

### Task 5.3: Document network segmentation policy
- [ ] Write a simple markdown doc: `docs/network-policy.md`
  - Tailnet only: HA, Traefik dashboard, Unraid, Proxmox, *arr apps, Prowlarr, Tautulli, Plex (admin)
  - Cloudflare exposed: OpenWebUI, Seerr, Authentik, maybe Matrix/Tuwunel
  - VPN-proxied: Prowlarr, qBittorrent, Sabnzbd
- [ ] If Unraid VLAN setup is easy, move cloudflared to an isolated bridge. If not, note it as future work.
- **Done when:** Document exists and you've reviewed it for accuracy.

---

## Phase 6: Observability

### Task 6.1: Deploy Langfuse
**Pre-work:** Phase 1 and LiteLLM running.

- [ ] Create `stacks/langfuse/compose.yaml`:
  - `langfuse-web`, `langfuse-worker`, `db` (postgres), `cache` (valkey)
  - Traefik labels + Authentik middleware for `langfuse.trkm.io`
- [ ] Generate env vars: `NEXTAUTH_SECRET`, `SALT`, `ENCRYPTION_KEY`
- [ ] Start stack, complete initial setup wizard
- [ ] In LiteLLM config/env, add:
  - `LANGFUSE_HOST=https://langfuse.trkm.io`
  - `LANGFUSE_PUBLIC_KEY=...`
  - `LANGFUSE_SECRET_KEY=...`
- [ ] Restart LiteLLM
- [ ] Send a chat via OpenWebUI and verify a trace appears in Langfuse
  - *Gotcha:* If traces don't appear, check LiteLLM logs for Langfuse connection errors.
- **Done when:** `langfuse.trkm.io` shows chat traces with prompts and responses.

---

### Task 6.2: Deploy SigNoz
**Pre-work:** None.

- [ ] Create `stacks/signoz/compose.yaml` using SigNoz all-in-one Docker setup
- [ ] Add Traefik labels + Authentik middleware for `signoz.trkm.io`
- [ ] Configure Docker log driver or OpenTelemetry collector to forward container logs
  - *Simplest:* Add `logging` driver to a few key stacks (LiteLLM, OpenWebUI, Traefik)
- [ ] Verify logs appear in SigNoz
- **Done when:** `signoz.trkm.io` shows logs and at least one service trace.

---

### Task 6.3: Enhance agent status tool with structured data
- [ ] Expand the Phase 3.4 JSON to include:
  - Per-service health status
  - Recent error counts (from Docker events)
  - Disk I/O wait (if easy to get via `iostat`)
- [ ] Add a simple "recommendation" field: e.g., if disk > 85%, suggest cleanup
- [ ] Verify the agent can answer "what's wrong?" with actionable info
- **Done when:** Agent status reports include health, errors, and basic recommendations.

---

## Phase 7: Media Polish

### Task 7.1: Fix Kometa collection visibility for restricted users
**Pre-work:** Kometa stack is defined and running.

- [ ] First, verify Kometa is actually working:
  - Check logs: `docker logs kometa`
  - Look for successful Plex connection and collection creation
  - *Gotcha:* The config uses `<<plexurl>>` but the env var is `KOMETA_PLEXURL`. Kometa's templating uses exact env var names. The placeholder should probably be `<<KOMETA_PLEXURL>>`. Check if the logs show "Unable to connect to Plex" or template errors.
- [ ] If templates aren't resolving, fix the config:
  - Either change env var names to remove `KOMETA_` prefix, or change placeholders to match env vars exactly
- [ ] Once Kometa runs successfully, focus on the kid profile issue:
  - In `config/config.yml`, the current setting is:
    ```yaml
    template_variables:
      collection_mode: hide_items
      collection_filtering: user
    ```
  - The problem: `collection_mode: hide_items` hides items inside collections from the library view, but combined with Plex user restrictions, it may hide items entirely from restricted users because the collection itself isn't filtered.
  - Fix option A: Change `collection_mode: default` (shows items in both collection and library)
  - Fix option B: Add `collection_minimum: 1` and `item_radarr_tag` / `item_sonarr_tag` to filter at the source
  - Fix option C: Use Kometa's `filters` on collections to exclude items based on content rating before they enter the collection
- [ ] Test with one collection first (e.g., `Christmas`)
  - Run Kometa with `--run-collection "Christmas"`
  - Check kid profile: can they see the collection? Can they see items inside it?
- [ ] If none of the config fixes work, document the exact behavior and consider it a Kometa bug/PR candidate
- **Done when:** Kid profiles can see age-appropriate items within collections, OR a documented workaround/blocker exists.

---

## Phase 8: Security Hardening & Advanced Integrations

### Task 8.1: Lock down Tuwunel (Matrix)
- [ ] Disable open registration: set `TUWUNEL_ALLOW_REGISTRATION: "false"` in compose
  - OR: Keep registration but require `TUWUNEL_REGISTRATION_TOKEN` and keep it secret
- [ ] Review `TUWUNEL_ALLOW_FEDERATION`: if you don't need federation, set to `"false"`
- [ ] If Matrix clients support OIDC, consider Authentik integration. Otherwise, keep on Tailnet.
- **Done when:** Random users cannot register on `matrix.trkm.io`.

---

### Task 8.2: Agent gates for server management
- [ ] Define the agent's authority boundary in a new file: `docs/agent-gates.md`
  - Read-only by default: container status, logs, file reads
  - Write requires explicit confirmation: `docker exec`, config changes, file writes, restart/stop
  - Never allowed: password/token retrieval, network reconfiguration, DB destructive ops
- [ ] Implement a simple gate in ContextForge or OpenClaw:
  - Wrap destructive MCP tools in a confirmation function
  - The agent must emit a "Confirm: [action]" message and wait for user reply
- [ ] Test: Ask agent to "restart the litellm container". It should ask for confirmation.
- **Done when:** Destructive actions require explicit user confirmation.

---

### Task 8.3: Add secure MCP servers
- [ ] **Email MCP:**
  - If using Proton: Set up Proton Bridge container, then add MCP server that connects via IMAP to the bridge
  - If using Gmail/Outlook: Use IMAP/SMTP MCP server with app-specific password
  - Register in ContextForge
  - Test: "What emails did I receive today?"
  - *Guardrail:* Start with read-only. Add send capability only after confirming the gate works.
- [ ] **Calendar MCP:**
  - Add CalDAV MCP server pointing to Baikal (`dav.trkm.io`)
  - Test: "What's on my calendar tomorrow?"
- [ ] **Budget MCP:**
  - Use YNAB API: create a personal access token at `https://app.ynab.com/settings/developer`
  - Add a custom MCP server (or use an existing YNAB MCP if available) that calls YNAB API
  - Test: "What's my budget status?"
  - *Guardrail:* Do NOT build a custom budget app. Use YNAB's API directly.
- **Done when:** Agent can query email, calendar, and budget via MCP tools.

---

## Appendix A: Common Gotchas & Time Sinks

| Problem | Where It Happens | How to Avoid |
|---------|-----------------|--------------|
| Double auth | OpenWebUI, Seerr, *arr apps | Decide: Authentik OAuth (disable app auth) OR Authentik proxy + app auth. Don't mix without a plan. |
| *arr `External` auth mode | Radarr, Sonarr, Lidarr, Prowlarr | Traefik must pass `X-Auth-User` header. If Authentik doesn't, *arr rejects. Use Authentik proxy provider, not OAuth, for these. |
| HA behind proxy | Home Assistant | Don't. Keep HA on Tailnet with its own auth. Zigbee/Z-Wave + proxy = pain. |
| Kometa template vars | Kometa config | Env var `KOMETA_PLEXURL` requires placeholder `<<KOMETA_PLEXURL>>`, not `<<plexurl>>`. Check logs for template errors. |
| Shared network DNS | Seerr -> Radarr | If services are on different Docker networks, DNS fails. Add both networks to the consumer stack. |
| VPN-proxied apps | Prowlarr, qBittorrent, Sabnzbd | `network_mode: service:vpn` means Traefik labels go on the `vpn` service, not the `app` service. Verify this is correct in your current compose files. |
| Cloudflare Tunnel 404s | All exposed services | Tunnel internal URL must match Traefik's internal service name. Use `http://traefik:80` if Traefik handles HTTP internally. |

## Appendix B: If You Get Stuck

1. **Write the blocker in `TODO.md` with the exact error message.**
2. **Move to the next task.** The plan is designed so tasks are mostly independent within phases.
3. **Come back to blockers in a "bug fix" hour** after you've made progress elsewhere.
