#!/usr/bin/env bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
output=$(realpath -m "${1:?Indicare la directory di destinazione}")
name=polis-ai-v0.2.0-cpanel-update.zip
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
mkdir -p "$work/stage" "$output"
git diff --quiet HEAD
git diff --quiet v0.1.1 HEAD -- composer.json composer.lock
scope=(app bootstrap config content lang public resources/views routes)
test -z "$(git diff --name-only --diff-filter=D v0.1.1 HEAD -- "${scope[@]}")"
mapfile -t files < <(git diff --name-only --diff-filter=AM v0.1.1 HEAD -- "${scope[@]}")
test "${#files[@]}" -gt 0
git archive HEAD "${files[@]}" docs/deployment-methodos.md | tar -x -C "$work/stage"
test -f public/build/manifest.json
mkdir -p "$work/stage/public"
cp -a public/build "$work/stage/public/build"
git rev-parse HEAD > "$work/stage/REVISIONE.txt"
(cd "$work/stage" && zip -q -r "$work/$name" .)
unzip -tq "$work/$name"
mv "$work/$name" "$output/$name"
(cd "$output" && sha256sum "$name" > "$name.sha256")
