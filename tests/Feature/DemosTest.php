<?php

namespace Tests\Feature;

use App\Http\Controllers\AtlasController;
use App\Statistics\Demos;
use RuntimeException;
use Tests\TestCase;

final class DemosTest extends TestCase
{
    public function test_atlas_and_downloads_expose_only_validated_aggregates(): void
    {
        foreach (array_keys(AtlasController::PAGES) as $section) {
            $this->get('/nova/'.$section)->assertOk()->assertSee('100.000')->assertSee('5.000')
                ->assertSee('Popolazione sintetica')->assertSee('Calibrazione parziale');
        }
        $this->get('/nova/generazione')->assertSee('Il Polis Index resta indisponibile.');
        $this->get('/nova/statistiche.json')->assertOk()
            ->assertJsonPath('totals.population', 100000)->assertJsonPath('totals.firms', 5000)
            ->assertJsonPath('polis_index', null)->assertJsonMissingPath('people');
        $response = $this->get('/nova/statistiche.csv')->assertOk()->assertDownload('nova-demos.csv');
        $this->assertStringContainsString('gruppo,categoria,valore,unita', $response->streamedContent());
        $this->get('/nova/non-esiste')->assertNotFound();
    }

    public function test_invalid_exports_fail_closed(): void
    {
        $demos = app(Demos::class);
        $data = $demos->load();
        $data['groups']['age']['100+']++;
        $this->expectException(RuntimeException::class);
        $demos->validate($data);
    }
}
