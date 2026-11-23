<?php

namespace Tests\Feature;

use App\Http\Controllers\GovernorController;
use Illuminate\Support\Facades\Artisan;
use Tests\TestCase;

final class ArchonTest extends TestCase
{
    public function test_government_pages_and_offline_export_are_read_only(): void
    {
        $this->get('/nova/governo')->assertOk()->assertSee('Prova offline');
        foreach (array_keys(GovernorController::SECTIONS) as $section) {
            $this->get('/nova/governo/'.$section)->assertOk();
        }
        $this->post('/nova/governo')->assertMethodNotAllowed();
        $this->get('/nova/governo/statistiche.json')->assertOk()->assertHeader('X-Archon-Export-SHA256');
        $this->get('/nova/governo/statistiche.sha256')->assertOk();
        self::assertSame(0, Artisan::call('archon:validate'));
    }
}
