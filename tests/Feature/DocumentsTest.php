<?php

namespace Tests\Feature;

use App\Documents\Library;
use App\Documents\Markdown;
use Illuminate\Support\Facades\Artisan;
use Illuminate\Support\Facades\File;
use PHPUnit\Framework\Attributes\DataProvider;
use RuntimeException;
use Tests\TestCase;

final class DocumentsTest extends TestCase
{
    private string $root;

    private const SOURCE = "## Preambolo\n\nTest sintetico.\n\n## Titolo I — Test\n\n### Articolo 1 — Equità\n\nPrincipio di parità. Vedi [articolo 2](#articolo-2).\n\n### Articolo 2 — Tutela\n\nPrincipio di tutela.\n\n## Dichiarazione conclusiva\n\nFine del test.\n";

    protected function setUp(): void
    {
        parent::setUp();
        $this->root = sys_get_temp_dir().'/polis-fixtures-'.bin2hex(random_bytes(8));
        File::ensureDirectoryExists($this->root.'/documents/it/costituzione');
        File::ensureDirectoryExists($this->root.'/metadata');
        config(['polis.content' => $this->root]);
    }

    protected function tearDown(): void
    {
        if (isset($this->root)) {
            File::deleteDirectory($this->root);
        }
        parent::tearDown();
    }

    public function test_versioned_constitution_allows_search_read_download_and_integrity_checks(): void
    {
        $this->publishFixture(self::SOURCE);
        self::assertSame(0, Artisan::call('documents:validate'));
        self::assertStringContainsString('Versioni validate: 2', Artisan::output());
        $this->get('/biblioteca?q=parit%C3%A0')->assertOk()->assertSee('Scheda sintetica');
        $this->get('/biblioteca/costituzione/1.1')->assertOk()->assertSee(hash('sha256', self::SOURCE));
        $this->get('/costituzione?q=parità')->assertOk()->assertSee('Risultati della ricerca')->assertSee('id="articolo-1"', false);
        $this->get('/costituzione?q=2')->assertOk()->assertSee('/costituzione/versione/1.2/articolo/2', false);
        $this->get('/costituzione?q=inesistente')->assertOk()->assertSee('Nessun articolo trovato.');
        $this->get('/costituzione/articolo/2')->assertOk()->assertSee('Principio di tutela aggiornato.')->assertSee('Articolo precedente');
        $this->get('/costituzione/versione/1.1/articolo/1')->assertOk()->assertSee('Articolo successivo')->assertSee('Principio di parità.')->assertSee('href="/costituzione/versione/1.1#articolo-2"', false);
        $this->get('/costituzione/versione/1.0/articolo/1')->assertNotFound();
        $this->get('/biblioteca/costituzione/1.1/markdown')->assertOk()
            ->assertHeader('Content-Disposition', 'attachment; filename="costituzione-1.1.md"')
            ->assertContent(self::SOURCE);
    }

    public function test_changed_bytes_fail_closed(): void
    {
        $this->publishFixture(self::SOURCE);
        File::append($this->root.'/documents/it/costituzione/1.1.md', 'modifica');
        $this->get('/biblioteca/costituzione/1.1/markdown')->assertServerError();
        $this->expectException(RuntimeException::class);
        $this->expectExceptionMessage('Integrità non verificata');
        app(Library::class)->validate();
    }

    public function test_invalid_metadata_fails_validation(): void
    {
        $this->publishFixture(self::SOURCE, ['date' => '2026-02-30']);
        $this->expectException(RuntimeException::class);
        $this->expectExceptionMessage('Metadati non validi');
        app(Library::class)->validate();
    }

    public function test_original_version_enforces_declared_article_and_title_counts(): void
    {
        $this->publishFixture(self::SOURCE);
        $path = $this->root.'/metadata/documents.json';
        $data = File::json($path);
        $data['it']['costituzione']['versions']['1.0'] = $data['it']['costituzione']['versions']['1.1'];
        File::put($path, json_encode($data, JSON_THROW_ON_ERROR));
        $this->expectException(RuntimeException::class);
        $this->expectExceptionMessage('Requisiti della struttura costituzionale non validi');
        app(Library::class)->validate();
    }

    public function test_constitution_parser_accepts_a_synthetic_structure_of_71_articles(): void
    {
        $source = "## Preambolo\n\nFixture sintetica.\n";
        for ($index = 1; $index <= 71; $index++) {
            if (($index - 1) % 6 === 0) {
                $source .= "\n## Titolo ".(intdiv($index - 1, 6) + 1)." — Fixture\n";
            }
            $source .= "\n### Articolo {$index} — Fixture\n\nContenuto sintetico {$index}.\n";
        }
        $source .= "\n## Dichiarazione conclusiva\n\nFine della fixture.\n";
        $result = app(Markdown::class)->render($source, ['articles' => 71, 'titles' => 12]);
        self::assertCount(71, $result['articles']);
        self::assertStringContainsString('Contenuto sintetico 71.', $result['articles'][71]['html']);
    }

    public function test_unregistered_markdown_fails_validation(): void
    {
        $this->publishFixture(self::SOURCE);
        File::put($this->root.'/documents/it/costituzione/1.3.md', self::SOURCE);
        $this->expectException(RuntimeException::class);
        $this->expectExceptionMessage('File Markdown assente dal manifest');
        app(Library::class)->validate();
    }

    public static function invalidStructures(): iterable
    {
        yield 'duplicato' => [str_replace('Articolo 2 — Tutela', 'Articolo 1 — Tutela', self::SOURCE)];
        yield 'mancante' => [str_replace('### Articolo 2 — Tutela', '### Tutela', self::SOURCE)];
        yield 'riferimento mancante' => [str_replace('#articolo-2', '#articolo-90', self::SOURCE)];
        yield 'preambolo mancante' => [str_replace('## Preambolo', '## Introduzione', self::SOURCE)];
    }

    #[DataProvider('invalidStructures')]
    public function test_invalid_constitution_structure_is_rejected(string $source): void
    {
        $this->publishFixture($source);
        $this->expectException(RuntimeException::class);
        app(Library::class)->validate();
    }

    public function test_markdown_renders_without_raw_html_or_unsafe_links(): void
    {
        $result = app(Markdown::class)->render("# Indice\n\n<em>Testo</em> [link](javascript:void%280%29)");
        self::assertStringContainsString('id="sezione-1"', $result['html']);
        self::assertStringNotContainsString('<em>', $result['html']);
        self::assertStringNotContainsString('href="javascript:', $result['html']);
    }

    private function publishFixture(string $source, array $overrides = []): void
    {
        $metadata = $overrides + [
            'date' => '2026-11-22', 'author' => 'Fixture sintetica', 'status' => 'Test',
            'sha256' => hash('sha256', $source), 'provenance' => 'Suite PHPUnit', 'changes' => 'Fixture',
            'original_language' => 'it', 'structure' => ['articles' => 2, 'titles' => 1],
        ];
        $new = str_replace('Principio di tutela.', 'Principio di tutela aggiornato.', $source);
        $updated = array_replace($metadata, ['sha256' => hash('sha256', $new), 'previous' => '1.1']);
        File::put($this->root.'/metadata/documents.json', json_encode(['it' => ['costituzione' => [
            'title' => 'Scheda sintetica', 'subtitle' => 'Esclusivamente per il test', 'type' => 'Test',
            'expected_version' => '1.1', 'expected_date' => 'novembre 2026',
            'current' => '1.2', 'versions' => ['1.2' => $updated, '1.1' => $metadata],
        ]]], JSON_THROW_ON_ERROR));
        File::put($this->root.'/documents/it/costituzione/1.1.md', $source);
        File::put($this->root.'/documents/it/costituzione/1.2.md', $new);
    }
}
