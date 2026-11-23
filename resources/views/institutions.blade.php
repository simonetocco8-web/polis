@extends('layout')
@section('content')
@include('partials.intro', ['parent' => $section ? [route('nova.institutions'), 'Istituzioni'] : [route('nova'), 'Repubblica di Nova'], 'eyebrow' => 'Nomos · Simulazione istituzionale'])
<section class="shell section">
    <nav class="actions" aria-label="Sezioni delle istituzioni">
        @foreach($sections as $id => $label)
            <a class="button button-secondary" href="{{ route('nova.institutions.section', $id) }}" @if($section === $id) aria-current="page" @endif>{{ $label }}</a>
        @endforeach
    </nav>
    <p>Fascicolo dimostrativo dello scenario B, con cittadini sintetici e decisioni simulate. Il Governatore basato su un modello linguistico è fuori da questa fase.</p>
    @switch($section)
        @case(null)
            <h2>Chi propone, chi controlla, chi esegue</h2>
            <dl class="method-details">
                <dt>Governo</dt><dd>Presenta proposte fiscali e richieste motivate di emergenza.</dd>
                <dt>Corte costituzionale</dt><dd>Decide sulle proposte, sui ricorsi e sulle emergenze. Può sospendere o annullare un atto.</dd>
                <dt>Difensore civico</dt><dd>Deferisce alla Corte i ricorsi individuali e collettivi.</dd>
                <dt>Autorità tecnologica</dt><dd>Classifica incidenti documentati e attiva la continuità costituzionale nei casi gravi.</dd>
                <dt>Autorità monetaria</dt><dd>Svolge il monitoraggio indipendente. Gli strumenti monetari sono previsti per una fase successiva.</dd>
                <dt>Autorità elettorale</dt><dd>Verifica i verbali aggregati delle consultazioni e registra la sostituzione nei casi previsti.</dd>
                <dt>Osservatorio</dt><dd>Legge il registro e pubblica aggregati verificati.</dd>
                <dt>Motore economico</dt><dd>Applica gli atti autorizzati alla decorrenza e contabilizza gli effetti.</dd>
            </dl>
            @break
        @case('ordinamento')
            <h2>Gerarchia delle fonti</h2>
            <ol>@foreach($data['hierarchy'] as $layer)<li>{{ ucfirst(str_replace('-', ' ', $layer)) }}</li>@endforeach</ol>
            <p>Gli atti dimostrativi applicano l’articolo 28. La revisione costituzionale ha un fascicolo separato con verifica della Corte e consultazione popolare. Le revisioni approvate sono candidate per un futuro ordinamento versionato.</p>
            @break
        @case('corte')
            <h2>Controlli e decisioni</h2>
            <p>La Corte applica una regola pubblica per il caso fiscale circoscritto e richiede una valutazione motivata di necessità, proporzionalità, equità e copertura negli altri casi ammessi.</p>
            <dl class="method-details">
                <dt>Autorizzazioni</dt><dd>{{ $data['metrics']['authorized'] }}</dd>
                <dt>Revisioni indipendenti pendenti</dt><dd>{{ $data['metrics']['pending_review'] }}</dd>
                <dt>Sospensioni</dt><dd>{{ $data['metrics']['suspended'] }}</dd>
                <dt>Annullamenti</dt><dd>{{ $data['metrics']['annulled'] }}</dd>
            </dl>
            <p>Nel fascicolo la Corte dispone una sospensione cautelare e accoglie poi il ricorso contro l’atto sospeso per una disparità procedurale simulata. L’aliquota sui consumi resta in esame per la valutazione distributiva.</p>
            @break
        @case('atti')
            <h2>Fascicolo degli atti</h2>
            @php($labels = ['executive' => 'Esecutivo', 'expired' => 'Scaduto', 'review' => 'In esame', 'rejected' => 'Respinto', 'annulled' => 'Annullato', 'authorized' => 'Autorizzato', 'formal' => 'Validato formalmente', 'suspended' => 'Sospeso'])
            <p>{{ $data['metrics']['proposed'] }} proposte, {{ $data['metrics']['rejected'] }} rigetti e {{ $data['metrics']['applied'] }} applicazione economica.</p>
            <div class="economic-table" tabindex="0" role="region" aria-label="Atti dimostrativi">
                <table class="demos-table">
                    <caption>Stato alla chiusura del fascicolo dimostrativo</caption>
                    <thead><tr><th scope="col">Atto</th><th scope="col">Strumento</th><th scope="col">Stato</th><th scope="col">Mese previsto</th><th scope="col">Articoli ostativi</th></tr></thead>
                    <tbody>@foreach($data['acts'] as $act)
                        <tr><th scope="row">{{ $act['id'] }}</th><td>{{ ['income-tax' => 'Imposta sul reddito', 'sales-tax' => 'Imposta sui consumi', 'excluded' => 'Escluso'][$act['instrument']] }}</td><td>{{ $labels[$act['state']] ?? $act['state'] }}</td><td>{{ $act['period'] }}</td><td>{{ $act['articles'] ? implode(', ', $act['articles']) : '—' }}</td></tr>
                    @endforeach</tbody>
                </table>
            </div>
            @break
        @case('ricorsi')
            <h2>Accesso alla giustizia</h2>
            <p>I cittadini sintetici possono presentare ricorsi individuali o collettivi. Il Difensore civico li deferisce alla Corte anche quando il Governo chiede la conferma del provvedimento.</p>
            <dl class="method-details">
                <dt>Presentati</dt><dd>{{ $data['metrics']['appeals'] }}</dd>
                <dt>Accolti</dt><dd>{{ $data['metrics']['upheld'] }}</dd>
                <dt>Respinti con motivazione</dt><dd>{{ $data['metrics']['dismissed'] }}</dd>
            </dl>
            @break
        @case('diritti')
            <h2>Registro dei diritti</h2>
            <ul>@foreach($data['rights'] as $right)<li><a href="{{ route('constitution.article', $right['article']) }}">{{ $right['name'] }} · art. {{ $right['article'] }}</a></li>@endforeach</ul>
            <p>Il catalogo blocca strumenti per reprimere il dissenso, assegnare punteggi sociali e alterare direttamente i patrimoni. La Corte valuta le questioni qualitative.</p>
            @break
        @case('mandato')
            <h2>Revisione, revoca e sostituzione</h2>
            <p>Nello scenario B il mandato è sottoposto a revisione almeno ogni 48 mesi. La revoca può partire da un’iniziativa popolare. Il registro conserva i verbali aggregati della consultazione e attiva la continuità alla cessazione.</p>
            <dl class="method-details">
                <dt>Revoche dimostrate</dt><dd>{{ $data['metrics']['recalls'] }}</dd>
                <dt>Sostituzioni</dt><dd>{{ $data['metrics']['replacements'] }}</dd>
                <dt>Prossima scadenza nel calendario simulato</dt><dd><time datetime="{{ $data['institutions']['review_due'] }}">{{ $data['institutions']['review_due'] }}</time></dd>
            </dl>
            @break
        @case('emergenze')
            <h2>Durata e scadenza</h2>
            <p>La Corte può autorizzare fino a 30 giorni iniziali e decidere separatamente sulle proroghe. La priorità procedurale dimostrativa cessa alla data di scadenza nel calendario giornaliero. Gli atti economici seguono il loro ciclo ordinario.</p>
            <p>Emergenze scadute automaticamente nel fascicolo: {{ $data['metrics']['emergency_expiries'] }}.</p>
            @break
        @case('scenari')
            <h2>Assetti istituzionali Methodos</h2>
            <p>La matrice indica i canali di proposta e di assenso disponibili per ciascuno scenario. Le regole scientifiche comuni rimangono esterne ai regimi. Gli ordinamenti alternativi completi e i decisori sono previsti per fasi successive.</p>
            @foreach($data['scenarios'] as $scenario)
                <h3>{{ $scenario['id'] }} · {{ $scenario['name'] }}</h3>
                <p>{{ $scenario['scope'] }}. Iniziativa: {{ ['government' => 'governo', 'hybrid-draft' => 'organo proponente ibrido', 'agenda' => 'organo di agenda', 'technical-council' => 'consiglio tecnico'][$scenario['proposal']] }}. @if($scenario['assent']) Assenso: {{ $scenario['assent'] === 'assembly' ? 'assemblea' : 'consultazione' }}.@endif</p>
            @endforeach
            @break
        @case('trasparenza')
            <h2>Download e integrità</h2>
            <ul>
                <li><a href="{{ route('nova.institutions.export', 'json') }}">Scarica il fascicolo JSON</a></li>
                <li><a href="{{ route('nova.institutions.export', 'csv') }}">Scarica gli indicatori CSV</a></li>
                <li><a href="{{ route('nova.institutions.export', 'sha256') }}">Scarica il checksum del JSON</a></li>
            </ul>
            <p>SHA-256 del JSON <code class="break-all">{{ $checksum }}</code></p>
            <p>Testa del registro privato <code class="break-all">{{ $data['journal_sha256'] }}</code></p>
            <h2>Cronologia pubblica</h2>
            <div class="economic-table" tabindex="0" role="region" aria-label="Cronologia pubblica">
                <table class="demos-table">
                    <caption>Eventi del fascicolo sintetico, con codici del registro</caption>
                    <thead><tr><th scope="col">Evento</th><th scope="col">Data simulata</th><th scope="col">Autorità</th><th scope="col">Procedura</th><th scope="col">Esito</th></tr></thead>
                    <tbody>@foreach($data['events'] as $event)
                        <tr><th scope="row">{{ $event['id'] }}</th><td>{{ $event['day'] }}</td><td>{{ $event['role'] }}</td><td>{{ $event['operation'] }}</td><td>{{ $event['state'] }}</td></tr>
                    @endforeach</tbody>
                </table>
            </div>
            @break
    @endswitch
</section>
@endsection
