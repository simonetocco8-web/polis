# Experimentum 1.0

## Protocollo e ruoli

Congelare il contratto JSON con il comando freeze e conservare il digest fuori dal file congelato. Il comando usa creazione esclusiva. Una nuova versione richiede un nuovo identificativo o numero di versione e una nuova anchor. Il runner accetta soltanto un protocollo validato a fronte di un digest atteso, profilo smoke e budget API zero. La prova iniziale è stata congelata in un commit anteriore alla prima esecuzione. Le versioni storiche del motore e i relativi risultati restano intatti.

Il runner importa Demos, Oikonomia e Stabilitas R. Non avvia un decisore, non utilizza credenziali Nomos o OpenAI e non importa il provider. I checkpoint sono salvati in una directory privata creata in modo esclusivo e separata dagli export. Ogni replica ha stato e registro indipendenti. Theoria legge l'export in sola lettura, verifica fonti, protocollo, calendario, catena mensile, prove di replay e aggregati. La CLI di verifica richiede inoltre il digest dell'intero export da un canale indipendente. Senza tale digest una catena riscritta interamente non autentica la fonte. La verifica Theoria non esegue l'economia. Il replay vero viene eseguito dal motore a partire dal checkpoint. Nessuna operazione istituzionale è esposta da Experimentum.

## Appaiamento e maturità

Per ogni seme il runner confronta l'esecuzione dal checkpoint iniziale con una nuova istanza ricostruita dallo stesso checkpoint. I due passaggi condividono popolazione, imprese, risorse, parametri, calendario e shock. Il calendario produttivo deriva da un dominio SHA-256 separato dal RNG del simulatore, precalcolato prima dei passi. Una morte, nascita o altra transizione interna non cambia quel calendario. Il flusso esogeno del pilota riguarda solo la finestra produttiva. Il pilota non dimostra equivalenza di tutti gli shock o dei regimi. Non c'è una coppia di politiche dalla quale inferire un effetto.

| Regime | Maturità | Mancanze principali |
| --- | --- | --- |
| A | Dimostrazione istituzionale | Competizione, programmi, elezioni, mandati, alternanza, deliberazione e controllo delle politiche operativi |
| B | Percorso tecnico | Nomos e Archon verificati, inclusa una prova singola reale. Calibrazione e prove replicate del decisore mancanti |
| C | Dimostrazione istituzionale | Ordinamento esteso e decisore completi |
| D | Dimostrazione istituzionale | Partecipazione umana e deliberazione ibrida operativa |
| E | Dimostrazione istituzionale | Elettorato, voto e deliberazione operativi |
| F | Dimostrazione istituzionale | Funzione decisionale e obiettivi validati |

Il confronto B–A è bloccato. Lo scenario A non è sostituito da una politica fissa. Il pilota usa un percorso tecnico di Nova senza atti. Methodos specifica le precondizioni scientifiche. Oikonomia riconcilia i conti, Stabilitas documenta la fragilità nel lungo periodo e Theoria distingue interpretazione e integrità. La combinazione non è un'economia validata fuori campione.

## Stati e statistica

NOT_READY identifica l'assenza di prerequisiti. PREREGISTERED registra il protocollo congelato. TECHNICAL_VALIDATION è il ramo eseguibile. COMPLETED significa che tutti gli esiti sono stati registrati, compresi gli errori. REPRODUCED richiede simmetria dei checkpoint, uguaglianza delle serie e dei saldi. INVALIDATED conserva i fallimenti. Il grafo prevede EXPLORATORY e CONFIRMATORY_ELIGIBLE, ma l'esecutore di questa versione non abilita tali rami. Una nuova prova dopo l'esame dei dati deve essere dichiarata come tale. Le corse estese non sono abilitate.

Sono disponibili medie mensili, deviazione campionaria, range, numerosità e mancanti. Gli arresti tecnici rimangono nel denominatore. Arretrati, cessazioni e zero produzione sono esiti economici distinti dai guasti software. Inferenza appaiata, intervalli, sensibilità e potenza statistica rimangono da implementare e validare prima del confronto. L'uguaglianza tecnica di una replica e del proprio replay non è una stima causale. Il Polis Index definitivo non è attivo.

## Comandi

Da simulation/ con il lockfile Python del simulatore:

```sh
python -m experimentum.cli readiness B A
python -m experimentum.cli freeze DRAFT.json FROZEN.json
python -m experimentum.cli run FROZEN.json CHECKPOINT_DIR --expected HASH_PROTOCOLLO > REPORT.json
python -m experimentum.cli verify REPORT.json --expected HASH_PROTOCOLLO --export-sha256 HASH_EXPORT
```

CHECKPOINT_DIR deve essere una nuova directory privata. Le misure aggregate sono disponibili in JSON e CSV dal laboratorio Laravel. Il validatore Artisan verifica il fascicolo autorizzato e bloccato dalla release. Il portale non legge gli stati privati.
