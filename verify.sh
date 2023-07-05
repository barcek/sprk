#!/usr/bin/sh

introduce() {
  echo "[$0] Running $1..."
}

introduce "static type check (via Mypy external library)"
mypy --python-version=3.8 sprk verify.py

introduce "docstring interactive examples (via standard library doctest module)"
./sprk SPRK_TEST_DOCS
