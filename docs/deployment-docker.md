# Docker per lo sviluppo

```sh
docker build -t polis-ai:dev .
docker run --rm -p 127.0.0.1:8000:8000 polis-ai:dev
docker run --rm polis-ai:dev composer test
```

Il build usa Node 24 per Vite e PHP 8.4 con Composer per i test e il server. L’immagine copia il manifest degli asset e dipendenze risolte dai lockfile. Ricostruire dopo modifiche. La porta di esempio è limitata all’host e il server PHP integrato è per sviluppo.

Se la rete usa una CA privata, passa a BuildKit il bundle PEM attendibile già configurato sul computer. Il mount serve soltanto a verificare TLS durante l’installazione e il certificato resta fuori dall’immagine.

```sh
docker build --secret "id=build_ca,src=${SSL_CERT_FILE:?}" -t polis-ai:dev .
```

Se la rete autorizza `codeload.github.com` ma blocca gli archivi di `api.github.com`, aggiungi `--build-arg COMPOSER_USE_CODELOAD=1`. La build usa un lockfile temporaneo che conserva versioni e riferimenti dei commit. Il lockfile del repository resta il riferimento per l’installazione standard.
