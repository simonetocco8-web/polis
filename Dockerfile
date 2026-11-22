FROM node:24-bookworm-slim AS assets
WORKDIR /build
COPY package.json package-lock.json ./
RUN --mount=type=secret,id=build_ca \
    if [ -s /run/secrets/build_ca ]; then export NODE_EXTRA_CA_CERTS=/run/secrets/build_ca; fi \
    && npm ci
COPY vite.config.js ./
COPY resources resources
RUN npm run build

FROM php:8.4-cli-bookworm
COPY --from=composer:2 /usr/bin/composer /usr/local/bin/composer
RUN apt-get update \
    && apt-get install -y --no-install-recommends libonig-dev unzip \
    && docker-php-ext-install -j2 mbstring \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY . .
COPY --from=assets /build/public/build public/build
ARG COMPOSER_USE_CODELOAD=0
RUN --mount=type=secret,id=build_ca \
    if [ -s /run/secrets/build_ca ]; then export COMPOSER_CAFILE=/run/secrets/build_ca; fi \
    && if [ "$COMPOSER_USE_CODELOAD" = 1 ]; then \
        composer_tmp="$(mktemp -d)" \
        && trap 'rm -rf "$composer_tmp"' EXIT \
        && php scripts/composer-codeload-lock.php "$composer_tmp" \
        && export COMPOSER="$composer_tmp/composer.json"; \
    fi \
    && composer install --no-interaction --prefer-dist
ENV APP_ENV=local APP_DEBUG=false APP_URL=http://localhost:8000
EXPOSE 8000
CMD ["php", "-S", "0.0.0.0:8000", "-t", "public"]
