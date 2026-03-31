#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE USER authentik WITH PASSWORD '$AUTHENTIK_POSTGRES_PASSWORD';
    CREATE DATABASE authentik OWNER authentik;
EOSQL
