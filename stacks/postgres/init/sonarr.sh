#!/bin/bash
set -e
source /docker-entrypoint-initdb.d/_lib.sh

ensure_user sonarr "$SONARR_POSTGRES_PASSWORD"
ensure_db sonarr_hd sonarr
ensure_db sonarr_hd_log sonarr
ensure_db sonarr_uhd sonarr
ensure_db sonarr_uhd_log sonarr
ensure_db sonarr_anime sonarr
ensure_db sonarr_anime_log sonarr
