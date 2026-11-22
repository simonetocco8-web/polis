# Simulatore Methodos · Confini e interfacce

Il portale Laravel rende consultabili testo e configurazioni. Il simulatore futuro sarà prevalentemente Python e avrà un sistema di esecuzione separato. Questa release non introduce processi Python né endpoint che ricevano proposte.

| Componente | Responsabilità e interfaccia prevista |
| --- | --- |
| Motore | Unico scrittore dello stato. Applica transizioni e atti autorizzati al confine temporale. Produce snapshot immutabili ed eventi. |
| Agenti individuali | Stati demografici e comportamenti modellati. Ricevono informazioni e aggiornano intenzioni tramite regole del motore. |
| Famiglie | Composizione e bilanci familiari. Producono intenzioni di consumo e altre transizioni autorizzate. |
| Imprese | Produzione, investimenti, bilanci e domanda di lavoro. Presentano ordini e intenzioni al motore. |
| Mercati | Accoppiano le intenzioni secondo regole versionate. Producono scambi che il motore contabilizza in partita doppia. |
| Istituzioni | Mandati, competenze e regole per ciascuno scenario. Forniscono i vincoli al decisore e ai controlli. |
| Governo AI | Legge solo snapshot filtrati e presenta proposte JSON. |
| Corte costituzionale | Verifica competenza, legalità, proporzionalità, copertura, scadenze, ricorsi e revoca. Restituisce decisioni motivate e tracciabili. |
| Osservatorio | Accesso in sola lettura a snapshot e log. Applica formule versionate, produce metriche e registra fallimenti. |
| Registro eventi | Sequenza append-only per universo, periodo e replica. Consente audit, checkpoint e replay. |
| Archivio decisioni | Conserva le proposte, le decisioni di controllo e le revoche. Collega gli identificativi agli eventi applicati. |

## Contratto proposto

[Schema JSON 1.0](government-proposal-1.0.schema.json). Identificativi, strumenti e competenze devono risolversi in registri autorizzati per scenario. Lo schema strutturale è un primo controllo. Il catalogo del singolo strumento deve fissare parametri ammessi, unità, intervalli, destinatari, costi e scadenze. Testi di motivazione ed effetti attesi si archiviano come dati inerti. Un giudizio costituzionale richiede una decisione separata e motivata. Il motore applica una sola volta gli atti autorizzati e respinge identificativi duplicati.

Il decisore avrà un canale per leggere snapshot filtrati e inviare proposte. Nessun codice arbitrario, SQL, filesystem, accesso diretto allo stato, semi, eventi futuri o dati di altre repliche. Il motore e l’Osservatorio mantengono credenziali e permessi separati. I dettagli sui semi restano nell’archivio riservato. Il replay ripete gli atti registrati con le versioni congelate e resta distinto da una nuova generazione AI.

## Configurazione e preregistrazione

`content/research/methodos-1.0.json` raccoglie le ipotesi e la struttura dei cataloghi. `php artisan research:validate` verifica il manifest e segnala lo stato. I livelli sono `hypothesized` (proposta), `calibrated` (parametri stimati), `validated` (verifiche indipendenti) e `frozen` (versione bloccata con evidenze). Le voci nulle restano da definire. La prontezza strutturale richiede fonti, regimi, formule, crisi, repliche e riferimenti alle evidenze. La loro verifica scientifica è una responsabilità distinta. Il manifest 1.0 corrente non autorizza prove confermative.
