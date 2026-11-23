#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../simulation"
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
python -m archon_lab "$work"
cmp "$work/archon.json" ../content/statistics/archon.json
cmp "$work/archon.sha256" ../content/statistics/archon.sha256
