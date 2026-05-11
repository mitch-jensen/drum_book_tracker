sync:
    uv sync --all-groups --locked

typecheck format="json": sync
    uv run pyrefly check --output-format {{ format }}

format-python files="src/": sync
    uv run ruff format {{ files }}

format-html-templates files="src/": sync
    uv run djlint --reformat {{ files }}

format: format-python format-html-templates

lint-python files="src/" format="json": sync
    uv run ruff check {{ files }} --output-format {{ format }}

lint-html-templates files="src/": sync
    uv run djlint --lint {{ files }}

lint: lint-python lint-html-templates

test files="src/tests": sync
    uv run pytest {{ files }}

migrate: sync
    uv run python src/manage.py migrate

makemigrations: sync
    uv run python src/manage.py makemigrations

compose := "docker compose -f compose.yml"

# --- DEV ---
dev-build:
    {{compose}} -f compose.dev.yml build

dev-up: dev-build
    {{compose}} -f compose.dev.yml up -d

dev-down:
    {{compose}} -f compose.dev.yml down

dev-exec-backend cmd="bash":
    {{compose}} -f compose.dev.yml exec backend {{ cmd }}

dev-migrate:
    {{compose}} -f compose.dev.yml exec backend python manage.py migrate

# --- TEST ---
test-build:
    {{compose}} -f compose.test.yml build

test-up: test-build
    {{compose}} -f compose.test.yml up -d

test-down:
    {{compose}} -f compose.test.yml down

test-exec-backend cmd="bash":
    {{compose}} -f compose.test.yml exec backend {{ cmd }}

test-migrate:
    {{compose}} -f compose.test.yml exec backend python manage.py migrate

test-logs:
    {{compose}} -f compose.test.yml logs -f

test-e2e:
    {{compose}} -f compose.test.yml exec playwright npx playwright test

test-ps:
    {{compose}} -f compose.test.yml ps

# --- PROD ---
prod-build:
    {{compose}} -f compose.prod.yml build

prod-up: prod-build
    {{compose}} -f compose.prod.yml up -d

prod-down:
    {{compose}} -f compose.prod.yml down
