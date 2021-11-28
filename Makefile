SHELL = /bin/bash

NAME := science
PYMAJOR := 3
PYREV := 9
PYPATCH := 7
PYVERSION := ${PYMAJOR}.${PYREV}.${PYPATCH}
PYENV := ~/.pyenv/versions/${PYVERSION}
VENV_NAME := ${NAME}-${PYVERSION}
VENV := ${PYENV}/envs/${VENV_NAME}
EGGLINK := ${VENV}/lib/python${PYMAJOR}.${PYREV}/site-packages/${NAME}.egg-link
BREW_SSL := /usr/local/opt/openssl@1.1
BREW_READLINE := /usr/local/opt/readline
export LDFLAGS = -L${BREW_SSL}/lib -L${BREW_READLINE}/lib
export CFLAGS = -I${BREW_SSL}/include -I${BREW_READLINE}/include
export CPPFLAGS = -I${BREW_SSL}/include -I${BREW_READLINE}/include
# delberately smash this so we keep arm64-homebrew out of our field of view
export PATH = ${VENV}/bin:/usr/local/bin:/usr/local/sbin:/usr/bin:/bin:/usr/sbin:/sbin

${BREW_READLINE}:
	arch -x86_64 /usr/local/bin/brew install readline

${BREW_SSL}:
	arch -x86_64 /usr/local/bin/brew install openssl@1.1

${PYENV}: ${BREW_SSL} ${BREW_READLINE}
	arch -x86_64 /usr/local/bin/pyenv install ${PYVERSION}

${VENV}: ${PYENV}
	arch -x86_64 /usr/local/bin/pyenv virtualenv ${PYVERSION} ${VENV_NAME}
	${VENV}/bin/python -m pip install -U pip setuptools wheel
	${VENV}/bin/python -m pip install -U poetry

.python-version: ${VENV}
	echo ${VENV_NAME} >.python-version

${EGGLINK}: poetry.lock
	PYENV_VERSION=${NAME} VIRTUAL_ENV=${VENV} ${VENV}/bin/poetry install -E functions -E labs -E kvasir -E test
	# an update-install might not necessarily update this
	touch ${EGGLINK}

setup: .python-version ${EGGLINK}
	git submodule update --init

clean:
	git clean -fdx -e '*.ipynb'

nuke:
	git clean -fdx -e '*.ipynb'
	rm -f .python-version
	/usr/local/bin/pyenv uninstall -f ${PYVERSION}

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
