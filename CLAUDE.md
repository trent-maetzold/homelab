# Homelab

Docker Compose stacks for a home server running on Unraid.

## Structure

    stacks/<service>/compose.yaml   — Service definitions
    config/<service>/               — Service configuration files

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
- Service names: kebab-case (`immich-server`, `home-assistant`) — used as DNS hostnames
- Everything else snake_case: stack directory names, container names, volume names, network names
  - Container names match the service name or use a scoped prefix for support services (`immich_db`, `immich_cache`, `authelia_redis`)

### Environment variables
- Always quote all values: `PUID: "99"`, `TZ: "America/Chicago"`, `KOMODO_LOCAL_AUTH: "true"`
- `TZ: "America/Chicago"` on every service
- Prefer inline `environment:` over `env_file:` unless the service
  requires many variables

### Volumes
- Config/appdata storage: `/mnt/user/appdata/<service>/`
- Database data storage: `/mnt/user/appdata-db/<service>/`
- Shared data: `/mnt/user/data/`
- Use `:ro` for read-only mounts
- Named volumes (snake_case) for persistent data that doesn't need a host path
- Bind mounts for everything else

### Networks
- External networks declared with `external: true`
- Internal stack networks defined at the bottom of the file

### Labels
- Unraid labels on every service:
  - `net.unraid.docker.icon`: every service must have an icon. Resolution
    order:
    1. dashboard-icons PNG — try
       `https://raw.githubusercontent.com/homarr-labs/dashboard-icons/refs/heads/main/png/<name>.png`
       first, but curl to verify it returns 200. If not found on `main`,
       search the repo tree (`png/` dir via GitHub API) for the correct filename.
    2. Find an icon from another authoritative source (e.g. official GitHub
       repo avatar, project website).
    3. Generate one with an image model.
    Never omit this label.
  - `net.unraid.docker.webui`: the web UI URL — omit the label entirely if the service has no web UI
  - `net.unraid.docker.shell`: `/bin/bash` if available, `/bin/sh`
    otherwise — test with `podman run --rm --entrypoint /bin/bash <image> -c "echo ok"`
    to verify before using `/bin/bash`
- Always quote all label values: `traefik.enable: "true"`, `net.unraid.docker.shell: "/bin/bash"`
- Traefik labels follow the standard router/service pattern

### Consistency
- All stacks must follow the same patterns. When adding or modifying a
  stack, check an existing one (e.g., `radarr`) as a reference.
- New stacks should be based on `_template/compose.yaml`

### Git
- Conventional commits: `feat:`, `fix:`, `refactor:`, `docs:`, `chore:`
