#!/bin/bash

ensure_user() {
    local user=$1
    local password=$2
    psql -v ON_ERROR_STOP=1 <<EOSQL
CREATE USER IF NOT EXISTS $user WITH PASSWORD '$password';
ALTER USER $user WITH PASSWORD '$password';
EOSQL
}

ensure_db() {
    local db=$1
    local owner=$2
    psql -v ON_ERROR_STOP=1 <<EOSQL
SELECT 'CREATE DATABASE $db OWNER $owner' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$db')
\gexec
EOSQL
}
