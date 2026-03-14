import { test, expect } from '@playwright/test';

test.describe('Bot Management', () => {
  test('should load the dashboard and verify elements', async ({ page }) => {
    // Navigate to the app root
    await page.goto('/');

    // Check that we see the login screen initially
    await expect(page.getByRole('heading', { name: 'OmniTrader' })).toBeVisible();

    // Fill in a dummy API key
    await page.getByPlaceholder('Paste your API key here').fill('test-api-key');

    // Mock API requests for login
    await page.route('/api/auth/verify', async route => {
      await route.fulfill({ status: 200, json: { ok: true } });
    });

    // Mock API requests for dashboard loading
    await page.route('/api/status', async route => {
      await route.fulfill({ status: 200, json: {} });
    });
    await page.route('/api/position', async route => {
      await route.fulfill({ status: 200, json: {} });
    });
    await page.route('/api/balance', async route => {
      await route.fulfill({ status: 200, json: {} });
    });
    await page.route('/api/env', async route => {
      await route.fulfill({ status: 200, json: {} });
    });

    await page.getByRole('button', { name: 'Sign In' }).click();

    // Verify successful login
    await expect(page.getByText('Dashboard')).toBeVisible();
  });
});
