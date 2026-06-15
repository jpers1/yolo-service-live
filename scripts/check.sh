#!/usr/bin/env bash
set -euo pipefail

python -m pytest
ruff check app tests
git diff --check
