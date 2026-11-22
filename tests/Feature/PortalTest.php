<?php

namespace Tests\Feature;

use App\Http\Controllers\PortalController;
use Illuminate\Support\Env;
use PHPUnit\Framework\Attributes\DataProvider;
use Tests\TestCase;

final class PortalTest extends TestCase
{
    public static function pages(): iterable
    {
        foreach (['/', ...array_values(PortalController::PAGES), '/costituzione', '/biblioteca', '/biblioteca/manifesto', '/biblioteca/costituzione', '/diario', '/diario/avvio-del-portale'] as $path) {
            yield $path => [$path];
        }
    }

    #[DataProvider('pages')]
    public function test_pages_work_without_database_or_session_cookie(string $path): void
    {
        $response = $this->get($path);
        $response->assertOk()->assertHeader('X-Robots-Tag', 'noindex, nofollow');
        $response->assertDontSee('data-action="start-simulation"', false);
        self::assertFalse($response->headers->has('Set-Cookie'));
    }

    public function test_missing_documents_have_no_downloads_or_invented_articles(): void
    {
        $this->get('/costituzione')->assertOk()->assertSee('In attesa del documento originale')->assertDontSee('Scarica Markdown');
        $this->get('/costituzione/articolo/1')->assertNotFound()->assertSee('Pagina non trovata');
        $this->get('/biblioteca/manifesto/1.0')->assertNotFound();
        $this->get('/biblioteca/manifesto/1.0/markdown')->assertNotFound();
        $this->get('/osservatorio')->assertSee('Non sono ancora disponibili risultati sperimentali.');
    }

    public function test_invalid_routes_and_queries_are_rejected(): void
    {
        foreach (['/biblioteca/%2E%2E%2Fconfig', '/biblioteca/Manifesto', '/biblioteca/manifesto/../abc', '/costituzione/articolo/0', '/costituzione/articolo/abc', '/diario/inesistente', '/storage/private.txt'] as $path) {
            $this->get($path)->assertNotFound();
        }
        $this->get('/biblioteca?q[]=a')->assertUnprocessable();
        $this->get('/biblioteca?q=Costituzione')->assertOk()->assertSee('Costituzione della Repubblica di Nova')->assertDontSee('Documento fondativo del progetto di ricerca');
        $this->get('/biblioteca?q='.str_repeat('a', 151))->assertUnprocessable();
    }

    public function test_sitemap_robots_and_headers(): void
    {
        $this->get('/sitemap.xml')->assertOk()
            ->assertHeader('Content-Type', 'application/xml; charset=UTF-8')
            ->assertSee('/diario/avvio-del-portale')
            ->assertDontSee('/costituzione/articolo/1');
        $this->get('/robots.txt')->assertOk()->assertSee('Disallow: /');
        $this->get('/')->assertHeader('Content-Security-Policy')->assertHeader('X-Content-Type-Options', 'nosniff');
        config(['polis.indexable' => true]);
        $this->get('/robots.txt')->assertSee('Allow: /')->assertSee('sitemap.xml')->assertHeaderMissing('X-Robots-Tag');
    }

    public function test_production_turns_debug_off_and_indexation_requires_https(): void
    {
        foreach (['APP_ENV' => 'production', 'APP_DEBUG' => 'true', 'POLIS_INDEXABLE' => 'true', 'APP_URL' => 'http://example.test'] as $key => $value) {
            Env::getRepository()->clear($key);
            Env::getRepository()->set($key, $value);
        }
        try {
            self::assertFalse((require config_path('app.php'))['debug']);
            self::assertFalse((require config_path('polis.php'))['indexable']);
        } finally {
            foreach (['APP_ENV', 'APP_DEBUG', 'POLIS_INDEXABLE', 'APP_URL'] as $key) {
                Env::getRepository()->clear($key);
            }
            Env::getRepository()->set('APP_ENV', 'testing');
            Env::getRepository()->set('APP_DEBUG', 'false');
        }
    }
}
