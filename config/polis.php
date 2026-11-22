<?php

return [
    'name' => 'POLIS AI',
    'title' => 'Il filosofo-re artificiale',
    'international_title' => 'The Artificial Philosopher-King',
    'description' => 'Dalla Repubblica di Platone alla sperimentazione informatica del governo algoritmico.',
    'payoff' => 'Philosophy. Intelligence. Governance.',
    'founded' => 2026,
    'status' => 'Fase fondativa e definizione metodologica',
    'version' => '0.1.1',
    'features' => ['library' => true, 'journal' => true, 'simulation' => false, 'observatory' => false, 'governance' => false],
    'indexable' => env('APP_ENV') === 'production' && env('POLIS_INDEXABLE', false) && str_starts_with((string) env('APP_URL'), 'https://'),
    'content' => base_path('content'),
];
