#!/bin/bash
set -e
source /docker-entrypoint-initdb.d/_lib.sh

ensure_user seerr "$SEERR_POSTGRES_PASSWORD"
ensure_db seerr seerr
