.PHONY: check test dev fixtures

check:
	.venv/bin/ruff check apps nexus manage.py
	.venv/bin/mypy apps nexus
	.venv/bin/lint-imports
	.venv/bin/pytest

test:
	.venv/bin/pytest

dev:
	@trap 'kill 0' EXIT; \
	.venv/bin/python manage.py runserver & \
	(cd frontend && npm run dev) & \
	wait

fixtures:
	.venv/bin/python manage.py migrate
	.venv/bin/python manage.py generate_fixture_piles
