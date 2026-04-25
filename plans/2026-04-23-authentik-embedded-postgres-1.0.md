# Authentik Stack Rebuild Plan

## Objective
Move the authentik database from the external postgres stack to an embedded postgres service within the authentik stack itself.

## Changes Required

### 1. Update `stacks/authentik/compose.yaml`

**Remove:**
- External `postgres` network from server and worker services
- External `postgres` network definition

**Add:**
- New `postgres` service within the stack
- `depends_on` with healthcheck conditions for server and worker
- Healthcheck configuration for the postgres service

**Update:**
- Server and worker to use internal postgres service name (`postgres` → keep same name for minimal config changes)

### 2. Updated compose.yaml Structure

```yaml
services:
  server:
    # Remove external postgres network
    networks:
      - net
      - proxy
    depends_on:
      postgres:
        condition: service_healthy
    # Keep AUTHENTIK_POSTGRESQL__HOST: "postgres" (same name)

  worker:
    # Remove external postgres network
    networks:
      - net
    depends_on:
      postgres:
        condition: service_healthy

  postgres:
    container_name: authentik_postgres
    image: postgres:16-alpine
    restart: unless-stopped
    volumes:
      - /mnt/cache/dbdata/postgres/authentik/data:/var/lib/postgresql/data
    networks:
      - net
    environment:
      TZ: "America/Chicago"
      POSTGRES_DB: "authentik"
      POSTGRES_USER: "authentik"
      POSTGRES_PASSWORD: "${POSTGRES_PASSWORD:?POSTGRES_PASSWORD is required}"
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "authentik", "-d", "authentik"]
      interval: 5s
      timeout: 5s
      retries: 12
      start_period: 30s
      start_interval: 1s

networks:
  net:
  proxy:
    external: true
  # Remove: postgres external network
```

## Environment Variables
The `.env` file will need:
- `AUTHENTIK_VERSION` (existing)
- `POSTGRES_PASSWORD` (existing - used for embedded db)
- `AUTHENTIK_SECRET_KEY` (existing)

## Migration Steps
1. Stop authentik stack
2. Backup existing database from external postgres
3. Deploy new stack with embedded postgres
4. Restore data if needed (or start fresh)
