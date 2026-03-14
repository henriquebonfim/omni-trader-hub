import { test, expect } from '@playwright/test';

test.describe('Environment Config', () => {
  test('should load settings page and verify configuration form', async ({ page }) => {
    // Intercept login specifically testing API key auth
    await page.route('**/api/auth/verify', async route => route.fulfill({ status: 200, json: { ok: true } }));
    
    // Intercept config load route specifically
    await page.route('**/api/env', async route => {
      await route.fulfill({ status: 200, json: { OMNITRADER_PAPER_MODE: { value: 'true', masked: false, description: 'test', requires_restart: false } } });
    });

    await page.route('**/*', async route => {
      const url = route.request().url();
      if (url.includes('/api/auth/verify')) {
        await route.fulfill({ status: 200, json: { ok: true } });
      } else if (url.includes('/api/')) {
        await route.fulfill({ status: 200, json: {} });
      } else {
        await route.continue();
      }
    });

    await page.goto('/');
    
    await page.getByPlaceholder('Paste your API key here').fill('test');
    await page.getByRole('button', { name: 'Sign In' }).click();

    await expect(page.getByText('Dashboard')).toBeVisible();

    await page.getByRole('link', { name: /Settings/i }).click();

    // Verify settings header is loaded
    await expect(page.getByRole('heading', { name: 'Settings', exact: true })).toBeVisible();

    // Optionally check if we have a table or list of config keys
    await page.getByRole('button', { name: 'Environment' }).click();
    await expect(page.getByText('Changes marked with 🔄 require a service restart')).toBeVisible();
    await expect(page.getByRole('button', { name: 'Restart Services' })).toBeVisible();
  });
});
