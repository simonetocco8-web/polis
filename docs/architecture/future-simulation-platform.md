# Futura piattaforma di simulazione

1. Il portale pubblico pubblica documenti, protocolli e risultati approvati.
2. L’applicazione scientifica Vue.js gestisce utenti, configurazione degli esperimenti e confronto delle esecuzioni.
3. Il motore Python applica regole versionate, mantiene lo stato degli agenti e registra eventi riproducibili.
4. Il Governo artificiale usa interfacce per modelli intercambiabili e propone atti strutturati.
5. L’Autorità costituzionale valida permessi, schemi, limiti e vincoli sugli atti.
6. L’Osservatorio riceve eventi e misure a partire da dati di sola lettura.
7. L’archivio conserva input, versioni, semi casuali, atti, rigetti, esiti ed esportazioni.
8. Il gateway REST applica autenticazione, autorizzazioni, versionamento, tracciabilità e limiti di traffico.

## Confini di responsabilità

Il Governo invia proposte. Solo il motore può applicare gli atti validati. L’accesso del Governo esclude database degli agenti, formule economiche, regole demografiche, generatore casuale, stato interno dell’Osservatorio, criteri di valutazione e registro degli esperimenti. Autorizzazioni minime e ruoli distinti devono riflettere questi confini.

PostgreSQL può ospitare metadati scientifici. Redis e worker asincroni possono gestire la coda delle esecuzioni quando il carico lo richiederà. Definire prima schema degli eventi, modelli di accesso, unità temporale, checkpoint, idempotenza e ripetibilità. La fase 1 pubblica il disegno senza introdurre servizi o API.
