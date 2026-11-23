# Archon v0.6.0 su cPanel

Richiede PHP 8.4.1 o successivo della serie 8.4, Apache con riscrittura URL, document root public/ e permessi di scrittura su storage/ e bootstrap/cache/. Si applicano le estensioni e la configurazione indicate nella [guida cPanel](deployment-cpanel.md). Il portale serve dati statici con Laravel. Python, database, Redis, Node.js, worker e credenziali OpenAI non sono richiesti.

## Aggiornamento da Nomos v0.5.0 via SSH

Scaricare ZIP e checksum dalla release. Verificare dalla directory di download.

```sh
sha256sum -c polis-ai-v0.6.0-cpanel-update.zip.sha256
unzip -t polis-ai-v0.6.0-cpanel-update.zip
```

Conservare un backup privato dell'installazione. Usare il binario PHP 8.4 del proprio hosting e sostituire i percorsi di esempio.

```sh
cd /percorso/privato/polis-ai
php artisan optimize:clear
unzip -o /percorso/download/polis-ai-v0.6.0-cpanel-update.zip -d "$PWD"
php artisan documents:validate
php artisan nomos:validate
php artisan archon:validate
php artisan optimize
```

Verificare /nova/governo, /nova/governo/decisioni e i download. Conservare .env, APP_KEY, dipendenze PHP esistenti e document root. In caso di errore ripristinare il backup e ricreare le cache.

Per un checkout Git pulito, dopo il backup usare `git fetch origin tag v0.6.0` e `git merge --ff-only 'v0.6.0^{commit}'`. Estrarre gli asset dal pacchetto di aggiornamento con `unzip -o /percorso/download/polis-ai-v0.6.0-cpanel-update.zip 'public/build/*'` e rieseguire le verifiche Artisan.

## Installazione nuova

Verificare il checksum dello ZIP completo, estrarlo in una directory privata e seguire la guida cPanel. Le dipendenze PHP di produzione e gli asset Vite sono inclusi. Creare la configurazione locale dalla copia di esempio, attivare HTTPS e generare una nuova APP_KEY per la nuova installazione. Verificare anche `php artisan archon:validate`. Eseguire la simulazione Archon separatamente. [Configurazione del provider](architecture/archon.md)
