# Media staging (not deployed)

`apps/media/` is the source for the k3s media workloads. Plex and the existing PostgreSQL stack stay on Unraid. `just sync-stacks` excludes the migrated stacks so `rsync --delete` leaves the running Unraid copies alone. Remove the exclusions only when intentionally retiring those copies.

## Before cutover

- **Storage:** Plan how to expose the existing app config and `/mnt/user/data` on the target. Keep the existing container paths (`/data`, `/data/torrents`, `/data/usenet`), UID/GID access, and the single filesystem view the Arr apps need for hardlinks and atomic moves. Do not point two live instances at the same config or databases.
- **PostgreSQL:** Lidarr, Prowlarr, Radarr, and Sonarr still use the shared `postgres` host. Provide private reachability and the existing credentials without renaming any main or log database, including the separate HD/UHD/anime pairs. Seerr's input instead uses its own `db` service, `seerr` database, and existing dedicated data directory. Confirm the live Seerr DB before planning a backup/restore; do not assume the shared cluster's `seerr` DB is its active one. No database service, schema, or data was moved.
- **Networking:** Replace the Compose `pvr`, `proxy`, and `postgres` network assumptions with Kubernetes Services and access controls. Prowlarr's Gluetun sidecar shares its pod network; verify it can reach the required internal services.
- **Downloaders:** Follow hotio's WireGuard guides for [qBittorrent](https://hotio.dev/containers/qbittorrent/#wireguard) and [SABnzbd](https://hotio.dev/containers/sabnzbd/#wireguard). Provision a separate Proton WireGuard file at `/config/wireguard/wg0.conf` in each app's config mount; keep keys and any generated tunnel files out of Git. Use a Proton endpoint and profile with port forwarding enabled for qBittorrent only. hotio handles that port natively; do not publish it on the host or reintroduce the old Gluetun callbacks. When testing restored config, check for stale qBittorrent interface bindings (`lo` or the old Gluetun interface). Verify WireGuard and `NET_ADMIN` support, VPN-only egress on tunnel loss, qBittorrent port updates, and Web UI/API reachability from Traefik and the Arr apps.

## Helm release prerequisites

The releases in `apps/media/` are not wired into `clusters/nidavellir`.

- In `media`, provide `nas-data` and the `local-path` StorageClass. Restore each app's `/config` (Seerr: `/app/config`) into its own PVC. FlareSolverr is stateless. Make sure the NFS `torrents` and `usenet` subdirectories exist and are writable by the downloaders.
- Restore the Arr databases behind `arr-postgres-rw` and Seerr's database behind `seerr-postgres-rw`, both in `media`. The releases do not provision PostgreSQL.
- Provide Secrets named `sonarr`, `radarr`, `lidarr`, and `prowlarr`, each with `api-key` and `postgres-password`, plus `seerr` with `postgres-password`. Prowlarr also needs `wireguard-private-key` and `firewall-outbound-subnets`. Scope the latter to the required internal endpoints; never use a default route as a bypass.
- Seed each Hotio PVC with its own `wireguard/wg0.conf`. Check tunnel and local connectivity before starting production traffic, and verify egress is blocked when each tunnel is down.

## Cutover checklist: update saved service URLs

After restoring app configs and databases, check saved URLs in each app's UI or API. Docker container names and aliases do not resolve in k3s; use these Service addresses inside `media`:

| Target | New URL |
| --- | --- |
| Sonarr HD / UHD / Anime | `http://sonarr-hd:8989/hd`, `http://sonarr-uhd:8989/uhd`, `http://sonarr-anime:8989/anime` |
| Radarr HD / UHD / Anime | `http://radarr-hd:7878/hd`, `http://radarr-uhd:7878/uhd`, `http://radarr-anime:7878/anime` |
| Lidarr | `http://lidarr:8686` |
| Prowlarr | `http://prowlarr:9696` |
| qBittorrent (old `qbittorrent_vpn`) | `http://qbittorrent:8080` |
| SABnzbd (old `sabnzbd_vpn`) | `http://sabnzbd:8080` |
| FlareSolverr | `http://flaresolverr:8191` |
| Seerr | `http://seerr:5055` |

- [ ] **Seerr:** Update and test every Sonarr/Radarr connection, keeping the correct URL base and API key. Check the existing Plex connection separately; Plex stays on Unraid.
- [ ] **Prowlarr:** Update and test every Arr connection, Prowlarr's advertised URL for indexer sync, the FlareSolverr proxy, and any configured download clients. Verify its VPN permits those internal connections. Re-sync indexers and test them in Sonarr, Radarr, and Lidarr.
- [ ] **Sonarr, Radarr, and Lidarr:** Test all saved download clients and check media paths and any remote path mappings. Check any connect hooks, webhooks, and indexers for old names. Verify the downloader paths still match `/data/torrents` and `/data/usenet`.
- [ ] **Kometa and Recyclarr on Unraid:** Update any Arr URLs that point at migrated instances (`RADARR_*_URL` and `SONARR_*_URL` for Recyclarr; `radarrurl` and `sonarrurl` for Kometa). Use LAN-reachable routes, not Kubernetes Service names. Check other external clients and scripts for the same issue.
- [ ] **Access:** Set up LAN ingress before moving external clients. These releases only expose ClusterIP services; for a quick test after deployment, forward `svc/seerr` from Yggdrasil over SSH and open `http://localhost:5055`:

  ```sh
  ssh -L 5055:127.0.0.1:5055 tm@10.10.20.10 'sudo k3s kubectl -n media port-forward svc/seerr 5055:5055'
  ```

## Validation

CI renders the pinned chart with the ConfigMap values and inline overrides, then validates the resulting workloads with kubeconform. It needs no cluster access.

After k3s boots, run this from a checkout of this repo on Yggdrasil:

```sh
sudo bash scripts/nidavellir-preflight.sh
```

It checks Flux sync, the CNPG operator, and the storage claims. It creates a temporary Job and local PVC, tests UID 99/GID 100 writes and NFS hardlinks, then cleans up. It does not test database restores, live app connections, or VPN behavior.
