#!/usr/bin/env bash
# Cierre mensual reproducible. La logica y la lectura CSV se implementan en Python.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 scripts/cierre.py
