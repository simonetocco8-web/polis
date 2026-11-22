<?php

use App\Documents\Library;
use Illuminate\Support\Facades\Artisan;

Artisan::command('documents:validate', function (Library $library): void {
    $count = $library->validate();
    $this->info("Versioni validate: {$count}");
})->purpose('Controlla metadati, integrità e struttura dei documenti');
