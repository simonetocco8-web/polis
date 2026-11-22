# Limiti e requisiti di pubblicazione

- Acquisire, verificare e autorizzare la pubblicazione dei due originali, inclusi la data esatta, il formato e i diritti. Il parser è testato su fixture sintetiche.
- Definire dominio, impostazioni HTTPS, hosting, responsabilità, recapiti per privacy, accessibilità e sicurezza e conservazione dei log.
- Completare la verifica WCAG con tecnologie assistive e con i testi definitivi.
- Verificare il deployment cPanel nell’infrastruttura scelta. La build Docker e la risposta HTTP del container sono state verificate in cloud.
- GitHub Actions deve eseguire la CI sul repository remoto. In cloud l’audit npm è riuscito e l’audit Composer ha ricevuto un 403 dal proxy per Packagist. Ripetere l’audit PHP quando il dominio è autorizzato.
- Inglese, PDF ufficiali, dashboard, motore di simulazione, governo e osservatorio dati sono previsti per fasi successive.
