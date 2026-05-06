FROM nousresearch/hermes-agent:latest

USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
  libolm-dev \
  && rm -rf /var/lib/apt/lists/*

RUN /opt/hermes/.venv/bin/pip install 'mautrix[encryption]'

USER hermes
