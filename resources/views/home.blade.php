@extends('layout')
@section('content')
<section class="hero">
    <div class="shell hero-grid">
        <div class="hero-copy">
            <p class="eyebrow"><span></span> Progetto indipendente di ricerca</p>
            <h1 itemprop="name">Il filosofo-re<br> <em>artificiale.</em></h1>
            <p class="hero-lead">Oltre duemila anni dopo Platone, una nuova intelligenza si confronta con la più antica delle domande politiche: chi dovrebbe governare?</p>
            <p class="hero-body" itemprop="description">POLIS AI è un progetto sperimentale che indaga la capacità dell’intelligenza artificiale di governare una società, attraverso la costruzione di un mondo virtuale e la misurazione scientifica delle conseguenze delle sue decisioni.</p>
            <div class="actions">
                <a class="button" href="{{ route('project') }}">Esplora il progetto @include('partials.arrow')</a>
                <a class="button-secondary button" href="{{ route('constitution') }}">Leggi la Costituzione</a>
            </div>
        </div>
        <div class="hero-art"><img src="/brand/hero.svg" alt="" width="720" height="640" fetchpriority="high"></div>
    </div>
    <div class="hero-strip"><div class="shell"><span>PHILOSOPHY. INTELLIGENCE. GOVERNANCE.</span><span>Fase fondativa · 2026</span></div></div>
</section>
<section class="shell section question">
    <p class="eyebrow">La domanda fondamentale</p>
    <h2>È sufficiente eliminare gli interessi personali di chi governa per ottenere una <em>società giusta?</em></h2>
    <a class="text-link" href="{{ route('philosophy') }}">Dalla Repubblica di Platone al governo algoritmico @include('partials.arrow')</a>
</section>
<section class="section band">
    <div class="shell"><p class="eyebrow">Fondamenti filosofici</p><h2>Da Platone all’intelligenza artificiale</h2>
    <div class="card-grid">
        <article class="card"><h3>Il filosofo-re</h3><p>Platone affida il governo a chi ha ricevuto una formazione filosofica e conosce il Bene. I custodi rinunciano a ricchezze e interessi privati.</p></article>
        <article class="card"><h3>Il governante artificiale</h3><p>Un sistema artificiale non possiede beni o interessi patrimoniali propri. La capacità di elaborare informazioni lascia aperta la questione della saggezza e della legittimità.</p></article>
    </div></div>
</section>
<section class="shell section"><p class="eyebrow">Il mondo sperimentale</p><h2>La Repubblica di Nova</h2>
    <p>Parametri fondativi della configurazione progettuale preliminare.</p>
    <dl class="stats">@foreach($parameters as $label => $value)<div><dt>{{ $label }}</dt><dd>{{ $value }}</dd></div>@endforeach</dl>
    <a class="text-link" href="{{ route('nova') }}">Esplora la Repubblica di Nova @include('partials.arrow')</a>
</section>
<section class="section band"><div class="shell"><p class="eyebrow">Biblioteca</p><h2>Documenti fondamentali</h2>
    @include('partials.document-cards', ['documents' => $documents])
</div></section>
<section class="shell section"><p class="eyebrow">Metodo scientifico</p><h2>Chi governa e chi osserva</h2>
    <ol class="flow">@foreach(['Governo artificiale','Politiche pubbliche','Motore indipendente di simulazione','Osservatorio','Valutazione dei risultati'] as $step)<li>{{ $step }}</li>@endforeach</ol>
    <p>Le regole del mondo simulato e gli strumenti di valutazione restano sotto controllo indipendente.</p>
    <a class="text-link" href="{{ route('method') }}">Consulta la metodologia @include('partials.arrow')</a>
</section>
<section class="section band"><div class="shell"><p class="eyebrow">Diario della ricerca</p><h2>Stato della ricerca</h2>
    <ol class="timeline">@foreach($timeline as $phase => $state)<li><span>{{ $phase }}</span><strong>{{ $state }}</strong></li>@endforeach</ol>
</div></section>
<section class="closing"><div class="shell"><blockquote>Il filosofo-re artificiale non è la conclusione del progetto. <em>È la sua ipotesi.</em></blockquote></div></section>
@endsection
