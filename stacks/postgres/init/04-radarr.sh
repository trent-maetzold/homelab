#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE USER radarr WITH PASSWORD '$RADARR_POSTGRES_PASSWORD';
    CREATE DATABASE radarr_hd OWNER radarr;
    CREATE DATABASE radarr_hd_log OWNER radarr;
    CREATE DATABASE radarr_uhd OWNER radarr;
    CREATE DATABASE radarr_uhd_log OWNER radarr;
    CREATE DATABASE radarr_anime OWNER radarr;
    CREATE DATABASE radarr_anime_log OWNER radarr;
EOSQL
