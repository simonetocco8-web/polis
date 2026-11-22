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
    await page.getByRole('searchbox').fill('costituzione');
    await page.getByRole('button', { name: 'Cerca' }).click();
    await expect(page.getByRole('heading', { name: 'Costituzione della Repubblica di Nova' })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'POLIS AI — Il filosofo-re artificiale' })).toHaveCount(0);
    await page.getByRole('heading', { name: 'Costituzione della Repubblica di Nova' }).getByRole('link').click();
    await expect(page.getByText('In attesa del documento originale')).toBeVisible();
    expect((await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa']).analyze()).violations).toEqual([]);
    await page.emulateMedia({ media: 'print' });
    await expect(page.locator('.masthead')).toBeHidden();
    await expect(page.getByRole('heading', { level: 1 })).toBeVisible();
    expect(errors).toEqual([]);
});

test('ricerca utilizzabile senza JavaScript', async ({ browser, baseURL }) => {
    const page = await browser.newPage({ javaScriptEnabled: false, baseURL });
    await page.goto('/biblioteca');
    await page.getByRole('searchbox').fill('costituzione');
    await page.getByRole('button', { name: 'Cerca' }).click();
    await expect(page.getByRole('heading', { name: 'Costituzione della Repubblica di Nova' })).toBeVisible();
    await page.close();
});
