const { chromium } = require('playwright');
const OUT = '/home/user/oshxona-menyu/chop-etish/';
(async () => {
  const b = await chromium.launch({ proxy: { server: process.env.HTTPS_PROXY } });
  const ctx = await b.newContext({ viewport: { width: 420, height: 600 }, deviceScaleFactor: 4 });
  const p = await ctx.newPage();
  await p.goto('file://' + __dirname + '/card2.html', { waitUntil: 'networkidle' });
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
  await b.close();
})();
