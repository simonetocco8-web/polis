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
