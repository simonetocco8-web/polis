<header class="page-intro"><div class="shell">
    <nav class="breadcrumb" aria-label="Percorso"><a href="{{ route('home') }}">{{ __('ui.home') }}</a> <span aria-hidden="true"> / </span>
        @isset($parent)<a href="{{ $parent[0] }}">{{ $parent[1] }}</a> <span aria-hidden="true"> / </span>@endisset
        <span aria-current="page">{{ $title }}</span>
    </nav>
    @isset($eyebrow)<p class="eyebrow">{{ $eyebrow }}</p>@endisset
    <h1 itemprop="name">{{ $title }}</h1>
    @isset($description)<p itemprop="description">{{ $description }}</p>@endisset
</div></header>
