#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE USER lidarr WITH PASSWORD '$LIDARR_POSTGRES_PASSWORD';
    CREATE DATABASE lidarr OWNER lidarr;
    CREATE DATABASE lidarr_log OWNER lidarr;
EOSQL
