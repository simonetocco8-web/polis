# Rapporto tecnico Oikonomia v0.4.0

Profilo standard Demos UE-27, seed dimostrativo 20261122, 100.000 cittadini, 48.212 nuclei e 5.000 imprese all’apertura. Tutti i 600 mesi hanno superato identità finanziarie, delle scorte, del bilancio pubblico e del PIL. La corsa baseline è riproducibile. Gli aggregati sono una prova tecnica e non costituiscono una previsione o una valutazione empirica. Il profilo economico non è calibrato.

| Indicatore | Mese 1 | Mese 12 | Mese 600 |
| --- | ---: | ---: | ---: |
| PIL nominale mensile (EUR) | 62.045.152,00 | 60.835.090,67 | 3.916.339,08 |
| PIL reale mensile a base 2022 (EUR) | 62.045.152,00 | 62.031.680,13 | 9.076.104,47 |
| Mediana del reddito disponibile mensile per membro (EUR) | 766,17 | 420,00 | 0,00 |
| Gini del reddito tra nuclei | 0,411735 | 0,464697 | 0,956155 |
| Occupati a fine mese | 41.030 | 26.412 | 1.940 |
| Disoccupazione (% forza lavoro) | 18,01 | 47,04 | 93,44 |
| IPC del bene composito (base 100) | 100,00 | 97,76 | 43,14 |
| Inflazione mensile (%) | non disponibile | 0,69 | 1,68 |
| Saldo pubblico mensile (EUR) | −5.047.622,69 | −12.454.448,97 | 0,00 |
| Debito pubblico (EUR) | 31.625.000,00 | 128.375.835,88 | 1.500.000.000,00 |
| Depositi bancari totali (EUR) | 755.066.052,00 | 882.419.873,51 | 186.563.234,74 |
| Credito bancario totale (EUR) | 32.036.283,00 | 164.548.111,42 | 1.513.741.722,63 |
| Patrimonio netto bancario (EUR) | 10.165.030,00 | 15.323.036,91 | 2.060.373.286,89 |
| Imprese ancora attive | 5.000 | 4.988 | 205 |

Il PIL nominale del primo anno è 666.357.503,06 EUR, nell’ultimo anno 25.887.777,49 EUR. Il calo si sviluppa nel modello a bene unico, con imprese senza ricambio, scorte vincolanti, domanda e leva finanziaria, salari e trasferimenti razionati e tetto al credito pubblico. Al mese 600 il Tesoro ha cassa zero e arretrati sul servizio del debito. Il saldo del mese pari a zero è un saldo di cassa e coesiste con l’incapienza. Il rapporto debito/PIL mobile è 5794,24%. La banca resta sopra la soglia di chiusura del credito, anche per gli interessi riscossi nelle fasi precedenti e la semplificazione di riserve fisse. Il modello non simula ristrutturazione del debito pubblico o una risoluzione bancaria.

La povertà relativa è indisponibile quando la mediana è zero. Il modello registra 29.706 nuclei sotto il fabbisogno essenziale al mese 600. La disoccupazione di apertura Demos è l’8,50%; il primo mese include la ricerca di lavoro degli autonomi Demos, limiti di liquidità e rimappatura produttiva. Questi dati misurano una traiettoria tecnica e fortemente deteriorata. Non sono statistiche empiriche e non sono stati ritoccati per far convergere il risultato ai target Methodos.

## Stress tecnici, profilo standard, 12 mesi

Shock nei mesi 4–9. Stessa popolazione di apertura. Le differenze dipendono dai parametri e dalla risposta endogena; non si attribuisce un effetto di governo. Nella recessione, la minore spesa e la riduzione temporanea delle assunzioni cambiano anche i fabbisogni di credito. La disoccupazione al mese 12 più bassa del baseline non identifica un beneficio della recessione.

| Variante | PIL nominale annuo (EUR) | Disoccupazione mese 12 | Cessazioni |
| --- | ---: | ---: | ---: |
| Baseline | 666.357.503,06 | 47,04% | 12 |
| Recessione | 642.560.560,32 | 33,96% | 0 |
| Shock produttivo | 527.622.346,30 | 57,96% | 30 |
| Crisi di credito | 641.559.380,59 | 48,29% | 0 |

Il blocco programmato delle nuove erogazioni dura sei mesi. Nel test di shock produttivo la perdita creditizia mensile massima è 266.054,68 EUR. I tre stress e il profilo baseline hanno superato le identità mensili.

## Riproducibilità, prestazioni e limiti

| Artefatto | SHA-256 |
| --- | --- |
| Demos di origine | `4cb3e30dbc6800e56b211277145e22d74815fe7cf5464a21a726c57fef43df0c` |
| Stato economico di apertura | `d12de75af361ccf5fb46d1f972894b0068a6ac3f21273b710e128155a93e2313` |
| Stato economico al mese 600 | `f9aa3a372a02828eb612494f59403de2c06911b5a9e25373a980c1f0ecf2f6b2` |
| Catena finale del giornale | `9b7edd573070f37ece528a65bfae2b9f28d66dad7a5ed8ac1db32b63ab17f89e` |

Oikonomia ha eseguito e serializzato 600 mesi in 113,42 s, picco 99.484 KiB RSS, Python 3.12.14 e NumPy 2.3.5 su Linux x86-64. Checkpoint NPZ: 4.371.558 byte totali. Registro tecnico: 899.223 byte senza gambe individuali opzionali. L’architettura e le formule sono riportate nella [specifica](../docs/architecture/oikonomia.md).

Non sono disponibili un paniere multiprodotto, commercio estero operativo, bilanci aziendali civilistici, una banca centrale comportamentale, procedure complete di insolvenza, deprezzamento del capitale pubblico, lavoro autonomo come settore produttivo, rientri e successioni. Le misure di reddito e produttività sono limitate al perimetro simulato e le prove di sensibilità sono illustrative. Nessuna taratura economica è stata stimata. Methodos resta preliminare.
