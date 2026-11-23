<?php

namespace App\Http\Controllers;

use App\Statistics\Experimentum;
use Illuminate\Contracts\View\View;
use Symfony\Component\HttpFoundation\Response;

final class ExperimentumController
{
    public const PAGES = [
        'protocolli' => 'Protocolli', 'scenari' => 'Scenari', 'repliche' => 'Repliche', 'indicatori' => 'Indicatori',
        'risultati' => 'Risultati', 'confronti' => 'Confronti', 'metodologia' => 'Metodologia',
        'trasparenza' => 'Trasparenza',
    ];

    public function show(Experimentum $lab, ?string $section = null): View
    {
        abort_if($section !== null && ! isset(self::PAGES[$section]), 404);

        return view('experimentum', ['title' => self::PAGES[$section] ?? 'Laboratorio scientifico', 'section' => $section,
            'sections' => self::PAGES, 'data' => $lab->load(), 'checksum' => Experimentum::HASH]);
    }

    public function download(Experimentum $lab, string $format): Response
    {
        $data = $lab->load();
        $headers = ['X-Experimentum-Export-SHA256' => Experimentum::HASH,
            'Content-Disposition' => 'attachment; filename="experimentum.'.$format.'"'];
        if ($format !== 'csv') {
            return response()->file(config('polis.content').'/statistics/experimentum.'.$format,
                $headers + ['Content-Type' => $format === 'json' ? 'application/json' : 'text/plain']);
        }

        return response()->stream(static function () use ($data): void {
            $out = fopen('php://output', 'w');
            if ($out === false) {
                throw new \RuntimeException('Flusso CSV non disponibile.');
            }
            fputcsv($out, ['month', 'indicator', 'n', 'missing', 'mean', 'sd'], escape: '');
            foreach ($data['aggregates'] as $row) {
                foreach ($row['indicators'] as $key => $summary) {
                    fputcsv($out, [$row['month'], $key, $summary['n'], $summary['missing'], $summary['mean'], $summary['sd']], escape: '');
                }
            }
            fclose($out);
        }, 200, $headers + ['Content-Type' => 'text/csv; charset=UTF-8']);
    }
}
