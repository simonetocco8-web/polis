<?php

namespace Tests\Feature;

use App\Http\Controllers\TheoriaController;
use App\Statistics\Theoria;
use Illuminate\Support\Facades\Artisan;
use Tests\TestCase;

final class TheoriaTest extends TestCase
{
    public function test_public_exports_and_pages_only_include_the_offline_fixture(): void
    {
        $this->get('/nova/osservatorio')->assertOk()->assertSee('Fixture offline pubblica');
        foreach (array_keys(TheoriaController::PAGES) as $section) {
            $this->get('/nova/osservatorio/'.$section)->assertOk();
        }
        $this->post('/nova/osservatorio')->assertMethodNotAllowed();
        $this->get('/nova/osservatorio/statistiche.json')->assertOk()->assertHeader('X-Theoria-Export-SHA256', Theoria::HASH);
        $csv = $this->get('/nova/osservatorio/statistiche.csv')->assertOk()->streamedContent();
        self::assertStringContainsString('fixture-1,B,1,INSUFFICIENT_INFORMATION', $csv);
        self::assertStringNotContainsString('archon-live', $csv);
        self::assertSame(0, Artisan::call('theoria:validate'));
    }
}
