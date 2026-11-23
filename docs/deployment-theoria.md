# Theoria v0.7.0 su cPanel

Usare PHP 8.4.1 o successivo della serie 8.4, Apache con riscrittura degli URL e document root public/. Le directory storage/ e bootstrap/cache/ devono essere scrivibili da PHP. Il portale legge gli export statici. Python, Node.js, database e credenziali OpenAI non sono richiesti. Per le estensioni PHP e HTTPS consultare la [guida cPanel](deployment-cpanel.md).

## Aggiornamento da Archon v0.6.0 via SSH

Conservare un backup privato dell'applicazione. Scaricare lo ZIP di aggiornamento e il file SHA-256. Dalla directory di download, verificarli:

```sh
sha256sum -c polis-ai-v0.7.0-cpanel-update.zip.sha256
unzip -t polis-ai-v0.7.0-cpanel-update.zip
```

Dalla directory dell'applicazione:

```sh
php artisan optimize:clear
unzip -o /percorso/download/polis-ai-v0.7.0-cpanel-update.zip -d "$PWD"
php artisan documents:validate
php artisan archon:validate
php artisan theoria:validate
php artisan optimize
```

Verificare /nova/osservatorio, le pagine Archon e gli export. Conservare .env, APP_KEY, vendor/ e document root. Per rollback ripristinare il backup di Archon e ricreare le cache. Per un'installazione nuova, verificare il checksum dello ZIP completo ed estrarlo in una directory privata. Include vendor/ di produzione e gli asset compilati. Seguire la guida cPanel e verificare con php artisan theoria:validate.
