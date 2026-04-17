FROM python:3.14-alpine AS requirements

COPY --from=ghcr.io/astral-sh/uv:0.5.21 /uv /uvx /bin/
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
