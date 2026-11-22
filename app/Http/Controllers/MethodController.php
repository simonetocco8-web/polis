<?php

namespace App\Http\Controllers;

use App\Research\Methodos;
use Illuminate\Contracts\View\View;
use Illuminate\Http\Request;

final class MethodController
{
    public function __invoke(Request $request, Methodos $methodos): View
    {
        $section = substr($request->route()->getName(), strlen('method.'));
        $titles = ['scenarios' => 'Universi sperimentali', 'indicators' => 'Catalogo degli indicatori', 'index' => 'Polis Index'];
        abort_unless(isset($titles[$section]), 404);
        $config = $methodos->load();

        return view('research', [
            'title' => $titles[$section], 'section' => $section, 'method' => $config,
            'ready' => $methodos->ready($config),
            'score' => $methodos->score($config['polis_index']['domains'], array_fill_keys(array_column($config['polis_index']['domains'], 'id'), 50), false),
        ]);
    }
}
