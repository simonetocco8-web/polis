<?php

use App\Documents\Library;
use App\Research\Methodos;
use App\Statistics\Demos;
use Illuminate\Support\Facades\Artisan;

Artisan::command('documents:validate', function (Library $library): void {
    $count = $library->validate();
    $this->info("Versioni validate: {$count}");
})->purpose('Controlla metadati, integrità e struttura dei documenti');

Artisan::command('research:validate', function (Methodos $methodos): void {
    $config = $methodos->load();
    $this->info($methodos->ready($config) ? 'Configurazione congelata e completa' : 'Configurazione preliminare: conferma non autorizzata');
})->purpose('Valida la configurazione sperimentale versionata');

Artisan::command('demos:validate', function (Demos $demos): void {
    $snapshot = $demos->load();
    $this->info('Esportazione Demos verificata: '.$snapshot['snapshot_sha256']);
})->purpose('Controlla metadata e riconciliazione degli aggregati Demos');
