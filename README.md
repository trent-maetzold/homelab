# Homelab

Docker Compose stacks for Unraid and Compose inputs for the k3s media migration.

## Structure

```
stacks/<service>/compose.yaml   — Service definitions
compose/media/<stack>/          — Compose inputs for Kompose
compose/jobs/<job>/             — Compose inputs for Kometa and Recyclarr (not deployed)
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
`compose/`; Flux will reconcile those once the workloads are ready.

Before enabling reconciliation, wire up Secrets, storage and permissions,
unique workload and Service names, and ingress. Keep the media mount at `/data`,
restore the app databases and configs from Mimir before starting the new writers,
and validate the VPN-backed workloads. Prowlarr still needs its Gluetun network
namespace translated explicitly; Kompose does not preserve it. Plex and the
shared PostgreSQL stack stay on Unraid. Kometa and Recyclarr are excluded from
conversion until a scheduler is chosen.

## Usage

```bash
cd stacks/<service>
docker compose up -d
```
