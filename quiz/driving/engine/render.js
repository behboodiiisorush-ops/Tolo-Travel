#!/usr/bin/env node
// Render a driving-quiz episode (template.html + episode.json + timeline.json) to video.
// usage: node render.js <episode_dir> [--still 1.0,12.5] [--workers 3] [--ep episode.json] [--name epNN_quiz]
//   --ep picks another episode file in the folder (e.g. episode.de-subs.json); --name the output file name.
// Headless Chromium draws each frame (renderAt(t)); frames go straight into ffmpeg, one slice per worker,
// then the slices are joined and audio/mix.wav is muxed in.
const { chromium } = require('playwright');
const { spawn, execFileSync } = require('child_process');
const fs = require('fs'), path = require('path');

const args = process.argv.slice(2);
const EP = path.resolve(args[0]);
const opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const STILL = opt('--still', ''), W = +opt('--workers', 3);
const ep = JSON.parse(fs.readFileSync(`${EP}/${opt('--ep', 'episode.json')}`, 'utf8'));
const tl = JSON.parse(fs.readFileSync(`${EP}/timeline.json`, 'utf8'));
const OUTNAME = opt('--name', path.basename(EP) + '_quiz');

async function newPage(browser) {
  const pg = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await pg.goto('file://' + path.join(__dirname, 'template.html'));
  await pg.evaluate(([e, t]) => init(e, t), [ep, tl]);
  await pg.evaluate(() => document.fonts.ready);
  await pg.waitForTimeout(300);
  return pg;
}

(async () => {
  const browser = await chromium.launch({ args: ['--font-render-hinting=none'] });
  if (STILL) {
    fs.mkdirSync(`${EP}/stills`, { recursive: true }); const pre = opt('--name', '');
    const pg = await newPage(browser);
    for (const s of STILL.split(',')) {
      const t = +s; await pg.evaluate(t => renderAt(t), t);
      await pg.screenshot({ path: `${EP}/stills/${pre}t${t.toFixed(2).padStart(6, '0')}.png` });
    }
    await browser.close(); return;
  }
  fs.mkdirSync(`${EP}/out`, { recursive: true });
  const N = Math.round(tl.duration * tl.fps), per = Math.ceil(N / W);
  const parts = [];
  await Promise.all([...Array(W).keys()].map(async k => {
    const f0 = k * per, f1 = Math.min(N, (k + 1) * per), out = `${EP}/out/part${k}.mp4`; parts[k] = out;
    const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(tl.fps), '-c:v', 'mjpeg', '-i', '-',
      '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', out], { stdio: ['pipe', 'inherit', 'inherit'] });
    const done = new Promise(r => ff.on('close', r));
    const pg = await newPage(browser);
    for (let f = f0; f < f1; f++) {
      await pg.evaluate(t => renderAt(t), f / tl.fps);
      const buf = await pg.screenshot({ type: 'jpeg', quality: 94 });
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if ((f - f0) % 150 === 0) console.log(`worker ${k}: ${f}/${f1}`);
    }
    ff.stdin.end(); await done;
  }));
  await browser.close();
  fs.writeFileSync(`${EP}/out/parts.txt`, parts.map(p => `file '${p}'`).join('\n'));
  const silent = `${EP}/out/${OUTNAME}_silent.mp4`, final = `${EP}/out/${OUTNAME}.mp4`;
  execFileSync('ffmpeg', ['-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', `${EP}/out/parts.txt`, '-c', 'copy', silent]);
  execFileSync('ffmpeg', ['-v', 'error', '-y', '-i', silent, '-i', `${EP}/audio/mix.wav`, '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
    '-shortest', '-movflags', '+faststart', final]);
  parts.forEach(p => fs.unlinkSync(p)); fs.unlinkSync(`${EP}/out/parts.txt`);
  console.log('done:', final);
})();
