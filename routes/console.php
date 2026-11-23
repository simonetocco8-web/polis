<?php

use App\Documents\Library;
use App\Research\Methodos;
use App\Statistics\Archon;
use App\Statistics\Demos;
use App\Statistics\Nomos;
use App\Statistics\Oikonomia;
use App\Statistics\Stabilitas;
use App\Statistics\Theoria;
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

Artisan::command('oikonomia:validate', function (Oikonomia $economy): void {
    $data = $economy->load();
    $this->info('Esportazione Oikonomia verificata: '.$data['months'].' mesi · '.$data['final_sha256']);
})->purpose('Verifica hash, provenienza e riconciliazione economica');

Artisan::command('stabilitas:validate', function (Stabilitas $audit): void {
    $data = $audit->load();
    $this->info('Stabilitas: '.count($data['standard']).' prove standard e '.count($data['exploratory']).' corse esplorative verificate');
})->purpose('Verifica provenienza e riconciliazione dell’audit Stabilitas');

Artisan::command('nomos:validate', function (Nomos $nomos): void {
    $data = $nomos->load();
    $this->info('Nomos: '.count($data['events']).' eventi verificati · '.$nomos->checksum());
})->purpose('Verifica versione, provenienza e coerenza dell’esportazione Nomos');

Artisan::command('archon:validate', function (Archon $archon): void {
    $data = $archon->load();
    $this->info('Archon: '.count($data['decisions']).' decisioni offline verificate · '.$archon->checksum());
})->purpose('Valida il fascicolo statico e la provenienza offline di Archon');

Artisan::command('theoria:validate', function (Theoria $theoria): void {
    $data = $theoria->load();
    $this->info('Theoria: '.count($data['cases']).' casi offline verificati');
})->purpose('Valida il fascicolo pubblico di Theoria');
