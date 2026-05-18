FROM nousresearch/hermes-agent:latest

# Set install locations and path for tools installed below
ENV DEBIAN_FRONTEND=noninteractive \
  HOME=/opt/hermes
ENV CARGO_HOME=${HOME}/.local/share/cargo \
  RUSTUP_HOME=${HOME}/.local/share/rustup \
  GOPATH=${HOME}/.local/share/go \
  npm_config_prefix=${HOME}/.local/share/npm \
  PATH="${HOME}/.local/share/cargo/bin:\
  ${HOME}/.local/share/rustup/bin:\
  ${HOME}/.local/share/go/bin:\
  ${HOME}/.local/share/npm/bin:\
  ${PATH}"

COPY ./pre-entrypoint.sh /opt/hermes/docker/pre-entrypoint.sh

# Apt Dependencies
RUN apt-get update && \
  apt-get install -y --no-install-recommends \
  docker-cli docker-compose \
  golang-go rustup \
  bat fd-find fzf && \
  rm -rf /var/lib/apt/lists/* && \
  ln -s /usr/bin/fdfind /usr/local/bin/fd

RUN chmod -R a+rX /opt/hermes && \
  chown -R hermes:hermes /opt/hermes/ui-tui /opt/hermes/node_modules && \
  # Install Opencode
  curl -fsSL \
  https://github.com/anomalyco/opencode/releases/latest/download/opencode-linux-x64.tar.gz \
  | tar -xz -C /usr/local/bin && \
  chmod +x /usr/local/bin/opencode && \
  # Install Claude Code
  LATEST=$(curl -fsSL https://downloads.claude.ai/claude-code-releases/latest) && \
  curl -fsSL "https://downloads.claude.ai/claude-code-releases/${LATEST}/linux-x64/claude" \
  -o /usr/local/bin/claude && \
  chmod +x /usr/local/bin/claude

# Set install locations and path for the running agent
ENV HOME=/opt/data/home
ENV CARGO_HOME=${HOME}/.local/share/cargo \
  RUSTUP_HOME=${HOME}/.local/share/rustup \
  GOPATH=${HOME}/.local/share/go \
  npm_config_prefix=${HOME}/.local/share/npm \
  PATH="${HOME}/.local/share/cargo/bin:\
  ${HOME}/.local/share/rustup/bin:\
  ${HOME}/.local/share/go/bin:\
  ${HOME}/.local/share/npm/bin:\
  ${PATH}"

ENTRYPOINT [ "/usr/bin/tini", "-g", "--", "/opt/hermes/docker/pre-entrypoint.sh" ]
