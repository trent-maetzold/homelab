#!/bin/bash
set -e
source /docker-entrypoint-initdb.d/_lib.sh

ensure_user prowlarr "$PROWLARR_POSTGRES_PASSWORD"
ensure_db prowlarr prowlarr
ensure_db prowlarr_log prowlarr
