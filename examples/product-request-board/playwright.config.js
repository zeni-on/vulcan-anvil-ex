const { defineConfig, devices } = require('@playwright/test');
const path = require('node:path');

const port = Number(process.env.REQUEST_BOARD_TEST_PORT || 8161);
const db = path.join(__dirname, '.local', `e2e-${process.pid}.sqlite3`);

module.exports = defineConfig({
  testDir: './tests/browser',
  timeout: 30000,
  expect: { timeout: 5000 },
  workers: 1,
  retries: 0,
  forbidOnly: true,
  failOnFlakyTests: true,
  reporter: [['list'], ['html', { open: 'never' }], ['json', { outputFile: 'test-results/results.json' }]],
  use: { baseURL: `http://127.0.0.1:${port}`, trace: 'retain-on-failure', screenshot: 'only-on-failure' },
  webServer: {
    command: `python -B app.py --demo --port ${port} --db "${db}"`,
    url: `http://127.0.0.1:${port}/api/demo/users`,
    reuseExistingServer: false,
    timeout: 30000,
  },
  projects: [
    { name: 'desktop', use: { ...devices['Desktop Chrome'], viewport: { width: 1440, height: 1000 } } },
    { name: 'mobile', use: { ...devices['Desktop Chrome'], viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true } },
  ],
});
