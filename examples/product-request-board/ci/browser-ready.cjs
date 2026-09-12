const fs = require('node:fs');
const { chromium } = require('@playwright/test');

(async () => {
  if (!fs.existsSync(chromium.executablePath())) throw new Error('Chromium executable is missing');
  const browser = await chromium.launch({ headless: true });
  await browser.close();
  console.log(JSON.stringify({ status: 'ready' }));
})().catch(error => {
  console.error(JSON.stringify({ status: 'environment_blocked', reason: error.message }));
  process.exitCode = 3;
});
