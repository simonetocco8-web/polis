<?php

namespace Tests\Feature;

use App\Statistics\Stabilitas;
use RuntimeException;
use Tests\TestCase;

final class StabilitasTest extends TestCase
{
    public function test_observatory_and_downloads_are_aggregate_and_preserve_origin(): void
    {
        $this->get('/nova/economia/stabilita')->assertOk()->assertSee('Cronologia della traiettoria originale')
            ->assertSee('4.677')->assertSee('Cinque esecuzioni')->assertSee('Prove tecniche non calibrate');
        $this->get('/nova/economia/stabilita/statistiche.csv')->assertOk()->assertDownload('nova-stabilitas.csv');
        $download = $this->get('/nova/economia/stabilita/statistiche.json')->assertOk()->assertDownload('nova-stabilitas.json');
        $data = json_decode(file_get_contents($download->baseResponse->getFile()->getPathname()), true);
        self::assertCount(30, $data['exploratory']);
        self::assertSame(Stabilitas::HISTORY['final_sha256'], $data['historical']['final_sha256']);
        self::assertArrayNotHasKey('enterprise_entries', $data['standard'][3]);
        self::assertNull($data['polis_index']);
    }

    public function test_rejects_historical_drift(): void
    {
        $audit = app(Stabilitas::class);
        $data = $audit->load();
        $data['standard'][0]['rows'][0]['employed']++;
        $this->expectException(RuntimeException::class);
        $audit->validate($data);
    }
}
