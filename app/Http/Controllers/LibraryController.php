<?php

namespace App\Http\Controllers;

use App\Documents\Library;
use Illuminate\Contracts\View\View;
use Illuminate\Http\Request;
use Illuminate\Http\Response;

final class LibraryController
{
    public function __construct(private Library $library) {}

    public function index(Request $request): View
    {
        $query = $this->query($request);
        $documents = array_filter($this->library->documents(), function (array $document, string $id) use ($query): bool {
            $text = $document['title'].' '.$document['subtitle'];
            if ($query !== '') {
                foreach (array_keys($document['versions']) as $version) {
                    $text .= ' '.($this->library->read($id, $version)['source'] ?? '');
                }
            }

            return $query === '' || mb_stripos($text, $query) !== false;
        }, ARRAY_FILTER_USE_BOTH);

        return view('library', ['title' => __('ui.nav.library'), 'description' => __('pages.library'), 'documents' => $documents, 'query' => $query]);
    }

    public function show(Request $request, string $document, ?string $version = null): View
    {
        return $this->documentView($request, $document, $version, false);
    }

    public function constitution(Request $request, ?string $version = null): View
    {
        return $this->documentView($request, 'costituzione', $version, true);
    }

    public function versionedArticle(string $version, string $numero): View
    {
        return $this->article($numero, $version);
    }

    public function article(string $numero, ?string $version = null): View
    {
        $entry = $this->library->entry('costituzione');
        $record = $this->library->read('costituzione', $version);
        $article = $record['articles'][(int) $numero] ?? null;
        abort_unless($entry && $record && $article, 404);
        $number = (int) $numero;

        return view('article', ['title' => $article['label'], 'description' => $article['title'].' · Versione '.$record['version'], 'entry' => $entry, 'record' => $record, 'article' => $article, 'number' => $number, 'canonicalPath' => route('constitution.article.version', [$record['version'], $number], false)]);
    }

    public function download(string $document, string $version): Response
    {
        $record = $this->library->read($document, $version);
        abort_unless($record, 404);

        return response($record['source'], 200, [
            'Content-Type' => 'text/markdown; charset=UTF-8',
            'Content-Disposition' => 'attachment; filename="'.$document.'-'.$version.'.md"',
        ]);
    }

    private function documentView(Request $request, string $id, ?string $version, bool $constitution): View
    {
        $entry = $this->library->entry($id);
        abort_unless($entry, 404);
        $record = $this->library->read($id, $version);
        abort_if($version !== null && $record === null, 404);
        $query = $constitution ? $this->query($request) : '';
        $matches = $query === '' ? [] : array_filter(
            $record['articles'] ?? [],
            static fn (array $article, int $number): bool => ctype_digit($query)
                ? $number === (int) $query
                : mb_stripos($article['label'].' '.$article['text'], $query) !== false,
            ARRAY_FILTER_USE_BOTH
        );

        return view('document', [
            'title' => $entry['title'], 'description' => $entry['subtitle'], 'entry' => $entry,
            'record' => $record, 'id' => $id, 'constitution' => $constitution, 'query' => $query, 'matches' => $matches,
        ]);
    }

    private function query(Request $request): string
    {
        $query = $request->query('q', '');
        abort_unless(is_string($query) && mb_strlen($query) <= 150, 422);

        return trim($query);
    }
}
