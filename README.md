# Homelab

Docker Compose stacks for a home server running on Unraid.

## Structure

```
stacks/<service>/compose.yaml   — Service definitions
config/<service>/               — Service configuration files
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

## Usage

```bash
cd stacks/<service>
docker compose up -d
```
