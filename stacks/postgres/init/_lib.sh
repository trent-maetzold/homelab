#!/bin/bash

ensure_user() {
    local user=$1
    local password=$2
    psql -v ON_ERROR_STOP=1 <<EOSQL
DO \$\$ BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '$user') THEN
    CREATE ROLE $user WITH LOGIN PASSWORD '$password';
  ELSE
    ALTER ROLE $user WITH PASSWORD '$password';
  END IF;
END \$\$;
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
