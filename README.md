# Homelab

Docker Compose stacks for Unraid and Compose inputs for the k3s media migration.

## Structure

```
stacks/<service>/compose.yaml   — Service definitions
compose/media/<stack>/          — Compose inputs for Kompose
```

## Stacks

| Stack | Description |
|-------|-------------|
| authelia | Authentication server |
| baikal | CalDAV/CardDAV server |
| cloudflare-ddns | Dynamic DNS updater |
| flaresolverr | Proxy for Cloudflare protection |
| gitea | Git hosting |
| gitlab-runner | GitLab CI runner |
| gluetun | VPN client container |
| headscale | Tailscale coordination server |
| home-assistant | Home automation |
| immich | Photo management |
| kometa | Plex metadata manager |
| lidarr | Music management |
| ollama | Local LLM inference |
| openclaw | Media server |
| overseerr | Media request management |
| plex | Media server |
| prowlarr | Indexer manager |
| qbittorrent | BitTorrent client |
| radarr | Movie management |
| recyclarr | TRaSH Guides sync |
| sabnzbd | Usenet downloader |
| sonarr | TV management |
| traefik | Reverse proxy |

## k3s media migration

PR CI uses Azure Kubernetes Bake with Kompose 1.38.0 and uploads a
`kompose-preview-<stack>-not-for-deployment` artifact for each media stack.
It uses placeholder values, not live credentials. Do not point Flux at these
artifacts. Keep the reviewed Kubernetes manifests and overlays separate from
`compose/`. All eight migration stacks have Flux HelmReleases under
`apps/media/`, using the same pinned app-template chart. Sonarr and Radarr each
share one values file across HD, UHD, and anime. `clusters/nidavellir` does not
reference these releases yet.

Before enabling reconciliation, restore configs and databases, provision the
Secrets and storage listed in [the cutover notes](docs/media-staging.md), and
test VPN fail-closed behavior. Plex and the existing PostgreSQL stack stay on
Unraid. Kometa and Recyclarr remain under `stacks/`.

## Usage

```bash
cd stacks/<service>
docker compose up -d
```
