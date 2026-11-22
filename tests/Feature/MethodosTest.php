<?php

namespace Tests\Feature;

use App\Research\Methodos;
use InvalidArgumentException;
use Tests\TestCase;

final class MethodosTest extends TestCase
{
    public function test_protocol_preserves_the_original_and_renders_tables(): void
    {
        $file = base_path('content/documents/it/protocollo/1.0.md');
        $hash = 'ab71d3ad157631e76edd3b40237eea2adbc449e35648cc1d87f379661953b422';
        self::assertSame($hash, hash_file('sha256', $file));
        $this->get('/biblioteca/protocollo/1.0')->assertOk()->assertSee($hash)->assertSee('<table>', false);
        $this->get('/biblioteca/protocollo/1.0/markdown')->assertOk()->assertContent(file_get_contents($file));
    }

    public function test_public_research_pages_expose_only_preliminary_configuration(): void
    {
        $this->get('/metodologia')->assertOk()->assertSee('/biblioteca/protocollo/1.0/markdown', false);
        $scenarios = $this->get('/metodologia/scenari')->assertOk()->assertSee('Esperimenti confermativi non autorizzati.');
        foreach (range('a', 'f') as $id) {
            $scenarios->assertSee('id="scenario-'.$id.'"', false);
        }
        $this->get('/metodologia/indicatori')->assertOk()->assertSee('Da definire')->assertSee('Fonte candidata');
        $this->get('/metodologia/polis-index')->assertOk()->assertSee('Punteggio dimostrativo: 50 / 100')->assertSee('condizione autonoma');
        $this->get('/diario/definizione-metodo-scientifico')->assertOk();
    }

    public function test_incomplete_configuration_cannot_be_frozen(): void
    {
        $service = app(Methodos::class);
        $config = $service->load();
        self::assertFalse($service->ready($config));
        $config['maturity'] = 'frozen';
        $this->expectException(InvalidArgumentException::class);
        $service->validate($config);
    }

    public function test_veto_and_missing_or_out_of_range_scores_have_no_weighted_result(): void
    {
        $service = app(Methodos::class);
        $domains = $service->load()['polis_index']['domains'];
        $values = array_fill_keys(array_column($domains, 'id'), 0);
        $values['prosperity'] = 100;
        $values['stability'] = 50;
        self::assertSame(30.0, $service->score($domains, $values, false));
        self::assertNull($service->score($domains, $values, true));
        $values['prosperity'] = 101;
        self::assertNull($service->score($domains, $values, false));
        unset($values['prosperity']);
        self::assertNull($service->score($domains, $values, false));
    }
}
