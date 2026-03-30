#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE USER sonarr WITH PASSWORD '$SONARR_POSTGRES_PASSWORD';
    CREATE DATABASE sonarr_hd OWNER sonarr;
    CREATE DATABASE sonarr_hd_log OWNER sonarr;
    CREATE DATABASE sonarr_uhd OWNER sonarr;
    CREATE DATABASE sonarr_uhd_log OWNER sonarr;
    CREATE DATABASE sonarr_anime OWNER sonarr;
    CREATE DATABASE sonarr_anime_log OWNER sonarr;
EOSQL
