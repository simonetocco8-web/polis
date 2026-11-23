<?php

namespace Tests\Feature;

use App\Http\Controllers\EconomyController;
use App\Statistics\Oikonomia;
use RuntimeException;
use Tests\TestCase;

final class OikonomiaTest extends TestCase
{
    public function test_economy_pages_and_aggregate_downloads(): void
    {
        $this->get('/nova/economia')->assertOk()->assertSee('Prova tecnica con economia chiusa');
        foreach (array_keys(EconomyController::PAGES) as $section) {
            $this->get('/nova/economia/'.$section)->assertOk()->assertSee('600 mesi')->assertSee('Scarica CSV aggregato');
        }
        $response = $this->get('/nova/economia/statistiche.json')->assertOk()->assertDownload('nova-oikonomia.json');
        $data = json_decode(file_get_contents($response->baseResponse->getFile()->getPathname()), true);
        self::assertCount(600, $data['rows']);
        self::assertNull($data['polis_index']);
        self::assertArrayNotHasKey('people', $data);
        $this->get('/nova/economia/statistiche.csv')->assertOk()->assertDownload('nova-oikonomia.csv');
        $this->get('/nova/economia/non-esiste')->assertNotFound();
    }

    public function test_rejects_inconsistent_accounting(): void
    {
        $validator = app(Oikonomia::class);
        $data = $validator->load();
        $data['rows'][0]['gdp_income']++;
        $this->expectException(RuntimeException::class);
        $validator->validate($data);
    }
}
