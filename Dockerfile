FROM python:3.14-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:0.3.3 /uv /bin/uv