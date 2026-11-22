@extends('layout')
@section('content')
@include('partials.intro', ['parent' => [route('method'), __('ui.nav.method')]])
<section class="shell section">
    @include('partials.method-nav')
    <p class="empty">Configurazione v{{ $method['version'] }} · {{ $ready ? 'Prerequisiti di configurazione soddisfatti' : 'Configurazione preliminare. Esperimenti confermativi non autorizzati.' }} Non sono ancora disponibili risultati sperimentali.</p>

    @if($section === 'scenarios')
        <p>Solo lo scenario B applica la Costituzione originaria di Nova. Gli altri sono ordinamenti alternativi simulati.</p>
        <div class="card-grid">
        @foreach($method['scenarios'] as $scenario)
            <article class="card" id="scenario-{{ strtolower($scenario['id']) }}">
                <h2 class="text-2xl">{{ $scenario['id'] }} — {{ $scenario['name'] }}</h2>
                <dl class="method-details">
                    <dt>Modalità decisionali</dt><dd>{{ $scenario['decision'] }}</dd>
                    <dt>Limiti del potere</dt><dd>{{ $scenario['limits'] }}</dd>
                    <dt>Obiettivo scientifico</dt><dd>{{ $scenario['objective'] }}</dd>
                    <dt>Comparabilità</dt><dd>{{ $scenario['comparison'] }}</dd>
                    <dt>Stato</dt><dd>{{ $scenario['status'] }}</dd>
                    <dt>Riferimento</dt><dd><a class="text-link" href="{{ route('library.version', ['protocollo', '1.0']) }}">{{ $scenario['reference'] }}</a></dd>
                </dl>
            </article>
        @endforeach
        </div>
    @elseif($section === 'indicators')
        <p>Le fonti sono candidate. Formule, soglie e serie vanno verificate prima del congelamento.</p>
        <div class="card-grid">
        @foreach($method['indicators'] as $indicator)
            <article class="card" id="{{ $indicator['id'] }}">
                <p class="eyebrow">{{ $indicator['category'] }}</p>
                <h2 class="text-2xl">{{ $indicator['name'] }}</h2>
                <p>{{ $indicator['definition'] }}</p>
                <dl class="method-details">
                    <dt>Identificativo</dt><dd><code>{{ $indicator['id'] }}</code></dd>
                    <dt>Unità</dt><dd>{{ $indicator['unit'] }}</dd>
                    <dt>Formula</dt><dd>{{ $indicator['formula'] ?? 'Da definire' }}</dd>
                    <dt>Periodicità</dt><dd>{{ $indicator['frequency'] }}</dd>
                    <dt>Direzione desiderata</dt><dd>{{ $indicator['direction'] }}</dd>
                    <dt>Fonte candidata</dt><dd>{{ $method['sources'][$indicator['source'] ?? ''] ?? 'Da definire' }}</dd>
                    <dt>Soglia</dt><dd>{{ $indicator['threshold'] ?? 'Da definire' }}</dd>
                    <dt>Stato e versione</dt><dd>{{ ['hypothesized' => 'Ipotizzato', 'calibrated' => 'Calibrato', 'validated' => 'Validato', 'frozen' => 'Congelato'][$indicator['status']] }} · {{ $indicator['version'] }}</dd>
                </dl>
            </article>
        @endforeach
        </div>
    @else
        <div class="reading">
            <p>Calcolatore dimostrativo. I valori da 0 a 100 sono ipotesi inserite dal visitatore. La normalizzazione scientifica e il trattamento dei dati mancanti sono da definire.</p>
        </div>
        <noscript><p>Per usare il calcolatore dimostrativo è necessario JavaScript.</p></noscript>
        <form class="index-form card" data-polis-index hidden>
            <fieldset>
                <legend class="text-xl">Punteggi ipotetici per dominio</legend>
                @foreach($method['polis_index']['domains'] as $domain)
                    <div class="index-control">
                        <label for="domain-{{ $domain['id'] }}">{{ $domain['name'] }} ({{ $domain['weight'] }}%)</label>
                        <input id="domain-{{ $domain['id'] }}" type="range" min="0" max="100" step="1" value="50" data-weight="{{ $domain['weight'] }}">
                        <span aria-hidden="true">50</span>
                    </div>
                @endforeach
            </fieldset>
            <label class="index-veto"><input type="checkbox" data-rights-veto> Ipotizza una violazione grave accertata dei diritti fondamentali</label>
            <p><output aria-live="polite" aria-atomic="true" id="index-result">Punteggio dimostrativo: {{ $score }} / 100</output></p>
        </form>
        <p class="reading">Le violazioni gravi accertate costituiscono una condizione autonoma di fallimento. Miglioramenti negli altri domini non le compensano.</p>
    @endif
</section>
@endsection
