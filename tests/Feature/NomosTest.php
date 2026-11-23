<?php

namespace Tests\Feature;

use App\Http\Controllers\InstitutionController;
use App\Statistics\Nomos;
use Illuminate\Support\Facades\Artisan;
use Tests\TestCase;

final class NomosTest extends TestCase
{
    public function test_institutional_pages_and_exports_are_available_without_a_database(): void
    {
        $this->get('/nova')->assertSee('Repubblica di Nova — Istituzioni');
        foreach (array_keys(InstitutionController::SECTIONS) as $section) {
            $this->get('/nova/istituzioni/'.$section)->assertOk();
        }
        $this->get('/nova/istituzioni')->assertOk()->assertSee('Difensore civico');
        $this->get('/nova/istituzioni/inesistente')->assertNotFound();
        $this->post('/nova/istituzioni')->assertMethodNotAllowed();
        self::assertSame(0, Artisan::call('nomos:validate'));
        $checksum = app(Nomos::class)->checksum();
        $this->get('/nova/istituzioni/statistiche.json')->assertOk()->assertHeader('X-Nomos-Export-SHA256', $checksum);
        $csv = $this->get('/nova/istituzioni/statistiche.csv')->assertOk();
        $this->assertStringContainsString('pending_review,1', $csv->streamedContent());
    }
}
