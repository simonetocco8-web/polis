<?php

namespace App\Http\Controllers;

use App\Documents\Library;
use App\Documents\Markdown;
use Illuminate\Contracts\View\View;
use Illuminate\Http\Request;
use Illuminate\Http\Response;
use Illuminate\Support\Facades\File;

final class PortalController
{
    public const PAGES = [
        'project' => '/progetto', 'philosophy' => '/filosofia', 'nova' => '/nova',
        'method' => '/metodologia', 'simulator' => '/simulatore', 'observatory' => '/osservatorio',
        'transparency' => '/trasparenza', 'privacy' => '/privacy', 'accessibility' => '/accessibilita',
    ];

    public function __construct(private Library $library, private Markdown $markdown) {}

    public function home(): View
    {
        return view('home', [
            'documents' => $this->library->documents(),
            'parameters' => [
                'Cittadini' => '100.000', 'Imprese' => '5.000', 'PIL iniziale' => '€3 mld',
                'PIL pro capite' => '€30.000', 'Orizzonte sperimentale' => '50 anni',
                'Scenari di governo' => '6', 'Articoli costituzionali previsti' => '71',
            ],
            'timeline' => [
                'Fondamenti filosofici' => 'Documentati nel portale',
                'Costituzione' => 'In acquisizione',
                'Portale pubblico' => 'Implementato · pubblicazione da verificare',
                'Protocollo scientifico' => 'In definizione',
                'Motore economico e sociale' => 'Da avviare',
                'Governo artificiale' => 'Da avviare',
                'Simulazioni comparative' => 'Da avviare',
                'Pubblicazione dei risultati' => 'Da avviare',
            ],
        ]);
    }

    public function page(Request $request): View
    {
        $name = $request->route()->getName();
        $page = __('pages.'.$name);
        $path = config('polis.content').'/editorial/'.app()->getLocale().'/'.$name.'.md';

        return view('editorial', [
            'title' => __('ui.nav.'.$name),
            'description' => $page,
            'page' => $name,
            'html' => $this->markdown->render(File::get($path))['html'],
        ]);
    }

    public function journal(): View
    {
        return view('journal', ['title' => __('ui.nav.journal'), 'description' => __('pages.journal'), 'entries' => $this->entries()]);
    }

    public function journalEntry(string $slug): View
    {
        $entry = $this->entries()[$slug] ?? null;
        abort_unless($entry, 404);
        $path = config('polis.content').'/journal/'.app()->getLocale().'/'.$slug.'.md';

        return view('editorial', [
            'title' => $entry['title'],
            'description' => $entry['description'],
            'entry' => $entry,
            'html' => $this->markdown->render(File::get($path))['html'],
        ]);
    }

    public function sitemap(): Response
    {
        $paths = ['/', '/costituzione', '/biblioteca', '/diario', ...array_values(self::PAGES)];
        foreach ($this->library->documents() as $id => $document) {
            $paths[] = route('library.show', $id, false);
            foreach (array_keys($document['versions']) as $version) {
                $paths[] = route('library.version', [$id, $version], false);
                if ($id === 'costituzione') {
                    $paths[] = route('constitution.version', $version, false);
                    foreach (array_keys($this->library->read($id, $version)['articles']) as $number) {
                        $paths[] = route('constitution.article.version', [$version, $number], false);
                    }
                }
            }
        }
        foreach (array_keys($this->entries()) as $slug) {
            $paths[] = route('journal.show', $slug, false);
        }
        $base = rtrim(config('app.url'), '/');
        $xml = '<?xml version="1.0" encoding="UTF-8"?>'."\n".'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">';
        foreach ($paths as $path) {
            $xml .= '<url><loc>'.htmlspecialchars($base.$path, ENT_XML1 | ENT_QUOTES, 'UTF-8').'</loc></url>';
        }

        return response($xml.'</urlset>', 200, ['Content-Type' => 'application/xml; charset=UTF-8']);
    }

    public function robots(): Response
    {
        $robots = "User-agent: *\n";
        $robots .= config('polis.indexable')
            ? "Allow: /\nSitemap: ".rtrim(config('app.url'), '/')."/sitemap.xml\n"
            : "Disallow: /\n";

        return response($robots, 200, ['Content-Type' => 'text/plain; charset=UTF-8']);
    }

    private function entries(): array
    {
        return File::json(config('polis.content').'/metadata/journal.json')[app()->getLocale()] ?? [];
    }
}
