# Architettura del portale

Le route Laravel raggruppano pagine editoriali, biblioteca, visualizzatore e diario. Blade rende HTML sul server. Tailwind e Vite compilano asset statici. Il JavaScript abilita solo stampa e appunti. Il menu usa l’elemento HTML details.

Le pagine editoriali e il diario leggono Markdown dal repository. La biblioteca usa un manifest per lingua. Prima di leggere un documento controlla la presenza della versione e verifica percorso, codifica e SHA-256. CommonMark rimuove HTML grezzo e disabilita URL pericolosi. Il parser costituzionale costruisce indice e articoli a partire dallo stesso albero Markdown.

`config/polis.php` centralizza identità, stato e disponibilità delle funzionalità. Le pagine di Simulatore e Osservatorio illustrano funzionalità future. Porta pubblica in sola lettura e cache su file consentono l’esecuzione senza database. Le route non avviano sessioni.

Per una versione inglese preparare cataloghi `lang/en/`, contenuti `content/editorial/en/`, documenti per lingua e strategia URL/localizzazione prima di esporre un selettore. La lingua originale e i metadati di traduzione sono separati dalla versione.
