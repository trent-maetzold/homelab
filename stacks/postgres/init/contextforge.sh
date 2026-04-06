#!/bin/bash
set -e
source /docker-entrypoint-initdb.d/_lib.sh

ensure_user contextforge "$CONTEXTFORGE_POSTGRES_PASSWORD"
ensure_db contextforge contextforge
