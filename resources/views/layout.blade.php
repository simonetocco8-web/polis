@php
    $description ??= config('polis.description');
    $canonical = rtrim(config('app.url'), '/').($canonicalPath ?? request()->getPathInfo());
    $pageTitle = isset($title) ? $title.' | POLIS AI' : 'POLIS AI — Il filosofo-re artificiale';
@endphp
<!doctype html>
<html lang="{{ app()->getLocale() }}">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{{ $pageTitle }}</title>
    <meta name="description" content="{{ $description }}">
    <link rel="canonical" href="{{ $canonical }}">
    <meta name="robots" content="{{ config('polis.indexable') ? 'index,follow' : 'noindex,nofollow' }}">
    <meta property="og:type" content="website">
    <meta property="og:title" content="{{ $pageTitle }}">
    <meta property="og:description" content="{{ $description }}">
    <meta property="og:url" content="{{ $canonical }}">
    <meta property="og:image" content="{{ rtrim(config('app.url'), '/').'/brand/open-graph.png' }}">
    <meta name="twitter:card" content="summary_large_image">
    <link rel="apple-touch-icon" href="/brand/icon-192.png">
    <link rel="icon" href="/brand/favicon.svg" type="image/svg+xml">
    @vite(['resources/css/app.css', 'resources/js/app.js'])
</head>
<body itemscope itemtype="https://schema.org/WebPage">
<meta itemprop="url" content="{{ $canonical }}">
<a class="skip" href="#contenuto">{{ __('ui.skip') }}</a>
<header class="masthead">
    <div class="shell masthead-inner">
        <a class="brand" href="{{ route('home') }}" aria-label="POLIS AI, {{ __('ui.home') }}"><img src="/brand/mark.svg" width="38" height="38" alt=""><span>POLIS AI</span></a>
        <nav class="main-nav" aria-label="Navigazione principale">
            @foreach(['project','philosophy','nova','constitution','method'] as $key)
                <a @if(request()->routeIs($key, $key.'.*')) aria-current="page" @endif href="{{ route($key) }}">{{ __('ui.nav.'.$key) }}</a>
            @endforeach
            <a class="nav-library" href="{{ route('library') }}">{{ __('ui.nav.library') }} @include('partials.arrow')</a>
        </nav>
        <details class="mobile-nav">
            <summary>{{ __('ui.menu') }}</summary>
            <nav aria-label="Navigazione mobile">
                @foreach(__('ui.nav') as $key => $label)
                    <a @if(request()->routeIs($key, $key.'.*')) aria-current="page" @endif href="{{ route($key) }}">{{ $label }}</a>
                @endforeach
            </nav>
        </details>
    </div>
</header>
<main id="contenuto" tabindex="-1">
    @yield('content')
</main>
<footer class="site-footer">
    <div class="shell footer-grid">
        <div><a class="brand" href="{{ route('home') }}"><img src="/brand/mark.svg" width="38" height="38" alt=""><span>POLIS AI</span></a><p>Progetto indipendente di ricerca sperimentale · Dal 2026</p><p>{{ config('polis.status') }}</p></div>
        <nav aria-label="Risorse">
            @foreach(['library','simulator','observatory','journal','transparency','privacy','accessibility'] as $key)
                <a href="{{ route($key) }}">{{ __('ui.nav.'.$key) }}</a>
            @endforeach
        </nav>
    </div>
</footer>
</body>
</html>
