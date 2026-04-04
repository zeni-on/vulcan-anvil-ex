/**
 * REQ-011 UX 리뷰 — QHD 27인치 환경 스크린샷
 */
import { chromium } from '@playwright/test';
import path from 'path';
import { fileURLToPath } from 'url';

const PROJECT_ID = 'local-julyi-Documents-workspace-antigravity-Vulcan-Dev-kweVml';
const DETAIL_URL = `http://localhost:3001/projects/${PROJECT_ID}`;
const OUT_DIR = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../docs/04-review/screenshots/ux');

async function capture() {
  const browser = await chromium.launch({ headless: true });

  // QHD 27인치: 2560x1440 (devicePixelRatio=1로 설정)
  const page = await browser.newPage({ viewport: { width: 2560, height: 1440 } });
  await page.goto(DETAIL_URL, { waitUntil: 'networkidle', timeout: 15000 });
  await page.waitForSelector('[data-testid="stats-section"]', { timeout: 10000 }).catch(() => {});

  // 전체 페이지
  await page.screenshot({ path: path.join(OUT_DIR, 'UX-detail-stats-qhd.png'), fullPage: false });
  console.log('Captured UX-detail-stats-qhd.png');

  // stats-section 클로즈업
  const statsEl = await page.$('[data-testid="stats-section"]');
  if (statsEl) {
    await statsEl.screenshot({ path: path.join(OUT_DIR, 'UX-stats-section-qhd.png') });
    console.log('Captured UX-stats-section-qhd.png');
  }

  await page.close();
  await browser.close();
}

capture().catch(err => { console.error(err); process.exit(1); });
