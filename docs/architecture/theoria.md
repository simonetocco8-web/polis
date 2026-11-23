# Theoria 1.0

Theoria è un valutatore offline in sola lettura. Il ruolo observer esistente di Nomos consente osservazione, export, verifica e replay. Le prove negative verificano che quella credenziale non possa agire come Governo, Corte, motore o altro universo. Il processo di valutazione non richiede token Nomos, segreti del provider, motore attivo o diritti di scrittura nelle fonti. Distribuire il processo con input in sola lettura e output in una directory dedicata. Un custode fidato prepara gli archivi necessari al replay privato. I JSONL storici possono contenere motivazioni e identificativi riservati, quindi restano nel perimetro del custode. L'Osservatorio riceve il fascicolo aggregato autorizzato. La proiezione candidata omette testo libero, identificativi di decisione, osservazioni, riferimenti privati e ricevute. Il suo stato ne impedisce l'importazione nel portale.

## Audit

Il comando theoria.cli audit richiede due anchor custodite indipendentemente. Verifica catene, origine Nomos, prompt, schema di decisione, stesso universo, hash della vista e dell'input inviabile al modello. Ripete la vista dal prefisso Nomos alla data della decisione, inclusi ritardi, unità, disponibilità, definizioni e calibrazione. Confronta proposta e ricevuta con la sequenza e lo stato giuridico. Questi controlli stabiliscono integrità e riproducibilità. La provenienza remota è verificata solo parzialmente. Un'identità di risposta registrata localmente non è un'attestazione indipendente del fornitore.

Le misure successive sono descrittive e mantengono unità, fonte, periodo e qualità. Una previsione rimane il testo dichiarato. L'analisi del merito qualitativo richiede un revisore e non modifica la classificazione deterministica. Nessun caso riceve un punteggio automatico di bontà economica. La pendenza giuridica viene distinta dalla causalità.

| Stato | Condizione |
| --- | --- |
| VERIFIED | Invarianti applicabili verificate sui dati disponibili |
| PARTIALLY_VERIFIED | Solo parte delle evidenze è supportata |
| UNVERIFIED | Esito tecnico o istituzionale non confermato |
| NOT_APPLICABLE | Misura inapplicabile, per esempio effetti di un atto non presentato |
| INSUFFICIENT_EVIDENCE | Fonti mancanti o base insufficiente per una conclusione |
| PENDING_OUTCOME | Pronuncia, applicazione o osservazioni ancora pendenti |
| INTEGRITY_FAILURE | Catena, anchor, ricostruzione o ricevuta incompatibile |

Gli stati sono ricalcolati per nuove evidenze, conservando ogni versione del fascicolo precedente. Si passa da pendente a un esito solo in presenza di evidenza successiva verificabile. Un errore d'integrità richiede ripristino verificato. La versione delle regole e il digest sono esportati. Il commit lega il codice che interpreta le regole. Per nuove valutazioni congelare commit, pacchetto di regole, fonti e anchor prima dell'analisi.

## Uso e pubblicazione

Dalla directory simulation/ con i lockfile del simulatore, `python -m theoria.cli audit ARCHON NOMOS --archon-anchor SHA --nomos-anchor SHA` genera il fascicolo privato. Conservare l'output in una directory riservata. Il parametro opzionale --candidate produce una proiezione da sottoporre ad autorizzazione. La release PHP accetta il checksum dell'unica fixture offline pubblicata. `python -m theoria.cli fixture ../content/statistics/archon.json` riproduce il fascicolo pubblico, con export CSV prodotto dall'applicazione. Il portale rimane in sola lettura.

I sei scenari condividono un controllo preliminare dei manifest con riferimenti per condizioni iniziali, shock, calibrazione, finestra, esclusioni, piano statistico e repliche. Manifest coincidenti non bastano a giustificare confronti. Maturità dei regimi, adeguatezza campionaria e metodi rimangono prerequisiti della ricerca. Nessun ranking o Polis Index definitivo.
