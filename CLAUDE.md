# Homelab

Docker Compose stacks for a home server running on Unraid.

## Structure

    stacks/<service>/compose.yaml   — Service definitions
    config/<service>/               — Service configuration files

## Conventions

### Compose files
- Always named `compose.yaml` (not `docker-compose.yml`)
- Top-level key order: `services` → `volumes` → `networks`
- Every service must have `restart: unless-stopped`

### Service key ordering

Keys within each service definition must follow this order:

1. `container_name`
2. `image`
3. `restart`
4. `ports`
5. `cap_add`
6. `volumes`
7. `network_mode` or `networks`
8. `environment`
9. `env_file`
10. `depends_on`
11. `healthcheck`
12. `command`
13. `labels`

Omit keys that don't apply. Don't reorder.

### Naming
- Service names: kebab-case (`immich-server`, `home-assistant`)
- Container names: match the service name, or use a scoped prefix for
  support services (`immich-db`, `immich-cache`, `authelia-redis`)

### Environment variables
- Always quote numeric values: `PUID: "99"`, `PGID: "100"`
- `TZ: America/Chicago` on every service
- Prefer inline `environment:` over `env_file:` unless the service
  requires many variables

### Volumes
- Config storage: `/mnt/user/appdata/<service>/`
- Shared data: `/mnt/user/data/`
- Use `:ro` for read-only mounts
- Named volumes only when shared between services in the same stack

### Networks
- External networks declared with `external: true`
- Internal stack networks defined at the bottom of the file

### Labels
- Unraid icon labels use dashboard-icons PNG URLs
- Traefik labels follow the standard router/service pattern

### Consistency
- All stacks must follow the same patterns. When adding or modifying a
  stack, check an existing one (e.g., `radarr`) as a reference.
- New stacks should be based on `_template/compose.yaml`

### Git
- Conventional commits: `feat:`, `fix:`, `refactor:`, `docs:`, `chore:`
