# Rapporto Demos · Profilo standard

## Fonti e separazione dei periodi

UE-27 nella composizione EU27_2020. Il 2022 è il riferimento comune per cui l’estrazione contiene sia popolazione per singola età e sesso sia tavole di mortalità omogenee. Nella stessa estrazione le celle 85–99 risultano assenti nel 2019 e nel 2020. Il 2023 è riservato al confronto trasversale fuori campione. Le fonti UE-27 aggregano conteggi di persone, quindi gli Stati non hanno peso uniforme. Si campiona direttamente dalla distribuzione congiunta sesso×età. Qx è quello pubblicato per UE-27 per sesso ed età, senza media aritmetica dei Paesi. Il [manifest di acquisizione](sources/manifest.json) registra URL, data, disponibilità, definizioni, licenza, hash e trasformazioni. I due snapshot JSON sono disponibili per la ripetizione offline.

| Serie | Esito |
| --- | --- |
| Eurostat demo_pjan | Acquisita. Distribuzione iniziale età/sesso 2022 e confronto 2023. |
| Eurostat demo_mlifetable | Acquisita. Qx 2022 per sesso ed età esatta, estensione sopra 94 anni ipotizzata. |
| EU-LFS e EU-SILC | Candidate per lavoro, istruzione, famiglie e reddito. Nessuna serie armonizzata acquisita per Demos. |
| Fertilità e migrazioni Eurostat | Candidate per età, tassi, composizione e flussi. Parametri Demos ipotetici. |
| Eurostat sbs_sc_ovw | Candidata per dimensione e settore. Da armonizzare con copertura di aziende pubbliche, autonome e agricole. |
| ISTAT | Comparatore nazionale candidato, non usato per sostituire o pesare UE-27. |
| OCSE, OMS e UN DESA | Candidate per confronto esterno e stress test. Nessuna serie usata. |

Il campionamento condizionato e le coabitazioni vincolate sono adatti alla struttura di Demos. Una sintesi IPF per famiglie, redditi e lavoro richiederebbe margini compatibili e tabelle aggregate congiunte da acquisire. L'IPF non è applicato. Correlazioni tra salute ed età, istruzione e occupazione, reddito e posizione occupazionale e tra preferenze sono assunzioni. Le fonti aggregate adottate non le identificano.

## Risultati effettivi

Seed dimostrativo `20261122`. Il profilo ha generato **100.000** residenti, **48.212** nuclei residenti e **5.000** imprese. Le classi F e M contano rispettivamente 51.240 e 48.760 residenti. Età media 43,64 anni. Forza lavoro 50.076, di cui 4.256 disoccupati. L’8,50% arrotondato rispecchia la quota imposta. Gli altri target macro di Methodos non sono stimati.

La distanza di variazione totale sulle 202 celle sesso×età è **1,521%** rispetto al 2022 di stima e **1,669%** rispetto al 2023 fuori campione. `demos.cli compare` riproduce quote target e ottenute e scostamento per cella. Il confronto non valida le traiettorie, le distribuzioni familiari o l’efficacia predittiva del modello. Le probabilità empiriche di mortalità non sono state valutate su tassi di mortalità fuori campione in questa release.

Al mese 600 la prova tecnica conta **74.383** residenti dopo 29.632 nascite, 66.759 morti, 26.885 ingressi e 15.375 uscite. Il bilancio è stato verificato a ogni passo. Questa traiettoria non è una previsione. In particolare non simula variazioni di fertilità, economia, mobilità familiare o miglioramenti della mortalità.

| Misura tecnica | Risultato |
| --- | --- |
| SHA-256 canonico iniziale | `4cb3e30dbc6800e56b211277145e22d74815fe7cf5464a21a726c57fef43df0c` |
| SHA-256 canonico al mese 600 | `743cc44d209d7a0411c56147203ba4253b09c9bb242529222f95b696238631c5` |
| Generazione e salvataggio iniziali | 1,10 s; RSS massimo 51.576 KiB |
| Esecuzione 600 mesi con log e checkpoint finale | 53,85 s; RSS massimo 76.452 KiB |
| Dimensioni | NPZ iniziale 3.299.912 byte; finale 4.141.291 byte; log 1.512.606 byte |

Tempi di parete su ambiente cloud Linux x86-64, Python 3.12.14, NumPy 2.3.5. RSS del processo figlio incluso il runtime. Il profilo Demos resta a calibrazione parziale e Methodos mantiene il proprio stato preliminare.
