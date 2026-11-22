# Importare i documenti originali

La versione iniziale attende i testi integrali del Documento fondativo e della Costituzione della Repubblica di Nova, entrambi v1.0 di novembre 2026.

1. Acquisire i file dal promotore e verificare fonte, testo, data e diritti. Se l’originale è in un altro formato, preservare il file acquisito e documentare una trascrizione Markdown confrontata riga per riga. Conservare i byte del Markdown verificato.
2. Salvare `content/documents/it/manifesto/1.0.md` e `content/documents/it/costituzione/1.0.md`. Non aggiungere testo o cambiare disposizioni.
3. Calcolare `sha256sum` per ciascun file. Impostare `current` a `"1.0"` e aggiungere un record sotto `versions["1.0"]` in `content/metadata/documents.json`.

```json
{
  "date": "AAAA-MM-GG",
  "author": "autore dichiarato dopo verifica",
  "status": "stato editoriale verificato",
  "sha256": "64 caratteri esadecimali minuscoli",
  "provenance": "riferimento di acquisizione pubblico",
  "changes": "Prima pubblicazione del testo acquisito",
  "previous": null,
  "original_language": "it",
  "structure": { "articles": 71, "titles": 12 }
}
```

L’esempio riporta segnaposto da sostituire. `structure` riguarda solo la Costituzione. Nella versione originaria sono richiesti intestazioni Markdown di primo livello strutturale per Preambolo, 12 Titoli numerati, 71 Articoli in ordine e Dichiarazione conclusiva. I link frammento devono puntare agli ID riconosciuti. Gli articoli ricevono ancora `#articolo-N`, il preambolo `#preambolo` e la dichiarazione `#dichiarazione-conclusiva`. Verificare la compatibilità con le intestazioni effettive. Adattare il parser se necessario e mantenere fedele il testo acquisito.

Eseguire la validazione documentale, i test e la verifica visiva della struttura, degli articoli e di eventuali riferimenti. Il browser può produrre un PDF di stampa. Un PDF ufficiale richiede acquisizione o generazione verificata e metadati propri prima di essere offerto in download.
