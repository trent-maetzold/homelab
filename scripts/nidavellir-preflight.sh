#!/usr/bin/env bash
set -euo pipefail

k() { k3s kubectl "$@"; }
media() { k -n media "$@"; }

k wait --for=condition=Ready node/yggdrasil --timeout=60s
k -n flux-system wait --for=condition=Ready --timeout=120s \
  fluxinstance/flux gitrepository/flux kustomization/flux
k -n cnpg-system rollout status deployment/cloudnative-pg --timeout=120s
media wait --for=jsonpath='{.status.phase}'=Bound pvc/mimir-media --timeout=60s
k get storageclass/local-path

name="media-check-$RANDOM-$RANDOM"
claim_created=false
job_created=false
cleanup() {
  if $job_created; then
    media delete job "$name" --cascade=foreground --timeout=60s || return
  fi
  if $claim_created; then
    media delete pvc "$name" --timeout=60s
  fi
}
trap cleanup EXIT

media create -f - <<EOF_PVC
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: $name
spec:
  storageClassName: local-path
  accessModes: [ReadWriteOnce]
  resources:
    requests:
      storage: 16Mi
EOF_PVC
claim_created=true

media create -f - <<EOF_JOB
apiVersion: batch/v1
kind: Job
metadata:
  name: $name
spec:
  backoffLimit: 0
  activeDeadlineSeconds: 180
  template:
    spec:
      restartPolicy: Never
      automountServiceAccountToken: false
      securityContext:
        runAsUser: 99
        runAsGroup: 100
        runAsNonRoot: true
      containers:
        - name: test
          image: busybox:1.37.0
          command: [sh, -ec]
          args:
            - |
              local_file=\$(mktemp /local/.nidavellir-check.XXXXXX)
              echo ok > "\$local_file"
              test "\$(cat "\$local_file")" = ok
              rm -- "\$local_file"
              echo 'PASS: local-path write/read as 99:100'
              for source in torrents usenet; do
                echo "Testing /data/\$source -> /data/media"
                src=\$(mktemp "/data/\$source/.nidavellir-check.XXXXXX")
                dst=
                trap 'rm -f -- "\$src"; if [ -n "\$dst" ]; then rm -f -- "\$dst/link"; rmdir -- "\$dst"; fi' EXIT
                dst=\$(mktemp -d /data/media/.nidavellir-check.XXXXXX)
                echo ok > "\$src"
                ln -- "\$src" "\$dst/link"
                test "\$(cat "\$dst/link")" = ok
                rm -- "\$dst/link" "\$src"
                rmdir -- "\$dst"
                trap - EXIT
              done
              echo 'PASS: Mimir write/read and hardlinks as 99:100'
          volumeMounts:
            - name: local
              mountPath: /local
            - name: media
              mountPath: /data
      volumes:
        - name: local
          persistentVolumeClaim:
            claimName: $name
        - name: media
          persistentVolumeClaim:
            claimName: mimir-media
EOF_JOB
job_created=true

if ! media wait --for=condition=Complete "job/$name" --timeout=210s; then
  media logs "job/$name" || true
  media describe pods -l "job-name=$name" || true
  exit 1
fi
media logs "job/$name"
