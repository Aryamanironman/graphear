const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const FPS = 30;
const DUR = 42;
const OUT = path.join(__dirname, 'out', 'frames');

(async () => {
  const mode = process.argv[2] || 'all';
  fs.mkdirSync(OUT, { recursive: true });

  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  await page.goto('file:///C:/Users/asus/graphear/video.html?render=1', { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(300);

  if (mode === 'poster') {
    for (const t of [2.2, 7.4, 12.0, 16.6, 22.5, 28.8, 34.5, 39.2]) {
      await page.evaluate((tt) => window.seek(tt), t);
      await page.waitForTimeout(80);
      await page.screenshot({ path: path.join(__dirname, 'out', `poster_${String(t).replace('.', '_')}.png`) });
    }
    await browser.close();
    console.log('posters done');
    return;
  }

  const total = FPS * DUR;
  for (let i = 0; i < total; i++) {
    const t = i / FPS;
    await page.evaluate((tt) => window.seek(tt), t);
    await page.screenshot({ path: path.join(OUT, `f_${String(i).padStart(5, '0')}.jpg`), type: 'jpeg', quality: 92 });
    if (i % 150 === 0) console.log(`frame ${i}/${total}`);
  }
  await browser.close();
  console.log(`rendered ${total} frames`);
})();
