FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:0.3.3 /uv /bin/uv
WORKDIR /app
COPY . .