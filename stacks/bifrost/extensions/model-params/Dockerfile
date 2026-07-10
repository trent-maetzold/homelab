FROM astral/uv:python3.13-trixie AS builder

ENV UV_SYSTEM_PYTHON=1 \
  UV_COMPILE_BYTECODE=1 \
  UV_LINK_MODE=copy \
  UV_NO_EDITABLE=1 \
  UV_PROJECT_ENVIRONMENT=/opt/venv

WORKDIR /app
COPY pyproject.toml uv.lock ./
COPY src/ ./src/

RUN --mount=type=cache,target=/root/.cache/uv \
  uv sync --no-dev --frozen

FROM python:3.13-slim-trixie AS runtime

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"

EXPOSE 8000

ENTRYPOINT ["granian", "--interface", "asgi"]
CMD ["modelparams.main:app", "--host", "0.0.0.0", "--port", "8000"]
