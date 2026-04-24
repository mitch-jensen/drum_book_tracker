FROM python:3.14-alpine AS requirements

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /requirements
# hadolint ignore=SC2094
RUN --mount=type=bind,source=pyproject.toml,target=/requirements/pyproject.toml \
    --mount=type=bind,source=uv.lock,target=/requirements/uv.lock \
    uv export --no-dev --format requirements.txt > requirements.txt

FROM python:3.14-alpine AS base

# -S = system user/group, -G = assign group, -H = no home directory
RUN addgroup -S app && adduser -S -G app -H app
WORKDIR /app

FROM base AS production

RUN --mount=type=bind,from=requirements,source=/requirements/requirements.txt,target=/app/requirements.txt \
    --mount=type=cache,target=/root/.cache/pip \
    pip install -r /app/requirements.txt

COPY --chown=app:app --exclude=tests --exclude=tests/** ./src /app/src
WORKDIR /app/src

USER app
CMD ["sh", "-c", "python manage.py collectstatic --noinput && exec python -m uvicorn core.asgi:application --host 0.0.0.0 --port 8000"]

FROM base AS development
# Use the system Python environment
ENV UV_PROJECT_ENVIRONMENT="/usr/local/" \
    UV_LINK_MODE=copy

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN --mount=type=bind,source=uv.lock,target=/app/uv.lock \
    --mount=type=bind,source=pyproject.toml,target=/app/pyproject.toml \
    --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

COPY --chown=app:app --exclude=tests --exclude=tests/** ./src /app/src
WORKDIR /app/src

USER app
CMD [ "python", "-m", "debugpy", "--listen", "0.0.0.0:5678", "manage.py", "runserver", "0.0.0.0:8000" ]

FROM python:3.14-bookworm AS test

ENV UV_PROJECT_ENVIRONMENT="/usr/local/" \
    UV_LINK_MODE=copy

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

RUN --mount=type=bind,source=uv.lock,target=/app/uv.lock \
    --mount=type=bind,source=pyproject.toml,target=/app/pyproject.toml \
    --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --group test && \
    playwright install --with-deps

COPY ./src /app/src
COPY pyproject.toml /app/pyproject.toml
WORKDIR /app/src

ENTRYPOINT ["/bin/bash"]
