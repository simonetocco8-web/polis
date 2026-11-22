<?php

return [
    'name' => env('APP_NAME', 'POLIS AI'),
    'env' => env('APP_ENV', 'production'),
    'debug' => env('APP_ENV', 'production') !== 'production' && env('APP_DEBUG', false),
    'url' => env('APP_URL', 'http://localhost:8000'),
    'timezone' => 'Europe/Rome',
    'locale' => env('APP_LOCALE', 'it'),
    'fallback_locale' => 'it',
    'key' => env('APP_KEY'),
    'cipher' => 'AES-256-CBC',
];
