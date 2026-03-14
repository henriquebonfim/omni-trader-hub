import { test, expect } from '@playwright/test';

test.describe('Strategy Creation', () => {
  test('should allow navigating to strategy lab', async ({ page }) => {
    // Intercept login specifically testing API key auth
    await page.route('**/api/auth/verify', async route => route.fulfill({ status: 200, json: { ok: true } }));
    
    // Intercept required dashboard routes
    await page.route('**/api/status', async route => route.fulfill({ status: 200, json: {} }));
    await page.route('**/api/position', async route => route.fulfill({ status: 200, json: {} }));
    await page.route('**/api/balance', async route => route.fulfill({ status: 200, json: {} }));
    await page.route('**/api/env', async route => route.fulfill({ status: 200, json: {} }));
    await page.route('**/api/graph/crisis', async route => route.fulfill({ status: 200, json: { active: false } }));
    
    // Intercept strategies
    await page.route('**/api/strategies', async route => {
      await route.fulfill({ status: 200, json: { strategies: [], active: null } });
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

    // First, ensure the dashboard loaded and we see the nav
    await expect(page.getByText('Dashboard')).toBeVisible();

    // Ensure we can see 'Strategy Lab' directly or inside a link
    await page.getByRole('link', { name: /Strategy Lab/i }).click();

    // Verify Lab is loaded by looking for a specific text header on the page
    await expect(page.getByRole('heading', { name: /Strategy Lab/i })).toBeVisible();
    await expect(page.getByRole('heading', { name: /Built-in Strategies/i })).toBeVisible();
  });
});
