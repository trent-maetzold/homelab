# Homelab

Docker Compose stacks for Unraid and Helm releases for k3s media apps.

## Structure

```
stacks/<service>/compose.yaml   — Service definitions
apps/media/<app>/               — Flux HelmRelease definitions and values
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

PR CI renders the Flux HelmReleases, validates the Kubernetes resources, and
uploads the rendered manifests for review. It does not deploy them. All eight
media apps use the same pinned app-template chart. Sonarr and Radarr each
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
