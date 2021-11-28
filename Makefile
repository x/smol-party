PYVERSION := 3.9.1
VENV_NAME := "smolparty-${PYVERSION}"

# Environment
setup-poetry:
	pip install poetry && poetry install

# Only do this if you use pyenv-virtualenv like a fucking psychopath
setup-pyenv-virtualenv:
	pyenv virtualenv ${PYVERSION} ${VENV_NAME}

setup-.python-version:
	echo ${VENV_NAME} >.python-version

setup: setup-poetry migrate

setup-plus: setup-poetry setup-pyenv-virtualenv setup-.python-version migrate

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

deploy: verify-requirements collectstatic app-deploy
