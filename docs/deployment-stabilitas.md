# Installare Stabilitas v0.4.1 su cPanel

Richiede PHP 8.4 aggiornato (minimo 8.4.1), estensioni Laravel, HTTPS e Apache con riscrittura. Il portale legge soltanto aggregati. Python, Node.js, database e Redis non servono in produzione.

## Aggiornamento da Oikonomia v0.4.0 con SSH

Salvare un backup di codice, dati, asset e `.env`. Verificare il checksum accanto al file scaricato:

```sh
sha256sum -c polis-ai-v0.4.1-cpanel-update.zip.sha256
```

Entrare nella directory dell’installazione con `artisan`, quindi eseguire:

```sh
unzip -o /percorso/polis-ai-v0.4.1-cpanel-update.zip
php artisan optimize:clear
php artisan documents:validate
php artisan research:validate
php artisan demos:validate
php artisan oikonomia:validate
php artisan stabilitas:validate
php artisan optimize
```

Conservare `.env`, `APP_KEY`, `vendor/` e document root `public/`. Verificare `/nova/economia`, `/nova/economia/stabilita` e i download. Stabilitas deve indicare cinque prove standard e trenta corse esplorative. In caso di problemi ripristinare il backup e ricreare le cache.

## Git e SSH

Dopo il backup e la verifica che il checkout Oikonomia sia pulito, eseguire `git fetch origin tag v0.4.1` e `git merge --ff-only 'v0.4.1^{commit}'`. Estrarre dall’archivio di aggiornamento gli asset con `unzip -o /percorso/polis-ai-v0.4.1-cpanel-update.zip 'public/build/*'`. Eseguire gli stessi comandi Artisan. Per una nuova installazione usare lo ZIP completo, con `vendor/` e gli asset presenti. [Guida cPanel](deployment-cpanel.md)
