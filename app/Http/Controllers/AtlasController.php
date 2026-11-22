<?php

namespace App\Http\Controllers;

use App\Statistics\Demos;
use Illuminate\Contracts\View\View;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\HttpFoundation\StreamedResponse;

final class AtlasController
{
    public const PAGES = [
        'popolazione' => ['Popolazione', ['age' => 'Abitanti per fascia di età']],
        'demografia' => ['Demografia', ['age' => 'Distribuzione per età']],
        'famiglie' => ['Famiglie', ['households' => 'Nuclei familiari']],
        'istruzione' => ['Istruzione', ['education' => 'Livelli di istruzione']],
        'occupazione' => ['Occupazione', ['employment' => 'Stato occupazionale']],
        'salute' => ['Salute', ['health' => 'Stato sanitario sintetico']],
        'imprese' => ['Imprese', ['sectors' => 'Imprese per settore', 'firm_sizes' => 'Imprese per dimensione potenziale']],
        'territorio' => ['Territorio', ['territories' => 'Abitanti per area', 'dwelling_capacity' => 'Capacità abitativa ipotizzata']],
        'generazione' => ['Generazione e fonti', []],
    ];

    public function show(string $section, Demos $demos): View
    {
        abort_unless(isset(self::PAGES[$section]), 404);
        [$title, $groups] = self::PAGES[$section];

        return view('atlas', ['title' => $title, 'groups' => $groups, 'section' => $section, 'data' => $demos->load()]);
    }

    public function download(string $format, Demos $demos): Response
    {
        $data = $demos->load();
        if ($format === 'json') {
            return response()->json($data)->header('Content-Disposition', 'attachment; filename="nova-demos.json"');
        }

        return new StreamedResponse(static function () use ($data): void {
            $stream = fopen('php://output', 'w');
            fputcsv($stream, ['gruppo', 'categoria', 'valore', 'unita'], escape: '');
            foreach ($data['groups'] as $id => $group) {
                foreach ($group as $label => $value) {
                    fputcsv($stream, [$id, $label, $value, Demos::GROUPS[$id]], escape: '');
                }
            }
            fclose($stream);
        }, 200, ['Content-Type' => 'text/csv; charset=UTF-8', 'Content-Disposition' => 'attachment; filename="nova-demos.csv"']);
    }
}
