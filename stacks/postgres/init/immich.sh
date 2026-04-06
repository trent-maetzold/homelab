#!/bin/bash
set -e
source /docker-entrypoint-initdb.d/_lib.sh

ensure_user immich "$IMMICH_POSTGRES_PASSWORD"
ensure_db immich immich
