<?php

namespace App\Http\Controllers;

use App\Statistics\Nomos;
use Illuminate\Contracts\View\View;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\HttpFoundation\StreamedResponse;

final class InstitutionController
{
    public const SECTIONS = [
        'ordinamento' => 'Ordinamento',
        'corte' => 'Corte costituzionale',
        'atti' => 'Atti dimostrativi',
        'ricorsi' => 'Ricorsi',
        'diritti' => 'Diritti',
        'mandato' => 'Mandato e revoca',
        'emergenze' => 'Emergenze',
        'scenari' => 'Scenari',
        'trasparenza' => 'Trasparenza',
    ];

    public function show(Nomos $nomos, ?string $section = null): View
    {
        abort_if($section !== null && ! isset(self::SECTIONS[$section]), 404);

        return view('institutions', [
            'title' => self::SECTIONS[$section] ?? 'Istituzioni della Repubblica di Nova',
            'section' => $section,
            'sections' => self::SECTIONS,
            'data' => $nomos->load(),
            'checksum' => $nomos->checksum(),
        ]);
    }

    public function download(Nomos $nomos, string $format): Response
    {
        $data = $nomos->load();
        $headers = [
            'Content-Disposition' => 'attachment; filename="nova-nomos.'.$format.'"',
            'X-Nomos-Export-SHA256' => $nomos->checksum(),
            'X-Nomos-Journal-SHA256' => $data['journal_sha256'],
        ];
        if ($format === 'json') {
            return response()->file(config('polis.content').'/statistics/nomos.json', $headers + ['Content-Type' => 'application/json']);
        }
        if ($format === 'sha256') {
            return response()->file(config('polis.content').'/statistics/nomos.sha256', $headers + ['Content-Type' => 'text/plain']);
        }

        return new StreamedResponse(static function () use ($data): void {
            $stream = fopen('php://output', 'w');
            if ($stream === false) {
                throw new \RuntimeException('Flusso CSV indisponibile.');
            }
            fputcsv($stream, ['version', 'regime', 'journal_sha256', 'metric', 'value'], escape: '');
            foreach ($data['metrics'] as $key => $value) {
                fputcsv($stream, [$data['version'], $data['regime'], $data['journal_sha256'], $key, $value], escape: '');
            }
            fclose($stream);
        }, 200, $headers + ['Content-Type' => 'text/csv; charset=UTF-8']);
    }
}
