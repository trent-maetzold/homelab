# Hermes on k3s

`apps/hermes/` runs the Hermes agent and its dashboard on the Niðavellir
cluster. It replaces the per-host NixOS gateway: one backend, reachable from
the tailnet through the cluster Traefik.

## Before Flux reconciles it

Flux creates the `hermes` namespace on the first reconcile. Create the Secret
by hand once it exists (or create the namespace first); it is never committed:

```sh
sudo k3s kubectl -n hermes create secret generic hermes-secrets \
  --from-literal=HERMES_DASHBOARD_BASIC_AUTH_PASSWORD="$(openssl rand -hex 16)" \
  --from-literal=HERMES_DASHBOARD_BASIC_AUTH_SECRET="$(openssl rand -base64 32)" \
  --from-literal=HERMES_DASHBOARD_SESSION_TOKEN="$(openssl rand -hex 32)" \
  --from-literal=DEEPSEEK_API_KEY=... \
  --from-literal=OPENCODE_API_KEY=...
```

The browser signs in with `tm` plus the basic-auth password.
`HERMES_DASHBOARD_SESSION_TOKEN` is the token Hermes Desktop presents; copy it
into `~/.config/hermes/remote-token` (mode 0600) on a desktop.

## Routing

The Service is a ClusterIP. The cluster Traefik reaches it directly — no
NodePort or hostPort — and the Ingress asks cert-manager for the certificate:

| Host | Ingress backend | Certificate |
| --- | --- | --- |
| `hermes.ts.trkm.io` | `hermes:9119` (dashboard) | `hermes/hermes-tls` |

`hermes.ts.trkm.io` resolves through Headscale MagicDNS to Yggdrasil
(`100.64.0.2`), where the k3s Traefik terminates TLS. The Ingress uses the
`letsencrypt-cloudflare` ClusterIssuer from the Seerr/cert-manager change, so
provision the `cert-manager/cloudflare-dns01` Secret first.

Dotfiles no longer defines a Heimdall route for this host; it keeps only the
`gw.hermes.ts.trkm.io` API-server route until the NixOS `hermes-agent` service
on Yggdrasil is retired.

## Validation

```sh
sudo k3s kubectl -n hermes get deploy,svc,pvc,ingress,certificate
sudo k3s kubectl -n hermes logs deploy/hermes -f
curl -sSI https://hermes.ts.trkm.io/ | head -1   # 401 until you sign in
```

`config.yaml` is generated into the `hermes-config` ConfigMap and mounted at
`/opt/data/config.yaml`. The image runs as root to chown the data volume, so
the pod deliberately has no `runAsNonRoot`.
