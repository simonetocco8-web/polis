<?php

namespace Tests\Feature;

use App\Http\Controllers\ExperimentumController;
use App\Statistics\Experimentum;
use Illuminate\Support\Facades\Artisan;
use Tests\TestCase;

final class ExperimentumTest extends TestCase
{
    public function test_technical_fixture_is_read_only_and_comparison_is_blocked(): void
    {
        $this->get('/ricerca/esperimenti')->assertOk()->assertSee('Pilota tecnico offline');
        foreach (array_keys(ExperimentumController::PAGES) as $section) {
            $this->get('/ricerca/esperimenti/'.$section)->assertOk();
        }
        $this->get('/ricerca/esperimenti/confronti')->assertSee('Non ammissibile');
        $this->post('/ricerca/esperimenti')->assertMethodNotAllowed();
        $this->get('/ricerca/esperimenti/statistiche.json')->assertOk()->assertHeader('X-Experimentum-Export-SHA256', Experimentum::HASH);
        $csv = $this->get('/ricerca/esperimenti/statistiche.csv')->assertOk()->streamedContent();
        self::assertStringContainsString('1,gdp,3,0', $csv);
        self::assertSame(0, Artisan::call('experimentum:validate'));
    }
}
