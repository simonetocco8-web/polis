#!/usr/bin/env bash
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"
output=$(realpath -m "${1:?Indicare la directory di destinazione}")
version=${2:-v0.1.0}
[[ "$version" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]
name=polis-ai-${version}-cpanel.zip
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
stage=$work/stage
mkdir -p "$stage" "$output"

git diff --quiet HEAD
git archive HEAD app artisan bootstrap composer.json composer.lock config content lang public resources/views routes storage .env.example docs/licenses docs/deployment-cpanel.md | tar -x -C "$stage"
test -f public/build/manifest.json
cp -a public/build "$stage/public/build"
git rev-parse HEAD > "$stage/REVISIONE.txt"
case "$version" in
    v0.2.0) cp docs/deployment-methodos.md "$stage/docs/" ;;
    v0.3.0) cp docs/deployment-demos.md "$stage/docs/" ;;
    v0.6.0) cp docs/deployment-archon.md "$stage/docs/" ;;
    v0.5.0) cp docs/deployment-nomos.md "$stage/docs/" ;;
    v0.4.1) cp docs/deployment-stabilitas.md "$stage/docs/" ;;
    v0.4.0)
        cp docs/deployment-oikonomia.md "$stage/docs/"
        mkdir -p "$stage/docs/architecture"
        cp docs/architecture/oikonomia.md "$stage/docs/architecture/"
        ;;
esac

cd "$stage"
composer install --no-dev --prefer-dist --no-interaction --optimize-autoloader
composer check-platform-reqs --no-dev
php artisan documents:validate
case "$version" in
    v0.2.0) php artisan research:validate ;;
    v0.3.0) php artisan research:validate; php artisan demos:validate ;;
    v0.4.0) php artisan research:validate; php artisan demos:validate; php artisan oikonomia:validate ;;
    v0.6.0) php artisan research:validate; php artisan demos:validate; php artisan oikonomia:validate; php artisan stabilitas:validate; php artisan nomos:validate; php artisan archon:validate ;;
    v0.5.0) php artisan research:validate; php artisan demos:validate; php artisan oikonomia:validate; php artisan stabilitas:validate; php artisan nomos:validate ;;
    v0.4.1) php artisan research:validate; php artisan demos:validate; php artisan oikonomia:validate; php artisan stabilitas:validate ;;
esac
rm -f bootstrap/cache/*.php
sed -i 's/^APP_ENV=local$/APP_ENV=production/;s/^APP_DEBUG=true$/APP_DEBUG=false/;s#^APP_URL=.*#APP_URL=https://example.invalid#' .env.example
test ! -e .env
test ! -d node_modules
test ! -d vendor/phpunit
grep -qx 'APP_KEY=' .env.example

cat > INSTALLAZIONE.txt <<'INSTRUCTIONS'
POLIS AI · Pacchetto completo

1. Estrarre lo ZIP in una directory dell'account cPanel fuori dalla document root attuale.
2. Impostare la document root del dominio su public/ e attivare HTTPS.
3. Copiare .env.example in .env. Impostare APP_ENV=production, APP_DEBUG=false e APP_URL=https://dominio.
4. Eseguire php artisan key:generate --force dalla directory del progetto.
5. Rendere storage/ e bootstrap/cache/ scrivibili da PHP. Eseguire php artisan documents:validate e php artisan optimize.
6. Verificare homepage, biblioteca, Costituzione, asset e robots.txt prima di consentire l'indicizzazione.

Requisiti: PHP 8.4.1 o successivo della serie 8.4, con ctype, DOM, fileinfo, filter, hash, mbstring, OpenSSL, PCRE, session e tokenizer. Apache deve supportare .htaccess e la riscrittura degli URL.
Vendor e asset compilati sono inclusi. Non occorrono database, Composer, npm o processi Node.js sull'hosting.
INSTRUCTIONS

zip -q -r "$work/$name" .
unzip -tq "$work/$name"
mv "$work/$name" "$output/$name"
cd "$output"
sha256sum "$name" > "$name.sha256"
