# Environment
setup-poetry:
	pip install poetry && poetry install

setup: setup-poetry migrate


# Django
migrate:
	python manage.py migrate

up:
	python manage.py runserver


# Formatting
format-black:
	poetry run black .

format-isort:
	poetry run isort .

format: format-isort format-black


# Linting
lint-isort:
	poetry run isort --check .

lint-black:
	poetry run black --check .

lint-requirements:
	poetry export -f requirements.txt | diff requirements.txt -

lint: lint-isort lint-black lint-requirements


# Build
requirements:
	poetry export -f requirements.txt -o requirements.txt
