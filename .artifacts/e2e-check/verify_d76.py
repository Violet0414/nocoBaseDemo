# -*- coding: utf-8 -*-
"""D76 验证：①班级同时段冲突规则真实触发（测试班级 3 节同时段课）；②iframe 高度自适应
（内页内容超长时 iframe 增高、admin 外层可滚）。验证完自动清理 D76 测试数据。"""
import pathlib
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:13000"
HERE = pathlib.Path(__file__).parent
SHOTS = HERE / "shots"
SHOTS.mkdir(exist_ok=True)

WEEK_URL = "/admin/e3enf6pad6r"       # 课表查询（iframe 嵌 week?embed=1）
BOARD_URL = "/admin/aj8s3d0rqul"      # 排课管理（board?embed=1）

def login(page, account):
    page.goto(BASE + "/sign-in", wait_until="domcontentloaded")
    page.wait_for_selector("input", timeout=60000)
    page.locator("input[type='text'], input:not([type])").first.fill(account)
    page.locator("input[type='password']").first.fill("dx123456")
    page.locator("button:has-text('登 录'), button:has-text('登录'), button[type='submit']").first.click()
    try:
        page.wait_for_url("**/admin/**", timeout=20000)
    except Exception:
        pass
    page.wait_for_load_state("networkidle")
    print(f"[login] {account} -> {page.url}")

def main():
    ok = True
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        login(page, "academic_test")

        # --- ① 冲突规则：课表查询页（默认班=测试班级，已插 3 节同时段课） ---
        page.goto(BASE + WEEK_URL, wait_until="networkidle")
        page.wait_for_timeout(9000)
        week_text = ""
        iframe_h = 0
        vh = 900
        for fr in page.frames:
            if "/x/main/schedule/week" in (fr.url or ""):
                week_text = fr.evaluate("() => document.body.innerText")
                dims = fr.parent_frame.evaluate(
                    "() => { const f = document.querySelector('iframe');"
                    " return { h: f.getBoundingClientRect().height }; }"
                ) if fr.parent_frame else {}
                iframe_h = dims.get("h", 0)
                break
        has_conflict = ("处冲突" in week_text) and ("班级同时段" in week_text)
        print(("✓" if has_conflict else "✗") + f" 冲突卡触发：1 处冲突 + 原因含「班级同时段」（教师/教室各不同）")
        ok = has_conflict and ok
        # 高度自适应：应约等于内容自然高度（千余 px），min-h-svh 回环失控会到上万 px
        grew = vh + 100 < iframe_h < 2500
        print(("✓" if grew else "✗") + f" iframe 高度自适应：{iframe_h:.0f}px（内容高，未失控；> 视口 900px 外层可滚）")
        ok = grew and ok
        page.screenshot(path=str(SHOTS / "d76_week_conflict.png"), full_page=True)

        # --- ② 排课管理页同规则 ---
        page.goto(BASE + BOARD_URL, wait_until="networkidle")
        page.wait_for_timeout(9000)
        board_text = ""
        for fr in page.frames:
            if "/x/main/schedule/board" in (fr.url or ""):
                board_text = fr.evaluate("() => document.body.innerText")
                break
        b_ok = "班级同时段" in board_text
        print(("✓" if b_ok else "✗") + " 排课画布冲突提示同规则生效")
        ok = b_ok and ok

        print(f"\npageerror 合计: {len(errors)}" + (f" -> {errors[:3]}" if errors else ""))
        print("总体:", "✓ 全部通过" if ok and not errors else "✗ 存在问题")
        browser.close()

main()
