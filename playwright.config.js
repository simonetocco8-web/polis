import { defineConfig, devices } from '@playwright/test';

const address = 'http://127.0.0.1:8055';

export default defineConfig({
    testDir: './tests/browser',
    fullyParallel: true,
    workers: 2,
    use: {
        baseURL: address,
        launchOptions: { executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE },
    },
    projects: [
        { name: 'desktop', use: { ...devices['Desktop Chrome'] } },
        { name: 'tablet', use: { ...devices['iPad Mini'], defaultBrowserType: 'chromium' } },
        { name: 'mobile', use: { ...devices['Pixel 7'] } },
    ],
    webServer: {
        command: 'php -S 127.0.0.1:8055 -t public',
        url: address,
        env: { APP_URL: address, APP_ENV: 'testing', APP_DEBUG: 'false' },
        reuseExistingServer: false,
    },
});
