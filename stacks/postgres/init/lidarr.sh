#!/bin/bash
set -e
source /docker-entrypoint-initdb.d/_lib.sh

ensure_user lidarr "$LIDARR_POSTGRES_PASSWORD"
ensure_db lidarr lidarr
ensure_db lidarr_log lidarr
