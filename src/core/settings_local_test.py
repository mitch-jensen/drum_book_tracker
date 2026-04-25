"""Django settings for local test runs without Docker.

This module keeps base settings behavior and only swaps the database backend
for a local SQLite database used by pytest.
"""

import os

# core.settings currently requires these environment variables at import time.
os.environ.setdefault("SECRET_KEY", "local-test-secret-key")
os.environ.setdefault("DATABASE_NAME", "unused-local-test-db")
os.environ.setdefault("DATABASE_USER", "unused-local-test-user")
os.environ.setdefault("DATABASE_PASSWORD", "unused-local-test-password")
os.environ.setdefault("DATABASE_HOST", "unused-local-test-host")


from core.settings import *  # noqa: F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db_test.sqlite3",  # noqa: F405
    },
}
