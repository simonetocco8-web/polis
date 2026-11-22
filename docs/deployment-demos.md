# Installazione di Demos v0.3.0 su cPanel

Usare PHP 8.4 aggiornato (minimo 8.4.1), estensioni Laravel, Apache con riscrittura URL e HTTPS. Entrambi i pacchetti includono la nuova directory `public/build`. Il completo include `vendor/` e un `.env.example` senza segreti. Il portale legge soltanto aggregati convalidati e non richiede Python, Node.js, database, Redis, worker o servizi AI.

## Aggiornamento da Methodos via SSH

1. Verificare di partire da Methodos v0.2.0. Salvare una copia del progetto, degli asset e del file `.env`.
2. Scaricare lo ZIP di aggiornamento e il checksum nella stessa directory, fuori dalla document root. Eseguire `sha256sum -c polis-ai-v0.3.0-cpanel-update.zip.sha256`.
3. Entrare nella directory dell’installazione, quella con `artisan`, poi eseguire:

   ```sh
   unzip -o /percorso/polis-ai-v0.3.0-cpanel-update.zip
   php artisan optimize:clear
   php artisan documents:validate
   php artisan research:validate
   php artisan demos:validate
   php artisan optimize
   ```

4. Verificare l’Atlante, la demografia e i download CSV/JSON. La validazione documentale deve indicare tre versioni. Il comando Demos deve riportare l’hash dello snapshot iniziale. Conservare `.env`, `APP_KEY`, `vendor/` e la document root `public/`. In caso di problemi ripristinare il backup e rigenerare le cache.

## Aggiornamento Git e SSH

Dopo backup e conferma di un working tree pulito basato su Methodos:

```sh
git fetch origin tag v0.3.0
git merge --ff-only 'v0.3.0^{commit}'
unzip -o /percorso/polis-ai-v0.3.0-cpanel-update.zip 'public/build/*'
php artisan optimize:clear
php artisan documents:validate
php artisan research:validate
php artisan demos:validate
php artisan optimize
```

Se Git rifiuta il fast-forward, preservare le modifiche locali e preparare un checkout separato. I lockfile PHP e Node sono invariati. Per una nuova installazione usare lo ZIP completo e seguire la [guida cPanel](deployment-cpanel.md), saltando la compilazione e l’installazione delle dipendenze già incluse.

## Simulatore in ambiente separato

[Guida del simulatore](../simulation/README.md). Usare Python 3.12.14 con NumPy 2.3.5 o l’immagine Docker. Generare ed esportare gli aggregati sul computer scientifico. Versionare solo `content/statistics/demos.json` nel portale e convalidarlo con `php artisan demos:validate`. Non copiare eventi, archivi di cittadini o seed riservati sull’hosting.
