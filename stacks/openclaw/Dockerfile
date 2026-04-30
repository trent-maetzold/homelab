FROM archlinux:base-devel

ARG OPENCLAW_USER=claw
ARG OPENCLAW_GROUP=agents

RUN pacman -Syyu --noconfirm \
  # languages and runtimes
  nodejs \
  npm \
  rustup \
  go \
  uv \
  # cli tools
  github-cli \
  khal \
  vdirsyncer \
  # build dependencies
  libffi \
  openssl \
  sqlite \
  zlib \
  # networking and version control
  curl \
  wget \
  git \
  && pacman -Scc --noconfirm

RUN groupadd -g 1000 ${OPENCLAW_GROUP} && \
  useradd -m -u 1000 -g 1000 -s /bin/bash ${OPENCLAW_USER}

ENV HOME=/home/${OPENCLAW_USER}

USER ${OPENCLAW_USER}
WORKDIR ${HOME}

# Override default tool directories
ENV NPM_CONFIG_PREFIX=${HOME}/.local/share/npm
ENV NPM_CONFIG_CACHE=${HOME}/.local/share/npm/cache
ENV RUSTUP_HOME=${HOME}/.local/share/rustup
ENV CARGO_HOME=${HOME}/.local/share/cargo
ENV GOPATH=${HOME}/.local/share/go

ENV PATH=${NPM_CONFIG_PREFIX}/bin:${PATH}
ENV PATH=${CARGO_HOME}/bin:${PATH}
ENV PATH=${GOPATH}/bin:${PATH}
ENV PATH=${HOME}/.local/bin:${PATH}

RUN rustup default stable && \
  curl -fsSL https://openclaw.ai/install.sh | bash && \
  curl -fsSL https://forgecode.dev/cli | sh

CMD ["/bin/bash"]
