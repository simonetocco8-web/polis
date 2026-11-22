@extends('layout')
@section('content')
@include('partials.intro', ['eyebrow' => $entry['type'], 'parent' => [route('library'), __('ui.nav.library')]])
<section class="shell section">
@if(!$record)
    <div class="empty"><strong>{{ __('ui.missing') }}</strong><p>Versione prevista {{ $entry['expected_version'] }} · {{ $entry['expected_date'] }}. Testo elaborato tramite ChatGPT secondo la provenienza dichiarata dal promotore.</p></div>
    <p>La scheda sarà aggiornata dopo l’acquisizione e la verifica del testo integrale.</p>
    @if($id === 'costituzione' && !$constitution)<a class="text-link" href="{{ route('constitution') }}">Visualizzatore della Costituzione @include('partials.arrow')</a>@endif
@else
    <div class="doc-grid">
        <div class="reading">
            @if($constitution)
                <aside class="empty" aria-label="Nota metodologica">
                    <p><strong>Nota metodologica</strong></p>
                    <p>La Costituzione della Repubblica di Nova è stata elaborata dall'intelligenza artificiale in autonomia, senza indicazioni ideologiche del promotore circa i valori, i diritti, i poteri e l'organizzazione istituzionale da adottare. Il testo costituisce il primo risultato dell'esperimento POLIS AI e viene conservato nella sua formulazione originaria.</p>
                    <p>La Costituzione disciplina una società virtuale e non ha efficacia giuridica reale.</p>
                </aside>
                <form class="search" method="get" action="{{ route('constitution.version', $record['version']) }}">
                    <label>Parola chiave o numero di articolo <input name="q" type="search" maxlength="150" value="{{ $query }}"></label>
                    <button class="button">{{ __('ui.search') }}</button>
                </form>
                @if($query !== '')
                    <section class="no-print">
                        <h2>Risultati della ricerca</h2>
                        <ul>@forelse($matches as $n => $match)
                            <li><a href="{{ route('constitution.article.version', [$record['version'], $n]) }}">{{ $match['label'] }}</a></li>
                        @empty<li>Nessun articolo trovato.</li>@endforelse</ul>
                    </section>
                @endif
            @endif
            <div class="actions">
                <a class="button" href="{{ route('library.download', [$id, $record['version']]) }}">Scarica Markdown</a>
                <button class="button-secondary button" type="button" data-action="print" hidden>{{ __('ui.print') }}</button>
                <button class="button-secondary button" type="button" data-action="copy-link" hidden>Copia il collegamento</button>
                @if($id === 'costituzione' && !$constitution)<a class="button-secondary button" href="{{ route('constitution.version', $record['version']) }}">Visualizzatore</a>@endif
            </div>
            <p id="action-status" class="no-print" role="status"></p>
            {!! $record['html'] !!}
        </div>
        <aside class="doc-aside">
            <h2 class="text-2xl">Versione {{ $record['version'] }}</h2>
            @include('partials.metadata')
            <h3>Versioni e modifiche</h3>
            <ul>@foreach($entry['versions'] as $version => $history)
                <li><a class="text-link" @if($version === $record['version']) aria-current="page" @endif href="{{ $constitution ? route('constitution.version', $version) : route('library.version', [$id, $version]) }}">{{ $version }}</a> · {{ $history['changes'] }}</li>
            @endforeach</ul>
            <div class="no-print">
                <h3>Indice</h3>
                <ul>@foreach($record['outline'] as $heading)
                    <li><a href="#{{ $heading['id'] }}">{{ $heading['label'] }}</a>
                    @if($constitution && $heading['article'] !== null)<a class="text-link" aria-label="Pagina di {{ $heading['label'] }}" href="{{ route('constitution.article.version', [$record['version'], $heading['article']]) }}">@include('partials.arrow')</a>@endif</li>
                @endforeach</ul>
            </div>
        </aside>
    </div>
@endif
</section>
@endsection
