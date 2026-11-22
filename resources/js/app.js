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

const calculator = document.querySelector('[data-polis-index]');
if (calculator) {
    const sliders = [...calculator.querySelectorAll('[data-weight]')];
    const result = calculator.querySelector('output');
    const veto = calculator.querySelector('[data-rights-veto]');
    const refresh = () => {
        let weighted = 0;
        for (const slider of sliders) {
            slider.nextElementSibling.textContent = slider.value;
            weighted += slider.valueAsNumber * Number(slider.dataset.weight);
        }
        result.textContent = veto.checked
            ? 'Fallimento autonomo: violazione grave dei diritti. Punteggio sospeso.'
            : `Punteggio dimostrativo: ${(weighted / 100).toLocaleString('it-IT', { maximumFractionDigits: 2 })} / 100`;
    };
    calculator.addEventListener('input', refresh);
    calculator.addEventListener('change', refresh);
    refresh();
    calculator.hidden = false;
}
