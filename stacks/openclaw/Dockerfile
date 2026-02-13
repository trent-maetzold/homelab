FROM node:22-bookworm

# Install Bun (required for build scripts)
RUN curl -fsSL https://bun.sh/install | bash
ENV PATH="/root/.bun/bin:${PATH}"

RUN corepack enable

# Install apt packages
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      git \
      vim \
      curl \
      wget \
      jq \
      python3 \
      python3-pip \
      python3-venv \
      openssh-client \
      ca-certificates \
      gnupg \
      build-essential \
      procps \
      file \
      # CalDAV tools
      vdirsyncer \
      khal \
      todoman \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Docker CLI + GitHub CLI (apt repos)
RUN install -m 0755 -d /etc/apt/keyrings && \
    # Docker
    curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc && \
    chmod a+r /etc/apt/keyrings/docker.asc && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian bookworm stable" > /etc/apt/sources.list.d/docker.list && \
    # GitHub CLI
    curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg -o /etc/apt/keyrings/githubcli.gpg && \
    chmod a+r /etc/apt/keyrings/githubcli.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli.gpg] https://cli.github.com/packages stable main" > /etc/apt/sources.list.d/github-cli.list && \
    # Install both
    apt-get update && \
    apt-get install -y --no-install-recommends docker-ce-cli gh && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Himalaya (static binary)
RUN HIMALAYA_VERSION=$(curl -sL https://api.github.com/repos/pimalaya/himalaya/releases/latest | jq -r .tag_name) && \
    curl -fsSL "https://github.com/pimalaya/himalaya/releases/download/${HIMALAYA_VERSION}/himalaya.x86_64-linux.tgz" | \
    tar xz -C /usr/local/bin himalaya

# Install uv (Python package manager)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    mv /root/.local/bin/uv /usr/local/bin/uv && \
    mv /root/.local/bin/uvx /usr/local/bin/uvx && \
    rm -rf /root/.local

# Clone and build OpenClaw
WORKDIR /app
RUN git clone --depth 1 https://github.com/openclaw/openclaw.git .

RUN pnpm install --frozen-lockfile

RUN OPENCLAW_A2UI_SKIP_MISSING=1 pnpm build
ENV OPENCLAW_PREFER_PNPM=1
RUN pnpm ui:build

ENV NODE_ENV=production

# Use existing node user (uid 1000) from base image
RUN chown -R node:node /app

USER node

CMD ["node", "openclaw.mjs", "gateway", "--allow-unconfigured", "--bind", "lan"]
