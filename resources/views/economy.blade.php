@extends('layout')
@section('content')
@include('partials.intro', ['parent' => [route('nova'), 'Repubblica di Nova'], 'eyebrow' => 'Osservatorio economico'])
<section class="shell section">
    <nav class="actions" aria-label="Sezioni dell’economia">
        @foreach($pages as $id => [$label])
            <a class="button button-secondary" href="{{ $id === 'sintesi' ? route('nova.economy') : route('nova.economy.section', $id) }}" @if($id === $section) aria-current="page" @endif>{{ $label }}</a>
        @endforeach
        <a class="button button-secondary" href="{{ route('nova.stability') }}">Stabilità economica</a>
    </nav>
    <p class="empty"><strong>Prova tecnica con economia chiusa · {{ $data['months'] }} mesi.</strong> Il modello economico non è calibrato. Nessun confronto tra governi e nessun Polis Index.</p>
    <p><a class="text-link" href="{{ route('nova.economy.export', 'csv') }}">Scarica CSV aggregato</a> · <a class="text-link" href="{{ route('nova.economy.export', 'json') }}">Scarica JSON aggregato</a></p>
    @if($section === 'finanza-pubblica' && $last['public_arrears'])
        <p class="empty">Il Tesoro è in arretrato sul servizio del debito al mese {{ $last['month'] }}. Il saldo misura i soli pagamenti effettuati.</p>
    @endif
    @if($section === 'banche')
        <p>Nuove erogazioni al termine della prova: {{ $last['bank_credit_halted'] ? 'sospese' : 'abilitate entro i limiti' }}.</p>
    @endif
    @if($fields !== [])
        <div class="card-grid">
            @foreach(array_slice($fields, 0, 4) as $key)
                <article class="card"><h2 class="text-2xl">{{ $labels[$key][0] }}</h2><p>{{ $format($last[$key], $labels[$key][1]) }} @if($last[$key] !== null){{ $labels[$key][1] }}@endif</p></article>
            @endforeach
        </div>
        @if($chart !== [])
            <figure class="economic-chart">
                <figcaption>{{ $labels[$fields[0]][0] }} · serie mensile simulata</figcaption>
                <svg viewBox="0 0 600 148" aria-hidden="true" focusable="false">
                    <path d="M10 20H590M10 77H590M10 135H590" class="economic-grid"/>
                    <polyline points="{{ $chart['points'] }}" class="economic-line"/>
                </svg>
                <p>Dal mese 1 al mese {{ $data['months'] }}. Minimo {{ $format($chart['low'], $labels[$fields[0]][1]) }}, massimo {{ $format($chart['high'], $labels[$fields[0]][1]) }} {{ $labels[$fields[0]][1] }}. La tabella mostra gli ultimi dodici mesi.</p>
            </figure>
        @endif
        <div class="economic-table" tabindex="0" role="region" aria-label="Serie mensile">
            <table class="demos-table">
                <caption>Ultimi dodici mesi · {{ $title }}</caption>
                <thead><tr><th scope="col">Mese</th>@foreach($fields as $field)<th scope="col">{{ $labels[$field][0] }} ({{ $labels[$field][1] }})</th>@endforeach</tr></thead>
                <tbody>@foreach(array_slice($data['rows'], -12) as $row)
                    <tr><th scope="row">{{ $row['month'] }}</th>@foreach($fields as $field)<td>{{ $format($row[$field], $labels[$field][1]) }}</td>@endforeach</tr>
                @endforeach</tbody>
            </table>
        </div>
    @elseif($section === 'commercio')
        <p>Importazioni ed esportazioni non sono operative. Il resto del mondo è un settore di confine senza transazioni registrate.</p>
    @else
        <div class="reading">
            <h2>Provenienza, unità e ipotesi</h2>
            <p>Modello {{ $data['model'] }}, periodo mensile, base prezzi {{ $data['base_year'] }}. Le statistiche derivano da stati e scambi simulati. CSV e JSON usano centesimi di euro per gli importi.</p>
            <p>Il PIL annuo di 3 miliardi EUR, l’inflazione del 2,3% e il rapporto debito/PIL del 90% appartengono alle ipotesi Methodos. Oikonomia non forza questi target. L’evidenza demografica UE-27 riguarda la popolazione iniziale e la mortalità.</p>
            <p>Le tre identità del PIL e il bilancio bancario sono riconciliati nel perimetro del modello. Riferimenti metodologici ESA 2010 e SNA 2025.</p>
        </div>
    @endif
    @if($section === 'ricchezza')
        <h2>Reddito disponibile dei nuclei per territorio</h2>
        <table class="demos-table">
            <caption>Mese {{ $last['month'] }} · EUR per area, totali dei nuclei all’inizio del passo</caption>
            <thead><tr><th scope="col">Area</th><th scope="col">Reddito</th></tr></thead>
            <tbody>@foreach(['Centro urbano', 'Cintura suburbana', 'Distretti rurali'] as $i => $area)
                <tr><th scope="row">{{ $area }}</th><td>{{ $format($last['income_by_region'][$i], 'EUR') }}</td></tr>
            @endforeach</tbody>
        </table>
    @endif
    <dl class="doc-aside">
        <dt>Snapshot Demos di origine</dt><dd><code>{{ $data['demos_origin'] }}</code></dd>
        <dt>Snapshot economico finale</dt><dd><code>{{ $data['final_sha256'] }}</code></dd>
        <dt>Generato il</dt><dd><time datetime="{{ $data['generated_at'] }}">{{ \Illuminate\Support\Carbon::parse($data['generated_at'])->tz('Europe/Rome')->format('d/m/Y H:i T') }}</time></dd>
    </dl>
</section>
@endsection
