@extends('layout')
@section('content')
@include('partials.intro')
<section class="shell section">
    <div class="card-grid">
        @forelse($entries as $slug => $entry)
            <article class="card">
                <p class="eyebrow"><time datetime="{{ $entry['date'] }}">{{ $entry['date'] }}</time> · {{ implode(', ', $entry['categories']) }}</p>
                <h2 class="text-3xl"><a href="{{ route('journal.show', $slug) }}">{{ $entry['title'] }}</a></h2>
                <p>{{ $entry['description'] }}</p>
                <a class="text-link" href="{{ route('journal.show', $slug) }}">Leggi @include('partials.arrow')</a>
            </article>
        @empty<p>Nessuna pubblicazione disponibile.</p>@endforelse
    </div>
</section>
@endsection
