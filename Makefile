SHELL = /bin/bash

NAME := smolparty
PYMAJOR := 3
PYREV := 10
PYPATCH := 3
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
	PYENV_VERSION=${NAME} VIRTUAL_ENV=${VENV} ${VENV}/bin/poetry install
	# an update-install might not necessarily update this
	touch ${EGGLINK}


# General repo and env managements
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
format:
	poetry run black .
	poetry run isort .


# Linting
lint:
	poetry run python ./run_linters.py
