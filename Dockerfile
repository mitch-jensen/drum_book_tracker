FROM python:3.14-alpine AS requirements

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /requirements
RUN --mount=type=bind,source=pyproject.toml,target=/requirements/pyproject.toml \
    --mount=type=bind,source=uv.lock,target=/requirements/uv.lock \
    uv export --no-dev --format requirements.txt > requirements.txt

FROM python:3.14-alpine AS production

WORKDIR /app
RUN --mount=type=bind,from=requirements,source=/requirements/requirements.txt,target=/app/requirements.txt \
    --mount=type=cache,target=/root/.cache/pip \
    pip install -r /app/requirements.txt

COPY ./src /app/src
WORKDIR /app/src

CMD ["sh", "-c", "python manage.py collectstatic --noinput && exec python -m uvicorn core.asgi:application --host 0.0.0.0 --port 8000"]

FROM python:3.14-alpine AS development
# Use the system Python environment
ENV UV_PROJECT_ENVIRONMENT="/usr/local/" \
    UV_LINK_MODE=copy

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

RUN --mount=type=bind,source=pyproject.toml,target=/app/pyproject.toml \
    --mount=type=cache,target=/root/.cache/uv \
    uv sync --all-groups

COPY ./src /app/src
WORKDIR /app/src

CMD [ "python", "-m", "debugpy", "--listen", "0.0.0.0:5678", "manage.py", "runserver", "0.0.0.0:8000" ]
