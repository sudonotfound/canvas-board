#!/usr/bin/env python3
"""ボードのデータ（board.json）から、見るだけのキャンバスHTML（board.html）を作る。

使い方:
    python3 build-board.py [board.json のパス]

省略時はカレントディレクトリの board.json を読む。
HTML は board.json と同じフォルダに board.html として書き出す。
データの項目は README.md を参照。配置は中身に合わせて自動で決まる。
"""
import json
import sys
from pathlib import Path

DEFAULT_DB = Path("board.json")
COLORS = {"green", "yellow", "gray", "red", "orange", "blue", "pink", "purple"}


def validate(db):
    errors = []
    sections = {s["id"]: s for s in db["sections"]}
    if len(sections) != len(db["sections"]):
        errors.append("section の id が重複しています")
    for s in db["sections"]:
        if s.get("parent") and s["parent"] not in sections:
            errors.append(f"section {s['id']}: parent {s['parent']} がありません")
    ids = set()
    for it in db["items"]:
        if it["id"] in ids:
            errors.append(f"item の id が重複しています: {it['id']}")
        ids.add(it["id"])
        if it["section"] not in sections:
            errors.append(f"item {it['id']}: section {it['section']} がありません")
        if it.get("color") and it["color"] not in COLORS:
            errors.append(f"item {it['id']}: color {it['color']} は使えません（{', '.join(sorted(COLORS))}）")
    return errors


def main():
    db_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_DB
    db = json.loads(db_path.read_text(encoding="utf-8"))
    errors = validate(db)
    if errors:
        print("board.json に問題があります:", *errors, sep="\n  ", file=sys.stderr)
        sys.exit(1)
    data = json.dumps(db, ensure_ascii=False).replace("</", "<\\/")
    html = TEMPLATE.replace("__TITLE__", db.get("title", "タスクボード")).replace("__DATA__", data)
    out = db_path.with_name("board.html")
    out.write_text(html, encoding="utf-8")
    print(f"書き出しました: {out}（セクション {len(db['sections'])} / アイテム {len(db['items'])}）")


TEMPLATE = r"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<style>
:root {
  --bg: #f4f3ef; --dot: #d6d3cb; --ink: #23221f; --muted: #6b6860;
  --section: rgba(255,255,255,.72); --section-line: #d9d5cc; --section-title: #3d3b36;
  --sub: rgba(244,243,239,.9);
  --bar: rgba(255,255,255,.92); --bar-line: #e2dfd8; --accent: #3b6fd8;
  --s-green: #cdeccf; --s-yellow: #fff1a8; --s-gray: #e6e4df; --s-red: #ffc9c2;
  --s-orange: #ffd8ad; --s-blue: #c6e0ff; --s-pink: #ffd3ea; --s-purple: #e0d4ff;
  --s-ink: #23221f; --link-bg: #ffffff;
  --shadow: 0 1px 2px rgba(0,0,0,.08), 0 4px 12px rgba(0,0,0,.06);
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #1b1b1a; --dot: #34332f; --ink: #ecebe6; --muted: #a29f97;
    --section: rgba(40,40,38,.8); --section-line: #45433e; --section-title: #e3e1da;
    --sub: rgba(30,30,29,.85);
    --bar: rgba(36,36,34,.94); --bar-line: #45433e; --accent: #7aa2f7;
    --s-green: #a9d4ac; --s-yellow: #e8d784; --s-gray: #c9c6bf; --s-red: #e9aaa2;
    --s-orange: #e8bb88; --s-blue: #a5c4ea; --s-pink: #e5b2cd; --s-purple: #c2b3ea;
    --link-bg: #2a2a28;
    --shadow: 0 1px 2px rgba(0,0,0,.4), 0 4px 12px rgba(0,0,0,.3);
  }
}
:root[data-theme="dark"] {
  --bg: #1b1b1a; --dot: #34332f; --ink: #ecebe6; --muted: #a29f97;
  --section: rgba(40,40,38,.8); --section-line: #45433e; --section-title: #e3e1da;
  --sub: rgba(30,30,29,.85);
  --bar: rgba(36,36,34,.94); --bar-line: #45433e; --accent: #7aa2f7;
  --s-green: #a9d4ac; --s-yellow: #e8d784; --s-gray: #c9c6bf; --s-red: #e9aaa2;
  --s-orange: #e8bb88; --s-blue: #a5c4ea; --s-pink: #e5b2cd; --s-purple: #c2b3ea;
  --link-bg: #2a2a28;
  --shadow: 0 1px 2px rgba(0,0,0,.4), 0 4px 12px rgba(0,0,0,.3);
}
* { box-sizing: border-box; }
html, body { margin: 0; height: 100%; overflow: hidden; }
body {
  background: var(--bg); color: var(--ink);
  font-family: -apple-system, BlinkMacSystemFont, "Hiragino Sans", "Noto Sans JP", sans-serif;
  -webkit-font-smoothing: antialiased;
}
#viewport { position: fixed; inset: 0; cursor: grab; touch-action: none;
  background-image: radial-gradient(var(--dot) 1px, transparent 1px); }
#viewport.dragging { cursor: grabbing; }
#world { position: absolute; left: 0; top: 0; transform-origin: 0 0; padding: 40px;
  display: flex; flex-direction: column; gap: 36px; width: max-content; }

/* 配置は中身に合わせて自動で決める（board.json の x/y/w/h は使わない） */
.board-title { font-weight: 800; font-size: 40px; letter-spacing: .02em; white-space: nowrap; margin-left: 4px; }
.section { border: 2px solid var(--section-line); border-radius: 14px; background: var(--section); padding: 18px 22px 22px; }
.section .section { background: var(--sub); border-width: 1px; padding: 14px 16px 16px; }
.s-head { display: flex; align-items: baseline; gap: 12px; margin-bottom: 16px; white-space: nowrap; }
.s-title { font-weight: 700; font-size: 28px; color: var(--section-title); }
.section .section .s-title { font-size: 19px; }
.section .section .section .s-title { font-size: 16px; }
.section .section .s-head { margin-bottom: 12px; }
.s-note { font-size: 14px; color: var(--muted); }
.s-count { font-weight: 600; color: var(--muted); font-size: 14px; font-variant-numeric: tabular-nums; }
.row { display: flex; gap: 20px; align-items: flex-start; }
.grid { display: grid; grid-template-columns: repeat(var(--cols), max-content); gap: 14px; align-items: start; }
.stack { display: flex; flex-direction: column; gap: 10px; }
.col { width: 260px; align-self: stretch; }
.empty { font-size: 14px; color: var(--muted); padding: 4px 2px; }

.item { position: relative; cursor: pointer; }
.sticky { width: 220px; min-height: 96px; background: var(--c); color: var(--s-ink); border-radius: 4px;
  box-shadow: var(--shadow); padding: 12px 14px; font-size: 16px; line-height: 1.5; word-break: break-word; }
.col .sticky { width: auto; }
.sticky .s-text { display: -webkit-box; -webkit-box-orient: vertical; -webkit-line-clamp: 5; overflow: hidden; white-space: pre-line; }
.sticky .meta { display: block; font-size: 12px; opacity: .65; margin-top: 8px; }
.sticky .tag { display: inline-block; font-size: 12px; font-weight: 600; background: rgba(0,0,0,.08);
  border-radius: 999px; padding: 1px 8px; margin-bottom: 6px; }
.item:hover { outline: 3px solid var(--accent); outline-offset: 2px; }
.link { width: 240px; background: var(--link-bg); border: 1px solid var(--section-line); border-radius: 10px;
  box-shadow: var(--shadow); padding: 14px 16px; }
.link .l-title { font-weight: 700; font-size: 15px; line-height: 1.35; }
.link .l-desc { font-size: 13px; color: var(--muted); margin-top: 6px; line-height: 1.45;
  display: -webkit-box; -webkit-box-orient: vertical; -webkit-line-clamp: 2; overflow: hidden; }
.link .l-site { font-size: 12px; color: var(--muted); margin-top: 8px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.priority { grid-column: 1 / -1; display: flex; align-items: center; gap: 12px; font-weight: 700; font-size: 15px;
  pointer-events: none; cursor: default; }
.priority .p-line { flex: 1; height: 6px; border-radius: 3px; background: linear-gradient(90deg, var(--ink), transparent); opacity: .6; }
.text { white-space: pre-wrap; }

#bar { position: fixed; top: 12px; left: 12px; right: 12px; display: flex; gap: 8px; align-items: center;
  flex-wrap: wrap; pointer-events: none; }
#bar > * { pointer-events: auto; }
.pill { background: var(--bar); border: 1px solid var(--bar-line); border-radius: 10px; box-shadow: var(--shadow);
  display: flex; align-items: center; gap: 2px; padding: 4px; backdrop-filter: blur(8px); }
.pill.title { padding: 8px 14px; gap: 10px; }
.pill.title b { font-size: 15px; }
.pill.title span { font-size: 12px; color: var(--muted); }
.spacer { flex: 1; }
button, select { font: inherit; font-size: 14px; color: var(--ink); background: transparent; border: 0;
  border-radius: 7px; padding: 6px 10px; cursor: pointer; }
button:hover, select:hover { background: rgba(127,127,127,.15); }
#zoom { min-width: 56px; text-align: center; font-variant-numeric: tabular-nums; }
select { max-width: 200px; }

#panel { position: fixed; right: 12px; top: 64px; bottom: 12px; width: min(420px, calc(100vw - 24px));
  background: var(--bar); border: 1px solid var(--bar-line); border-radius: 12px; box-shadow: var(--shadow);
  padding: 18px 20px; overflow: auto; display: none; backdrop-filter: blur(8px); }
#panel.open { display: block; }
#panel .path { font-size: 12px; color: var(--muted); }
#panel .body { white-space: pre-wrap; line-height: 1.7; margin-top: 12px; font-size: 15px; }
#panel dl { display: grid; grid-template-columns: auto 1fr; gap: 4px 12px; font-size: 13px; margin: 14px 0 0; }
#panel dt { color: var(--muted); }
#panel dd { margin: 0; }
#panel .close { float: right; margin: -6px -8px 0 0; }
.hint { position: fixed; left: 12px; bottom: 12px; font-size: 12px; color: var(--muted); }
@media (max-width: 640px) { .hint { display: none; } .pill.title span { display: none; } }
</style>
</head>
<body>
<div id="viewport"><div id="world"></div></div>
<div id="bar">
  <div class="pill title"><b id="title"></b><span id="updated"></span></div>
  <div class="spacer"></div>
  <div class="pill"><select id="jump" aria-label="セクションへ移動"></select></div>
  <div class="pill">
    <button id="out" aria-label="縮小">−</button><button id="zoom" title="100%にする"></button><button id="in" aria-label="拡大">＋</button>
    <button id="fit">全体</button>
  </div>
</div>
<aside id="panel" aria-live="polite"></aside>
<div class="hint">ドラッグ / 2本指スクロールで移動・ピンチ / ⌘+ホイールで拡大縮小・0 で全体・付箋クリックで全文</div>
<script type="application/json" id="data">__DATA__</script>
<script>
const db = JSON.parse(document.getElementById('data').textContent);
const world = document.getElementById('world');
const viewport = document.getElementById('viewport');
const sections = new Map(db.sections.map(s => [s.id, s]));
const els = new Map();  // section id → 要素
const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));

document.getElementById('title').textContent = db.title;
document.getElementById('updated').textContent = '更新 ' + (db.updated || '');
document.title = db.title;

function path(id) { const out = []; let s = sections.get(id); while (s) { out.unshift(s.name); s = s.parent && sections.get(s.parent); } return out.join(' › '); }
const childrenOf = id => db.sections.filter(s => s.parent === id);
const itemsOf = id => db.items.filter(it => it.section === id);
const div = (cls, html = '') => { const el = document.createElement('div'); el.className = cls; el.innerHTML = html; return el; };

function renderItem(it) {
  const type = it.type ?? 'sticky';
  const el = div('item ' + type);
  if (type === 'sticky') {
    el.style.setProperty('--c', `var(--s-${it.color || 'yellow'})`);
    const meta = [it.due && '期限 ' + it.due, it.goal && '完了条件あり'].filter(Boolean).join('・');
    el.innerHTML = (it.project ? `<span class="tag">${esc(it.project)}</span>` : '') + `<div class="s-text">${esc(it.text)}</div>` +
      (meta ? `<span class="meta">${esc(meta)}</span>` : '');
  } else if (type === 'link') {
    el.innerHTML = `<div class="l-title">${esc(it.title)}</div>` + (it.desc ? `<div class="l-desc">${esc(it.desc)}</div>` : '') +
      `<div class="l-site">🔗 ${esc(it.url || it.site)}</div>`;
  } else if (type === 'priority') {
    el.innerHTML = '<span>優先度　高</span><div class="p-line"></div><span>低</span>';
  } else if (type === 'text') {
    el.style.fontSize = (it.size || 18) + 'px'; el.style.width = (it.w || 400) + 'px';
    el.textContent = it.text;
  }
  el.dataset.id = it.id;
  return el;
}
// 並べる数に合わせて列数を決める（横に長くなりすぎないように）
function grid(nodes) {
  const g = div('grid');
  g.style.setProperty('--cols', Math.min(4, Math.max(1, Math.ceil(Math.sqrt(nodes.length * 1.5)))));
  nodes.forEach(n => g.appendChild(n));
  return g;
}
// 最上位のセクションで、子が入れ子を持たないセクションだけなら、同じ幅の列（カンバン）として並べる
function renderSection(s, depth, asCol = false) {
  const kids = childrenOf(s.id), items = itemsOf(s.id);
  const board = depth === 0 && kids.length && !items.length && kids.every(k => !childrenOf(k.id).length);
  const el = div('section' + (asCol ? ' col' : ''));
  const n = items.filter(it => ['sticky', 'link'].includes(it.type ?? 'sticky')).length;
  el.appendChild(div('s-head', `<span class="s-title">${esc(s.name)}</span>` +
    (depth ? `<span class="s-count">${n}</span>` : '') + (s.note ? `<span class="s-note">${esc(s.note)}</span>` : '')));
  const kidEls = kids.map(k => renderSection(k, depth + 1, board)), itemEls = items.map(renderItem);
  let body;
  if (!kidEls.length && !itemEls.length) body = div('empty', 'なし');
  else if (depth === 0) {
    body = div('row');
    kidEls.forEach(k => body.appendChild(k));
    if (itemEls.length) body.appendChild(grid(itemEls));
  } else if (asCol) { body = div('stack'); itemEls.forEach(i => body.appendChild(i)); }
  else body = grid([...kidEls, ...itemEls]);
  el.appendChild(body);
  els.set(s.id, el);
  return el;
}

world.appendChild(div('board-title', esc(db.title)));
db.sections.filter(s => !s.parent).forEach(s => world.appendChild(renderSection(s, 0)));

// 表示位置（パン・ズーム）
let v = {x: 0, y: 0, k: 1};
const MIN = 0.05, MAX = 4;
const zoomLabel = document.getElementById('zoom');
function apply(save = true) {
  world.style.transform = `translate(${v.x}px, ${v.y}px) scale(${v.k})`;
  let g = 24 * v.k; while (g < 12) g *= 4;
  viewport.style.backgroundSize = `${g}px ${g}px`;
  viewport.style.backgroundPosition = `${v.x}px ${v.y}px`;
  zoomLabel.textContent = Math.round(v.k * 100) + '%';
  if (save) try { localStorage.setItem('board-view-v2', JSON.stringify(v)); } catch (e) {}
}
function zoomAt(cx, cy, k) {
  k = Math.min(MAX, Math.max(MIN, k));
  v.x = cx - (cx - v.x) * (k / v.k); v.y = cy - (cy - v.y) * (k / v.k); v.k = k; apply();
}
// world 上の位置と大きさ（いまの表示位置から逆算する）
function rectOf(el) { const r = el.getBoundingClientRect();
  return {x: (r.left - v.x) / v.k, y: (r.top - v.y) / v.k, w: r.width / v.k, h: r.height / v.k}; }
function fitTo(r, pad = 48, max = MAX) {
  const top = 64, W = innerWidth - pad * 2, H = innerHeight - top - pad * 2;
  v.k = Math.min(max, Math.max(MIN, Math.min(W / r.w, H / r.h)));
  v.x = pad + (W - r.w * v.k) / 2 - r.x * v.k; v.y = top + pad + (H - r.h * v.k) / 2 - r.y * v.k; apply();
}
function fitAll() { fitTo(rectOf(world)); }
// 最初に開いたとき：幅に合わせて上から見せる（文字が小さくなりすぎないように）
function fitWidth() { const r = rectOf(world);
  v.k = Math.min(1, Math.max(MIN, (innerWidth - 32) / r.w)); v.x = (innerWidth - r.w * v.k) / 2; v.y = 56; apply(); }
const fitSection = id => fitTo(rectOf(els.get(id)), 48, 1.2);

viewport.addEventListener('wheel', e => {
  e.preventDefault();
  if (e.ctrlKey || e.metaKey) zoomAt(e.clientX, e.clientY, v.k * Math.exp(-e.deltaY * 0.01));
  else { v.x -= e.deltaX; v.y -= e.deltaY; apply(); }
}, {passive: false});

// ドラッグで移動・ピンチで拡大縮小（タッチ）
const pts = new Map(); let moved = 0, pinch = null;
viewport.addEventListener('pointerdown', e => {
  pts.set(e.pointerId, {x: e.clientX, y: e.clientY}); moved = 0;
  viewport.setPointerCapture(e.pointerId); viewport.classList.add('dragging');
  if (pts.size === 2) { const [a, b] = [...pts.values()]; pinch = {d: Math.hypot(a.x - b.x, a.y - b.y), k: v.k}; }
});
viewport.addEventListener('pointermove', e => {
  const p = pts.get(e.pointerId); if (!p) return;
  const dx = e.clientX - p.x, dy = e.clientY - p.y; moved += Math.abs(dx) + Math.abs(dy);
  p.x = e.clientX; p.y = e.clientY;
  if (pts.size === 2 && pinch) {
    const [a, b] = [...pts.values()];
    zoomAt((a.x + b.x) / 2, (a.y + b.y) / 2, pinch.k * Math.hypot(a.x - b.x, a.y - b.y) / pinch.d);
  } else if (pts.size === 1) { v.x += dx; v.y += dy; apply(); }
});
function up(e) {
  pts.delete(e.pointerId); if (pts.size < 2) pinch = null;
  if (!pts.size) viewport.classList.remove('dragging');
}
viewport.addEventListener('pointerup', e => {
  if (pts.size === 1 && moved < 5) {
    const el = document.elementFromPoint(e.clientX, e.clientY)?.closest('.item');
    el ? show(el.dataset.id) : hide();
  }
  up(e);
});
viewport.addEventListener('pointercancel', up);

// 全文パネル
const panel = document.getElementById('panel');
function show(id) {
  const it = db.items.find(i => i.id === id); if (!it || it.type === 'priority') return;
  const rows = [['プロジェクト', it.project], ['期限', it.due], ['完了条件', it.goal], ['URL', it.url]]
    .filter(r => r[1]).map(([k, val]) => `<dt>${k}</dt><dd>${esc(val)}</dd>`).join('');
  panel.innerHTML = `<button class="close" aria-label="閉じる">✕</button><div class="path">${esc(path(it.section))} · ${esc(it.id)}</div>` +
    (it.type === 'link' ? `<h3>${esc(it.title)}</h3><div class="body">${esc(it.desc)}\n${esc(it.site)}</div>` : `<div class="body">${esc(it.text)}</div>`) +
    (rows ? `<dl>${rows}</dl>` : '');
  panel.querySelector('.close').onclick = hide;
  panel.classList.add('open');
}
function hide() { panel.classList.remove('open'); }

// ツールバー
const jump = document.getElementById('jump');
jump.innerHTML = '<option value="">セクションへ移動…</option>' + db.sections.filter(s => !s.parent || sections.get(s.parent) && !sections.get(s.parent).parent)
  .map(s => `<option value="${esc(s.id)}">${s.parent ? '　' : ''}${esc(s.name)}</option>`).join('');
jump.onchange = () => { if (jump.value) fitSection(jump.value); jump.value = ''; };
const center = () => [innerWidth / 2, innerHeight / 2];
document.getElementById('in').onclick = () => zoomAt(...center(), v.k * 1.25);
document.getElementById('out').onclick = () => zoomAt(...center(), v.k / 1.25);
zoomLabel.onclick = () => zoomAt(...center(), 1);
document.getElementById('fit').onclick = fitAll;
addEventListener('keydown', e => {
  if (e.target.tagName === 'SELECT') return;
  if (e.key === '0') fitAll();
  else if (e.key === '+' || e.key === '=') zoomAt(...center(), v.k * 1.25);
  else if (e.key === '-') zoomAt(...center(), v.k / 1.25);
  else if (e.key === 'Escape') hide();
});

let restored = false;
const target = sections.get(decodeURIComponent(location.hash.slice(1)));
if (target) { fitSection(target.id); restored = true; }
else try { const s = JSON.parse(localStorage.getItem('board-view-v2')); if (s && s.k) { v = s; apply(false); restored = true; } } catch (e) {}
if (!restored) fitWidth();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
