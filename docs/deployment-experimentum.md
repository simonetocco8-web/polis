# Experimentum v0.8.0 su cPanel

Requisiti: PHP 8.4.1 o successivo della serie 8.4, Apache con riscrittura URL, document root public/ e permessi di scrittura su storage/ e bootstrap/cache/. Il portale non necessita di Python, Node.js, database, worker o credenziali del provider. Consultare la [guida cPanel](deployment-cpanel.md) per estensioni e HTTPS.

## Aggiornamento da Theoria v0.7.0 via SSH

Fare un backup privato. Verificare il checksum e la struttura dello ZIP prima dell'estrazione.

```sh
sha256sum -c polis-ai-v0.8.0-cpanel-update.zip.sha256
unzip -t polis-ai-v0.8.0-cpanel-update.zip
```

Dalla directory dell'applicazione, sostituendo il percorso dell'archivio:

```sh
php artisan optimize:clear
unzip -o /percorso/download/polis-ai-v0.8.0-cpanel-update.zip -d "$PWD"
php artisan documents:validate
php artisan theoria:validate
php artisan experimentum:validate
php artisan optimize
```

Controllare /ricerca/esperimenti, le esportazioni e le pagine Theoria. Conservare .env, APP_KEY, vendor e la document root. Per rollback, ripristinare il backup completo di Theoria e ricreare le cache.

Per una nuova installazione, verificare il checksum dello ZIP completo ed estrarlo fuori dalla document root precedente. Il pacchetto include vendor di produzione e asset Vite compilati. Seguire la guida cPanel e verificare gli export con php artisan experimentum:validate.
