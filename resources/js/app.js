for (const button of document.querySelectorAll('[data-action]')) {
    const action = button.dataset.action;
    if (action !== 'print' && !navigator.clipboard) continue;

    button.hidden = false;
    button.addEventListener('click', async () => {
        if (action === 'print') {
            window.print();
            return;
        }
        const status = document.getElementById('action-status');
        const text = action === 'copy-text'
            ? document.getElementById('article-text').innerText
            : window.location.href;
        try {
            await navigator.clipboard.writeText(text);
            status.textContent = 'Copiato negli appunti.';
        } catch {
            status.textContent = 'Copia non riuscita. Seleziona il testo per copiarlo manualmente.';
        }
    });
}
