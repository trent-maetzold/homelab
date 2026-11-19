# Media staging (not deployed)

`compose/media/` contains migration inputs, not Flux workloads. Plex and the shared PostgreSQL stack stay on Unraid. The running media stacks also stay there for now: `just sync-stacks` excludes their old directories so `rsync --delete` leaves the production copies alone. Merge both phases together; the move-only commit does not contain this protection. Remove the exclusions only when intentionally retiring those copies.

## Before cutover

- **Storage:** Plan how to expose the existing app config and `/mnt/user/data` on the target. Keep the existing container paths (`/data`, `/data/torrents`, `/data/usenet`), UID/GID access, and the single filesystem view the Arr apps need for hardlinks and atomic moves. Do not point two live instances at the same config or databases.
- **PostgreSQL:** Lidarr, Prowlarr, Radarr, and Sonarr still use the shared `postgres` host. Provide private reachability and the existing credentials without renaming any main or log database, including the separate HD/UHD/anime pairs. Seerr's input instead uses its own `db` service, `seerr` database, and existing dedicated data directory. Confirm the live Seerr DB before planning a backup/restore; do not assume the shared cluster's `seerr` DB is its active one. No database service, schema, or data was moved.
- **Networking:** Replace the Compose `pvr`, `proxy`, and `postgres` network assumptions with target DNS, routing, and access controls. Preserve the Radarr/Sonarr `/hd`, `/uhd`, and `/anime` URLs and check download-client, indexer, Plex, and FlareSolverr connectivity. Prowlarr still uses Gluetun and `network_mode: service:vpn`; it needs an explicit VPN networking design on the target.
- **Downloaders:** Follow hotio's WireGuard guides for [qBittorrent](https://hotio.dev/containers/qbittorrent/#wireguard) and [SABnzbd](https://hotio.dev/containers/sabnzbd/#wireguard). Provision a separate Proton WireGuard file at `/config/wireguard/wg0.conf` in each app's config mount; keep keys and any generated tunnel files out of Git. Use a Proton endpoint and profile with port forwarding enabled for qBittorrent only. hotio handles that port natively; do not publish it on the host or reintroduce the old Gluetun callbacks. When testing restored config, check for stale qBittorrent interface bindings (`lo` or the old Gluetun interface). Verify WireGuard and `NET_ADMIN` support, VPN-only egress on tunnel loss, qBittorrent port updates, and Web UI/API reachability from Traefik and the Arr apps. The legacy downloader DNS aliases are retained on `pvr` for Compose only.

## Manual jobs

Kometa and Recyclarr stay out of generated Deployments. On a Compose host with the expected mounts, `pvr` network, service endpoints, and credentials, run from the repository root:

```sh
docker compose -f compose/jobs/kometa/compose.yaml run --rm app
docker compose -f compose/jobs/recyclarr/compose.yaml run --rm app
```

These run Kometa with `--run` and Recyclarr with `sync` (v8 CLI syntax), then remove the one-off container. Both jobs write to the configured services; check the endpoints before running them.

## CI previews

Convert each `compose/media/*/compose.yaml` separately into its own directory: stacks reuse service names such as `app` and `vpn`. Keep `compose/jobs/` out of conversion. Use dummy values for required interpolation (`ARR_API_KEY`, `POSTGRES_PASSWORD`, and Prowlarr's `WIREGUARD_PRIVATE_KEY`), never live credentials. Treat output as preview only: Compose aliases, shared VPN namespaces, host mounts, and Traefik labels do not establish equivalent Kubernetes routing, storage, or VPN behavior.
