
let frameEl = null;
let ro = null;

function syncHeight() {
  if (!frameEl) return;
  try {
    const d = frameEl.contentDocument;
    if (!d || !d.documentElement) return;
    const h = Math.max(d.documentElement.scrollHeight, (d.body && d.body.scrollHeight) || 0);
    // 精确取内容高度：内页 body 有 min-h-svh（最矮=iframe 视口），h 只会≥当前高，
    // 设为 h 天然收敛；若多加缓冲（h+24）会抬高视口→min-h 跟涨→无限回环（实测 11512px 失控）
    if (h > 100) frameEl.style.height = h + 'px';
  } catch (e) {}
}

function watch() {
  if (!frameEl) return;
  syncHeight();
  try {
    const d = frameEl.contentDocument;
    const w = d && d.defaultView;
    if (w && 'ResizeObserver' in w) {
      if (ro) ro.disconnect();
      ro = new w.ResizeObserver(syncHeight);
      ro.observe(d.documentElement);
    }
  } catch (e) {}
}

ctx.render(
  <div style={{ margin: -24 }}>
    <iframe
      ref={(el) => { frameEl = el; }}
      src="/x/main/schedule/board?embed=1"
      style={{ width: '100%', height: 'calc(100vh - 140px)', border: 0, display: 'block' }}
      title="board"
      onLoad={watch}
    />
  </div>
);
setTimeout(watch, 3000);
setTimeout(watch, 8000);
