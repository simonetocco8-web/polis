# Archon 1.0 · Specifica del Governatore

## Flusso e confini

Archon è un client proponente per lo scenario B. I ruoli indipendenti rimangono quelli di Nomos. Il client importa solo il proprio codice, legge una credenziale governativa e comunica con una socket Unix. Il processo deve essere separato dal motore, dalla directory privata del servizio, dagli altri universi e dagli altri ruoli. L'immagine dedicata include il solo client. Il modello riceve una stringa JSON di dati e uno schema di risposta. Non riceve strumenti, token istituzionali, percorso della socket, seed, microdati, indici futuri, identificativi privati o output di altre repliche. Il modello non può invocare direttamente operazioni Nomos.

I file della Costituzione, del protocollo e dello schema Methodos sono quelli storici. Le modifiche additive a Nomos lasciano riproducibile il fascicolo v0.5.0. La configurazione privata del motore abilita la pubblicazione degli indicatori degli esperimenti Archon con archon_indicators uguale a true. I valori entrano nel registro solo a periodo concluso, mediante il ruolo motore. Il canale governativo restituisce una finestra di sei osservazioni per serie. Popolazione, produzione, prezzi e finanza pubblica corrente hanno ritardo zero dalla chiusura. Occupazione, disoccupazione, reddito, povertà, PIL, debito e credito hanno un mese di ritardo ulteriore. Ogni serie porta periodo, unità, definizione, ritardo, calibrazione e disponibilità. Il primo ciclo può iniziare con serie vuote. Il portale dichiara le osservazioni non calibrate.

## Contratto, mandato e memoria

Il prompt costituzionale 1.0 è archon/prompt-1.0.txt. Il provider riceve lo stesso prompt versionato per il run. La risposta strutturata distingue PROPOSE, ABSTAIN e INSUFFICIENT_INFORMATION. L'orchestratore registra PROVIDER_FAILURE per errori di formato, budget, timeout e indisponibilità del provider. Problema, obiettivo, alternativa, motivazione, incertezza ed effetto atteso sono sintesi pubbliche. Il modello seleziona strumento, aliquota e durata. Il client lega il mese, l'ID stabile, competenza fiscale, destinatari, costo nullo e articolo 28 nel formato Methodos. Nomos valida integralmente con lo schema originale e applica i limiti di legalità. La Corte usa una procedura indipendente. Le proposte rinviate rimangono da valutare.

Il mandato è verificato da Nomos a ogni accesso e invio. La memoria strutturata comprende osservazioni, proposte, minimi dettagli dei controlli, ricevute, esiti conosciuti, calendario e applicazione. Gli effetti visibili nei cicli successivi rimangono separati dalle previsioni. Il successore usa una credenziale e un archivio nuovi e può leggere la finestra amministrativa filtrata dal proprio universo. I fascicoli privati delle decisioni precedenti rimangono custoditi dall'operatore. Le motivazioni sostanziali della Corte non rientrano nella vista usata dal modello.

## Audit, ripetizione e costi

L'archivio JSONL si accoda con lock esclusivo e hash concatenati. Manifest e decisioni legano run, replica, mandato, modello richiesto, prompt e contratto, osservazioni e politiche informative, limiti, risposta validata, modello restituito, identificativo della risposta se presente, latenza, token, costo stimato e ricevuta giuridica. L'output malformato non viene archiviato. I dettagli delle eccezioni del provider non sono pubblicati. Il replay richiede la testa custodita indipendentemente, ricalcola i contratti e recupera le decisioni archiviate senza contattare il provider.

Si prenota il limite superiore a ogni chiamata prima di inviarla. Un crash con esito ignoto non comporta una nuova chiamata per lo stesso ciclo. Una richiesta a Nomos senza riscontro si riconcilia tramite ID e ricevuta senza rigenerare la proposta. La riconciliazione va tentata prima di avanzare il periodo. Se manca un atto autorizzato, la continuità economica resta al motore. Non ci sono retry automatici SDK o applicativi verso il provider. È consentita al più una proposta per periodo.

Il costo usa tariffe configurate in milionesimi di USD per token. Il tetto preventivo usa input massimo e output massimo per ciascuna prenotazione, inclusi i tentativi dall'esito ignoto. L'input usa un controllo locale conservativo basato su byte UTF-8 e margine per l'involucro API, seguito dal riscontro della telemetria. La Responses API impone il limite di output e l'integrazione imposta un limite temporale locale. Il budget rimane una stima e dipende dalle tariffe e dalla tokenizzazione del servizio. Usare un progetto API con propri limiti, credenziali dedicate e tariffe verificate. Il profilo live consente al massimo dodici chiamate per archivio. Il profilo offline non comunica in rete. Temperatura e fingerprint non vengono impostati o inventati.

## Esecuzione locale

Da simulation/ con Python 3.12, installare requirements-test.lock per motore e test. Il laboratorio riproducibile usa Nomos, il motore e una fixture a ruoli separati nel protocollo. Trattare la directory di output come privata.

```sh
python -m archon_lab /percorso/privato/fascicolo-archon
python -m archon.cli dry-run
python -m unittest discover -s tests -v
```

Per la prova operativa, preparare uno scenario B con Nomos seguendo [la guida Nomos](nomos.md). Nel file privato engine.json impostare seed della replica e archon_indicators. Avviare il servizio Nomos con una socket dedicata. Il processo del Governatore usa un account separato con accesso in lettura al solo token governativo e alla socket, oltre a un volume privato per il suo archivio. L'operatore del motore avanza il calendario e applica mensilmente. La Corte usa il proprio canale e decide prima della chiusura.

Il client offline usa `python -m archon.cli decide --socket SOCKET --token-file TOKEN --universe UNIVERSO --archive REGISTRO`. Si invoca una volta al mese, dopo la chiusura precedente e prima dell'applicazione. Il replay usa `python -m archon.cli replay REGISTRO --expected SHA256`. La combinazione arriva all'orizzonte mensile consentito da Nomos. I test pubblicati esercitano il solo profilo smoke.

Per una prova reale installare requirements-archon.lock nel solo ambiente client. Provider integrato OpenAI Responses API con SDK Python 2.15.0. Impostare ARCHON_MODEL e iniettare OPENAI_API_KEY tramite l'ambiente privato. Il file di configurazione JSON accetta max_calls, input_tokens, output_tokens, budget_micro_usd, input_micro_usd_per_token, output_micro_usd_per_token, timeout, technical_attempts e max_proposals_per_period. Gli ultimi due sono fissati a uno. I prezzi, il tetto e il modello vanno scelti dall'operatore. Prima di attivare la prova eseguire `python -m archon.cli dry-run --live --config LIMITI.json`. Per eseguire aggiungere `--live --authorize-paid-run --config LIMITI.json` al comando decide. Il budget richiede una configurazione esplicita. La chiave rimane fuori dal repository, dai registri e dall'hosting.

## Docker e isolamento

Costruire dalla directory simulation/ con `docker build -f Dockerfile.archon -t polis-archon .`. La variante live aggiunge `--build-arg INSTALL_OPENAI=1`. L'immagine usa un utente non privilegiato e contiene solo Archon. Avviare con filesystem in sola lettura, capability rimosse, escalation disabilitata e rete assente per la variante offline. Montare la directory della sola socket in lettura, il token governativo in lettura e un volume privato scrivibile per l'archivio. Predisporre un gruppo o una ACL Unix che permetta la connessione dalla UID 65532. In modalità live, l'operatore configura l'uscita controllata verso api.openai.com e il DNS necessario. Nessuna directory di stato del simulatore va montata.

Il servizio separato e la configurazione del sistema operativo costituiscono il confine di sicurezza. La libreria Python da sola non isola un processo eseguito con accesso al filesystem del motore. La prova di trasporto con SDK usa un server virtuale in memoria e non attesta connettività, autenticazione, prestazioni o compatibilità di uno specifico modello reale. [Rapporto tecnico](../../simulation/archon-report.md)
