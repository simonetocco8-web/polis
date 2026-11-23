# Stabilitas v0.4.1 · Audit della traiettoria Oikonomia

## Metodo e riproduzione

[Audit preliminare](stabilitas-audit-preliminare.md). Il baseline è stato riprodotto con il tag **v0.4.0**, Python 3.12.14, NumPy 2.3.5, seed 20261122, 100.000 residenti, 48.212 nuclei e 5.000 imprese. Tempo 92,697 s, picco RSS 96.756 KiB. La ripetizione è byte-identica al registro storico conservato. Hash di apertura `d12de75af361ccf5fb46d1f972894b0068a6ac3f21273b710e128155a93e2313`, finale `f9aa3a372a02828eb612494f59403de2c06911b5a9e25373a980c1f0ecf2f6b2`, registro JSONL non compresso `135af7b434a0472b94f92414aaa388a4bdd70f8a54814541d85c18d0057e00a5`. [Registro archiviato](archive/oikonomia-v0.4.0-events.jsonl.gz).

Il controllo strumentato usa la stessa dinamica storica. Un’osservazione supplementare valida, dal giornale, la variazione dei depositi e del patrimonio bancario e ricostruisce il PIL dal lato della spesa. Le prove condividono seme, demografia iniziale e sottostream per eventi, periodo e ID. Le priorità e le popolazioni ammissibili possono divergere per le regole economiche modificate. Si tratta di interventi sul modello e il confronto è condizionato all’insieme delle altre ipotesi.

| Fattore | Unica famiglia di intervento |
| --- | --- |
| R | Arrotondamento prezzi speculare con troncamento simmetrico dei punti base e arrotondamento intero simmetrico dei centesimi. |
| A | Continuità per l’autonomo titolare identificabile presso la propria impresa Demos quando esiste un posto locale e finanziabile; passa in busta paga. Gli autonomi senza posto entrano nella ricerca. Non viene creato un mercato autonomo separato. |
| B | Ogni dodici mesi un incumbent locale con risorse trasferisce €15.000 di depositi e 100 unità di capitale a una nuova impresa. Servono disoccupati locali e un posto cessato, senza debiti, scorte o depositi. Fino a 24 nuove identità slot/periodo, con capacità e territorio del posto. Il vecchio capitale residuo è stralciato come perdita reale esplicita. Nessuna dotazione gratuita. |
| C | Distribuzione per residente del 50% degli interessi incassati nel mese, entro patrimonio bancario positivo. La scrittura riduce il patrimonio e aumenta la passività per depositi. Nessun nuovo credito associato. |
| D | Tetto al debito pubblico di €1 miliardo anziché €1,5 miliardi; stessi strumenti e sequenza. È un confronto di severità del finanziamento, senza emissione illimitata. |
| E | Riserva di intermedi pari a circa un quarto dell’output più 10 unità anziché un sesto più 10. Nessun reintegro gratuito a scorte zero. |
| F | Chiusura dopo sei mesi consecutivi di incapienza anziché tre. Il costo del credito e la sua erogazione sono invariati. |
| B+C+E | Combinazione separata per osservare interazioni, senza attribuire la differenza a un singolo fattore. |
| C25 | Sensibilità: distribuzione del 25% degli interessi. |

Disegno: cinque corse standard da 600 mesi e trenta corse esplorative da 120 mesi. Ogni fattore esplorativo ha tre repliche accoppiate sul profilo smoke, seed 41 e 42 di base e 43 con recessione. Un solo seed standard, senza inferenza statistica. L’archivio pubblico contiene tutte le osservazioni mensili del controllo e, per le altre standard, apertura e cadenza annuale; i riepiloghi e le impronte provengono dai 600 passi. La CLI esporta CSV, JSON e SVG. Le serie di bilancio sono in centesimi, le quantità fisiche in unità, l’IPC ha base 100. Il reddito reale diagnostico usa reddito mediano nominale × 100 / IPC. La posizione finanziaria netta non bancaria è depositi meno debiti bancari. Non equivale al patrimonio reale; capitale e scorte sono mostrati a parte.

## Risultati causali e limiti

- **Discontinuità iniziale dimostrata.** 4.689 autonomi sono riclassificati prima del blocco del matching; 4.677 risultano disoccupati a chiusura del primo mese. L’occupazione privata di apertura non subisce licenziamenti dovuti a capacità o liquidità in quel primo passo. Restano gli effetti della transizione demografica e dei nuovi ingressi nella forza lavoro. Territorio, capacità, salario mensile e scorte entrano successivamente tramite eligibility, costo e piano di reclutamento. Il vincolo di liquidità diventa operativo e non si impone l’8,5%.
- **Drenaggio bancario dimostrato dentro il modello.** Gli interessi riducono i depositi non bancari e aumentano il patrimonio bancario a parità degli altri flussi. Il controllo ha incassato €2,134 miliardi in 600 mesi. La variante C restituisce €1,694 miliardi e nel caso standard muta la traiettoria. Non dimostra che la distribuzione produrrebbe gli stessi effetti in un’economia reale. Le repliche ridotte mostrano sensibilità al tasso di distribuzione.
- **Il credito pubblico interviene dopo le prime cadute.** Il calo occupazionale supera la soglia al mese 5; le prime cessazioni sono al mese 9 e la contrazione persistente della domanda inizia al 43. Il servizio del debito registra la prima insufficienza al 50, i trasferimenti vengono razionati dal 123 e il tetto è raggiunto al 231. La contrazione dell’output fisico oltre il 30% si registra al 368. Il razionamento e il tetto sono meccanismi distinti. I dati a flussi di cassa espongono spesa autorizzata, servizio dovuto e importi pagati. La competenza economica resta indisponibile.
- **Scorte e ricambio.** Una fixture con scorte complessive nulle dimostra lo stato assorbente della produzione senza intermedi. Il controllo non dimostra che questo limite, da solo, causi il collasso storico. La riserva maggiore cambia le disponibilità future e può anche sottrarre unità alla spesa corrente. L’impossibilità di rientrare dopo una cessazione è deterministica nel controllo; le nuove imprese finanziate sono fattibili nel test e nella combinazione standard. Il risultato combinato non identifica l’effetto isolato di B.
- **Correzioni numeriche.** Le scritture rifiutano importi fuori dominio e riduzioni che traboccherebbero. La correzione non cambia le scritture valide del baseline. R corregge il bias al ribasso introdotto dalla divisione intera dei prezzi, senza cambiare la regola storica utilizzata per riprodurre v0.4.0. R non elimina il deterioramento.
- **Contabilità nazionale.** La spesa è verificata in modo indipendente dal lato dell’output mediante batch monetari per consumi, imposte e investimenti, più differenza fisica delle scorte. Il surplus del lato reddito rimane residuale. Nuovi prestiti, rimborsi, interessi, stralci e trasferimenti restano fuori dal PIL. Caso manuale e invarianti automatizzati verificano classificazione e quadrature, senza validazione empirica.

Il PIL del primo anno storico è **€666,36 milioni** contro il riferimento ipotetico di €3 miliardi. Il tetto a lavoro, capitale, materiali e capacità produttiva si traduce in 31.154.276 unità prodotte al prezzo del bene composito; il valore aggiunto sottrae gli intermedi e il settore pubblico è valutato al costo diretto. Le ipotesi delle retribuzioni, della produttività e del prezzo di base sono leve da identificare prima di calibrare. Il confronto fra soli totali non permette di identificare separatamente queste leve.

## Fonti di riferimento

[Manifest di acquisizione](stabilitas-sources/manifest.json): serie UE-27 2022–2024 per conti nazionali, occupazione, salari, consumi, prezzi, imprese, debito pubblico e credito. Il manifest registra URL, filtri, unità, data, licenza, hash e limiti. 2022–2023 sono candidati per futura stima; 2024 è riservato al confronto. Nessuna stima è stata applicata. Eurostat misura economie effettive e rapporti settoriali diversi da Nova. [ESA 2010](https://ec.europa.eu/eurostat/web/esa-2010) · [SNA 2025](https://unstats.un.org/unsd/nationalaccount/sna2025.asp).

## Ripetere la prova

Dalla directory `simulation` con le dipendenze fissate:

```sh
python -m demos.cli generate runs/demos --seed 20261122
python -m oikonomia.diagnostics runs/stabilitas --snapshot runs/demos --workers 4
```

Usare un ambiente separato da cPanel. Solo gli aggregati e il checksum entrano nel portale. Python e PHP hanno test di integrità, casi deterministici, regressione, replay, isolamento e accessibilità. Methodos, Documento fondativo, Costituzione e aggregati originali rimangono invariati. Nessun Polis Index o governo AI.

## Riscontri quantitativi

Una prova aggiuntiva di **un solo mese** con il profilo standard e il fattore A mantiene i 4.689 titolari identificati in attività con rapporti di lavoro presso la propria impresa. Il tasso a fine mese è **8,664548%** contro **18,010511%** del controllo, senza modificare altri parametri. Il dato dimostra il meccanismo della discontinuità iniziale nel modello. Non fissa il tasso futuro e non costituisce una prova standard di 600 mesi.

| Prova standard | PIL anno 1, milioni EUR | PIL anno 50, milioni EUR | Disoccupazione finale % | Imprese attive finali | Ingressi |
| --- | ---: | ---: | ---: | ---: | ---: |
| Controllo | 666,36 | 25,89 | 93,44 | 205 | 0 |
| R | 666,89 | 49,44 | 94,44 | 225 | 0 |
| C | 665,05 | 238,67 | 40,84 | 553 | 0 |
| B+C+E | 663,46 | 249,43 | 39,80 | 639 | 296 |
| D | 666,36 | 50,44 | 97,35 | 299 | 0 |

D anticipa l’insufficienza nei trasferimenti dal mese 123 al mese 84, ma tocca il proprio tetto al mese 257 perché cambia la dinamica delle erogazioni e del rimborso. Il PIL dell’ultimo anno aumenta mentre la disoccupazione peggiora. Un solo indicatore non riassume la fragilità. Nelle tre prove ridotte il limite D non è vincolante e la differenza osservata è zero.

Nelle tre repliche ridotte, la mediana degli scarti accoppiati del PIL degli ultimi 12 mesi è +€269.652 per C, con intervallo min–max da +€110.544 a +€771.518. La variante C25 ha mediana +€138.007 e intervallo da −€277.904 a +€278.571. Le combinazioni possono dare segno diverso fra scale. Le statistiche sono descrittive e non consentono inferenza probabilistica. Per il credito Eurostat le dimensioni consolidato e non consolidato sono conservate separatamente nella risposta ufficiale; non devono essere sommate.

Le nuove impronte e le prestazioni per prova sono nella [traccia aggregata verificabile](../content/statistics/stabilitas.json). Gli export non contengono ID di cittadini, aziende o scritture individuali.

Nell’audit strumentato, il primo nucleo al limite di credito a fine mese appare al mese 3 e la prima impresa al mese 26. Il confronto per settori distingue imprese attive e produzione fisica. Le cinque prove standard finali hanno richiesto 169,80–193,97 secondi di parete l’una a concorrenza cinque, con picco massimo di 110.984 KiB RSS per processo. Questi tempi includono contesa delle risorse e strumentazione, mentre il baseline dal tag storico è stato misurato separatamente.
