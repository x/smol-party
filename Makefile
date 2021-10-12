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
lint-isort:
	poetry run isort --check .

lint-black:
	poetry run black --check .

lint-requirements:
	poetry export -f requirements.txt --without-hashes | diff requirements.txt -

lint: lint-isort lint-black lint-requirements


# Build
requirements:
	poetry export -f requirements.txt --without-hashes -o requirements.txt

app-deploy:
	gcloud app deploy --project=fluted-current-229319

deploy: lint-requirements collectstatic app-deploy
