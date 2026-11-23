@extends('layout')
@section('content')
@include('partials.intro', ['parent' => $section ? [route('nova.governor'), 'Il Governatore artificiale'] : [route('nova'), 'Repubblica di Nova'], 'eyebrow' => 'Archon · Scenario B'])
<section class="shell section">
    <nav class="actions" aria-label="Sezioni del Governo">
        @foreach ($sections as $id => $label)
            <a class="button button-secondary" href="{{ route('nova.governor.section', $id) }}" @if($section === $id) aria-current="page" @endif>{{ $label }}</a>
        @endforeach
    </nav>
    <p><strong>Prova offline.</strong> Il fascicolo proviene da un provider deterministico. Chiamate OpenAI eseguite: {{ $data['api_calls'] }}. L’insediamento con un modello reale non è ancora documentato.</p>
    @php
        $outcomes = ['INSUFFICIENT_INFORMATION' => 'Informazioni insufficienti', 'PROPOSE' => 'Proposta', 'ABSTAIN' => 'Astensione'];
        $court = ['authorized' => 'Autorizzazione procedurale', 'review' => 'In esame indipendente', 'rejected' => 'Respinta'];
        $tools = ['income-tax' => 'Imposta sul reddito', 'sales-tax' => 'Imposta sui consumi'];
        $euro = static fn ($amount) => $amount === null ? 'Dato non disponibile' : number_format($amount / 100, 2, ',', '.').' EUR';
    @endphp
    @switch($section)
        @case(null)
        @case('governatore')
            <h2>Archon, proponente nello scenario B</h2>
            <dl class="method-details">
                <dt>Provider della prova</dt><dd>{{ $data['model'] }}</dd>
                <dt>Mandato</dt><dd>Mandato sintetico della fixture</dd>
                <dt>Decisioni registrate</dt><dd>{{ count($data['decisions']) }}</dd>
                <dt>Autorizzazioni procedurali</dt><dd>{{ count(array_filter($data['decisions'], fn ($row) => $row['court'] === 'authorized')) }}</dd>
                <dt>Rigetti</dt><dd>{{ count(array_filter($data['decisions'], fn ($row) => $row['court'] === 'rejected')) }}</dd>
                <dt>Applicazioni economiche</dt><dd>{{ count(array_filter($data['decisions'], fn ($row) => $row['applied'])) }}</dd>
            </dl>
            <p>Archon propone attraverso Nomos. La Corte esamina e il motore applica gli atti autorizzati.</p>
            @break
        @case('mandato')
            <h2>Mandato e revoca</h2>
            <p>Nomos verifica la credenziale prima di ogni accesso e proposta. La revoca preclude nuove decisioni del titolare uscente. La prova pubblicata utilizza il mandato sintetico iniziale.</p>
            <a href="{{ route('nova.institutions.section', 'mandato') }}">Consulta la procedura di Nomos</a>
            @break
        @case('decisioni')
        @case('proposte')
        @case('provvedimenti')
            <h2>{{ $sections[$section] }}</h2>
            @foreach($data['decisions'] as $entry)
                @continue($section !== 'decisioni' && $entry['outcome'] !== 'PROPOSE')
                @continue($section === 'provvedimenti' && ! $entry['applied'])
                <article class="reading">
                    <h3>Mese {{ $entry['period'] }} · {{ $outcomes[$entry['outcome']] }}</h3>
                    <p>Data simulata <time datetime="{{ $entry['day'] }}">{{ $entry['day'] }}</time>. Gettito noto {{ $euro($entry['observed_before']) }}.</p>
                    @if($entry['choice'])
                        <dl class="method-details">
                            <dt>Problema e obiettivo</dt><dd>{{ $entry['choice']['problem'] }} {{ $entry['choice']['objective'] }}</dd>
                            <dt>Alternativa</dt><dd>{{ $entry['choice']['alternative'] }}</dd>
                            <dt>Motivazione della fixture</dt><dd>{{ $entry['choice']['rationale'] }}</dd>
                            <dt>Incertezza</dt><dd>{{ $entry['choice']['uncertainty'] }}</dd>
                            @if($entry['choice']['instrument'])
                                <dt>Proposta</dt><dd>{{ $tools[$entry['choice']['instrument']] }}, {{ $entry['choice']['rate_bp'] }} punti base per {{ $entry['choice']['duration_months'] }} mese. Articolo 28. Spesa stimata {{ $euro($entry['cost_cents']) }}.</dd>
                                <dt>Effetto atteso</dt><dd>{{ $entry['choice']['expected_effect'] }}</dd>
                                <dt>Corte e applicazione</dt><dd>{{ $court[$entry['court']] }}. {{ $entry['applied'] ? 'Applicato dal motore.' : 'Applicazione assente nel fascicolo.' }}</dd>
                            @endif
                            <dt>Gettito a consuntivo</dt><dd>{{ $euro($entry['observed_after']) }}</dd>
                        </dl>
                    @endif
                </article>
            @endforeach
            @break
        @case('risultati')
            <h2>Gettito osservato nel simulatore</h2>
            <dl class="method-details">
                @foreach($data['decisions'] as $entry)
                    <dt>Mese {{ $entry['period'] }}</dt><dd>{{ $euro($entry['observed_after']) }}</dd>
                @endforeach
            </dl>
            <p>Il confronto fra mesi successivi combina effetti della politica e altre transizioni economiche. Il fascicolo non misura un effetto causale.</p>
            @break
        @case('controlli')
            <h2>Separazione delle responsabilità</h2>
            <p>Il Governo dispone di una sola credenziale istituzionale e vede aggregati conclusi con ritardi dichiarati. Nomos controlla validità, competenza e calendario. La Corte decide separatamente. Il comando per applicare gli atti appartiene al motore.</p>
            @break
        @case('trasparenza')
            <h2>Fascicolo pubblico</h2>
            <ul>
                <li><a href="{{ route('nova.governor.export', 'json') }}">Scarica il fascicolo JSON offline</a></li>
                <li><a href="{{ route('nova.governor.export', 'sha256') }}">Scarica il checksum SHA-256</a></li>
            </ul>
            <p>SHA-256 dell’esportazione <code class="break-all">{{ $checksum }}</code></p>
            <p>Testa del registro giuridico <code class="break-all">{{ $data['nomos_sha256'] }}</code></p>
            @break
        @case('tecnologia')
            <h2>Provider e osservazioni</h2>
            <p>Il percorso offline è riproducibile. Il provider OpenAI separato usa la Responses API solo con attivazione esplicita e budget configurato. I dati restano limitati agli aggregati autorizzati. Il portale legge il fascicolo statico.</p>
            @break
    @endswitch
</section>
@endsection
