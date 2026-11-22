@extends('layout')
@section('content')
@include('partials.intro', isset($entry) ? ['parent' => [route('journal'), __('ui.nav.journal')]] : [])
<section class="shell section">
    <article class="reading">
        @isset($entry)
            <p class="muted"><time datetime="{{ $entry['date'] }}">{{ $entry['date'] }}</time> · {{ $entry['author'] }} · {{ $entry['phase'] }} · Portale {{ $entry['release'] }}</p>
        @endisset
        @if(($page ?? '') === 'observatory')<p class="empty"><strong>Non sono ancora disponibili risultati sperimentali.</strong></p>@endif
        {!! $html !!}
        @if(($page ?? '') === 'nova')
            <h2>Organigramma previsto</h2>
            <img class="organigram" src="/brand/nova.svg" width="960" height="440" loading="lazy" alt="I cittadini sono titolari della sovranità. La Costituzione disciplina Governatore, agenti specializzati, magistratura e autorità indipendenti.">
        @endif
    </article>
</section>
@endsection
