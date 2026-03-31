#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE USER prowlarr WITH PASSWORD '$PROWLARR_POSTGRES_PASSWORD';
    CREATE DATABASE prowlarr OWNER prowlarr;
    CREATE DATABASE prowlarr_log OWNER prowlarr;
EOSQL
