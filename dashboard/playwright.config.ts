import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './src/__tests__/e2e',
  timeout: 60_000,
  fullyParallel: false,
  workers: 1,
  retries: 0,
  reporter: [
    ['list'],
    ['html', { outputFolder: 'playwright-report', open: 'never' }],
  ],
  use: {
    baseURL: 'http://127.0.0.1:3001',
    headless: true,
    screenshot: 'on',
    trace: 'retain-on-failure',
  },
  webServer: {
    command: process.env.CI ? 'npm start' : 'npm run dev',
    url: 'http://127.0.0.1:3001',
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
})
