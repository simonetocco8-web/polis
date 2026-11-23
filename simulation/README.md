# Demos 0.3.0

Il motore tecnico è indipendente da PHP. Servono Python 3.12.14 e NumPy 2.3.5. Entrare in `simulation/` ed eseguire:

```sh
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-test.lock
python -m unittest discover -s tests -v
python -m demos.cli sources sources --offline
python -m demos.cli generate runs/initial --profile standard --reference eu27 --seed 20261122
python -m demos.cli validate runs/initial
python -m demos.cli compare runs/initial > runs/calibration.json
python -m demos.cli run runs/initial runs/month-600 --months 600
python -m demos.cli replay runs/initial runs/replayed --events runs/month-600/events.jsonl
python -m demos.cli clone runs/initial runs/universes
python -m demos.cli export runs/initial runs/export
```

Per riprendere un checkpoint, passarlo come primo argomento di `run` e scegliere una nuova directory di destinazione. Il limite totale è 600 mesi. I profili sono `smoke` (300/15), `development` (10.000/500) e `standard` (100.000/5.000). Usare `--reference hypothetical` per la dimostrazione senza fonti empiriche. L’opzione `sources DIR` senza `--offline` scarica una nuova acquisizione. Conservare il manifest e fissare gli snapshot prima di aggiornare le fonti.

```sh
docker build -t polis-demos:0.3.0 .
mkdir -p runs
docker run --rm --user "$(id -u):$(id -g)" -v "$PWD/runs:/runs" polis-demos:0.3.0 generate /runs/docker-smoke --profile smoke --seed 42
```

## Archiviazione e importazione

`manifest.json` riporta configurazione, hash, seed, replica, ambiente e timestamp. L’hash canonico usa l’header JSON ordinato e i byte little endian delle tabelle tipizzate. Timestamp, contenitore ZIP e nome della replica non entrano nell’hash. L’NPZ è privato e si carica senza pickle. Il log mensile è concatenato con SHA-256 e il replay riesegue le transizioni verificando ogni record. La clonazione copia configurazione e array per A–F. In Demos le copie sono baseline tecniche, senza scenari governativi eseguibili.

Per il portale copiare soltanto `runs/export/statistics.json` in `content/statistics/demos.json` alla radice del repository. La release accetta solo lo standard UE-27 al mese zero. Usare `php artisan demos:validate` e la CI, che rigenera lo snapshot e verifica l’uguaglianza degli aggregati. Non pubblicare NPZ, log, checkpoint o semi sperimentali futuri. Il seed di questa prova è dimostrativo e pubblico. PHP non invoca Python.

## Schema e regole

- **Cittadini** · Gli ID sono indici allocati in coda, mai riusati. La nascita è un mese relativo al gennaio 2022 simulato. L’età è periodo meno mese di nascita. Deceduti ed emigrati conservano identità e legami storici. Residenza e abitazione derivano dal nucleo; stato familiare da compagno e parentela. Un arco figlio→genitore richiede un divario di almeno 18 anni; questo esclude cicli. Il legame di coppia è reciproco.
- **Famiglie e territorio** · Taglie adulte 1–3, raggruppamento iniziale per età con perturbazione casuale, alcuni adulti anziani coabitano con nuclei più giovani. Minori raggiungono un nucleo di adulti compatibili per età, oppure una convivenza assistita. Se tutti gli adulti lasciano un nucleo, i minori restano in una convivenza assistita esplicita. La parentela simulata rappresenta un solo genitore. L’Atlante identifica le coabitazioni multigenerazionali con almeno due adulti e uno scarto di età di 30 anni o più. Tenure e capacità abitativa sono ipotetiche. La capacità è informativa, senza mercato immobiliare. Il reddito del nucleo è la somma dei redditi dei membri residenti, derivabile senza duplicare risorse individuali. Risorse condivise e trasferimenti non sono contabilizzati.
- **Istruzione, lavoro e imprese** · L’istruzione iniziale è condizionata all’età. Competenze, occupazione e reddito dipendono dal livello inizializzato; probabilità di partecipazione dipende anche dalla limitazione funzionale. Forza lavoro inizializzata a 18–64 anni, quota disoccupata imposta a 8,5% con arrotondamento sul conteggio. Privati assegnati a posti sintetici nel territorio; le assegnazioni eccedenti diventano autonomi senza impresa assegnata. Imprese e titolari sono distinti dai posti pubblici. Dimensione indica capacità potenziale, non classe osservata per addetti. Gli addetti si ricavano dai rimandi dei cittadini; i titolari autonomi si contano separatamente. Importi individuali in EUR sintetici, redditi annui e stock iniziali non riconciliati. Pensionamento, morte ed emigrazione cessano l’assegnazione; non ci sono assunzioni, nuovi titoli, pensioni dinamiche o impresa dinamica.
- **Salute e preferenze** · Le probabilità di limitazioni sono ipotesi condizionate all’età, distinte dalle tavole empiriche di mortalità. Nessuna diagnosi o prevalenza clinica. Le nove preferenze 0–100 sono una combinazione di fattore latente comune (25%) e variabile dedicata (75%), indipendenti da sesso, età e salute. Le correlazioni sono ipotesi, non stime empiriche. Condizioni croniche specifiche non modellate.
- **Passo mensile** · Compiere il mese, applicare mortalità e uscite, chiudere occupazioni e coppie dei non residenti, aggiornare fragilità, aggiungere nascite e immigrati, poi formare coppie fra alcuni adulti soli compatibili per età. Divari di coppia iniziale seguono il raggruppamento per età. Per un rischio annuale `p` si usa `1 − (1 − p)^(1/12)`. Il tasso migratorio in ingresso è invece un flusso atteso: residenti all’inizio × 0,006 / 12 con arrotondamento casuale. Emigrazione 0,004 annua per adulti, nascite 0,043 annua per residenti F di 18–44 anni e formazione coppie 0,05 annua per candidati. Sono ipotesi tecniche senza obiettivi riproduttivi imposti. Dopo i 94 anni si usa l'ultimo qx a età esatta. Il valore terminale aperto della tavola non è una probabilità annuale. Gli ingressi sono adulti e iniziano fuori forza lavoro. Il modello non effettua rientri o regressioni di stato.
- **Casualità** · Chiave SHA-256 troncata per seed, dominio e mese. Miscelazione vettoriale a 64 bit e conversione ai 53 bit di mantissa per singolo ID. L’ordine o il numero di estrazioni degli altri domini non sposta il sottostream.

Il motore non implementa produzione, prezzi, credito, governo AI o una simulazione confermativa. [Rapporto di calibrazione](calibration.md).

## Nomos

Dalla directory simulation/ eseguire `python -m nomos.cli demo DIRECTORY` per ricostruire il fascicolo istituzionale. La directory di output va trattata come riservata per la presenza del JSONL completo. Le esportazioni pubblicabili sono nomos.json e nomos.sha256. [Architettura e interfacce](../docs/architecture/nomos.md)

## Archon

Da simulation/ eseguire `python -m archon_lab DIRECTORY` per riprodurre la fixture offline. Il client, il provider reale opt-in e la separazione via Docker sono descritti nella [specifica Archon](../docs/architecture/archon.md).
