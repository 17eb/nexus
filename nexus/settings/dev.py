"""
Local development defaults on top of base.py. Never used in production —
`DJANGO_SECRET_KEY` still has no default, since a throwaway dev key
should still be explicit in `.env`, not baked into source.
"""

import os

os.environ.setdefault("DJANGO_DEBUG", "true")
os.environ.setdefault("POSTGRES_DB", "nexus_dev")
os.environ.setdefault("POSTGRES_USER", "nexus")
os.environ.setdefault("POSTGRES_PASSWORD", "nexus")
os.environ.setdefault("POSTGRES_HOST", "localhost")
os.environ.setdefault("POSTGRES_PORT", "5432")
os.environ.setdefault("DJANGO_SECRET_KEY", "dev-only-not-for-production")

from .base import *  # noqa: E402,F401,F403
