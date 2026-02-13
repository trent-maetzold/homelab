# Infra TODOs

## Immich
- [ ] Pin image versions (drop `${IMMICH_VERSION:-release}` pattern, use explicit tags)
- [ ] Review pgvecto-rs version — upstream may have newer
- [ ] Add backup/restore documentation
- [ ] Add `.env.example` with required vars

## Kebab-case Migration (appdata dirs)
- [ ] Rename `/mnt/user/appdata/home_assistant` → `home-assistant`
- [ ] Rename `/mnt/user/appdata/cloudflare_ddns` → `cloudflare-ddns`
- [ ] Update compose files after dir renames
- [ ] Coordinate renames with container downtime (stop → rename → update compose → start)

## Traefik / FQDN
- [ ] Add traefik labels + proxy network to all arr stacks
- [ ] Add traefik labels to immich, sabnzbd, qbittorrent, prowlarr, lidarr
- [ ] Decide: path-based (`radarr.trkm.io/4k`) vs subdomain (`radarr-4k.trkm.io`) for arr variants
- [ ] Set UrlBase in arr instances if going path-based
- [ ] Update Overseerr/Prowlarr API URLs after FQDN changes
