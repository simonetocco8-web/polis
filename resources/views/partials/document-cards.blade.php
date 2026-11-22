<div class="card-grid">
@forelse($documents as $id => $document)
    <article class="card">
        <p class="eyebrow">{{ $document['type'] }}</p>
        <h3><a href="{{ route('library.show', $id) }}">{{ $document['title'] }}</a></h3>
        <p>{{ $document['subtitle'] }}</p>
        <p class="muted">{{ $document['versions'] === [] ? __('ui.missing').' · '.$document['expected_version'].' · '.$document['expected_date'] : 'Versione '.$document['current'].' · '.$document['versions'][$document['current']]['date'].' · '.$document['versions'][$document['current']]['status'] }}</p>
        <a class="text-link" href="{{ route('library.show', $id) }}">Consulta @include('partials.arrow')</a>
    </article>
@empty
    <p>Nessun documento corrisponde alla ricerca.</p>
@endforelse
</div>
