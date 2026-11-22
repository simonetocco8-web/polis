# Gestione dei contenuti

- `content/editorial/it/` contiene le pagine istituzionali, con estratti localizzati in `lang/it/pages.php`.
- `content/journal/it/` conserva le voci Markdown. In `content/metadata/journal.json` registrare slug univoco, data, titolo, descrizione, autore dichiarato, fase, release e categorie.
- Le categorie previste sono filosofia, costituzione, metodologia, sviluppo software, simulazione, risultati, revisioni e decisioni AI. Collegare documenti e decisioni nel testo della voce quando pertinenti.
- `content/documents/{lingua}/{id}/{versione}.md` conserva i documenti acquisiti. Vedere [importazione](import-original-documents.md).

Usare link relativi alla radice per le pagine del portale. Indicare secondo il caso se il contenuto proviene dal promotore, da un modello AI, da una modifica umana o da una fonte esterna. Registrare soltanto eventi documentati. Per dati illustrativi, riportare l’origine e lo stato preliminare direttamente vicino ai valori.
