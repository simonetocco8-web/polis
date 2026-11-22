# Sicurezza

Le verifiche correnti si applicano alla fase 1. Prima dell’apertura pubblica, il gestore deve predisporre un canale di contatto riservato per le segnalazioni di vulnerabilità. Inserire nel canale descrizione, impatto e versione interessata, evitando dati personali, credenziali e dettagli non necessari. Conservare in forma privata le segnalazioni sensibili fino alla correzione.

Servire esclusivamente `public/`, usare HTTPS, configurare i log con accessi limitati e aggiornare le dipendenze tramite i lockfile. Eseguire gli audit di Composer e npm e le verifiche CI a ogni aggiornamento.
