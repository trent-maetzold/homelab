# Homelab

Docker Compose stacks for a home server running on Unraid.

## Structure

    stacks/<service>/compose.yaml           — Service definitions
    stacks/<service>/compose.override.yaml  — Unraid composeman labels (icon, webui, shell per service)
    stacks/<service>/name                   — Display name for the stack in the Unraid UI
    stacks/<service>/icon_url               — Icon URL for the stack in the Unraid UI
    stacks/<service>/config/                — Service configuration files (stack-local)

## Conventions

### Compose files

- Always named `compose.yaml` (not `docker-compose.yml`)
- Prefer inline JSON array form for `command:` and `healthcheck.test:`: `["cmd", "--flag", "value"]`
- Use multi-line list form when the array is too long to fit on one line (prettier will reformat inline arrays to a multi-line JSON block — convert those to YAML list form instead: `- "cmd"`):
- Never use a bare string for `healthcheck.test:` — it silently invokes CMD-SHELL
- Do not prefix `healthcheck.test` arrays with `"CMD"` — it is implicit and adds noise
- Use `CMD-SHELL` only when shell operators like `&&`, `||`, pipes, or redirects are genuinely needed
- First line: `# yaml-language-server: $schema=https://raw.githubusercontent.com/compose-spec/compose-spec/master/schema/compose-spec.json`
- Blank line after the yaml-language-server comment
- Top-level key order: `services` → `volumes` → `networks`
- Blank line between each service definition
- Blank line before each top-level key (`volumes:`, `networks:`)
- Every service must have `restart: unless-stopped`

### Service key ordering

Keys within each service definition must follow this order:

1. `container_name`
2. `hostname`
3. `image`
4. `restart`
5. `user`
6. `cap_add`
7. `devices`
8. `ports`
9. `volumes`
10. `network_mode` or `networks`
11. `environment`
12. `env_file`
13. `depends_on`
14. `healthcheck`
15. `command`
16. `ulimits`
17. `labels`

Omit keys that don't apply. Don't reorder.

### Naming

- Service names: kebab-case, generic to role — `server`, `worker`, `db`, `cache`, `vpn`, `app`, etc. The stack directory already provides the identity.
  - Exception: when upstream hardcodes service names for inter-service DNS (e.g. immich uses `immich-machine-learning` as the default ML hostname), override the env var instead and use the generic name.
  - Multi-instance stacks (same role, multiple instances): use the differentiator as the service name — `hd`, `uhd`, `anime` — scoped in the container name: `radarr_hd`, `sonarr_anime`.
- Everything else snake_case: stack directory names, container names, volume names, network names
  - Primary service container name = stack name: `authentik`, `immich`, `tensorzero`
  - Secondary/sidecar containers get a scoped prefix: `authentik_worker`, `immich_cache`, `tensorzero_db`

### Environment variables

- Always quote all values: `PUID: "99"`, `TZ: "America/Chicago"`, `KOMODO_LOCAL_AUTH: "true"`
- `TZ: "America/Chicago"` on every service
- Prefer inline `environment:` over `env_file:` unless the service
  requires many variables
- Required secrets must use `${VAR:?VAR is required}` — Compose will fail to start if the variable is unset or empty

### Volumes

- App storage: `/mnt/cache/appdata/<stack_name>/<service_name>/<mount_name>` — mount name is the semantic role (`config`, `data`, `logs`, etc.)
  - Use `shared` as the service name for mounts shared across multiple services: `/mnt/cache/appdata/<stack_name>/shared/<mount_name>`
  - e.g. `/mnt/cache/appdata/authentik/shared/data:/data`, `/mnt/cache/appdata/authentik/worker/certs:/certs`
- Database storage: `/mnt/cache/dbdata/<db_type>/<stack_name>/<mount_name>` where db_type is the engine (`postgres`, `mariadb`, `clickhouse`, etc.)
  - e.g. `/mnt/cache/dbdata/postgres/authentik/data:/var/lib/postgresql`
- Shared data: `/mnt/user/data/` — stays on Unraid FUSE (do not move to cache)
- Use `:ro` for read-only mounts
- Named volumes (snake_case) for persistent data that doesn't need a host path
- Bind mounts for everything else
- Volume ordering within a service: order by semantic type — `config` → `data` → `cache` → `logs` → device mounts → `/var/run/docker.sock`. All `./config/` mounts are config by nature.
- **Overlay ordering**: when one mount is a child path of another (e.g. a config file mounted inside an appdata directory), the parent mount must come first regardless of type — Docker applies mounts in list order and a later broader mount stomps an earlier specific one

### Shared database instances

A single DB container can serve multiple stacks. This applies to any engine — currently postgres and clickhouse are shared.

**When to use the shared instance vs. a dedicated one:**
- Use the shared instance by default
- Give an app its own instance when its DB requirements would monopolize a cluster-wide resource or capability of the shared instance — e.g. `pg_cron` is a single scheduler per postgres cluster, so any app that needs it gets a dedicated postgres (tensorzero does this). Apply the same logic for other engines: if an app needs an exclusive extension, config flag, or feature, spin its own instance.

**Structure:**
- The shared DB stack lives at `stacks/<engine>/` (e.g. `stacks/postgres/`, `stacks/clickhouse/`)
- Per-tenant init scripts live at `stacks/<engine>/init/`, mounted to `/docker-entrypoint-initdb.d/:ro` — both postgres and clickhouse use this convention; verify for other engines
- Each consumer gets its own user and database(s) within the instance
- The consumer's password is passed into the shared DB container as an env var (e.g. `RADARR_POSTGRES_PASSWORD`) and referenced in the init script

**Postgres init scripts** (`.sh`, run via `psql`):
```bash
#!/bin/bash
set -e
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE USER myapp WITH PASSWORD '$MYAPP_POSTGRES_PASSWORD';
    CREATE DATABASE myapp OWNER myapp;
EOSQL
```

**Clickhouse** creates the primary database and user from `CLICKHOUSE_DB` / `CLICKHOUSE_USER` / `CLICKHOUSE_PASSWORD` env vars automatically. Init `.sql` files are for supplemental grants or schema setup only.

**Generating passwords:**

Use 48-char hex so passwords are URL-safe in `DATABASE_URL` connection strings without encoding:
```
openssl rand -hex 24
```

**Adding a new consumer:**
1. Add a `<STACK>_POSTGRES_PASSWORD` (or equivalent) env var to the shared DB stack's `environment:` and `.env`
2. Add an init script at `stacks/<engine>/init/<stack>.<sh|sql>`
3. Reference the shared network and hostname in the consumer stack's environment

### Networks

- External networks declared with `external: true`
- Internal stack networks defined at the bottom of the file

### Labels

- Traefik labels go in `compose.yaml`, following the standard router/service pattern
- Always quote label values: `traefik.http.routers.foo.rule: "Host(\`foo.trkm.io\`)"`,`traefik.enable: "true"`
- Unraid composeman labels go in `compose.override.yaml`, never in `compose.yaml`:
  - `net.unraid.docker.managed: "composeman"` — required on every service
  - `net.unraid.docker.icon`: icon URL. Resolution order:
    1. dashboard-icons PNG — `https://raw.githubusercontent.com/homarr-labs/dashboard-icons/refs/heads/main/png/<name>.png` (curl to verify 200)
    2. Project's own hosted asset (GitHub repo avatar, official logo URL)
    3. Never omit.
  - `net.unraid.docker.webui`: the web UI URL — set to `""` if no web UI
  - `net.unraid.docker.shell`: `/bin/bash` if available, `/bin/sh` otherwise
- `name` file: plain text display name for the stack (e.g. `TensorZero`, `Baïkal`)
- `icon_url` file: same icon URL as used in `compose.override.yaml`

### Consistency

All stacks must follow the same patterns. Reference examples below.

**Simple stack** (`stacks/myapp/compose.yaml`):

```yaml
# yaml-language-server: $schema=https://raw.githubusercontent.com/compose-spec/compose-spec/master/schema/compose-spec.json

services:
  app:
    container_name: myapp
    image: example/myapp:latest
    restart: unless-stopped
    volumes:
      - ./config/myapp.yaml:/etc/myapp/config.yaml:ro
      - /mnt/cache/appdata/myapp/app/data:/data
    networks:
      - proxy
    environment:
      TZ: "America/Chicago"
      MY_SECRET: "${MY_SECRET}"
    healthcheck:
      test: ["wget", "--spider", "--quiet", "http://localhost:8080/health"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 10s
    labels:
      traefik.enable: "true"
      traefik.http.routers.myapp.rule: "Host(`myapp.trkm.io`)"
      traefik.http.services.myapp.loadBalancer.server.port: "8080"

networks:
  proxy:
    external: true
```

**Simple stack** (`stacks/myapp/compose.override.yaml`):

```yaml
services:
  app:
    labels:
      net.unraid.docker.managed: "composeman"
      net.unraid.docker.icon: "https://raw.githubusercontent.com/homarr-labs/dashboard-icons/refs/heads/main/png/myapp.png"
      net.unraid.docker.webui: "https://myapp.trkm.io"
      net.unraid.docker.shell: "/bin/bash"
```

**VPN-proxied stack** (`stacks/myapp/compose.yaml`):

```yaml
# yaml-language-server: $schema=https://raw.githubusercontent.com/compose-spec/compose-spec/master/schema/compose-spec.json

services:
  app:
    container_name: myapp
    image: example/myapp:latest
    restart: unless-stopped
    volumes:
      - /mnt/cache/appdata/myapp/app/config:/config
      - /mnt/user/data/downloads:/data/downloads
    network_mode: "service:vpn"
    environment:
      TZ: "America/Chicago"
      PUID: "99"
      PGID: "100"
    depends_on:
      - vpn

  vpn:
    container_name: myapp_vpn
    image: qmcgaw/gluetun:latest
    restart: unless-stopped
    cap_add:
      - NET_ADMIN
    devices:
      - /dev/net/tun:/dev/net/tun
    volumes:
      - /mnt/cache/appdata/myapp/vpn/config:/gluetun
    networks:
      - proxy
    environment:
      TZ: "America/Chicago"
      VPN_SERVICE_PROVIDER: "protonvpn"
      VPN_TYPE: "wireguard"
      WIREGUARD_PRIVATE_KEY: "${WIREGUARD_PRIVATE_KEY}"
      SERVER_CITIES: "Chicago"
    labels:
      traefik.enable: "true"
      traefik.http.routers.myapp.rule: "Host(`myapp.trkm.io`)"
      traefik.http.services.myapp.loadBalancer.server.port: "8080"

networks:
  proxy:
    external: true
```

### Git

- Conventional commits: `feat:`, `fix:`, `refactor:`, `docs:`, `chore:`
