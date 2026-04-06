#!/bin/bash
set -e
source /docker-entrypoint-initdb.d/_lib.sh

ensure_user baikal "$BAIKAL_POSTGRES_PASSWORD"
ensure_db baikal baikal
