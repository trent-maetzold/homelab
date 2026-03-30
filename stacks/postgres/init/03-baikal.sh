#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE USER baikal WITH PASSWORD '$BAIKAL_POSTGRES_PASSWORD';
    CREATE DATABASE baikal OWNER baikal;
EOSQL
