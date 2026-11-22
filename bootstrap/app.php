<?php

use App\Http\Middleware\PublicHeaders;
use Illuminate\Foundation\Application;
use Illuminate\Foundation\Configuration\Middleware;

return Application::configure(basePath: dirname(__DIR__))
    ->withRouting(using: function (): void {
        require base_path('routes/web.php');
    }, commands: __DIR__.'/../routes/console.php')
    ->withMiddleware(function (Middleware $middleware): void {
        $middleware->append(PublicHeaders::class);
    })
    ->withExceptions()
    ->create();
