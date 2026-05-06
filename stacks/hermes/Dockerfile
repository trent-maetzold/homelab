FROM nousresearch/hermes-agent:latest

USER root
WORKDIR /opt/hermes

RUN apt-get update && apt-get install -y --no-install-recommends \
  libolm-dev \
  && rm -rf /var/lib/apt/lists/*

RUN uv pip install --reinstall --no-cache-dir 'mautrix[encryption]'

USER hermes
