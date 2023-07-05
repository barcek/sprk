#!/usr/bin/python3

from pathlib import Path
from importlib import machinery

from mypy import api
from doctest import testmod

sprk = machinery.SourceFileLoader('sprk', './sprk').load_module()

# utility functions

def log(message: str) -> None:
  print(f'[{__file__}] {message}')

def introduce(task: str) -> None:
  log(f'Running {task}...')

# verification

introduce('static type check (via Mypy external library)')
print(api.run(['--python-version=3.8', 'sprk', 'verify.py'])[0], end='')

introduce('docstring interactive examples (via standard library doctest module)')
testmod(sprk, extraglobs=sprk.get_doctest_extraglobs(PATH_TO_SELF=Path('sprk').resolve()))
