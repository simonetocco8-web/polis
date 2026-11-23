@extends('layout')
@section('content')
@include('partials.intro', ['parent' => [route('nova.economy'), 'Economia'], 'eyebrow' => 'Stabilitas · Audit tecnico'])
@php
    $eventLabels = [
        'contraction_employment' => 'Occupazione in calo oltre il 10%',
        'production_crisis' => 'Produzione in calo oltre il 30%',
        'persistent_demand_contraction' => 'Domanda in calo oltre il 25% per almeno sei mesi',
        'first_firm_failure' => 'Prima cessazione',
        'firm_credit_cap' => 'Prima impresa al limite di credito, a fine mese',
        'household_credit_cap' => 'Primo nucleo al limite di credito, a fine mese',
        'public_credit_cap' => 'Raggiungimento del tetto al credito pubblico',
        'credit_arrears' => 'Prima insufficienza nel servizio del debito pubblico',
        'public_transfers_shortfall' => 'Primi trasferimenti pubblici razionati',
        'zero_median_income' => 'Mediana del reddito disponibile pari a zero',
        'persistent_low_active_firms' => 'Imprese attive sotto o al 10% per almeno sei mesi',
    ];
    $labels = ['control' => 'Baseline v0.4.0', 'R' => 'Arrotondamento simmetrico', 'C' => 'Distribuzione bancaria', 'B+C+E' => 'Ingresso, distribuzione, riserva', 'D' => 'Tetto di credito pubblico ridotto'];
    $euro = static fn ($cents) => number_format($cents / 100, 2, ',', '.').' EUR';
@endphp
<section class="shell section">
    <p class="empty"><strong>Prove tecniche non calibrate.</strong> Le varianti misurano risposte del simulatore. Non rappresentano governi, previsioni o valutazioni empiriche.</p>
    <p>Il controllo riproduce l’apertura e lo stato finale dei 600 mesi di Oikonomia v0.4.0. Al primo mese, {{ number_format($baseline['first_month']['autonomous_to_unemployment'], 0, ',', '.') }} autonomi di apertura risultano disoccupati. Il matching iniziale è bloccato per costruzione.</p>
    <p><a class="text-link" href="{{ route('nova.stability.export', 'csv') }}">Scarica CSV aggregato</a> · <a class="text-link" href="{{ route('nova.stability.export', 'json') }}">Scarica JSON con provenienza</a></p>
    <h2>Cronologia della traiettoria originale</h2>
    <p>Le soglie di contrazione sono relative al primo mese. Per le soglie persistenti è indicato l’inizio del tratto. L’ordine temporale, da solo, non identifica una causa.</p>
    <dl class="method-details">
        @foreach($eventLabels as $key => $label)
            <dt>{{ $label }}</dt><dd>{{ $baseline['timeline'][$key] === null ? 'Non osservata' : 'Mese '.$baseline['timeline'][$key] }}</dd>
        @endforeach
    </dl>
    <h2>Serie del controllo storico</h2>
    @foreach($charts as $chart)
        <figure class="economic-chart">
            <figcaption>{{ $chart['label'] }} · mesi 1–600</figcaption>
            <svg viewBox="0 0 600 148" aria-hidden="true" focusable="false"><path d="M10 20H590M10 77H590M10 135H590" class="economic-grid"/><polyline points="{{ $chart['points'] }}" class="economic-line"/></svg>
            <p>Minimo {{ number_format($chart['low'], 0, ',', '.') }}, massimo {{ number_format($chart['high'], 0, ',', '.') }} {{ $chart['unit'] }}. Serie mensile nel download.</p>
        </figure>
    @endforeach
    <h2>Confronto sullo stesso snapshot standard</h2>
    <div class="economic-table" tabindex="0" role="region" aria-label="Confronto delle prove standard">
    <table class="demos-table">
        <caption>Cinque esecuzioni, 600 mesi ciascuna, seed 20261122</caption>
        <thead><tr><th scope="col">Prova</th><th scope="col">PIL anno 1</th><th scope="col">PIL anno 50</th><th scope="col">Imprese attive finali</th><th scope="col">Ingressi totali</th><th scope="col">Disoccupazione finale</th></tr></thead>
        <tbody>
        @foreach($data['standard'] as $run)
            <tr><th scope="row">{{ $labels[$run['experiment']] }}</th>
            <td>{{ $euro($run['metrics']['first_year_gdp_cents']) }}</td><td>{{ $euro($run['metrics']['last_year_gdp_cents']) }}</td>
            <td>{{ $run['metrics']['last_active_firms'] }}</td><td>{{ $run['metrics']['total_entries'] }}</td>
            <td>{{ number_format($run['metrics']['last_unemployment_percent'], 2, ',', '.') }}%</td></tr>
        @endforeach
        </tbody>
    </table>
    </div>
    <h2>Flussi monetari e fragilità</h2>
    <p>Il controllo ha riscosso in banca {{ $euro($baseline['metrics']['total_interest_cents']) }} di interessi. Le nuove erogazioni, i rimborsi, gli interessi, le perdite, le distribuzioni e le obbligazioni pubbliche non pagate sono distinti nel JSON.</p>
    <table class="demos-table">
        <caption>Regolamento bancario e trasferimenti del controllo, mese 600</caption>
        <thead><tr><th scope="col">Flusso</th><th scope="col">Importo</th></tr></thead>
        @php($month = $baseline['rows'][599])
        <tbody>
            <tr><th scope="row">Nuove erogazioni bancarie</th><td>{{ $euro(array_sum($month['origination'])) }}</td></tr>
            <tr><th scope="row">Rimborsi di capitale</th><td>{{ $euro(array_sum($month['principal'])) }}</td></tr>
            <tr><th scope="row">Interessi incassati</th><td>{{ $euro(array_sum($month['interest'])) }}</td></tr>
            <tr><th scope="row">Stralci bancari</th><td>{{ $euro($month['bank_credit_losses']) }}</td></tr>
            <tr><th scope="row">Servizio del debito pubblico non pagato</th><td>{{ $euro($month['public_service_shortfall']) }}</td></tr>
            <tr><th scope="row">Trasferimenti pubblici dovuti</th><td>{{ $euro($month['transfers_due']) }}</td></tr>
            <tr><th scope="row">Trasferimenti pubblici pagati</th><td>{{ $euro($month['transfers_paid']) }}</td></tr>
        </tbody>
    </table>
    @php($last = $baseline['rows'][599])
    <dl class="method-details">
        <dt>Reddito reale mediano finale</dt><dd>{{ $euro($last['real_median_income']) }}</dd>
        <dt>Nuclei finali sotto il fabbisogno essenziale</dt><dd>{{ number_format($last['deprived_households'], 0, ',', '.') }}</dd>
        <dt>Depositi delle famiglie alla fine</dt><dd>{{ $euro($last['household_deposits']) }}</dd>
        <dt>Posizione finanziaria netta aggregata dei settori non bancari</dt><dd>{{ $euro($last['nonbank_net_financial']) }}</dd>
        <dt>Capitale privato finale</dt><dd>{{ number_format($last['capital_units'], 0, ',', '.') }} unità fisiche</dd>
    </dl>
    <div class="economic-table" tabindex="0" role="region" aria-label="Settori produttivi">
    <table class="demos-table">
        <caption>Settori del controllo, mesi 1 e 600</caption>
        <thead><tr><th scope="col">Settore</th><th scope="col">Imprese al mese 1</th><th scope="col">Imprese al mese 600</th><th scope="col">Unità prodotte al mese 1</th><th scope="col">Unità prodotte al mese 600</th></tr></thead>
        <tbody>@foreach(['Produzione', 'Commercio', 'Agricoltura', 'Industria', 'Servizi'] as $i => $sector)
            <tr><th scope="row">{{ $sector }}</th><td>{{ $baseline['rows'][0]['active_by_sector'][$i] }}</td><td>{{ $last['active_by_sector'][$i] }}</td><td>{{ $baseline['rows'][0]['sector_output'][$i] }}</td><td>{{ $last['sector_output'][$i] }}</td></tr>
        @endforeach</tbody>
    </table>
    </div>
    <h2>Repliche esplorative e sensibilità</h2>
    <p>Trenta corse ridotte, tre repliche accoppiate per variante e controllo, 120 mesi. Una replica include recessione. Il confronto misura la differenza rispetto al controllo con lo stesso seed e lo stesso shock.</p>
    <div class="economic-table" tabindex="0" role="region" aria-label="Dispersione delle repliche">
    <table class="demos-table">
        <caption>Differenza del PIL negli ultimi dodici mesi</caption>
        <thead><tr><th scope="col">Fattore</th><th scope="col">Minimo</th><th scope="col">Mediana</th><th scope="col">Massimo</th></tr></thead>
        @php($factors = ['R' => 'Arrotondamento simmetrico', 'A' => 'Continuità degli autonomi', 'B' => 'Ingresso di imprese', 'C' => 'Distribuzione bancaria 50%', 'D' => 'Tetto di credito pubblico ridotto', 'E' => 'Riserva di intermedi maggiore', 'F' => 'Soglia di insolvenza a sei mesi', 'B+C+E' => 'Ingresso, distribuzione, riserva', 'C25' => 'Distribuzione bancaria 25%'])
        <tbody>@foreach($data['paired_deltas'] as $id => $metrics)
            @php($sample = $metrics['last_year_gdp_cents'])
            <tr><th scope="row">{{ $id }} · {{ $factors[$id] }}</th><td>{{ $euro($sample['min']) }}</td><td>{{ $euro($sample['median']) }}</td><td>{{ $euro($sample['max']) }}</td></tr>
        @endforeach</tbody>
    </table>
    </div>
    <p class="reading">Il campione è esplorativo. Le fonti economiche UE-27 sono riferimenti per una futura stima. La contrazione del controllo resta un risultato osservato. Il PIL per reddito include un surplus residuale. La quadratura delle transazioni e il confronto con il registro non conferiscono validazione empirica.</p>
</section>
@endsection
