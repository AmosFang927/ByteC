const { chromium } = require('playwright');

(async () => {
  const email = process.env.INVOLVE_EMAIL || 'Amos.Fang@bytectech.com';
  const password = process.env.INVOLVE_PASSWORD || 'ByteC2025&';

  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  console.log('正在前往 Involve Asia 登入頁面...');
  await page.goto('https://app.involve.asia/v2', { waitUntil: 'networkidle' });

  // 等待登入表單載入
  console.log('等待登入表單...');

  // 嘗試常見的 email 輸入框選擇器
  const emailSelector = 'input[type="email"], input[name="email"], input[placeholder*="email" i], input[placeholder*="Email" i]';
  const passwordSelector = 'input[type="password"], input[name="password"]';
  const submitSelector = 'button[type="submit"], button:has-text("Login"), button:has-text("Sign in"), button:has-text("Log in")';

  await page.waitForSelector(emailSelector, { timeout: 30000 });

  // 填入帳號密碼
  console.log('正在填入帳號密碼...');
  await page.fill(emailSelector, email);
  await page.fill(passwordSelector, password);

  // 點擊登入按鈕
  console.log('正在登入...');
  await page.click(submitSelector);

  // 等待登入完成（頁面跳轉）
  await page.waitForNavigation({ waitUntil: 'networkidle', timeout: 30000 }).catch(() => {});

  console.log(`登入後頁面: ${page.url()}`);

  // 儲存登入狀態（cookies）
  const cookies = await context.cookies();
  const fs = require('fs');
  fs.writeFileSync('involve_cookies.json', JSON.stringify(cookies, null, 2));
  console.log('Cookies 已儲存至 involve_cookies.json');

  // 保持瀏覽器開啟讓使用者操作
  console.log('瀏覽器保持開啟中，按 Ctrl+C 結束...');
})();
