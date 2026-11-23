@extends('layout')
@section('content')
@include('partials.intro', ['parent' => $section ? [route('research.experiments'), 'Laboratorio'] : null, 'eyebrow' => 'Experimentum'])
<section class="shell section">
    <nav class="actions" aria-label="Sezioni del laboratorio">
        @foreach($sections as $id => $label)
            <a class="button button-secondary" href="{{ route('research.experiments.section', $id) }}" @if($section === $id) aria-current="page" @endif>{{ $label }}</a>
        @endforeach
    </nav>
    <p><strong>Pilota tecnico offline, economia non calibrata.</strong> Il confronto fra governi è bloccato.</p>
    @switch($section)
    @case(null)
        <h2>Preregistrazione e ripetibilità</h2>
        <p>Il laboratorio verifica condizioni iniziali, shock e registri. Il primo pilota ha riprodotto {{ count($data['replicas']) }} repliche di {{ $data['protocol']['months'] }} mesi dello stesso percorso tecnico.</p>
        @break
    @case('protocolli')
        <h2>{{ $data['protocol']['id'] }}</h2>
        <p>{{ $data['protocol']['hypothesis'] }}.</p>
        <p>SHA-256 <code class="break-all">{{ $data['protocol_sha256'] }}</code></p>
        @break
    @case('scenari')
        <h2>Maturità A–F</h2>
        <dl class="method-details">
            @foreach($data['regimes'] as $id => $regime)
                <dt>Scenario {{ $id }}</dt><dd>{{ $regime['status'] === 'technical-path' ? 'Percorso tecnico' : 'Dimostrazione istituzionale' }}. Mancano {{ implode(', ', $regime['missing']) }}.</dd>
            @endforeach
        </dl>
        @break
    @case('repliche')
        <h2>Replay da checkpoint</h2>
        <dl class="method-details">
            @foreach($data['replicas'] as $replica)
                <dt>{{ $replica['id'] }}</dt><dd>{{ $replica['status'] }}. Shock produttivo al mese {{ $replica['shock']['start'] }}.</dd>
            @endforeach
        </dl>
        @break
    @case('indicatori')
        <h2>Definizioni e unità</h2>
        <dl class="method-details">
            @foreach($data['indicators'] as $key => $indicator)
                <dt>{{ $key }}</dt><dd>{{ $indicator['formula'] }}. Unità {{ $indicator['unit'] }}.</dd>
            @endforeach
        </dl>
        @break
    @case('risultati')
        <h2>PIL nominale medio delle repliche tecniche</h2>
        <dl class="method-details">
            @foreach($data['aggregates'] as $row)
                <dt>Mese {{ $row['month'] }}</dt><dd>{{ $row['indicators']['gdp']['mean'] === null ? 'Indisponibile' : number_format($row['indicators']['gdp']['mean'] / 100, 2, ',', '.').' EUR' }}. Valori mancanti: {{ $row['indicators']['gdp']['missing'] }}.</dd>
            @endforeach
        </dl>
        @break
    @case('confronti')
        <h2>B–A · Non ammissibile</h2>
        <p>Lo scenario A manca di una democrazia rappresentativa pienamente operativa. Calibrazione, equivalenza istituzionale e potenza statistica devono essere verificate prima di stimare differenze fra regimi.</p>
        @break
    @case('metodologia')
        <h2>Shock e misure</h2>
        <p>Il calendario esogeno è fissato prima del replay. I risultati sono descrittivi e includono variabilità e dati mancanti. Le differenze fra repliche non identificano un effetto di governo.</p>
        @break
    @case('trasparenza')
        <h2>Esportazioni e hash</h2>
        <ul>
            @foreach(['json', 'csv', 'sha256'] as $format)
                <li><a href="{{ route('research.experiments.export', $format) }}">Scarica {{ strtoupper($format) }}</a></li>
            @endforeach
        </ul>
        <p>SHA-256 fascicolo <code class="break-all">{{ $checksum }}</code></p>
        @break
    @endswitch
</section>
@endsection
