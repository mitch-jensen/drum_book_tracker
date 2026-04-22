# Drum Book Tracker

Drum Book Tracker is a Django app for organizing drum method books, breaking them into sections and exercises, and recording practice history over time. It is built for a workflow where you want to track what you practiced, at what tempo, and how each exercise is progressing.

The project uses Django with HTMX for interactive CRUD screens, PostgreSQL for persistence, and Docker Compose for local development and production-style runs.

## Features

- Track authors, books, sections, tags, exercises, and practice logs.
- Browse exercises by book and section, with tag-based filtering.
- Bulk-create numbered exercises for a section with validated page-range mapping.
- Upload notation images for individual exercises.
- View exercise practice stats including tempo history, averages, difficulty, relaxation, and recent sessions.
- Run the app in development or production-oriented Docker configurations.

## Tech Stack

- Python 3.14
- Django 6
- HTMX via `django-htmx`
- PostgreSQL 18
- Bootstrap 5 with `crispy-forms`
- `uv` for dependency management
- `pytest` for tests
- `ruff` for linting

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Or, for a non-container workflow: Python 3.14, `uv`, and PostgreSQL

### Environment Variables

The app expects these environment variables:

- `SECRET_KEY`
- `DATABASE_NAME`
- `DATABASE_USER`
- `DATABASE_PASSWORD`

Docker Compose reads these from the root `.env` file.

## Run With Docker

Development uses the Compose override file automatically and starts the Django dev server with file sync and a debug port.

```bash
docker compose up --build
```

Once the containers are up:

```bash
docker compose exec backend python manage.py migrate
```

The app is then available at `http://127.0.0.1:8000`.

Useful commands:

```bash
docker compose down
docker compose exec backend python manage.py createsuperuser
docker compose exec backend python manage.py loaddata book_tracker/fixtures/data.json
```

## Run Locally Without Docker

Install dependencies and sync the environment:

```bash
uv sync --all-groups
```

Export the required environment variables, make sure PostgreSQL is running, then apply migrations and start the dev server:

```bash
cd src
python manage.py migrate
python manage.py runserver
```

## Tests And Checks

Run the test suite:

```bash
uv run pytest
```

Run linting:

```bash
uv run ruff check .
```

Apply Ruff autofixes:

```bash
uv run ruff check . --fix
```

## Project Layout

```text
.
├── compose.yml               # Base services: Django app + PostgreSQL
├── compose.override.yml      # Development ports, watch mode, debugpy
├── compose.prod.yml          # Production-oriented Caddy + static files setup
├── Dockerfile                # Multi-stage development and production images
├── pyproject.toml            # Dependencies and tool configuration
├── src/
│   ├── manage.py
│   ├── book_tracker/         # Models, forms, views, templates, migrations
│   ├── core/                 # Django settings, ASGI app, root URLs
│   └── tests/                # Pytest suite
└── caddy/                    # Reverse proxy config for production compose
```

## Main Workflows

- `/authors/`: manage book authors
- `/books/`: manage books and associated authors
- `/sections/`: organize books into ordered sections
- `/exercises/`: create, edit, filter, and bulk-create exercises
- `/logs/`: record practice sessions with tempo, notes, difficulty, and relaxation

Exercise detail pages include notation uploads and aggregated practice statistics.

> [!NOTE]
> Media uploads are stored under `src/media/` locally and in the `media_data` Docker volume when running in containers.

## Current Status

This repository already includes model, relation, view, bulk-create, filter, and notation tests under `src/tests/`, which makes it a good base for iterating on the tracking workflow without starting from scratch.
