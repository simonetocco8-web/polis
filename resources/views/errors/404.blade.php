@extends('layout', ['title' => 'Pagina non trovata'])
@section('content')
<section class="shell section"><p class="eyebrow">404</p><h1>Pagina non trovata</h1><a class="text-link" href="{{ route('home') }}">Torna alla homepage</a></section>
@endsection
