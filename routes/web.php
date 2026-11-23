<?php

use App\Http\Controllers\AtlasController;
use App\Http\Controllers\EconomyController;
use App\Http\Controllers\LibraryController;
use App\Http\Controllers\MethodController;
use App\Http\Controllers\PortalController;
use Illuminate\Support\Facades\Route;

Route::pattern('documento', '[a-z][a-z0-9-]*');
Route::pattern('slug', '[a-z][a-z0-9-]*');
Route::pattern('versione', '[0-9]+\.[0-9]+(?:\.[0-9]+)?');
Route::pattern('numero', '[1-9][0-9]{0,5}');

Route::get('/', [PortalController::class, 'home'])->name('home');
foreach (PortalController::PAGES as $name => $path) {
    Route::get($path, [PortalController::class, 'page'])->name($name);
}
Route::get('/metodologia/scenari', MethodController::class)->name('method.scenarios');
Route::get('/metodologia/indicatori', MethodController::class)->name('method.indicators');
Route::get('/metodologia/polis-index', MethodController::class)->name('method.index');
Route::get('/nova/statistiche.{format}', [AtlasController::class, 'download'])->where('format', 'csv|json')->name('nova.statistics');
Route::get('/nova/economia', [EconomyController::class, 'show'])->name('nova.economy');
Route::get('/nova/economia/statistiche.{format}', [EconomyController::class, 'download'])->where('format', 'csv|json')->name('nova.economy.export');
Route::get('/nova/economia/{section}', [EconomyController::class, 'show'])->name('nova.economy.section');
Route::get('/nova/{section}', [AtlasController::class, 'show'])->name('nova.atlas');
Route::get('/costituzione', [LibraryController::class, 'constitution'])->name('constitution');
Route::get('/costituzione/articolo/{numero}', [LibraryController::class, 'article'])->name('constitution.article');
Route::get('/costituzione/versione/{versione}', [LibraryController::class, 'constitution'])->name('constitution.version');
Route::get('/costituzione/versione/{versione}/articolo/{numero}', [LibraryController::class, 'versionedArticle'])->name('constitution.article.version');
Route::get('/biblioteca', [LibraryController::class, 'index'])->name('library');
Route::get('/biblioteca/{documento}', [LibraryController::class, 'show'])->name('library.show');
Route::get('/biblioteca/{documento}/{versione}', [LibraryController::class, 'show'])->name('library.version');
Route::get('/biblioteca/{documento}/{versione}/markdown', [LibraryController::class, 'download'])->name('library.download');
Route::get('/diario', [PortalController::class, 'journal'])->name('journal');
Route::get('/diario/{slug}', [PortalController::class, 'journalEntry'])->name('journal.show');
Route::get('/sitemap.xml', [PortalController::class, 'sitemap'])->name('sitemap');
Route::get('/robots.txt', [PortalController::class, 'robots'])->name('robots');
