@extends('layout')
@section('content')
@include('partials.intro', ['description' => $article['title'].' · Versione '.$record['version'], 'parent' => [route('constitution.version', $record['version']), __('ui.nav.constitution')]])
<section class="shell section doc-grid">
    <div class="reading">
        <div id="article-text">{!! $article['html'] !!}</div>
        <div class="actions">
            <button class="button" type="button" data-action="copy-text" hidden>Copia il testo</button>
            <button class="button-secondary button" type="button" data-action="copy-link" hidden>Copia il collegamento</button>
            <button class="button-secondary button" type="button" data-action="print" hidden>{{ __('ui.print') }}</button>
        </div>
        <p id="action-status" class="no-print" role="status"></p>
        <nav class="actions" aria-label="Navigazione tra articoli">
            @if(isset($record['articles'][$number - 1]))<a href="{{ route('constitution.article.version', [$record['version'], $number - 1]) }}">Articolo precedente</a>@endif
            <a href="{{ route('constitution.version', $record['version']).'#articolo-'.$number }}">Testo integrale</a>
            @if(isset($record['articles'][$number + 1]))<a href="{{ route('constitution.article.version', [$record['version'], $number + 1]) }}">Articolo successivo</a>@endif
        </nav>
    </div>
    <aside class="doc-aside"><h2 class="text-2xl">Metadati del testo</h2>@include('partials.metadata')</aside>
</section>
@endsection
