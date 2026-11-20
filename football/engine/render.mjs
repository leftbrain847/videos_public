// Render the story half: node render.mjs <video_dir> [--fps 30] [--stills t1,t2,...] [--draft]
// Plays the page on a virtual clock (frame by frame), pipes JPEG frames to ffmpeg -> build/top.mp4.
import { createRequire } from 'module';
import http from 'http'; import fs from 'fs'; import path from 'path'; import { spawn } from 'child_process';
const require = createRequire(import.meta.url);
const PW = process.env.PWMOD || '/opt/node-tools/node_modules/playwright';
const { chromium } = require(PW);
const CHROME = process.env.CHROME || '/opt/pw-browsers/chromium';

const args = process.argv.slice(2); const vd = path.resolve(args[0]);
const opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const fps = Number(opt('--fps', 24)); const draft = args.includes('--draft'); const stills = opt('--stills', null);
const root = path.dirname(new URL(import.meta.url).pathname);
const types = { '.js': 'text/javascript', '.html': 'text/html', '.otf': 'font/otf', '.json': 'application/json' };
const srv = http.createServer((q, s) => {
  const f = path.join(root, decodeURIComponent(q.url.split('?')[0]));
  if (!f.startsWith(root) || !fs.existsSync(f)) { s.writeHead(404); return s.end(); }
  s.writeHead(200, { 'Content-Type': types[path.extname(f)] || 'application/octet-stream' }); fs.createReadStream(f).pipe(s);
});
await new Promise((ok) => srv.listen(0, ok)); const port = srv.address().port;
const script = JSON.parse(fs.readFileSync(path.join(vd, 'video.json'), 'utf8'));
const timing = JSON.parse(fs.readFileSync(path.join(vd, 'build/timing.json'), 'utf8'));
const b = await chromium.launch({ executablePath: CHROME, args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const p = await b.newPage({ viewport: { width: 1080, height: 960 } });
p.on('pageerror', (e) => { console.error('page error:', e.message); process.exitCode = 1; });
await p.goto(`http://localhost:${port}/page.html${draft ? '?draft=1' : ''}`); await p.waitForFunction(() => window.ready, null, { timeout: 60000 });
await p.evaluate(([s, t]) => window.load(s, t), [script, timing]);
const dec = (u) => Buffer.from(u.slice(u.indexOf(',') + 1), 'base64');
if (stills) {
  for (const t of stills.split(',').map(Number)) fs.writeFileSync(path.join(vd, `build/still_${t}.jpg`), dec(await p.evaluate((t) => window.frame(t), t)));
} else {
  const n = Math.round(timing.target_s * fps);
  const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', path.join(vd, 'build/top.mp4')], { stdio: ['pipe', 'inherit', 'inherit'] });
  const t0 = Date.now();
  for (let i = 0; i < n; i++) {
    const buf = dec(await p.evaluate((t) => window.frame(t), i / fps));
    if (!ff.stdin.write(buf)) await new Promise((ok) => ff.stdin.once('drain', ok));
    if (i % (fps * 10) === 0) console.log(`frame ${i}/${n} ${((Date.now() - t0) / 1000).toFixed(0)}s`);
  }
  ff.stdin.end(); await new Promise((ok) => ff.on('close', ok));
  console.log(`top.mp4 ${n} frames in ${((Date.now() - t0) / 1000).toFixed(0)}s`);
}
await b.close(); srv.close();
