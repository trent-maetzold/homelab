FROM archlinux:base-devel

ARG AGENT_USER=claw
ARG AGENT_GROUP=agents

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# ── System packages ───────────────────────────────────────────────────────────
RUN mkdir -p /usr/local/bin && \
  pacman-key --init && \
  pacman-key --populate archlinux && \
  pacman -Syyu --noconfirm \
  curl wget git openssl \
  nodejs npm pnpm bun \
  rustup go uv \
  fzf bat fd \
  && pacman -Scc --noconfirm

RUN curl -fsSL https://github.com/tailcallhq/forgecode/releases/latest/download/forge-x86_64-unknown-linux-gnu \
  -o /usr/local/sbin/forge && chmod 755 /usr/local/sbin/forge && \
  curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-onboard

# ── Users and groups ──────────────────────────────────────────────────────────
RUN groupadd -g 2000 ${AGENT_GROUP} && \
  useradd -m -u 2000 -g 2000 -s /bin/bash ${AGENT_USER}

# ── agent ─────────────────────────────────────────────────────────────────────
USER ${AGENT_USER}

ENV NPM_CONFIG_PREFIX=/home/${AGENT_USER}/.local/share/npm \
  NPM_CONFIG_CACHE=/home/${AGENT_USER}/.local/share/npm/cache \
  RUSTUP_HOME=/home/${AGENT_USER}/.local/share/rustup \
  CARGO_HOME=/home/${AGENT_USER}/.local/share/cargo \
  GOPATH=/home/${AGENT_USER}/.local/share/go
ENV PATH=/home/${AGENT_USER}/.local/share/go/bin:${PATH}
ENV PATH=/home/${AGENT_USER}/.local/share/cargo/bin:${PATH}
ENV PATH=/home/${AGENT_USER}/.local/share/npm/bin:${PATH}
ENV PATH=/home/${AGENT_USER}/.local/bin:${PATH}

CMD ["node", "openclaw.mjs", "gateway", "--allow-unconfigured"]
