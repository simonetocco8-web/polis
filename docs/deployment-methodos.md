# Installare Methodos v0.2.0 su cPanel

Requisiti: PHP 8.4 aggiornato (minimo 8.4.1), estensioni Laravel, HTTPS e Apache con riscrittura degli URL. Il pacchetto completo contiene le dipendenze PHP di produzione e gli asset Vite. L’aggiornamento contiene i file modificati da Foundation e la nuova directory `public/build`. Il portale non richiede database, Redis, Node.js o processi Python.

## Aggiornamento da Foundation tramite SSH

1. Eseguire il backup di codice, file `.env` e asset dell'installazione. Scaricare dalla release lo ZIP di aggiornamento e il relativo file `.sha256`; verificare entrambi sul server con `sha256sum -c polis-ai-v0.2.0-cpanel-update.zip.sha256`.
2. Posizionarsi nella directory esistente del progetto, quella che contiene `artisan`. Estrarre lo ZIP lì con `unzip -o /percorso/polis-ai-v0.2.0-cpanel-update.zip`. Lo ZIP conserva `.env`, `APP_KEY` e `vendor/`. Lasciare la document root su `public/`.
3. Con il binario PHP 8.4 del proprio hosting, eseguire:

   ```sh
   php artisan optimize:clear
   php artisan documents:validate
   php artisan research:validate
   php artisan optimize
   ```

4. Verificare Metodologia, scenari, indicatori, Polis Index, PDF/stampa e download del protocollo. La validazione deve indicare tre versioni documentali e configurazione preliminare. In caso di problemi ripristinare i file del backup e rigenerare le cache.

## Aggiornamento tramite Git e SSH

Dalla directory del checkout Foundation verificare `git status --short` e completare il backup. Con working tree pulito e branch di produzione basato sulla release Foundation:

```sh
git fetch origin tag v0.2.0
git merge --ff-only 'v0.2.0^{commit}'
unzip -o /percorso/polis-ai-v0.2.0-cpanel-update.zip 'public/build/*'
php artisan optimize:clear
php artisan documents:validate
php artisan research:validate
php artisan optimize
```

Se il fast-forward è rifiutato, preservare le modifiche dell’hosting e preparare un checkout separato prima di cambiare document root. Non rigenerare la chiave applicativa e non modificare il file `.env` esistente. I lockfile sono invariati rispetto a Foundation.

## Installazione nuova

Usare il pacchetto completo. Seguire [le istruzioni cPanel](deployment-cpanel.md) per document root e configurazione. Generare la chiave solo per una nuova installazione. Per il pacchetto completo si possono omettere i passaggi di build e installazione delle dipendenze.
