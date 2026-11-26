# Claude 대시보드 페이지(index.html)를 GitHub Pages용 정적 페이지로 바꿉니다.
# 사용: python3 make_public.py <대시보드 page.html> <출력 폴더(안에 data/*.csv)> <루트 요소 id>
import re, sys, os, glob
src, out, root = sys.argv[1], sys.argv[2], sys.argv[3]
s = open(src, encoding='utf-8').read()
s = s.replace('<meta name="dash-one-writer">\n', '')
s = re.sub(r'@font-face \{[^}]*\}\n', '', s)
title = re.search(r'<h1>(.*?)</h1>', s).group(1)
s = s.replace(f'<h1>{title}</h1>', f'<a class="pub-back" href="../">← 리포트 허브</a>\n<h1>{title}</h1>', 1)
ids = sorted(os.path.basename(p)[:-4] for p in glob.glob(out + '/data/*.csv'))
shim = r'''
window.dash = (() => {
  const src = {}, calcs = {}, draws = {}, cache = {};
  const get = (id) => {
    if (src[id]) return { status: 'ok', data: src[id], columns: src[id].columns };
    const c = calcs[id]; if (!c) return { status: 'loading', data: [] };
    if (cache[id]) return cache[id];
    const ins = c.inputs.map((i) => get(i));
    if (ins.some((x) => x.status !== 'ok')) return { status: 'loading', data: null };
    return (cache[id] = { status: 'ok', data: c.fn(...ins.map((x) => x.data)) });
  };
  const run = (name) => { for (const el of document.querySelectorAll(`[data-draw="${name}"]`)) { try { draws[name](el); } catch (e) { console.error(name, e); } } };
  return {
    _load(id, rows) { src[id] = rows; for (const k in cache) delete cache[k]; },
    _all() { for (const n in draws) run(n); },
    data: get, calc(id, o) { calcs[id] = o; },
    draw(name, fn) { if (fn) { draws[name] = fn; run(name); } else if (draws[name]) run(name); },
    onData(fn) { try { fn(); } catch (e) { console.error(e); } }, params: () => ({}), setParams() {}, resetParams() {}, setLink() {}, refresh() {},
    colors: ['#2f6fdb', '#e8590c', '#0e9384', '#7a5af8', '#c0392b', '#b7791f'],
  };
})();
'''
loader = '''
Promise.all(%s.map((id) => fetch(`data/${id}.csv?v=${Date.now()}`).then((r) => r.text()).then((t) => [id, d3.csvParse(t, (r) => { for (const k in r) if (r[k] === '') r[k] = null; return r; })])))
  .then((all) => { for (const [id, rows] of all) dash._load(id, rows); dash._all(); })
  .catch((e) => console.error(e));
let pubRt; window.addEventListener('resize', () => { clearTimeout(pubRt); pubRt = setTimeout(() => dash._all(), 150); });
''' % repr(ids).replace("'", '"')
head_css = '''html, body { margin: 0; }
body { background: #ecebe7; padding: 24px max(16px, env(safe-area-inset-left, 0px)) 40px max(16px, env(safe-area-inset-right, 0px)); }
body:has(.ev-dark, .sc-dark, .bn-dark) { background: #121211; }
#%s { --cds-radius: 12px; --cds-gap-lg: 16px; --cds-font-weight-medium: 600; --font-anthropic-sans: system-ui; }
.dash-select { font: inherit; font-size: 12.5px; padding: 5px 8px; border: 1px solid var(--color-border-line); border-radius: 8px; }
.pub-back { display: inline-block; margin-bottom: 6px; font-size: 12px; color: var(--color-fg-muted); text-decoration: none; }
.pub-back:hover { text-decoration: underline; }
''' % root
s = s.replace('<style>', '<style>\n' + head_css, 1)
# 페이지의 첫 inline script 앞에 d3와 shim, 마지막에 loader
i = s.index('<script>')
s = s[:i] + '<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js"></script>\n<script>' + shim + '</script>\n' + s[i:]
s = s.rstrip() + '\n<script>' + loader + '</script>\n'
html = f'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="robots" content="noindex, nofollow">
<title>{title}</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">
</head>
<body>
{s}
</body>
</html>
'''
open(out + '/index.html', 'w', encoding='utf-8').write(html)
print(title, ids)
