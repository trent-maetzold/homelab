FROM node:22-bookworm

# Install tini for proper PID 1 signal handling
RUN apt-get update && \
    apt-get install -y --no-install-recommends tini && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Bun (required for build scripts)
RUN curl -fsSL https://bun.sh/install | bash
ENV PATH="/root/.bun/bin:${PATH}"

RUN corepack enable

# Install apt packages
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      git \
      curl \
      jq \
      ca-certificates \
      gnupg \
      procps \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Docker CLI (for managing stacks via dind)
RUN install -m 0755 -d /etc/apt/keyrings && \
    curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc && \
    chmod a+r /etc/apt/keyrings/docker.asc && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian bookworm stable" > /etc/apt/sources.list.d/docker.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends docker-ce-cli && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

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
ENV PATH="/home/node/.npm-global/bin:${PATH}"

EXPOSE 18789

# Use existing node user (uid 1000) from base image
RUN chown -R node:node /app
USER node

# Create global install directories
RUN mkdir -p /home/node/.npm-global

ENTRYPOINT ["tini", "--"]
CMD ["node", "openclaw.mjs", "gateway", "--bind", "lan", "--port", "18789"]
