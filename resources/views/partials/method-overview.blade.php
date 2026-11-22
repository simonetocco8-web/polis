@include('partials.method-nav')
<div class="actions">
    <a class="button" href="{{ route('library.version', ['protocollo', '1.0']) }}">Consulta il protocollo 1.0</a>
    <a class="button button-secondary" href="{{ route('library.download', ['protocollo', '1.0']) }}">Scarica Markdown</a>
</div>
<section aria-labelledby="monthly-flow">
    <h2 id="monthly-flow">Il ciclo mensile previsto</h2>
    <ol class="flow">
        <li>Snapshot filtrato e informazioni autorizzate</li>
        <li>Proposta di atto del governo</li>
        <li>Controlli indipendenti e applicazione dei soli atti autorizzati</li>
        <li>Eventi, transizioni e riconciliazione contabile</li>
        <li>Misurazione indipendente e registrazione</li>
    </ol>
</section>
