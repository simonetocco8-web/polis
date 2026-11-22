# Versionamento e rilascio documentale

Ogni nuova versione ha un file e un record di manifest propri. I record precedenti restano invariati. Una traduzione usa la stessa versione documentale sotto un’altra lingua e include data, autore o modello e stato di revisione.

1. Verificare provenienza, data e diritti di pubblicazione.
2. Aggiungere il file Markdown e il record con SHA-256, versione precedente e descrizione delle modifiche.
3. Eseguire `php artisan documents:validate` e `php scripts/check-document-history.php <SHA-base>`.
4. Controllare la pagina della versione e scaricare il Markdown per confrontarne l’hash.
5. Creare un tag annotato, preferibilmente firmato, e una release Git sul commit verificato. Allegare alla release `content/metadata/documents.json` e comunicare tag e hash attraverso un canale attendibile.

SHA-256 permette di confrontare i byte con il manifest di riferimento. La fiducia nella provenienza dipende dalla catena di acquisizione e dal riferimento usato. Le protezioni di branch, l’approvazione delle modifiche, le firme e la protezione dei tag sono attività amministrative da configurare separatamente.
