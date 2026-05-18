#!/bin/bash

set -e
mkdir -p /opt/data/home

if [ ! -f /opt/data/home/.claude.json ] || ! grep -q "hasCompletedOnboarding" /opt/data/home/.claude.json; then
  echo '{"hasCompletedOnboarding": true}' >/opt/data/home/.claude.json
fi

exec /opt/hermes/docker/entrypoint.sh "$@"
