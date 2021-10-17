# Environment
setup-poetry:
	pip install poetry && poetry install

setup: setup-poetry migrate


# Django
makemigrate:
	poetry run python manage.py makemigrations && poetry run python manage.py makemigrations events

migrate:
	poetry run python manage.py migrate

collectstatic:
	poetry run python manage.py collectstatic

runserver:
	poetry run python manage.py runserver

up: runserver


# Formatting
format-black:
	poetry run black .

format-isort:
	poetry run isort .

format: format-isort format-black


# Linting
isort-check:
	poetry run isort --check .

black-check:
	poetry run black --check .

flake8:
	poetry run flake8 .

verify-requirements:
	poetry export -f requirements.txt --without-hashes | diff requirements.txt -

lint: flake8 black-check isort-check verify-requirements


# Build
requirements:
	poetry export -f requirements.txt --without-hashes -o requirements.txt

app-deploy:
	gcloud app deploy --project=fluted-current-229319

deploy: lint-requirements collectstatic app-deploy
