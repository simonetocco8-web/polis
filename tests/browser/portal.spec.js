import { expect, test } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test('homepage, navigazione, ricerca e accessibilità essenziale', async ({ page, request }) => {
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    page.on('console', message => {
        if (message.type() === 'error') errors.push(message.text());
    });
    await page.goto('/');
    await expect(page.getByRole('heading', { level: 1 })).toHaveText('Il filosofo-re artificiale.');
    await page.keyboard.press('Tab');
    await expect(page.getByRole('link', { name: 'Vai al contenuto' })).toBeFocused();
    expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(page.viewportSize().width);
    expect((await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa']).analyze()).violations).toEqual([]);

    const links = await page.locator('a[href]').evaluateAll(anchors => [...new Set(anchors
        .map(anchor => new URL(anchor.href))
        .filter(url => url.origin === window.location.origin)
        .map(url => url.pathname))]);
    for (const path of links) expect((await request.get(path)).ok(), path).toBeTruthy();

    const mobileMenu = page.locator('.mobile-nav summary');
    if (await mobileMenu.isVisible()) {
        await mobileMenu.focus();
        await page.keyboard.press('Enter');
        await expect(page.getByRole('navigation', { name: 'Navigazione mobile' })).toBeVisible();
        await page.getByRole('navigation', { name: 'Navigazione mobile' }).getByRole('link', { name: 'Biblioteca' }).click();
    } else {
        await page.getByRole('navigation', { name: 'Navigazione principale' }).getByRole('link', { name: 'Biblioteca' }).click();
    }
    await page.getByRole('searchbox').fill('Natura della Repubblica');
    await page.getByRole('button', { name: 'Cerca' }).click();
    await expect(page.getByRole('heading', { name: 'Costituzione della Repubblica di Nova' })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'POLIS AI — Il filosofo-re artificiale' })).toHaveCount(0);
    await page.getByRole('heading', { name: 'Costituzione della Repubblica di Nova' }).getByRole('link').click();
    await expect(page.getByText('Testo originario acquisito')).toBeVisible();
    await expect(page.locator('#articolo-71')).toBeVisible();
    expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(page.viewportSize().width);
    expect((await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa']).analyze()).violations).toEqual([]);
    await page.emulateMedia({ media: 'print' });
    await expect(page.locator('.masthead')).toBeHidden();
    await expect(page.getByRole('heading', { level: 1 })).toBeVisible();
    expect(errors).toEqual([]);
});

test('ricerca utilizzabile senza JavaScript', async ({ browser, baseURL }) => {
    const page = await browser.newPage({ javaScriptEnabled: false, baseURL });
    await page.goto('/biblioteca');
    await page.getByRole('searchbox').fill('Natura della Repubblica');
    await page.getByRole('button', { name: 'Cerca' }).click();
    await expect(page.getByRole('heading', { name: 'Costituzione della Repubblica di Nova' })).toBeVisible();
    await page.close();
});

test('Costituzione: ricerca, frammenti, articoli e collegamenti', async ({ page, request }) => {
    await page.goto('/costituzione');
    const fragments = await page.locator('.doc-aside a[href^="#"]').evaluateAll(links => links
        .filter(link => !document.getElementById(link.hash.slice(1))).map(link => link.hash));
    expect(fragments).toEqual([]);
    await expect(page.getByRole('complementary', { name: 'Nota metodologica' })).toBeVisible();
    await page.getByRole('searchbox').fill('71');
    await page.getByRole('button', { name: 'Cerca' }).click();
    await page.locator('section.no-print').getByRole('link', { name: /Articolo 71/ }).click();
    await expect(page).toHaveURL(/versione\/1\.0\/articolo\/71$/);
    await expect(page.locator('#article-text')).not.toBeEmpty();
    await expect(page.getByRole('link', { name: 'Articolo precedente' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Articolo successivo' })).toHaveCount(0);
    expect((await request.get('/biblioteca/costituzione/1.0/markdown')).ok()).toBeTruthy();
});

test('Methodos: navigabilità, accessibilità e veto sui diritti', async ({ page, request }) => {
    await page.goto('/metodologia');
    await expect(page.getByRole('link', { name: 'Consulta il protocollo 1.0' })).toBeVisible();
    const download = await request.get('/biblioteca/protocollo/1.0/markdown');
    expect(download.ok()).toBeTruthy();
    for (const route of ['/biblioteca/protocollo/1.0', '/metodologia/scenari', '/metodologia/indicatori', '/metodologia/polis-index']) {
        await page.goto(route);
        expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(page.viewportSize().width);
        expect((await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa']).analyze()).violations).toEqual([]);
    }
    await page.getByRole('slider', { name: /Prosperità economica/ }).focus();
    await page.keyboard.press('End');
    await expect(page.locator('output')).toHaveText('Punteggio dimostrativo: 62,5 / 100');
    const veto = page.getByRole('checkbox', { name: /violazione grave/ });
    await veto.check();
    await expect(page.locator('output')).toHaveText(/Punteggio sospeso/);
});

test('Demos: atlante, piramide accessibile e download aggregato', async ({ page, request }) => {
    await page.goto('/nova');
    await page.getByRole('link', { name: /Repubblica di Nova — Atlante statistico/ }).click();
    await page.getByRole('link', { name: 'Demografia' }).click();
    await page.waitForLoadState('load');
    await expect(page.getByRole('heading', { name: 'Piramide demografica' })).toBeVisible();
    await expect(page.getByRole('table', { name: 'Residenti per fascia di età e categoria demografica' })).toBeVisible();
    expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(page.viewportSize().width);
    expect((await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa']).analyze()).violations).toEqual([]);
    const response = await request.get('/nova/statistiche.json');
    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(data.totals.population).toBe(100000);
    expect(data.polis_index).toBeNull();
    expect(data).not.toHaveProperty('people');
});

test('Oikonomia: serie simulata, accessibilità e download', async ({ page, request }) => {
    await page.goto('/nova');
    await page.getByRole('link', { name: 'Repubblica di Nova — Economia' }).click();
    await page.getByRole('link', { name: 'PIL e contabilità nazionale' }).click();
    await expect(page.getByRole('table', { name: /Ultimi dodici mesi/ })).toBeVisible();
    await expect(page.getByText(/Prova tecnica con economia chiusa/)).toBeVisible();
    await page.waitForLoadState('load');
    await page.evaluate(() => document.fonts.ready);
    await expect.poll(() => page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(page.viewportSize().width);
    expect((await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa']).analyze()).violations).toEqual([]);
    const response = await request.get('/nova/economia/statistiche.json');
    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(data.rows).toHaveLength(600);
    expect(data.polis_index).toBeNull();
    expect(data).not.toHaveProperty('people');
});

test('Stabilitas: audit, serie e accessibilità', async ({ page, request }) => {
    await page.goto('/nova/economia');
    await page.getByRole('link', { name: 'Stabilità economica' }).click();
    await page.waitForLoadState('load');
    await expect(page.getByRole('heading', { name: 'Cronologia della traiettoria originale' })).toBeVisible();
    await expect(page.getByRole('table', { name: /Cinque esecuzioni/ })).toBeVisible();
    expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(page.viewportSize().width);
    expect((await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa']).analyze()).violations).toEqual([]);
    expect((await request.get('/nova/economia/stabilita/statistiche.csv')).ok()).toBeTruthy();
});

test('Nomos: accessibilità, cronologia e download istituzionali', async ({ page, request }) => {
    test.setTimeout(60_000);
    await page.goto('/nova');
    await page.getByRole('link', { name: 'Repubblica di Nova — Istituzioni' }).click();
    await expect(page.getByRole('heading', { level: 1 })).toHaveText('Istituzioni della Repubblica di Nova');
    for (const section of ['ordinamento', 'corte', 'atti', 'ricorsi', 'diritti', 'mandato', 'emergenze', 'scenari', 'trasparenza']) {
        await page.goto('/nova/istituzioni/' + section, { waitUntil: 'load' });
        await page.evaluate(() => document.fonts.ready);
        expect(await page.evaluate(() => document.documentElement.scrollWidth), section).toBeLessThanOrEqual(page.viewportSize().width);
        expect((await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa']).analyze()).violations).toEqual([]);
    }
    const json = await request.get('/nova/istituzioni/statistiche.json');
    expect(json.ok()).toBeTruthy();
    expect((await json.json()).metrics.applied).toBe(1);
    const csv = await request.get('/nova/istituzioni/statistiche.csv');
    expect(csv.ok()).toBeTruthy();
    expect(await csv.text()).toContain('pending_review,1');
    expect(json.headers()['x-nomos-export-sha256']).toBe(csv.headers()['x-nomos-export-sha256']);
});

test('Archon: fascicolo offline accessibile e download verificabile', async ({ page, request }) => {
    await page.goto('/nova/governo');
    await expect(page.getByRole('heading', { level: 1 })).toHaveText('Il Governatore artificiale');
    await expect(page.getByText('Prova offline.')).toBeVisible();
    await page.getByRole('link', { name: 'Diario delle decisioni' }).click();
    await page.waitForLoadState('load');
    await page.evaluate(() => document.fonts.ready);
    await expect(page.getByRole('heading', { name: 'Mese 4 · Astensione' })).toBeVisible();
    await expect.poll(() => page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(page.viewportSize().width);
    expect((await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa']).analyze()).violations).toEqual([]);
    const response = await request.get('/nova/governo/statistiche.json');
    expect(response.ok()).toBeTruthy();
    expect((await response.json()).api_calls).toBe(0);
});

test('Theoria: fascicolo offline accessibile e integrità', async ({ page, request }) => {
    await page.goto('/nova/osservatorio');
    await expect(page.getByRole('heading', { level: 1 })).toHaveText('Osservatorio indipendente');
    await page.getByRole('link', { name: 'Fascicoli' }).click();
    await page.waitForLoadState('load');
    await page.evaluate(() => document.fonts.ready);
    await expect(page.getByRole('heading', { name: 'Mese 4 · Astensione' })).toBeVisible();
    await expect.poll(() => page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(page.viewportSize().width);
    expect((await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa']).analyze()).violations).toEqual([]);
    const response = await request.get('/nova/osservatorio/statistiche.json');
    expect((await response.json()).mode).toBe('offline-public-fixture');
});

test('Experimentum: pilota riprodotto e confronto scientifico bloccato', async ({ page, request }) => {
    await page.goto('/ricerca/esperimenti');
    await expect(page.getByRole('heading', { level: 1 })).toHaveText('Laboratorio scientifico');
    await page.getByRole('link', { name: 'Confronti' }).click();
    await page.waitForLoadState('load');
    await page.evaluate(() => document.fonts.ready);
    await expect(page.getByRole('heading', { name: /Non ammissibile/ })).toBeVisible();
    await expect.poll(() => page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(page.viewportSize().width);
    expect((await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa']).analyze()).violations).toEqual([]);
    const response = await request.get('/ricerca/esperimenti/statistiche.json');
    expect((await response.json()).readiness.state).toBe('NOT_READY');
});
