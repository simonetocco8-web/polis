@extends('layout', ['title' => 'Errore temporaneo'])
@section('content')
<section class="shell section"><p class="eyebrow">500</p><h1>Errore temporaneo</h1><a class="text-link" href="{{ route('home') }}">Torna alla homepage</a></section>
@endsection
