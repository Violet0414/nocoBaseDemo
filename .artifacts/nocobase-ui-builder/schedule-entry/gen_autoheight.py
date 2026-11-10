#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""D76：3 个 admin 排课入口 jsBlock 改为 iframe 高度自适应版。
内页（embed 模式不锁高）内容生长 → ResizeObserver + load/兜底定时同步 iframe 高度
→ admin 外层滚动条随内容增长。纯 ASCII 代码，dollar-quote $js$ 落 SQL 文件，
走 docker exec -i psql < 通路（D75 转义坑规避）。
"""
import json, pathlib

ART = pathlib.Path(__file__).parent

CODE_TEMPLATE = r'''
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
      src="__SRC__"
      style={{ width: '100%', height: 'calc(100vh - 140px)', border: 0, display: 'block' }}
      title="__TITLE__"
      onLoad={watch}
    />
  </div>
);
setTimeout(watch, 3000);
setTimeout(watch, 8000);
'''

ROWS = [
    ("s96hi0xk166", "/x/main/schedule/board?embed=1", "board"),
    ("ykhawbr91vm", "/x/main/schedule/week?embed=1", "week"),
    ("6nia4y84u97", "/x/main/schedule/seats?embed=1", "seats"),
]

stmts = []
for uid, src, title in ROWS:
    code = CODE_TEMPLATE.replace("__SRC__", src).replace("__TITLE__", title)
    stmts.append(
        "UPDATE \"flowModels\" SET options = jsonb_set(options::jsonb, "
        "'{stepParams,jsSettings,runJs,code}', to_jsonb($js$" + code + "$js$::text))::json "
        "WHERE uid='" + uid + "';"
    )
    # 留一份代码副本便于回查
    (ART / f"jsblock-autoheight-{title}.js").write_text(code, encoding="utf-8")

sql = "-- D76: iframe 高度自适应（配合 layout.tsx embed 不锁高 + api.ts 班级同时段冲突规则）\n" + "\n".join(stmts) + "\n"
(ART / "autoheight.sql").write_text(sql, encoding="utf-8")
print("written autoheight.sql + 3 code copies")
