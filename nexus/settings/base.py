"""
Shared settings. No secret defaults here — every environment-specific
value is read from the environment and fails loud if unset. `dev.py`
supplies developer-friendly defaults on top of this file.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def _env(name: str) -> str:
    try:
        return os.environ[name]
    except KeyError as exc:
        raise RuntimeError(f"Required environment variable {name!r} is not set.") from exc


SECRET_KEY = _env("DJANGO_SECRET_KEY")
DEBUG = os.environ.get("DJANGO_DEBUG", "false").lower() == "true"
ALLOWED_HOSTS = [h for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",") if h]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "apps.registry",
    "apps.documents",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "nexus.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "nexus.wsgi.application"
ASGI_APPLICATION = "nexus.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": _env("POSTGRES_DB"),
        "USER": _env("POSTGRES_USER"),
        "PASSWORD": _env("POSTGRES_PASSWORD"),
        "HOST": _env("POSTGRES_HOST"),
        "PORT": _env("POSTGRES_PORT"),
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Every registry model declares an explicit UUID primary key; this is a
# fallback for any future model that doesn't.

# Timestamps are timezone-aware UTC in the database (CLAUDE.md). PH
# working-day arithmetic (M3, tracking/calendar.py) converts explicitly —
# it does not rely on this setting.
USE_TZ = True
TIME_ZONE = "UTC"

LANGUAGE_CODE = "en-us"
USE_I18N = True

STATIC_URL = "static/"

# Files: django-storages, filesystem backend locally, S3-compatible in
# prod (CLAUDE.md). Django's own FileSystemStorage covers "filesystem
# locally" — django-storages itself only adds non-default backends
# (S3Boto3Storage, etc.), which nothing exercises yet, so it isn't a
# dependency until a prod backend is actually wired up. Swapping later
# is a one-line BACKEND change here plus one branch inside
# documents.services._presign().
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}
MEDIA_ROOT = BASE_DIR / "media"

# First real use of the DomainError -> HTTP status pattern CLAUDE.md
# documents (apps/documents/services.py raises DomainError subclasses;
# registry's own DomainError, in import_piles/upsert.py, never reaches
# HTTP so it never needed this).
REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "nexus.exceptions.handle_domain_error",
}
