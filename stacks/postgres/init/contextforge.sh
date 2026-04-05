#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE USER contextforge WITH PASSWORD '$CONTEXTFORGE_POSTGRES_PASSWORD';
    CREATE DATABASE contextforge OWNER contextforge;
EOSQL
