<dl class="muted">
    <dt>Stato editoriale</dt><dd>{{ $record['status'] }}</dd>
    <dt>Data</dt><dd><time datetime="{{ $record['date'] }}">{{ $record['date'] }}</time></dd>
    <dt>Autore dichiarato</dt><dd>{{ $record['author'] }}</dd>
    <dt>Provenienza</dt><dd>{{ $record['provenance'] }}</dd>
    <dt>Lingua</dt><dd>{{ $record['language'] }} · {{ $record['language'] === $record['original_language'] ? 'Testo in lingua originale' : 'Traduzione dall’'.$record['original_language'] }}</dd>
    @isset($record['translation_date'])
        <dt>Traduzione</dt><dd>{{ $record['translation_date'] }} · {{ $record['translator'] }} · {{ $record['translation_review'] }}</dd>
    @endisset
    @isset($record['previous'])<dt>Versione precedente</dt><dd>{{ $record['previous'] }}</dd>@endisset
    <dt>SHA-256</dt><dd><code>{{ $record['sha256'] }}</code></dd>
</dl>
