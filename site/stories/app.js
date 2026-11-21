// Gallery: reads videos.json (built by tools/build_site.py), one tab per set, tap a card to play.
// Text from data goes in with textContent only; links are https only.
(async () => {
  const CFG = { allLabel: 'All', storeKey: 'capy-gallery-set' };
  const $ = (id) => document.getElementById(id);
  const el = (tag, props = {}, kids = []) => { const e = document.createElement(tag); Object.assign(e, props); kids.forEach((k) => e.append(k)); return e; };
  const data = await (await fetch('videos.json', { cache: 'no-cache' })).json();
  // a video plays from this site or from this repo's GitHub Releases, nowhere else (the CSP allows the same hosts)
  const okVideo = (u) => /^https:\/\/github\.com\/leftbrain847\/videos_public\/releases\/download\/stories-(scary|heist|myth|space|mind)-[0-9a-z-]+\/(scary|heist|myth|space|mind)_\d+_[a-z0-9_]+\.mp4$/.test(u);
  const V = data.videos.filter((v) => okVideo(v.video));
  let set = 'all'; try { set = localStorage.getItem(CFG.storeKey) || 'all'; } catch (e) { /* storage may be unavailable */ }
  let list = [], cur = -1;

  function tabs() {
    const nav = $('tabs'); nav.replaceChildren();
    const opts = [['all', `${CFG.allLabel} (${V.length})`], ...Object.entries(data.sets).map(([k, name]) => [k, `${name} (${V.filter((v) => v.set === k).length})`])];
    for (const [k, label] of opts) {
      const b = el('button', { type: 'button', textContent: label });
      b.setAttribute('aria-pressed', String(k === set));
      b.onclick = () => { set = k; try { localStorage.setItem(CFG.storeKey, k); } catch (e) { /* ignore */ } tabs(); grid(); };
      nav.append(b);
    }
  }
  function grid() {
    list = V.filter((v) => set === 'all' || v.set === set);
    $('count').textContent = `${list.length} videos · tap one to play`;
    $('grid').replaceChildren(...list.map((v, i) => {
      const img = el('img', { src: v.poster, alt: '', loading: 'lazy', decoding: 'async' });
      const b = el('button', { type: 'button', className: 'card' }, [img, el('span', { textContent: v.title }, [el('small', { textContent: v.id })])]);
      b.onclick = () => open(i);
      return b;
    }));
  }
  function open(i) {
    cur = (i + list.length) % list.length; const v = list[cur];
    const pv = $('pv'); pv.poster = v.poster; pv.src = v.video;
    $('pt').textContent = v.title; $('ph').textContent = v.hook;
    $('ps').replaceChildren(...v.sources.filter((s) => /^https:\/\//.test(s.url)).map((s) => el('li', {}, [el('a', { href: s.url, textContent: s.title || s.url, target: '_blank', rel: 'noopener noreferrer' })])));
    const d = $('player'); if (!d.open) d.showModal();
    pv.play().catch(() => { /* autoplay may be blocked until tapped */ });
  }
  $('close').onclick = () => { $('pv').pause(); $('player').close(); };
  $('player').addEventListener('close', () => { $('pv').pause(); $('pv').removeAttribute('src'); $('pv').load(); });
  $('prev').onclick = () => open(cur - 1);
  $('next').onclick = () => open(cur + 1);
  $('pv').addEventListener('ended', () => open(cur + 1));
  tabs(); grid();
})();
