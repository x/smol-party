#!/usr/bin/env python3
"""
Formatting, linting, and typing rule this repo.

This script will run all of the linting tools and format checks on the repo in
parallel (but won't format the code if the format doesn't match). When one exits
with a non-zero exit code, all others will complete, but this script will exit
with a non-zero exit code.

# Flake8
An extendable and configurable code-linter for Python.
See https://flake8.pycqa.org/ for more information.
Use .flake8 to configure.

# Mypy
A type checker for Python.
See http://mypy-lang.org/ for more information.
Use pyproject.toml to configure.

# Black
A code formatter for Python.
See https://black.readthedocs.io/ for more information.
Use pyproject.toml to configure.

# iSort
A Python code formatter that just sorts imports.
See https://pycqa.github.io/isort/ for more information.
Use pyproject.toml to configure.

If `--format_github` is passed, all errors will be formatted to create github
annotations if run in a github action. The way it does this is by leveraging
github action's workflow commands API.

See:
    https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions
"""

import argparse
import asyncio
import os
import sys
from asyncio.subprocess import PIPE
from contextlib import contextmanager
from itertools import chain
from typing import Iterable, List, Optional, Tuple

PARSER = argparse.ArgumentParser(description="Runs all linters and format checks together at once.")
PARSER.add_argument("--format_github", action="store_true", help="Format for github annotations.")
PARSER.add_argument("--flake8_target", help="The target to run flake8 on.", default=".")
PARSER.add_argument("--mypy_target", help="The target to run mypy on.", default=".")
PARSER.add_argument("--black_target", help="The target to run black format check on.", default=".")
PARSER.add_argument("--isort_target", help="The target to run isort format check on.", default=".")

BLACK = "\033[30m"
RED = "\033[31m"
GREEN = "\033[32m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"
"""ANSI Ecape codes for coloring the terminal.

See:
    https://en.wikipedia.org/wiki/ANSI_escape_code
"""

FLAKE_GH_FORMAT = "::error file=%(path)s,line=%(row)d,col=%(col)d::[Flake8] %(code)s %(text)s"
"""Flake8 lets us directy format the error output. Instead of manually parsing
the errors like the other linters, we define that format here.

See:
    https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions#setting-an-error-message
"""


async def run_flake(target: str, format_github: bool) -> Tuple[List[str], List[str], int]:
    """Run flake8 on the target.

    Args:
        target: The target to run flake8 on.
        format_github: Whether to format for github annotations.

    Returns:
        STDOUT, STDERR, return code
    """
    format_arg = f"--format='{FLAKE_GH_FORMAT}'" if format_github else "--format=pylint"
    cmd = f"poetry run flake8 {format_arg} {target}"
    proc = await asyncio.create_subprocess_shell(cmd, stdout=PIPE, stderr=PIPE)
    stdout, stderr = await proc.communicate()
    returncode = proc.returncode or 0
    return stdout.decode("utf-8").splitlines(), stderr.decode("utf-8").splitlines(), returncode


async def run_mypy(target: str, format_github: bool) -> Tuple[List[str], List[str], int]:
    """Run mypy on the target.

    Args:
        target: The target to run mypy on.
        format_github: Whether to format for github annotations.

    Returns:
        STDOUT, STDERR, return code
    """
    format_arg = "" if format_github else "--pretty"
    cmd = (
        "mypy --ignore-missing-imports --warn-unused-ignores --namespace-packages "
        f"--show-column-numbers --config-file=pyproject.toml {format_arg} {target}"
    )
    proc = await asyncio.create_subprocess_shell(cmd, stdout=PIPE, stderr=PIPE)
    stdout, stderr = await proc.communicate()
    returncode = proc.returncode or 0
    return stdout.decode("utf-8").splitlines(), stderr.decode("utf-8").splitlines(), returncode


async def run_black_check(target: str) -> Tuple[List[str], List[str], int]:
    """Run black format check on the target.

    Args:
        target: The target to run black format check on.

    Returns:
        STDOUT, STDERR, return code
    """
    cmd = f"poetry run black --check {target}"
    proc = await asyncio.create_subprocess_shell(cmd, stdout=PIPE, stderr=PIPE)
    stdout, stderr = await proc.communicate()
    returncode = proc.returncode or 0
    return stdout.decode("utf-8").splitlines(), stderr.decode("utf-8").splitlines(), returncode


async def run_isort_check(target: str) -> Tuple[List[str], List[str], int]:
    """Run isort format check on the target.

    Args:
        target: The target to run isort format check on.

    Returns:
        STDOUT, STDERR, return code
    """
    cmd = f"poetry run isort --check {target}"
    proc = await asyncio.create_subprocess_shell(cmd, stdout=PIPE, stderr=PIPE)
    stdout, stderr = await proc.communicate()
    returncode = proc.returncode or 0
    return stdout.decode("utf-8").splitlines(), stderr.decode("utf-8").splitlines(), returncode


def gh_format_black_stderr(black_stderr: List[str]) -> Iterable[str]:
    """Format the black stderr output for github annotations.

    See:
        https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions#setting-an-error-message
    """
    for line in black_stderr:
        if "would reformat" in line:
            _, _, filename = line.split(" ")
            yield f"::error file={filename}::[Black] Would reformat {filename}"


def gh_format_isort_stderr(isort_stderr: List[str]) -> Iterable[str]:
    """Format the isort stderr output for github annotations.

    See:
        https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions#setting-an-error-message
    """
    for line in isort_stderr:
        if "ERROR" in line:
            _, filename, msg = line.split(" ", 2)
            yield f"::error file={filename}::[iSort] {msg.strip()}"


def gh_format_mypy_stdout(mypy_stdout: List[str]) -> Iterable[str]:
    """Format the mypy stdout output for github annotations.

    See:
        https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions#setting-an-error-message
    """
    for line in mypy_stdout:
        if " error:" in line:
            err_details, msg = line.split(" error:")
            filename, line, col, *_ = err_details.split(":") + ["", ""]
            yield f"::error file={filename},line={line},col={col}::[MyPy] {msg.strip()}"


def print_hr(
    title: Optional[str] = None,
    rule_char: str = "=",
    color: Optional[str] = None,
    bold: bool = True,
) -> None:
    """Print a horizontal rule along with an optional title."""
    try:
        cols, _ = os.get_terminal_size()
    except OSError:
        cols = 80
    if title:
        llen = (cols - len(title) - 2) // 2
        rlen = cols - llen - len(title) - 2
        out = f"{rule_char * llen} {title} {rule_char * rlen}"
    else:
        out = rule_char * cols
    if bold:
        out = f"{BOLD}{out}"
    if color:
        out = f"{color}{out}"
    print(f"{RESET}{out}{RESET}")


@contextmanager
def linter_decoration(title: str, returncode: int, with_group_annotations=False):
    """decorates the before and after of the linters output when used as a contextmanager.

    Args:
        title: Title of the linter.
        returncode: The returncode of the linter's process denoting success or failure.
        with_group_annotations: If true, will use the grouping workflow commands.
    """
    print_hr(f"Running {title}", "-", bold=True)
    if with_group_annotations:
        print(f"::group::{title}")
    yield
    if with_group_annotations:
        print("::endgroup::")
    if returncode == 0:
        print(f"{GREEN}✅ {title} Succeeded{RESET}")
    else:
        print(f"{RED}❌ {title} Failed{RESET}")
    print("")


async def _main():
    args = PARSER.parse_args()

    black_out, black_err, black_returncode = await run_black_check(args.black_target)
    isort_out, isort_err, isort_returncode = await run_isort_check(args.isort_target)
    flake_out, flake_err, flake_returncode = await run_flake(args.flake8_target, args.format_github)
    mypy_out, mypy_err, mypy_returncode = await run_mypy(args.mypy_target, args.format_github)

    with linter_decoration("Black Format Check", black_returncode, args.format_github):
        errs = gh_format_black_stderr(black_err) if args.format_github else black_err
        for line in chain(errs, black_out):
            print(line)

    with linter_decoration("iSort Imports Check", isort_returncode, args.format_github):
        errs = gh_format_isort_stderr(isort_err) if args.format_github else isort_err
        for line in chain(errs, isort_out):
            print(line)

    with linter_decoration("Flake8 Code Linter", flake_returncode, args.format_github):
        for line in chain(flake_err, flake_out):
            print(line)

    with linter_decoration("MyPy Type Linter", mypy_returncode, args.format_github):
        errs = gh_format_mypy_stdout(mypy_out) if args.format_github else mypy_out
        for line in chain(errs, mypy_err):
            print(line)

    if any([black_returncode, isort_returncode, flake_returncode, mypy_returncode]):
        print_hr("Linting Failed", "=", RED, bold=True)
        sys.exit(1)
    else:
        print_hr("Linting Passed", "=", GREEN, bold=True)
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(_main())
