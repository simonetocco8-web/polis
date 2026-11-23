<?php

namespace App\Http\Controllers;

use App\Statistics\Theoria;
use Illuminate\Contracts\View\View;
use Symfony\Component\HttpFoundation\Response;

final class TheoriaController
{
    public const PAGES = [
        'decisioni' => 'Decisioni analizzate',
        'fascicoli' => 'Fascicoli',
        'indicatori' => 'Indicatori',
        'controlli' => 'Controlli',
        'risultati' => 'Risultati',
        'metodologia' => 'Metodologia',
        'trasparenza' => 'Trasparenza',
    ];

    public function show(Theoria $theoria, ?string $section = null): View
    {
        abort_if($section !== null && ! isset(self::PAGES[$section]), 404);

        return view('theoria', ['title' => self::PAGES[$section] ?? 'Osservatorio indipendente', 'section' => $section,
            'sections' => self::PAGES, 'data' => $theoria->load(), 'checksum' => Theoria::HASH]);
    }

    public function download(Theoria $theoria, string $format): Response
    {
        $data = $theoria->load();
        $headers = ['X-Theoria-Export-SHA256' => Theoria::HASH, 'Content-Disposition' => 'attachment; filename="theoria.'.$format.'"'];
        if ($format !== 'csv') {
            return response()->file(config('polis.content').'/statistics/theoria.'.$format,
                $headers + ['Content-Type' => $format === 'json' ? 'application/json' : 'text/plain']);
        }

        return response()->stream(static function () use ($data): void {
            $out = fopen('php://output', 'w');
            if ($out === false) {
                throw new \RuntimeException('Flusso CSV non disponibile.');
            }
            $fields = ['id', 'scenario', 'period', 'outcome', 'procedure', 'effects', 'before_cents', 'after_cents'];
            fputcsv($out, $fields, escape: '');
            foreach ($data['cases'] as $case) {
                fputcsv($out, array_map(static fn ($field) => $case[$field], $fields), escape: '');
            }
            fclose($out);
        }, 200, $headers + ['Content-Type' => 'text/csv; charset=UTF-8']);
    }
}
