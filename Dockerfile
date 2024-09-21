FROM python:3.12-slim-bookworm AS development
COPY --from=ghcr.io/astral-sh/uv:0.4.14 /uv /bin/uv
CMD [ "sleep", "infinity" ]