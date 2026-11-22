# ADR 0001 · Portale Laravel in sola lettura

- **Contesto** · Consultazione pubblica, hosting cPanel, assenza di database nella fase 1.
- **Alternative** · SPA, generatore statico, Laravel con middleware di sessione.
- **Decisione** · Laravel 13 con Blade, route senza sessione, cache file, asset Vite e interazioni native. Nessun runtime Alpine richiesto per il menu o i pulsanti di stampa e copia.
- **Motivazione** · Il server può gestire ricerca, route documentali e rendering con PHP 8.4. La navigazione essenziale funziona con JavaScript disabilitato.
- **Compromessi** · Modifiche editoriali tramite commit e build degli asset quando cambia il frontend. La CSP di fase 1 è predisposta per asset compilati.
- **Formulata da** · Codex. Revisione umana da registrare.
