# Smol.Party

A simple event planner alternative to FB Events that doesn't require logins.

[https://smol.party]("https://smol.party")


## How to dev

By default, if you don't set a `GOOGLE_CLOUD_PROJECT`, then `settings.py` will
assume you're doing local development and connect to a `db.sqlite3` file.

1. `make setup`
2. `make up`


## Code Linting and Formatting

This repo uses the following:

* `flake8` - An extendable python code linter.
* `mypy` - A python type checker.
* `black` - A python code formatter.
* `isort` - A python import sorter and formatter.

The makefile provides two helpful commands:

* `make format` - Reformats the code using `black` and `isort`.
* `make lint` - Lints the code with `flake8` and `mypy` and ensure the format matches what `black` and `isort` would format it to.


## Contributing

Contributing is easy.

1. Use the above to setup a local dev environment and open a PR.
2. Make your change(s).
3. Use the above to ensure your code is formatted and passes the linters.
4. Open a pull request.
5. A github action will run the linters.
6. Once approved and merged into `main`, a github action will handle the deploy.
