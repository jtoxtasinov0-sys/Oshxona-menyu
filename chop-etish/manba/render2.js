const { chromium } = require('playwright');
const path = require('path'), os = require('os');
const OUT = process.env.OUT || path.join(__dirname, '..') + '/';
const HTML = path.join(process.env.WORK || os.tmpdir(), 'card2.html');
(async () => {
  const b = await chromium.launch({ proxy: { server: process.env.HTTPS_PROXY } });
  const ctx = await b.newContext({ viewport: { width: 420, height: 600 }, deviceScaleFactor: 4 });
  const p = await ctx.newPage();
  await p.goto('file://' + HTML, { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready);
  const fit = await p.evaluate(() => [...document.querySelectorAll('.page')].map(pg => {
    const f = pg.querySelector('footer').getBoundingClientRect(), g = pg.querySelector('.guide').getBoundingClientRect(), r = pg.getBoundingClientRect();
    return { footerToPageBottom: Math.round(r.bottom - f.bottom), gapGuideToFooter: Math.round(f.top - g.bottom) };
  }));
  console.log('fit:', JSON.stringify(fit));
  // NFC doiralari ikki tomonda ustma-ust tushishi kerak (orqa tomon ko'zgu)
  const nfc = await p.evaluate(() => [...document.querySelectorAll('.page')].map(pg => {
    const r = pg.getBoundingClientRect(), c = pg.querySelector('.nfc').getBoundingClientRect();
    return { x: +((c.left + c.width / 2 - r.left) * 25.4 / 96).toFixed(1), y: +((c.top + c.height / 2 - r.top) * 25.4 / 96).toFixed(1) };
  }));
  console.log('nfc centre mm  front:', JSON.stringify(nfc[0]), ' back (mirrored x):', JSON.stringify({ x: +(105 - nfc[1].x).toFixed(1), y: nfc[1].y }));
  const pages = await p.$$('.page');
  await pages[0].screenshot({ path: OUT + 'stol-kartochka-old.png' });
  await pages[1].screenshot({ path: OUT + 'stol-kartochka-orqa.png' });
  await p.pdf({ path: OUT + 'stol-kartochka-A6.pdf', width: '105mm', height: '148mm', printBackground: true });
  // Bosmaxona uchun: har tomondan 2 mm bleed (109x152), kesish o'lchami 105x148
  await p.goto('file://' + HTML.replace(/card2\.html$/, 'card2-bleed.html'), { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready);
  await p.pdf({ path: OUT + 'stol-kartochka-A6-bleed-2mm.pdf', width: '109mm', height: '152mm', printBackground: true });
  await b.close();
})();
