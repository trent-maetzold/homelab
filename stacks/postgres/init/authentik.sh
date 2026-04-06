#!/bin/bash
set -e
source /docker-entrypoint-initdb.d/_lib.sh

ensure_user authentik "$AUTHENTIK_POSTGRES_PASSWORD"
ensure_db authentik authentik
