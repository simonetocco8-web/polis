# Oikonomia 0.4.0 · Modello tecnico

## Perimetro e fonti

L’economia chiusa contiene famiglie, imprese, Tesoro e una banca di regolamento. Il resto del mondo è un settore di confine senza posizioni o scambi. Il modello distingue produzione, spesa e reddito secondo il perimetro interno documentato, ispirato a [ESA 2010](https://ec.europa.eu/eurostat/web/esa-2010) e [SNA 2025](https://unstats.un.org/unsd/nationalaccount/sna2025.asp). La riconciliazione riguarda le attività modellate. Non si dichiara una conformità integrale agli standard.

Il solo riferimento empirico impiegato resta quello demografico ereditato da Demos: Eurostat UE-27 2022 per età, sesso e mortalità, con confronto demografico 2023. Eurostat conti nazionali, HICP, EU-LFS, EU-SILC, dati sui bilanci pubblici e BCE per credito sono fonti future candidate. Nessuna di queste serie è stata acquisita o stimata per la prova economica. [Manifest demografico](../../simulation/sources/manifest.json).

Tutti i parametri economici in `simulation/config/oikonomia-1.json` sono ipotizzati. Nessun parametro economico è marcato calibrato, validato empiricamente o congelato. I target Methodos di PIL, inflazione e debito/PIL non sono vincoli di chiusura. Non ci sono governi, comparazioni AI–umani o Polis Index.

## Migrazione e responsabilità

`oikonomia.state.attach` verifica l’origine Demos al mese zero e clona gli array. Depositi iniziali delle famiglie = somma dei risparmi Demos × 100 centesimi. Le retribuzioni annuali Demos forniscono un’offerta mensile convertita con divisione per 12 e arrotondamento ai centesimi. Redditi diversi, patrimonio e debiti Demos sono esclusi dal bilancio di apertura. La dote di liquidità delle imprese e del Tesoro è esplicita in configurazione. Le riserve iniziali della banca hanno per contropartita tutti i depositi iniziali più la dotazione di patrimonio netto. I nuovi debiti iniziano da zero. L’avvio non carica il 90% di debito/PIL come stock osservato.

`engine` orchestra i moduli lavoro, produzione, mercati, famiglie, settore pubblico, credito e contabilità nazionale. Il saldo monetario può variare solo attraverso i trasferimenti convalidati o i movimenti bancari. L’identità antropodemografica e gli snapshot Demos mantengono il formato originale. Gli universi A–F sono copie indipendenti della stessa baseline, senza agenti governativi.

## Piano dei conti e unità

| Conto o variabile | Unità e tempo | Regola |
| --- | --- | --- |
| Depositi di famiglie, imprese, Tesoro | Centesimi interi, stock di fine mese | Attivo del titolare e passività della banca. Nessun contante separato. |
| Riserve e patrimonio netto banca | Centesimi interi, stock | Dotazione di riserve fissa. Patrimonio aumenta con interessi e cala con perdite su prestiti. |
| Credito e debito | Centesimi interi, stock | Crediti bancari = debiti di famiglie, imprese e Tesoro. Origination e rimborso cambiano simultaneamente debito e depositi. |
| Capitale e scorte | Unità fisiche, stock | Investimento converte beni in capitale. L’ammortamento sottrae capitale esistente. Scorte = apertura + output − intermedi − vendite finali. |
| Produzione, ricavi, consumi intermedi | Unità e centesimi, flusso mensile | Un solo bene composito a prezzo corrente uniforme. La contabilità nazionale valuta le scorte con il medesimo prezzo del mese. |
| Retribuzioni, imposte, trasferimenti, interessi | Centesimi, flusso mensile | Registrati sui pagamenti effettivi. I rimborsi sono movimenti patrimoniali. Le perdite su crediti non sono produzione. |
| Investimenti | Unità e centesimi, flusso mensile | Acquisti di capitale, distinti da consumi, trasferimenti e variazioni di scorte. |
| Saldo pubblico | Centesimi, flusso mensile | Imposte meno stipendi, trasferimenti, acquisti, investimenti e interessi. Variazione di cassa = saldo + variazione del debito. |
| PIL nominale/reale, pro capite e produttività | Centesimi, flusso mensile | Base composita 2022. Produttività privata per addetto effettivamente impiegato nel passo; pro capite su residenti finali. |
| Lavoro | Persone, stock di fine mese | Forza lavoro = occupati + disoccupati. L’emigrazione, i decessi e i pensionamenti chiudono l’impiego. |
| Reddito disponibile | Centesimi, flusso mensile | Salari pagati più trasferimenti meno imposte sui redditi. Mediana e Gini pesano ogni nucleo allo stesso modo sulla sua quota per membro. Redditi territoriali assegnati prima delle transizioni Demos. |

I movimenti si regolano in una sola banca. Una scrittura di trasferimento addebita il deposito del ricevente e accredita quello del pagatore nel sottoconto di attività. La passività aggregata per depositi resta invariata. Prestiti, interessi, rimborsi e stralci indicano esplicitamente conti dei debitori e della banca. Il libro raggruppa vettori interi di debiti e crediti separati per fase e conto. Identificativi `mese:causale`, impronte dei vettori e hash concatenati bloccano duplicati e consentono verifica. `--journal-detail` archivia le gambe individuali in JSONL gzip privato; il log ordinario contiene il capo catena e il replay rigenera le gambe. Il saldo totale di ogni scrittura è zero. Gli interi sono a 64 bit, con limiti di dominio e arrotondamento proporzionale esatto mediante somme cumulative; i prodotti grandi dell’apportionment usano interi Python.

## Sequenza e formule

1. Controllo orizzonte, stock iniziali, erogazione crediti entro limiti e finanziamento del Tesoro. La banca ha un tasso mensile ipotetico dello 0,5%; l’ammortamento è rotativo su debito residuo diviso per 24 con arrotondamento in alto, senza coorti a termine fisso.
2. Pianificazione lavoro per capacità, scorte e liquidità. Assunzioni locali, ordinate con competenza e sottostream stabile; eccedenze o salari inaccessibili causano perdita dell’impiego prima del pagamento. Lavoro autonomo Demos confluisce nella ricerca di lavoro all’avvio. Stipendi privati pagati integralmente agli addetti assegnati. Dipendenti pubblici ereditati da Demos, senza nuove assunzioni pubbliche.
3. Output pianificato = minimo fra capitale diviso 2 e somma della competenza ponderata × produttività × moltiplicatore settoriale. Output effettivo ≤ 10 × intermedi comprati dalle scorte precedenti. Lavoro, capitale e disponibilità fisica sono vincoli simultanei. Una quota fisica viene riservata al ciclo successivo. Il modello non distingue qualità o risorse naturali.
4. Pagamento pubblico vincolato alla liquidità, poi imposta sui salari. Pensioni e sussidi seguono condizioni demografiche e occupazionali. Il Tesoro finanzia il fabbisogno con prestiti entro tetto; salari e trasferimenti con fondi insufficienti sono razionati esplicitamente. I trasferimenti sono esclusi dalla spesa finale del PIL. La misura di lavoro pubblico registra lo status di impiego, anche quando il monte salari è razionato.
5. Domanda desiderata in funzione di reddito disponibile, risparmio, saldo liquido, prezzi e composizione del nucleo. I consumi effettivi sono limitati da stock, liquidità al prezzo comprensivo d’imposta ed eventuale credito. Divario sotto un fabbisogno fisico segnala privazione nel modello. Seguono acquisti pubblici e investimenti. Assegnazione proporzionale per unità e pagamenti interi; una volta vendute, le unità lasciano le scorte.
6. Interessi e capitale sono pagati entro la liquidità. Tre mesi di incapienza consecutiva chiudono le imprese indebitate e stralciano il residuo. Le scorte residue restano vendibili. La banca sospende nuove erogazioni a patrimonio non positivo. Non c’è risoluzione bancaria, creazione di banche, ingresso di nuove imprese o ristrutturazione del debito pubblico.
7. Prezzo successivo = prezzo attuale × (1 + 0,025 × (domanda − offerta) / max(domanda, offerta, 1)), arrotondato e limitato fra 4 e 100 EUR. IPC a un solo bene al lordo dell’imposta rispetto alla base 2022; non separa qualità e composizione. La prima variazione mensile è indisponibile.
8. PIL produzione = prezzo × (output − intermedi) + retribuzioni pubbliche effettive + imposta sui beni. PIL spesa = consumi famiglie, consumi pubblici, investimento e scorte. PIL reddito = retribuzioni + risultato operativo lordo, ricavato dal valore aggiunto al costo dei fattori, + imposta prodotti. Il reddito è una riconciliazione derivata, senza contabilità di redditi maturati indipendente. Il deflatore valorizza il bene a prezzo base e conserva il costo pubblico diretto. Il debito e il deficit usano una finestra mobile di 12 mesi solo quando disponibile.
9. Riconciliazione bancaria, di prodotto e fiscale. Poi transizioni Demos alla chiusura, archiviazione dei decessi/uscite, pensionamento e ingressi nella forza lavoro. Nessun pagamento economico dopo l’uscita nel periodo successivo. Depositi di nuclei senza residenti restano nello stock come saldi inattivi; eredità e divisioni patrimoniali non sono modellate. Gli indicatori sono calcolati su somme mensili e stati finali esplicitati.

La soglia relativa è il 60% della mediana positiva del reddito pro capite dei nuclei. Quando la mediana è nulla, la misura relativa è indisponibile. Il divario fisico del consumo essenziale resta misurabile. Nessuna formula è stata regolarizzata per evitare collassi durante la prova; questo è un modello esplorativo di stress, con mercato unico, capitale cumulabile e fine delle erogazioni fiscali al raggiungimento del tetto.

## Riproduzione

Dalla directory `simulation/`, con Python 3.12.14 e dipendenze in `requirements.lock`:

```sh
python -m demos.cli generate runs/demos --profile standard --reference eu27 --seed 20261122
python -m oikonomia.cli migrate runs/demos runs/initial
python -m oikonomia.cli run runs/initial runs/oikonomia --months 600
python -m oikonomia.cli validate runs/oikonomia
python -m oikonomia.cli replay runs/initial runs/replayed --events runs/oikonomia/events.jsonl
python -m oikonomia.cli clone runs/initial runs/universes
```

Lo stesso checkpoint è utilizzabile per riprendere una corsa con una nuova cartella. Gli stress usano `migrate --variant recession|production-shock|credit-crisis`, con eventi nei mesi 4–9. Docker usa `docker build -t polis-oikonomia:0.4.0 .` e `docker run --rm -v "$PWD/runs:/runs" --entrypoint python polis-oikonomia:0.4.0 -m oikonomia.cli ...`. I manifest canonici versionano configurazione, demografia, ancoraggio del giornale e stato. Il timestamp di esportazione è esterno allo snapshot.

Dopo la prova standard copiare soltanto `statistics.json` e `statistics.sha256` come `content/statistics/oikonomia.json` e `content/statistics/oikonomia.sha256`. Convalidare con `php artisan oikonomia:validate`. Il portale non esegue Python e non carica checkpoint, semi o transazioni individuali.
