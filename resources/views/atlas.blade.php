@extends('layout')
@section('content')
@include('partials.intro', ['parent' => [route('nova'), 'Repubblica di Nova'], 'eyebrow' => 'Atlante statistico'])
<section class="shell section">
    <nav class="actions" aria-label="Atlante statistico">
        @foreach(\App\Http\Controllers\AtlasController::PAGES as $id => [$label])
            <a class="button button-secondary" href="{{ route('nova.atlas', $id) }}" @if($id === $section) aria-current="page" @endif>{{ $label }}</a>
        @endforeach
    </nav>
    <p class="empty">Snapshot iniziale · Popolazione sintetica · Calibrazione {{ $data['calibration'] }}. Nessun esperimento confermativo.</p>
    <dl class="stats">
        <div><dt>Residenti</dt><dd>{{ number_format($data['totals']['population'], 0, ',', '.') }}</dd></div>
        <div><dt>Nuclei residenti</dt><dd>{{ number_format($data['totals']['households'], 0, ',', '.') }}</dd></div>
        <div><dt>Imprese iniziali</dt><dd>{{ number_format($data['totals']['firms'], 0, ',', '.') }}</dd></div>
    </dl>
    <p><a class="text-link" href="{{ route('nova.statistics', 'csv') }}">Scarica CSV aggregato</a> · <a class="text-link" href="{{ route('nova.statistics', 'json') }}">Scarica JSON aggregato</a></p>

    @if($section === 'demografia')
        <div class="reading">
            <h2>Piramide demografica</h2>
            <p>Età media sintetica {{ number_format($data['totals']['mean_age_years'], 2, ',', '.') }} anni. Le classi di sesso seguono le categorie della fonte.</p>
            @php($top = max([...array_values($data['groups']['age_f']), ...array_values($data['groups']['age_m'])]))
            <table class="demos-table">
                <caption>Residenti per fascia di età e categoria demografica</caption>
                <thead><tr><th scope="col">F</th><th scope="col">Età</th><th scope="col">M</th></tr></thead>
                <tbody>
                    @php($bands = $data['groups']['age'])
                    @php(uksort($bands, static fn ($a, $b) => (int) $b <=> (int) $a))
                    @foreach($bands as $band => $count)
                        <tr><td><meter class="demos-left" aria-hidden="true" min="0" max="{{ $top }}" value="{{ $data['groups']['age_f'][$band] }}"></meter>{{ $data['groups']['age_f'][$band] }}</td><th scope="row">{{ $band }}</th><td><meter aria-hidden="true" min="0" max="{{ $top }}" value="{{ $data['groups']['age_m'][$band] }}"></meter>{{ $data['groups']['age_m'][$band] }}</td></tr>
                    @endforeach
                </tbody>
            </table>
        </div>
    @endif
    @if($section === 'occupazione')
        <p>Disoccupazione sintetica iniziale: {{ number_format($data['totals']['unemployment_percent'], 2, ',', '.') }}% della forza lavoro. Il tasso iniziale è un parametro di generazione.</p>
    @endif
    @if($section === 'salute')
        <p>{{ $data['definitions']['health'] }} L’aspettativa di vita di Nova resta da stimare.</p>
    @endif
    <div class="card-grid">
        @foreach($groups as $group => $label)
            @php($max = max(1, max($data['groups'][$group])))
            <section class="card">
                <h2 class="text-2xl">{{ $label }}</h2>
                <table class="demos-table">
                    <thead><tr><th scope="col">Categoria</th><th scope="col">Totale ({{ \App\Statistics\Demos::GROUPS[$group] }})</th></tr></thead>
                    <tbody>
                        @php($rows = $data['groups'][$group])
                        @if($group === 'age') @php(uksort($rows, static fn ($a, $b) => (int) $a <=> (int) $b)) @endif
                        @foreach($rows as $name => $count)
                            <tr><th scope="row">{{ $name }}</th><td>{{ number_format($count, 0, ',', '.') }}<meter aria-hidden="true" min="0" max="{{ $max }}" value="{{ $count }}"></meter></td></tr>
                        @endforeach
                    </tbody>
                </table>
            </section>
        @endforeach
    </div>

    <section class="reading">
        <h2>Provenienza dello snapshot</h2>
        <dl class="doc-aside">
            <dt>SHA-256 dello snapshot</dt><dd><code>{{ $data['snapshot_sha256'] }}</code></dd>
            <dt>Versione del generatore</dt><dd>{{ $data['generator'] }}</dd>
            <dt>Profilo e mese</dt><dd>{{ $data['profile'] }} · mese {{ $data['month'] }}</dd>
            <dt>Generato il</dt><dd><time datetime="{{ $data['generated_at'] }}">{{ \Illuminate\Support\Carbon::parse($data['generated_at'])->tz('Europe/Rome')->format('d/m/Y H:i T') }}</time></dd>
            <dt>Fonti</dt><dd>@foreach($data['sources'] as $source)<a href="{{ $source['url'] }}">{{ $source['agency'] }} · {{ $source['code'] }} · {{ $source['period'] }}</a>@if(!$loop->last)<br>@endif @endforeach</dd>
        </dl>
        @if($section === 'generazione')
            <h2>Ipotesi macroeconomiche</h2>
            <p>PIL annuo 3 miliardi di euro, PIL pro capite 30.000 euro, inflazione 2,3%, debito/PIL 90% e aspettativa di vita 81 anni sono target di Methodos. Demos non stima queste grandezze. Il Polis Index resta indisponibile.</p>
            <p>Il portale legge soltanto aggregati. I microdati restano nell’ambiente di simulazione.</p>
        @endif
    </section>
</section>
@endsection
