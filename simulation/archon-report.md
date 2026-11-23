# Archon v0.6.0 · Rapporto di verifica

## Livello 1 · Fixture deterministica

Il laboratorio ha eseguito quattro decisioni nello scenario B, profilo smoke e singola replica. Due proposte sono risultate formalmente valide, nessuna invalida, una autorizzata proceduralmente e una rinviata all'esame indipendente. Nessun atto è stato respinto o sospeso nel fascicolo pubblico. Le altre decisioni sono un'astensione e un esito di informazioni insufficienti. La proposta autorizzata ha portato l'aliquota sul reddito a 1525 punti base per un mese. Il secondo atto richiedeva valutazione sostanziale e il motore non lo ha applicato.

| Mese simulato | Gettito conosciuto prima | Gettito osservato alla chiusura |
| --- | ---: | ---: |
| 1 | Non disponibile | 48.523,26 EUR |
| 2 | 48.523,26 EUR | 51.813,24 EUR |
| 3 | 51.813,24 EUR | 48.624,83 EUR |
| 4 | 48.624,83 EUR | 45.489,74 EUR |

Il confronto cronologico non identifica un effetto causale. I valori sono centesimi nominali del simulatore, senza calibrazione. Il replay dell'archivio verifica le decisioni, l'integrità della catena e le corrispondenze delle proposte. La prova ricostruisce il fascicolo statico byte per byte dal registro giuridico e dal percorso offline. La testa Nomos è 5dd11d9fbdda5295460980333e0ec6bd42be05d135f301a43ee65a33476978bc. La proiezione Archon nomina esplicitamente il provider fixture-1.0 e indica zero chiamate, token e costi API. I tempi registrati in archivio per il provider offline includono controlli locali. Non misurano latenza di un modello reale.

La suite verifica limiti, dati ritardati, assenza di seed, iniezione nell'output, inaccessibilità delle operazioni del motore e della Corte, rifiuto dell'universo estraneo, revoca durante la generazione, errori, budget, duplicazione, scadenza, recupero di una ricevuta e rilevamento dell'alterazione del registro. Il portale accetta il digest della proiezione pubblicata e respinge qualunque sostituzione che dichiari una prova reale senza un aggiornamento esplicito della provenienza. Gli export pubblicati contengono esclusivamente la fixture.

## Livello 2 · Responses API e prova reale

Il provider è integrato con il client ufficiale OpenAI Python 2.15.0. Un test con trasporto in memoria verifica la richiesta alla Responses API, lo schema di risposta, l'assenza di strumenti, il modello configurabile, store=false e la lettura della telemetria. Nessuna chiamata pagata, modello reale testato, risposta reale, costo o token effettivo. Rimangono da validare con una prova autorizzata compatibilità del modello scelto, autenticazione, esiti decisionali, tempi e costi effettivi.

## Livello 3 · Orizzonte e limiti

Il percorso a passi mensili usa l'orizzonte Nomos fino al mese 600. Questa release non ha eseguito una prova Archon di 600 mesi. I limiti del percorso live impediscono l'avvio implicito di un ciclo esteso. Il sistema operativo e l'operatore della simulazione rientrano nella base fidata. I budget sono stime basate su tariffe e token, non un limite di fatturazione imposto al servizio. Un'ancora verificata esternamente è necessaria contro la riscrittura totale dell'archivio. Gli esiti restano tecnici ed esplorativi. Nessun Polis Index, confronto fra regimi o inferenza sulla superiorità dell'AI. [Specifiche e istruzioni](../docs/architecture/archon.md)
