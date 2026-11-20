// node shoot.mjs <page.html> <out.jpg> [js expression returning a data URL, default window.shot()]
import { createRequire } from 'module'; const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PWMOD || '/opt/node-tools/node_modules/playwright');
import http from 'http'; import fs from 'fs'; import path from 'path';
const root = path.dirname(new URL(import.meta.url).pathname);
const [page, out, expr = 'window.shot()'] = process.argv.slice(2);
const types = { '.js': 'text/javascript', '.html': 'text/html', '.otf': 'font/otf' };
const srv = http.createServer((q, s) => { const f = path.join(root, decodeURIComponent(q.url.split('?')[0])); if (!f.startsWith(root) || !fs.existsSync(f)) { s.writeHead(404); return s.end(); }
  s.writeHead(200, { 'Content-Type': types[path.extname(f)] || 'application/octet-stream' }); fs.createReadStream(f).pipe(s); });
await new Promise((ok) => srv.listen(0, ok));
const b = await chromium.launch({ executablePath: process.env.CHROME || '/opt/pw-browsers/chromium', args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const p = await b.newPage(); p.on('pageerror', (e) => console.log('page error:', e.message));
await p.goto(`http://localhost:${srv.address().port}/${page}`); await p.waitForFunction(() => window.ready, null, { timeout: 60000 });
const u = await p.evaluate(expr); fs.writeFileSync(out, Buffer.from(u.split(',')[1], 'base64'));
await b.close(); srv.close();
