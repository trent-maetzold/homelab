#!/bin/bash
set -e
source /docker-entrypoint-initdb.d/_lib.sh

ensure_user radarr "$RADARR_POSTGRES_PASSWORD"
ensure_db radarr_hd radarr
ensure_db radarr_hd_log radarr
ensure_db radarr_uhd radarr
ensure_db radarr_uhd_log radarr
ensure_db radarr_anime radarr
ensure_db radarr_anime_log radarr
