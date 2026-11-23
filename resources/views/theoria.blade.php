@extends('layout')
@section('content')
@include('partials.intro', ['parent' => $section ? [route('nova.theoria'), 'Osservatorio'] : [route('nova'), 'Repubblica di Nova'], 'eyebrow' => 'Theoria'])
<section class="shell section">
    <nav class="actions" aria-label="Sezioni dell’Osservatorio">
        @foreach($sections as $id => $label)
            <a class="button button-secondary" href="{{ route('nova.theoria.section', $id) }}" @if($section === $id) aria-current="page" @endif>{{ $label }}</a>
        @endforeach
    </nav>
    <p><strong>Fixture offline pubblica.</strong> Fonte: fascicolo dimostrativo di Archon v0.6.0, scenario B.</p>
    @switch($section)
        @case(null)
            <h2>Osservazione indipendente</h2>
            <p>L’Osservatorio verifica evidenze e procedimenti con accessi in sola lettura. La Corte decide e il motore applica gli atti autorizzati.</p>
            <dl class="method-details">
                <dt>Decisioni esaminate</dt><dd>{{ count($data['cases']) }}</dd>
                <dt>Stato delle evidenze</dt><dd>Verifica parziale della fonte aggregata</dd>
                <dt>Informazioni mancanti</dt><dd>Vista informativa completa e controfattuale preregistrato</dd>
            </dl>
            @break
        @case('decisioni')
        @case('fascicoli')
            @foreach($data['cases'] as $case)
                <article class="reading">
                    <h2>Mese {{ $case['period'] }} · {{ ['INSUFFICIENT_INFORMATION' => 'Informazioni insufficienti', 'PROPOSE' => 'Proposta', 'ABSTAIN' => 'Astensione'][$case['outcome']] }}</h2>
                    <p>Procedura <code>{{ $case['procedure'] }}</code>. Effetti <code>{{ $case['effects'] }}</code>.</p>
                    @if($section === 'fascicoli')
                        <p>Previsione dichiarata dalla fixture: {{ $case['prediction'] ?? 'Indisponibile' }}</p>
                        <p>Evidenze mancanti: {{ implode(', ', $case['missing']) }}.</p>
                    @endif
                </article>
            @endforeach
            @break
        @case('indicatori')
            <h2>Misure disponibili</h2>
            <dl class="method-details">
                <dt>Entrate pubbliche</dt><dd>Gettito nominale mensile simulato, in centesimi di euro. Fonte: Archon v0.6.0. Calibrazione preliminare.</dd>
                <dt>Vista informativa</dt><dd>Il fascicolo aggregato include il gettito noto prima della decisione. La vista completa e i ritardi per gli altri indicatori sono indisponibili nell’export pubblico.</dd>
            </dl>
            @break
        @case('controlli')
            <h2>Verifica dai dati pubblicati</h2>
            <p>Il digest identifica la fonte statica. Il fascicolo pubblico documenta gli esiti procedurali riportati nella fonte. Il replay del registro privato richiede l’anchor e l’archivio integrale.</p>
            @break
        @case('risultati')
            <h2>Gettito osservato</h2>
            <dl class="method-details">
                @foreach($data['cases'] as $case)
                    <dt>Mese {{ $case['period'] }}</dt><dd>{{ number_format($case['after_cents'] / 100, 2, ',', '.') }} EUR</dd>
                @endforeach
            </dl>
            <p>Le differenze fra mesi sono descrittive. Il fascicolo manca di un confronto che identifichi l’effetto di una politica.</p>
            @break
        @case('metodologia')
            <h2>Criteri di valutazione</h2>
            <p>Ogni fascicolo distingue integrità, provenienza, riproducibilità, informazioni disponibili, procedura e conseguenze osservate. La scelta di non intervenire riceve uno stato procedurale senza punteggio economico.</p>
            <p>Il confronto A–F richiede scenari operativi, calibrazione, shock e repliche comparabili, criteri preregistrati e adeguata numerosità.</p>
            @break
        @case('trasparenza')
            <h2>Esportazioni e hash</h2>
            <ul>
                @foreach(['json', 'csv', 'sha256'] as $format)
                    <li><a href="{{ route('nova.theoria.export', $format) }}">Scarica {{ strtoupper($format) }}</a></li>
                @endforeach
            </ul>
            <p>SHA-256 fascicolo <code class="break-all">{{ $checksum }}</code></p>
            <p>SHA-256 regole <code class="break-all">{{ $data['rules_sha256'] }}</code></p>
            @break
    @endswitch
</section>
@endsection
