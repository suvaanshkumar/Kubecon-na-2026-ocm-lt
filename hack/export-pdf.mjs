// Render deck/index.html to deck/did-it-land.pdf (one 1920x1080 page per slide),
// plus a PNG per slide under deck/png/ for quick review.
// Usage: node hack/export-pdf.mjs   (needs `npm i playwright` and `npx playwright install chromium`)
import { chromium } from 'playwright';
import { mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const deck = pathToFileURL(join(root, 'deck', 'index.html')).href;

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
await page.goto(deck);

await page.pdf({
  path: join(root, 'deck', 'did-it-land.pdf'),
  width: '1920px',
  height: '1080px',
  printBackground: true,
  preferCSSPageSize: true,
});

const count = await page.locator('.slide').count();
mkdirSync(join(root, 'deck', 'png'), { recursive: true });
for (let i = 1; i <= count; i++) {
  const steps = await page.locator('.slide').nth(i - 1).evaluate(
    s => Math.max(0, ...Array.from(s.querySelectorAll('.frag, .frag-block'), f => +f.dataset.step)));
  for (let st = 0; st <= steps; st++) {
    await page.goto(`${deck}#${i}${st ? '.' + st : ''}`);
    await page.reload();
    await page.waitForTimeout(steps ? 900 : 0); // let build-step transitions finish
    const name = steps ? `slide-${i}-step-${st}.png` : `slide-${i}.png`;
    await page.screenshot({ path: join(root, 'deck', 'png', name) });
  }
}

await browser.close();
console.log(`wrote deck/did-it-land.pdf and ${count} PNGs`);
