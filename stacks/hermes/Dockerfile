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

# ---- Add tools here ----
RUN apt-get update && \
  apt-get install -y --no-install-recommends \
  golang-go rustup \
  bat fd-find fzf && \
  rm -rf /var/lib/apt/lists/* && \
  ln -s /usr/bin/fdfind /usr/local/bin/fd
RUN curl -fsSL \
  https://github.com/tailcallhq/forgecode/releases/latest/download/forge-x86_64-unknown-linux-gnu \
  -o /usr/local/bin/forge && \
  chmod +x /usr/local/bin/forge && \
  curl -fsSL \
  https://github.com/anomalyco/opencode/releases/latest/download/opencode-linux-x64.tar.gz \
  | tar -xz -C /usr/local/bin && \
  chmod +x /usr/local/bin/opencode && \
  chmod -R a+rX /opt/hermes && \
  chown -R hermes:hermes /opt/hermes/ui-tui /opt/hermes/node_modules

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
