# POLIS AI · Il filosofo-re artificiale

Portale pubblico di un progetto indipendente di ricerca sul governo algoritmico. La fase 1 descrive l’ipotesi di ricerca, la Repubblica di Nova e il disegno sperimentale. Il portale funziona senza database, account, chiavi AI o servizi scientifici in esecuzione.

## Avvio locale

Requisiti: PHP 8.4.1 o successivo della serie 8.4 con le estensioni richieste dal [framework Laravel](https://laravel.com/docs/13.x/deployment#server-requirements), Composer 2 e Node 22.12+ della serie 22 o Node 24. Per i test servono anche DOM, XMLWriter e XMLReader.

```sh
composer install
npm ci
npm run build
cp -n .env.example .env
php artisan key:generate
php -S 127.0.0.1:8000 -t public
```

Aprire http://127.0.0.1:8000. Per modifiche a CSS e JavaScript, eseguire di nuovo `npm run build`. I test browser avviano un server separato sulla porta 8055.

```sh
composer validate --strict
composer test
vendor/bin/pint --test
vendor/bin/phpstan analyse
php artisan documents:validate
npm run check
npx playwright install chromium
npm run test:browser
composer audit --locked
npm audit --audit-level=high
```

## Struttura

| Percorso | Responsabilità |
| --- | --- |
| `app/Http`, `routes/` | Pagine pubbliche, validazione delle richieste, risposte e intestazioni |
| `app/Documents` | Manifest, SHA-256, rendering Markdown e struttura costituzionale |
| `content/` | Contenuti editoriali, diario, originali acquisiti e metadati |
| `resources/`, `public/brand/`, `lang/` | Blade, design system, identità grafica e localizzazione |
| `docs/`, `tests/`, `.github/workflows/` | Procedure, decisioni, test e integrazione continua |

Le route pubbliche comprendono homepage, Progetto, Filosofia, Nova, Costituzione e articoli, Biblioteca e versioni, Metodologia, Simulatore, Osservatorio, Diario e voci, Trasparenza, Privacy e Accessibilità. `php artisan route:list` mostra i percorsi e i nomi.

## Documenti, deployment e licenze

- [Importazione degli originali](docs/import-original-documents.md) e [conservazione delle versioni](docs/document-versioning.md).
- [Deployment cPanel](docs/deployment-cpanel.md) e [sviluppo in Docker](docs/deployment-docker.md).
- [Architettura](docs/architecture/overview.md), [roadmap](docs/research-roadmap.md) e [limiti prima della pubblicazione](docs/known-limitations.md).
- [Proposte di licenza](docs/licensing.md) per codice e contenuti.
