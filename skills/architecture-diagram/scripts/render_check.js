// Render an HTML architecture page in headless Chromium/Edge/Chrome and verify layout once.
//   node render_check.js <page.html> [outDir]
// Writes fig<N>-light.png for every .figscroll, fig1-dark.png, phone-top.png, and checks:
//   1) horizontal page overflow at 1440px and 390px viewports
//   2) actual browser-measured SVG text spilling out of its enclosing box
const fs = require('fs');
const path = require('path');

function loadPlaywright() {
  const tries = [
    process.env.PLAYWRIGHT_CORE,
    'playwright-core',
    'playwright',
  ].filter(Boolean);
  for (const t of tries) {
    try { return require(t); } catch (_) { /* try next */ }
  }
  console.error('playwright-core / playwright not found; install playwright or set PLAYWRIGHT_CORE');
  process.exit(2);
}

async function launchBrowser(chromium) {
  for (const channel of ['msedge', 'chrome', undefined]) {
    try {
      return await chromium.launch(channel ? { channel, headless: true } : { headless: true });
    } catch (_) { /* fallback to next channel */ }
  }
  throw new Error('Failed to launch headless Chromium, Edge, or Chrome.');
}

const [, , pageArg, outArg] = process.argv;
if (!pageArg) {
  console.error('usage: node render_check.js <page.html> [outDir]');
  process.exit(2);
}
const pagePath = path.resolve(pageArg);
const outDir = path.resolve(outArg || path.dirname(pagePath));
fs.mkdirSync(outDir, { recursive: true });

const rawHtml = fs.readFileSync(pagePath, 'utf8');
const isFullDoc = /<!doctype\s+html|<html\b/i.test(rawHtml);
const wrapped = isFullDoc
  ? rawHtml
  : '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">' +
    '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">' +
    '<style>:root{color-scheme:light}body{margin:0;font:14px system-ui}img{max-width:100%}[hidden]{display:none!important}</style>' +
    '</head><body>' + rawHtml + '</body></html>';

const previewPath = path.join(outDir, '_preview.html');
fs.writeFileSync(previewPath, wrapped);
const url = 'file:///' + previewPath.replace(/\\/g, '/');

function measureSpills() {
  const out = [];
  document.querySelectorAll('svg g.node').forEach((g) => {
    const shape = g.querySelector('rect, polygon');
    if (!shape) return;
    const b = shape.getBBox();
    g.querySelectorAll('text').forEach((t) => {
      const r = t.getBBox();
      const over = Math.max(r.x + r.width - (b.x + b.width), b.x - r.x, 0);
      if (over > 1.5) out.push(`${Math.round(over)}px  "${t.textContent.slice(0, 40)}"`);
    });
  });
  return out;
}

(async () => {
  const { chromium } = loadPlaywright();
  const browser = await launchBrowser(chromium);
  let problems = 0;
  for (const scheme of ['light', 'dark']) {
    const ctx = await browser.newContext({ viewport: { width: 1440, height: 1000 }, colorScheme: scheme });
    const page = await ctx.newPage();
    await page.goto(url, { waitUntil: 'networkidle' });
    await page.evaluate(() => document.fonts.ready);
    const figs = await page.$$('.figscroll');
    if (scheme === 'light') {
      for (let i = 0; i < figs.length; i++) {
        await figs[i].screenshot({ path: path.join(outDir, `fig${i + 1}-light.png`) });
      }
      const sw = await page.evaluate(() => document.documentElement.scrollWidth);
      console.log(`page width at 1440: ${sw}${sw > 1440 ? '  <-- horizontal page scroll' : ''}`);
      if (sw > 1440) problems++;
      const spills = await page.evaluate(measureSpills);
      console.log(spills.length ? `text spilling out of boxes (${spills.length}):\n  ` + spills.join('\n  ') : 'text spills: none');
      problems += spills.length;
    } else if (figs[0]) {
      await figs[0].screenshot({ path: path.join(outDir, 'fig1-dark.png') });
    }
    await ctx.close();
  }
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 } });
  const page = await ctx.newPage();
  await page.goto(url, { waitUntil: 'networkidle' });
  const [sw, cw] = await page.evaluate(() => [document.documentElement.scrollWidth, document.documentElement.clientWidth]);
  console.log(`phone width ${cw}: scrollWidth ${sw}${sw > cw ? '  <-- horizontal page scroll' : ''}`);
  if (sw > cw) problems++;
  await page.screenshot({ path: path.join(outDir, 'phone-top.png') });
  await ctx.close();
  await browser.close();
  console.log(`screenshots in ${outDir}; problems: ${problems}`);
  process.exit(problems ? 1 : 0);
})().catch((e) => {
  console.error(e);
  process.exit(2);
});
