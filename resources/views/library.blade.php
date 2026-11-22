@extends('layout')
@section('content')
@include('partials.intro')
<section class="shell section">
    <form class="search" action="{{ route('library') }}" method="get">
        <label>Ricerca nei documenti <input name="q" type="search" maxlength="150" value="{{ $query }}"></label>
        <button class="button">{{ __('ui.search') }}</button>
    </form>
    @include('partials.document-cards')
</section>
@endsection
