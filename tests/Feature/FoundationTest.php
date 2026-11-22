<?php

namespace Tests\Feature;

use App\Documents\Library;
use Tests\TestCase;

final class FoundationTest extends TestCase
{
    private const HASHES = [
        'manifesto' => 'ff78fcaa07d14cf9bfaaa344a80577a7bbd2ca9deef964cac9efaf3950fadbf4',
        'costituzione' => 'b7f9710102f917324a91c5e22e191a2214b724a442a9cb153ce27ccfaa8dc52c',
    ];

    public function test_original_downloads_match_the_acquisition_hashes(): void
    {
        foreach (self::HASHES as $id => $expected) {
            $path = base_path("content/documents/it/{$id}/1.0.md");
            self::assertSame($expected, hash_file('sha256', $path));
            $this->get("/biblioteca/{$id}/1.0")->assertOk()->assertSee($expected);
            $this->get("/biblioteca/{$id}/1.0/markdown")
                ->assertOk()->assertContent(file_get_contents($path));
        }
    }

    public function test_original_documents_have_the_expected_structure(): void
    {
        $library = app(Library::class);
        $manifesto = $library->read('manifesto', '1.0');
        $constitution = $library->read('costituzione', '1.0');
        $sections = array_filter($manifesto['outline'], static fn (array $heading): bool => preg_match('/^\d+\. /', $heading['label']) === 1);
        self::assertSame(range(1, 16), array_values(array_map(static fn (array $heading): int => (int) $heading['label'], $sections)));
        $titles = array_filter($constitution['outline'], static fn (array $heading): bool => str_starts_with($heading['label'], 'TITOLO '));
        self::assertSame(['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII'], array_values(
            array_map(static fn (array $heading): string => substr($heading['label'], 7), $titles)
        ));
        $anchors = array_column($constitution['outline'], 'id');
        self::assertContains('preambolo', $anchors);
        self::assertContains('dichiarazione-conclusiva', $anchors);
        self::assertSame(range(1, 71), array_keys($constitution['articles']));
        foreach ($constitution['articles'] as $number => $article) {
            self::assertNotSame('', trim($article['text']));
            $this->get("/costituzione/versione/1.0/articolo/{$number}")
                ->assertOk()->assertSee($article['label'])->assertSee($article['title']);
        }
        $this->get('/costituzione/articolo/1')->assertOk()->assertSee('TITOLO I — Principi fondamentali');
    }

    public function test_search_matches_number_title_and_article_body(): void
    {
        $url = '/costituzione/versione/1.0?q=';
        foreach (['1', 'Natura della Repubblica'] as $query) {
            $this->get($url.rawurlencode($query))->assertOk()
                ->assertSee('Risultati della ricerca')->assertSee('/costituzione/versione/1.0/articolo/1', false);
        }
        $article = app(Library::class)->read('costituzione', '1.0')['articles'][1];
        $phrase = mb_substr(trim($article['text']), 0, 30);
        $this->get($url.rawurlencode($phrase))->assertOk()
            ->assertSee('Risultati della ricerca')->assertSee('/costituzione/versione/1.0/articolo/1', false);
    }
}
