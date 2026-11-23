#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

PYTHON="${PYTHON:-python3}"

if ! "$PYTHON" -c 'import customtkinter' >/dev/null 2>&1; then
    echo "Installation des dependances..."
    "$PYTHON" -m pip install -r requirements.txt
fi

exec "$PYTHON" main.py "$@"
