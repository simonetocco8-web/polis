# Aggiornare Stabilitas v0.4.1 a Nomos v0.5.0 su cPanel

Usare PHP **8.4.1 o successivo della serie 8.4**, sia nella CLI sia per il dominio, con ctype, DOM, fileinfo, filter, hash, mbstring, OpenSSL, PCRE, session e tokenizer. Apache deve applicare `.htaccess` e la riscrittura degli URL. La document root deve puntare a `public/`. L'account PHP deve poter scrivere in `storage/` e `bootstrap/cache/`. Il portale legge file statici validati e funziona senza database, Redis, Node.js, Python o worker.

## Aggiornamento via SSH

L'archivio di aggiornamento presuppone un'installazione integra di Stabilitas v0.4.1. Conservare un backup della directory dell'applicazione e della configurazione in un percorso privato. Scaricare ZIP e relativo file `.sha256` dalla release GitHub. Eseguire i controlli dalla directory di download.

```sh
sha256sum -c polis-ai-v0.5.0-cpanel-update.zip.sha256
unzip -t polis-ai-v0.5.0-cpanel-update.zip
```

Sostituire il percorso con quello dell'applicazione corrente. Se il binario di default punta a una versione PHP diversa, selezionare quello fornito dal proprio hosting per PHP 8.4.

```sh
cd /percorso/privato/polis-ai
php -v
php artisan optimize:clear
unzip -o /percorso/download/polis-ai-v0.5.0-cpanel-update.zip -d "$PWD"
php artisan documents:validate
php artisan research:validate
php artisan demos:validate
php artisan oikonomia:validate
php artisan stabilitas:validate
php artisan nomos:validate
php artisan optimize
```

Controllare `/nova/istituzioni`, `/nova/istituzioni/trasparenza` e i download JSON, CSV e SHA-256. Verificare la pagina Stabilitas e il caricamento degli asset. L'overlay conserva `.env`, `APP_KEY`, dipendenze PHP installate e document root. In caso di errore, ripristinare il backup e ricreare le cache.

## Installazione nuova

Verificare il checksum di `polis-ai-v0.5.0-cpanel.zip`, estrarlo in una nuova directory privata e seguire [la guida cPanel](deployment-cpanel.md). Sono inclusi `vendor/` di produzione, asset Vite e dati del fascicolo. Dopo la configurazione di HTTPS e la generazione della chiave per la nuova installazione, eseguire anche `php artisan nomos:validate`. La simulazione Python è disponibile nel repository ed è eseguita separatamente.
