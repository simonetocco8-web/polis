# Stabilitas · Audit preliminare del tag v0.4.0

Audit eseguito prima di introdurre le regole Stabilitas. Sono stati esaminati motore, migrazione Demos, scrutinio Methodos, lavoro, produzione, mercati, famiglie, banca, Tesoro, contabilità nazionale, giornale, configurazione e due documenti tecnici Oikonomia.

## Difetti dimostrati

- Il giornale accetta quattro gambe positive da 2^62 centesimi contro zero. La riduzione NumPy a 64 bit trabocca a zero prima del confronto. Non è stato osservato un importo di questo ordine nel baseline. È un difetto di validazione, privo di evidenza come causa del collasso storico.
- L’arrotondamento con divisione intera nell’aggiornamento prezzi usa il pavimento del rapporto con segno. Un lieve eccesso di offerta può produrre −1 punto base, mentre uno squilibrio positivo speculare produce 0. Il difetto è numerico. Il suo peso aggregato richiede una prova separata.
- L’identità del PIL per reddito si chiude per costruzione perché il surplus è residuo. La documentazione storica è corretta su questo punto. L’identità non è una stima indipendente del reddito.

## Limiti strutturali

Il primo passo trasforma tutti i 4.689 autonomi Demos in cercatori e blocca il matching. 4.677 di loro risultano disoccupati dopo la demografia. La forza lavoro passa da 50.076 a 50.043, la disoccupazione da 4.256 a 9.013 persone e nessun dipendente privato di apertura si ritrova disoccupato al mese uno. La discontinuità è una conseguenza riproducibile delle regole dichiarate, non un errore di conteggio.

Le imprese non possono entrare dopo una cessazione. La banca accumula interessi al netto delle perdite, senza distribuzioni o costi. Il Tesoro opera per cassa e raziona pagamenti. Il mercato è a bene unico. La produzione richiede scorte pregresse e la configurazione a zero scorte totali non può rigenerare intermedi. La disoccupazione cambia endogenamente dopo l’apertura.

## Ipotesi da sottoporre a prova

Il drenaggio monetario bancario può amplificare la scarsa liquidità delle imprese. Il vincolo di scorte può generare una retroazione fra produzione, reddito, domanda e assunzioni. Il tetto fiscale potrebbe intensificare una crisi già in atto. L’assenza di ricambio riduce monotonamente le imprese attive e può impedire il recupero. L’effetto e la sua dimensione dipendono dalla configurazione.

## Scelte normative e progettuali

Limiti e costo del credito, distribuzione dell’utile bancario, continuità del reddito per autonomi, regola di ingresso e riserva di intermedi richiedono una motivazione indipendente. I valori sperimentali sono dichiarati e non calibrati sul PIL obiettivo. Il margine di arbitrio resta parte dell’interpretazione.
