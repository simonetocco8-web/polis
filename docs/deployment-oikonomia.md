# Installare Oikonomia su cPanel

PHP 8.4 aggiornato (minimo 8.4.1), estensioni Laravel, Apache con riscrittura URL e HTTPS. Il portale legge soltanto aggregati. Python, Node.js, database e servizi permanenti non sono necessari sull’hosting.

## Aggiornamento da Demos v0.3.0 via SSH

Salvare un backup del progetto, degli asset e di `.env`. Scaricare i file della release nella stessa directory e verificare:

```sh
sha256sum -c polis-ai-v0.4.0-cpanel-update.zip.sha256
```

Entrare nella radice dell’installazione, dove si trova `artisan`, e conservare document root `public/`, `.env`, `APP_KEY` e `vendor/`:

```sh
unzip -o /percorso/polis-ai-v0.4.0-cpanel-update.zip
php artisan optimize:clear
php artisan documents:validate
php artisan research:validate
php artisan demos:validate
php artisan oikonomia:validate
php artisan optimize
```

Verificare `/nova/economia`, `/nova/economia/pil`, i download e gli asset. La validazione Oikonomia deve indicare 600 mesi. In caso di problema, ripristinare il backup e rigenerare le cache.

## Git e SSH

Sul checkout Demos pulito, dopo il backup, usare `git fetch origin tag v0.4.0` e `git merge --ff-only 'v0.4.0^{commit}'`. Estrarre dall’archivio di aggiornamento solo gli asset con `unzip -o /percorso/polis-ai-v0.4.0-cpanel-update.zip 'public/build/*'`. Eseguire i comandi Artisan sopra. Se il fast-forward fallisce, preservare le modifiche dell’hosting e predisporre un checkout separato. Non rigenerare la chiave per un aggiornamento.

## Nuova installazione

Il pacchetto completo contiene già `vendor/` e `public/build`. Configurare l’hosting secondo la [guida cPanel](deployment-cpanel.md). Il simulatore ha proprie [istruzioni di riproduzione](architecture/oikonomia.md) e gira separatamente.
