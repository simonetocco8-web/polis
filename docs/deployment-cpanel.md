# Deployment su cPanel

1. Selezionare PHP 8.4 e le relative estensioni Laravel per il dominio e la CLI. Preparare una release fuori da `public_html`.
2. Eseguire `npm ci && npm run build` su una macchina di build. Includere `public/build` nella release.
3. Installare con `composer install --no-dev --no-interaction --optimize-autoloader`. Predisporre `.env` fuori dal document root con `APP_ENV=production`, `APP_DEBUG=false`, `APP_URL=https://dominio` e `POLIS_INDEXABLE=false` per la prima verifica. Conservare la stessa `APP_KEY` tra aggiornamenti e generarla in modo sicuro alla prima installazione.
4. Impostare il document root del dominio sulla directory `public/`. Verificare riscrittura Apache e certificato HTTPS, forzare HTTPS nel pannello e configurare HSTS dopo la verifica. Consentire scrittura a PHP solo dove necessario, tra cui `storage/` e `bootstrap/cache/`. Evitare permessi globali di scrittura.
5. Eseguire `php artisan optimize:clear`, `php artisan documents:validate` e `php artisan optimize`. Confermare che il server usi il PHP selezionato.
6. Verificare homepage, biblioteca, Costituzione, asset, robots, sitemap, 404 e assenza di accesso a file interni. Verificare le impostazioni dei log e le informazioni mancanti in `known-limitations.md`. Abilitare `POLIS_INDEXABLE=true` dopo approvazione e ricreare le cache.

Per aggiornare, conservare la release precedente, confrontare il manifest storico e verificare la nuova release prima di cambiarne il document root. Per il rollback, ripristinare il document root della release precedente con la stessa configurazione sicura, ricreare le cache e ripetere le verifiche HTTP. In produzione bastano PHP e il server web per servire gli asset già compilati.
