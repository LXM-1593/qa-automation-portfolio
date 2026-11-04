#!/usr/bin/env bash
# Run the UI regression suite on macOS / Linux (and Git Bash on Windows).
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"

export NO_PROXY="${NO_PROXY:-} ,localhost,127.0.0.1,::1"
export no_proxy="$NO_PROXY"

if [[ -x "$root/.venv/Scripts/python.exe" ]]; then
  python_bin="$root/.venv/Scripts/python.exe"   # Windows venv layout
elif [[ -x "$root/.venv/bin/python" ]]; then
  python_bin="$root/.venv/bin/python"
else
  echo "Virtual environment not found. Run: python -m venv .venv && pip install -r requirements.txt" >&2
  exit 1
fi

exec "$python_bin" -m pytest "$@"
