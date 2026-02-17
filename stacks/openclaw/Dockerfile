FROM node:22-bookworm

# Install Bun (required for build scripts)
RUN curl -fsSL https://bun.sh/install | bash
ENV PATH="/root/.bun/bin:${PATH}"

RUN corepack enable

# Add Docker apt repo
RUN install -m 0755 -d /etc/apt/keyrings && \
    curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc && \
    chmod a+r /etc/apt/keyrings/docker.asc && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian bookworm stable" > /etc/apt/sources.list.d/docker.list

# Install apt packages
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      tini \
      jq \
      docker-ce-cli \
      build-essential \
      python3 \
      python3-venv \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install uv (Python package manager)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    mv /root/.local/bin/uv /usr/local/bin/uv && \
    mv /root/.local/bin/uvx /usr/local/bin/uvx && \
    rm -rf /root/.local

# Install Rust (system-wide)
ENV RUSTUP_HOME=/usr/local/rustup
ENV CARGO_HOME=/usr/local/cargo
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --no-modify-path
ENV PATH="/usr/local/cargo/bin:${PATH}"

# Install Go
RUN curl -fsSL https://go.dev/dl/go1.24.0.linux-amd64.tar.gz | tar -C /usr/local -xzf -
ENV PATH="/usr/local/go/bin:${PATH}"

# Clone and build OpenClaw
WORKDIR /app
RUN git clone --depth 1 https://github.com/openclaw/openclaw.git .

RUN pnpm install --frozen-lockfile

RUN OPENCLAW_A2UI_SKIP_MISSING=1 pnpm build
ENV OPENCLAW_PREFER_PNPM=1
RUN pnpm ui:build

# Runtime config
ENV NODE_ENV=production
ENV HOME=/home/node
ENV TERM=xterm-256color

# Global install paths under /home/node
ENV NPM_CONFIG_PREFIX=/home/node/.npm-global
ENV GOPATH=/home/node/go
ENV UV_TOOL_DIR=/home/node/.local/share/uv/tools
ENV UV_TOOL_BIN_DIR=/home/node/.local/bin
ENV PATH="/home/node/go/bin:/home/node/.local/bin:/home/node/.npm-global/bin:${PATH}"

EXPOSE 18789

# Use existing node user (uid 1000) from base image
RUN chown -R node:node /app
USER node

# Create global install directories
RUN mkdir -p /home/node/.npm-global /home/node/.local/bin /home/node/go

ENTRYPOINT ["tini", "--"]
CMD ["node", "openclaw.mjs", "gateway", "--bind", "lan", "--port", "18789"]
