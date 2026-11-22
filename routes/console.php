<?php

use App\Documents\Library;
use App\Research\Methodos;
use Illuminate\Support\Facades\Artisan;

Artisan::command('documents:validate', function (Library $library): void {
    $count = $library->validate();
    $this->info("Versioni validate: {$count}");
})->purpose('Controlla metadati, integrità e struttura dei documenti');

Artisan::command('research:validate', function (Methodos $methodos): void {
    $config = $methodos->load();
    $this->info($methodos->ready($config) ? 'Configurazione congelata e completa' : 'Configurazione preliminare: conferma non autorizzata');
})->purpose('Valida la configurazione sperimentale versionata');
