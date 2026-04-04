/**
 * REQ-011 UX 리뷰용 스크린샷 캡처 스크립트
 * 실행: node capture-011.mjs  (dashboard/ 디렉터리에서)
 */
import { chromium } from '@playwright/test';
import { fileURLToPath } from 'url';
import path from 'path';

const BASE_URL = 'http://localhost:3001';
const PROJECT_ID = 'local-julyi-Documents-workspace-antigravity-Vulcan-Dev-kweVml';
const DETAIL_URL = `${BASE_URL}/projects/${PROJECT_ID}`;

const OUT_DIR = path.resolve(
  path.dirname(fileURLToPath(import.meta.url)),
  '../docs/04-review/screenshots/ux'
);

const VIEWPORTS = [
  { name: 'desktop', width: 1280, height: 900 },
  { name: 'tablet',  width: 768,  height: 1024 },
  { name: 'mobile',  width: 375,  height: 812 },
];

async function capture() {
  const browser = await chromium.launch({ headless: true });

  for (const vp of VIEWPORTS) {
    const page = await browser.newPage({ viewport: { width: vp.width, height: vp.height } });

    // 프로젝트 상세 페이지 (stats 포함)
    await page.goto(DETAIL_URL, { waitUntil: 'networkidle', timeout: 15000 });
    // stats-section 로드 대기
    await page.waitForSelector('[data-testid="stats-section"]', { timeout: 10000 }).catch(() => {
      console.warn(`[WARN] stats-section not found at ${vp.name}`);
    });
    await page.screenshot({
      path: path.join(OUT_DIR, `UX-detail-stats-${vp.name}.png`),
      fullPage: true,
    });
    console.log(`Captured UX-detail-stats-${vp.name}.png`);

    // desktop 뷰 클로즈업
    if (vp.name === 'desktop') {
      const statsEl = await page.$('[data-testid="stats-section"]');
      if (statsEl) {
        await statsEl.screenshot({ path: path.join(OUT_DIR, 'UX-stats-section-closeup.png') });
        console.log('Captured UX-stats-section-closeup.png');
      }
      const cgpEl = await page.$('[data-testid="current-gate-panel"]');
      if (cgpEl) {
        await cgpEl.screenshot({ path: path.join(OUT_DIR, 'UX-current-gate-panel-closeup.png') });
        console.log('Captured UX-current-gate-panel-closeup.png');
      }
      const cardsEl = await page.$('[data-testid="stats-cards"]');
      if (cardsEl) {
        await cardsEl.screenshot({ path: path.join(OUT_DIR, 'UX-stats-cards-closeup.png') });
        console.log('Captured UX-stats-cards-closeup.png');
      }
    }

    await page.close();
  }

  await browser.close();
  console.log('\nAll screenshots saved to:', OUT_DIR);
}

capture().catch(err => { console.error(err); process.exit(1); });
