# Homelab

Docker Compose stacks for a home server running on Unraid.

## Structure

    stacks/<service>/compose.yaml           — Service definitions
    stacks/<service>/compose.override.yaml  — Unraid composeman labels (icon, webui, shell per service)
    stacks/<service>/name                   — Display name for the stack in the Unraid UI
    stacks/<service>/icon_url               — Icon URL for the stack in the Unraid UI
    config/<service>/                       — Service configuration files

## Conventions

### Compose files
- Always named `compose.yaml` (not `docker-compose.yml`)
- Prefer exec-form Compose `command:` and `healthcheck.test:` entries with one argument per list item, each double-quoted: `- "--quiet"`
- Use `CMD-SHELL` only as a special case when shell operators like `&&`, `||`, pipes, or similar shell syntax are genuinely needed
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
5. `cap_add`
6. `ports`
7. `volumes`
8. `network_mode` or `networks`
9. `environment`
10. `env_file`
11. `depends_on`
12. `healthcheck`
13. `command`
14. `labels`

Omit keys that don't apply. Don't reorder.

### Naming
- Service names: kebab-case, and should be generic to their role rather than named after the software — `server`, `worker`, `db`, `cache`, `vpn`, `app`, etc. The stack directory already provides the identity.
- Everything else snake_case: stack directory names, container names, volume names, network names
  - Container names use a scoped prefix: `authentik_server`, `authentik_db`, `immich_cache`

### Environment variables
- Always quote all values: `PUID: "99"`, `TZ: "America/Chicago"`, `KOMODO_LOCAL_AUTH: "true"`
- `TZ: "America/Chicago"` on every service
- Prefer inline `environment:` over `env_file:` unless the service
  requires many variables

### Volumes
- App storage: `/mnt/cache/appdata/<stack_name>/<service_name>/<mount_name>` — mount name is the semantic role (`config`, `data`, `logs`, etc.)
  - Use `shared` as the service name for mounts shared across multiple services: `/mnt/cache/appdata/<stack_name>/shared/<mount_name>`
  - e.g. `/mnt/cache/appdata/authentik/shared/data:/data`, `/mnt/cache/appdata/authentik/worker/certs:/certs`
- Database storage: `/mnt/cache/appdata-db/<db_type>/<stack_name>/<mount_name>` where db_type is the engine (`postgres`, `mariadb`, `clickhouse`, etc.)
  - e.g. `/mnt/cache/appdata-db/postgres/authentik/data:/var/lib/postgresql`
- Shared data: `/mnt/cache/data/`
- Use `:ro` for read-only mounts
- Named volumes (snake_case) for persistent data that doesn't need a host path
- Bind mounts for everything else
- Volume ordering within a service: this service's config (`./config/`) → this service's appdata → other service's config → other service's appdata → device mounts → `/var/run/docker.sock`

### Networks
- External networks declared with `external: true`
- Internal stack networks defined at the bottom of the file

### Labels
- Traefik labels go in `compose.yaml`, following the standard router/service pattern
- Always quote label values: `traefik.http.routers.foo.rule: "Host(\`foo.trkm.io\`)"`, `traefik.enable: "true"`
- Unraid composeman labels go in `compose.override.yaml`, never in `compose.yaml`:
  - `net.unraid.docker.managed: "composeman"` — required on every service
  - `net.unraid.docker.icon`: icon URL. Resolution order:
    1. dashboard-icons webp (pinned commit) — `https://raw.githubusercontent.com/homarr-labs/dashboard-icons/<sha>/webp/<name>.webp`
    2. Project's own hosted asset (GitHub repo avatar, official logo URL)
    3. Never omit.
  - `net.unraid.docker.webui`: the web UI URL — set to `""` if no web UI
  - `net.unraid.docker.shell`: `/bin/bash` if available, `/bin/sh` otherwise
- `name` file: plain text display name for the stack (e.g. `TensorZero`, `Baïkal`)
- `icon_url` file: same icon URL as used in `compose.override.yaml`

### Consistency
- All stacks must follow the same patterns. When adding or modifying a
  stack, check an existing one (e.g., `radarr`) as a reference.
- New stacks should be based on `_template/compose.yaml`

### Git
- Conventional commits: `feat:`, `fix:`, `refactor:`, `docs:`, `chore:`
