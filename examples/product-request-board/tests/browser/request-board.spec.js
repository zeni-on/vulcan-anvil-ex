const { test, expect } = require('@playwright/test');

async function signIn(page, user) {
  await page.goto('/');
  await page.getByLabel('테스트 계정').selectOption(user);
  await expect(page.getByLabel('테스트 계정')).toBeEnabled();
  await expect(page.locator('#request-list')).toHaveAttribute('aria-busy', 'false');
}

async function submit(page, content) {
  await page.getByLabel('요청 내용', { exact: true }).fill(content);
  const response = page.waitForResponse(r => r.url().endsWith('/api/requests') && r.request().method() === 'POST');
  await page.getByRole('button', { name: '요청 제출', exact: true }).click();
  const result = await (await response).json();
  await expect(page.locator('.detail-id')).toHaveText(`요청 #${result.id}`);
  await expect(page.getByLabel('테스트 계정')).toBeEnabled();
  return result.id;
}

async function select(page, id) {
  await page.getByRole('button', { name: '목록 새로고침' }).click();
  const item = page.locator(`[data-request-id="${id}"]`);
  await expect(item).toBeEnabled();
  await item.click();
  await expect(page.locator('.detail-id')).toHaveText(`요청 #${id}`);
}

async function decide(page, reason) {
  await page.getByLabel('반려 사유', { exact: true }).fill(reason || '');
  await page.getByRole('button', { name: reason ? '반려' : '승인', exact: true }).click();
  await expect(page.locator('.detail-title .badge')).toHaveText(reason ? '반려' : '승인');
  await expect(page.getByLabel('테스트 계정')).toBeEnabled();
}

async function resubmit(page, content) {
  await page.getByLabel('보완 내용').fill(content);
  await page.getByRole('button', { name: '재제출', exact: true }).click();
  await expect(page.locator('.detail-title .badge')).toHaveText('검토 대기');
  await expect(page.getByLabel('테스트 계정')).toBeEnabled();
}

test('SCN-001: private amendment, repeated rejection, resubmission and approval preserve history', { tag: '@resubmission' }, async ({ page, browser }, testInfo) => {
  const reviewerContext = await browser.newContext({ viewport: page.viewportSize() });
  const reviewer = await reviewerContext.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  try {
    await signIn(page, 'alice');
    const id = await submit(page, '노트북 2대가 필요합니다.');
    await signIn(reviewer, 'carol');
    await select(reviewer, id);
    await decide(reviewer, '사용 목적과 수량 근거를 보완해 주세요.');
    await select(page, id);
    const amendment = '신규 입사자 2명의 개발 업무용 노트북을 요청합니다.';
    await page.getByLabel('보완 내용').fill(amendment);
    await reviewer.reload();
    await select(reviewer, id);
    await expect(reviewer.locator('#detail > .content')).toHaveText('노트북 2대가 필요합니다.');
    await expect(reviewer.locator('#detail')).not.toContainText(amendment);
    await resubmit(page, amendment);
    await select(reviewer, id);
    await expect(reviewer.locator('#detail > .content')).toHaveText(amendment);
    await expect(reviewer.locator('.history-item .content').first()).toHaveText('노트북 2대가 필요합니다.');
    await signIn(reviewer, 'dana');
    await select(reviewer, id);
    await decide(reviewer, '납기와 예산을 추가해 주세요.');
    await select(page, id);
    const finalContent = `${amendment}\n예산 300만원, 10월 1일 전 납품 희망.`;
    await resubmit(page, finalContent);
    await select(reviewer, id);
    await decide(reviewer);
    await page.reload();
    await select(page, id);
    await expect(page.locator('.detail-title .badge')).toHaveText('승인');
    await expect(page.locator('.history-item')).toHaveCount(3);
    await expect(page.locator('.history-item').nth(2)).toContainText('노트북 2대가 필요합니다.');
    await expect(page.locator('.history-item').nth(2)).toContainText('사용 목적과 수량 근거를 보완해 주세요.');
    await expect(page.locator('.history-item').nth(1)).toContainText(amendment);
    await expect(page.locator('.history-item').nth(1)).toContainText('납기와 예산을 추가해 주세요.');
    await expect(page.locator('.history-item').first()).toContainText(finalContent);
    await expect(page.getByRole('button', { name: '재제출', exact: true })).toHaveCount(0);
    await expect(page.getByRole('button', { name: '목록 새로고침' }).locator('svg')).toBeVisible();
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    const screenshot = testInfo.outputPath('request-history.png');
    await page.screenshot({ path: screenshot, fullPage: true });
    await testInfo.attach('Approved request and preserved history', { path: screenshot, contentType: 'image/png' });
    expect(errors).toEqual([]);
  } finally {
    await reviewerContext.close();
  }
});

test('SEC-REG-001/002: another requester cannot read history; reviewer cannot review own request', { tag: '@access' }, async ({ page }) => {
  await signIn(page, 'alice');
  const id = await submit(page, '작성자와 검토자에게만 공개하는 요청');
  await signIn(page, 'bob');
  await expect(page.locator(`[data-request-id="${id}"]`)).toHaveCount(0);
  expect((await page.request.get(`/api/requests/${id}`)).status()).toBe(404);
  await signIn(page, 'carol');
  await submit(page, '검토자가 작성한 자기 요청');
  await expect(page.getByRole('button', { name: '승인', exact: true })).toHaveCount(0);
  await expect(page.getByRole('button', { name: '반려', exact: true })).toHaveCount(0);
});

test('SEC-REG-005: user content is text and a second submission selects the new request', { tag: '@render' }, async ({ page }) => {
  await signIn(page, 'alice');
  await submit(page, '첫 번째 요청');
  const unsafe = '<img src=x onerror="window.injected=true">' + '긴내용'.repeat(250);
  await submit(page, unsafe);
  await expect(page.locator('#detail > .content')).toHaveText(unsafe);
  await expect(page.locator('#detail img')).toHaveCount(0);
  expect(await page.evaluate(() => window.injected)).toBeUndefined();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
});

test('SEC-REG-005: delayed prior identity response cannot restore private content', { tag: '@identity' }, async ({ page }) => {
  await signIn(page, 'alice');
  const id = await submit(page, '이전 계정에만 보이는 요청');
  let release;
  const held = new Promise(resolve => { release = resolve; });
  let observed;
  const captured = new Promise(resolve => { observed = resolve; });
  let fulfilled;
  const completed = new Promise(resolve => { fulfilled = resolve; });
  let holdNext = true;
  await page.route('**/api/requests', async route => {
    if (!holdNext || route.request().method() !== 'GET') return route.continue();
    holdNext = false;
    const response = await route.fetch();
    observed();
    await held;
    await route.fulfill({ response });
    fulfilled();
  });
  await page.getByRole('button', { name: '목록 새로고침' }).click();
  await captured;
  await page.getByLabel('테스트 계정').selectOption('bob');
  await expect(page.getByLabel('테스트 계정')).toBeEnabled();
  release();
  await completed;
  await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
  await expect(page.locator(`[data-request-id="${id}"]`)).toHaveCount(0);
  await expect(page.locator('#detail')).not.toContainText('이전 계정에만 보이는 요청');
  expect((await page.request.get(`/api/requests/${id}`)).status()).toBe(404);
});

test('SEC-REG-005: another tab identity switch clears prior identity and unsent draft', { tag: '@tabs' }, async ({ page, context }) => {
  await signIn(page, 'alice');
  await submit(page, '계정 변경 전 요청');
  await page.getByLabel('요청 내용', { exact: true }).fill('아직 제출하지 않은 개인 입력');
  const other = await context.newPage();
  await signIn(other, 'bob');
  await expect(page.getByLabel('테스트 계정')).toHaveValue('bob');
  await expect(page.getByLabel('테스트 계정')).toBeEnabled();
  await expect(page.getByLabel('요청 내용', { exact: true })).toHaveValue('');
  await expect(page.locator('#detail')).not.toContainText('계정 변경 전 요청');
  await other.close();
});
