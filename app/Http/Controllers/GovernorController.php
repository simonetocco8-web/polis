<?php

namespace App\Http\Controllers;

use App\Statistics\Archon;
use Illuminate\Contracts\View\View;
use Symfony\Component\HttpFoundation\Response;

final class GovernorController
{
    public const SECTIONS = [
        'governatore' => 'Governatore', 'mandato' => 'Mandato', 'decisioni' => 'Diario delle decisioni',
        'proposte' => 'Proposte', 'provvedimenti' => 'Provvedimenti', 'risultati' => 'Risultati',
        'controlli' => 'Controlli', 'trasparenza' => 'Trasparenza', 'tecnologia' => 'Tecnologia',
    ];

    public function show(Archon $archon, ?string $section = null): View
    {
        abort_if($section !== null && ! isset(self::SECTIONS[$section]), 404);

        return view('governor', [
            'title' => self::SECTIONS[$section] ?? 'Il Governatore artificiale',
            'section' => $section,
            'sections' => self::SECTIONS,
            'data' => $archon->load(),
            'checksum' => $archon->checksum(),
        ]);
    }

    public function download(Archon $archon, string $format): Response
    {
        $archon->load();

        return response()->file(config('polis.content').'/statistics/archon.'.$format, [
            'Content-Type' => $format === 'json' ? 'application/json' : 'text/plain',
            'Content-Disposition' => 'attachment; filename="nova-archon.'.$format.'"',
            'X-Archon-Export-SHA256' => $archon->checksum(),
        ]);
    }
}
