# Hermes on k3s

`apps/hermes/` runs the Hermes agent and its dashboard/Webapp on the Niðavellir
cluster. It replaces the per-host NixOS gateway: one backend, reachable from the
tailnet through Heimdall's Traefik.

## Before Flux reconciles it

Create the namespace Secret by hand; it is never committed:

```sh
sudo k3s kubectl -n hermes create secret generic hermes-secrets \
  --from-literal=HERMES_DASHBOARD_BASIC_AUTH_PASSWORD="$(openssl rand -hex 16)" \
  --from-literal=HERMES_DASHBOARD_BASIC_AUTH_SECRET="$(openssl rand -base64 32)" \
  --from-literal=HERMES_DASHBOARD_SESSION_TOKEN="$(openssl rand -hex 32)" \
  --from-literal=DEEPSEEK_API_KEY=... \
  --from-literal=OPENCODE_API_KEY=...
```

The browser signs in with `tm` plus the basic-auth password. `HERMES_DASHBOARD_SESSION_TOKEN`
is the token Hermes Desktop presents; copy it into `~/.config/hermes/remote-token`
(mode 0600) on a desktop.

## Routes

The Service is a NodePort on Yggdrasil, so Heimdall's Traefik keeps terminating
TLS (Cloudflare DNS-01) and forwards plain HTTP:

| Host | NodePort | Backend |
| --- | --- | --- |
| `dash.hermes.ts.trkm.io` | `30911` | dashboard, 9119 |
| `hermes.ts.trkm.io` | `30912` | Webapp, 9120 |

`nix/hosts/heimdall/edge.nix` in dotfiles points those routes at
`100.64.0.2:30911` and `100.64.0.2:30912`. Keep the NixOS `hermes-agent`
service on Yggdrasil until this Deployment is healthy; it uses 9119/9120
directly, not the NodePorts, so the two do not collide.

## Validation

```sh
sudo k3s kubectl -n hermes get deploy,svc,pvc
sudo k3s kubectl -n hermes logs deploy/hermes -f
curl -fsS http://100.64.0.2:30911/health
```

`config.yaml` is generated into the `hermes-config` ConfigMap and mounted at
`/opt/data/config.yaml`. The image runs as root to chown the data volume, so
the pod deliberately has no `runAsNonRoot`.
