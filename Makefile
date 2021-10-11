setup-poetry:
	pip install poetry && poetry install

migrate:
	python manage.py migrate

setup: setup-poetry migrate

up:
	python manage.py runserver

format:
	poetry run isort . && poetry run black .

