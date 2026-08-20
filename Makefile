install:
	uv pip install --system -r pyproject.toml

build:
	./build.sh

migrate:
	python3 manage.py migrate

collectstatic:
	python3 manage.py collectstatic --noinput

render-start:
	gunicorn task_manager.wsgi

# --- local development helpers (run against the local uv virtualenv) ---

dev:
	uv run python manage.py runserver

shell:
	uv run python manage.py shell

lint:
	uv run flake8

.PHONY: install build migrate collectstatic render-start dev shell lint
