# -*- coding: utf-8 -*-
"""A2/A3 新页无头验证：领用报表（custom bar 图 + 领用明细表）、库存流水（pie + 流水表）。
登录 leader_test（r_leader 已授权两新页）。"""
import pathlib
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:13000"
HERE = pathlib.Path(__file__).parent
SHOTS = HERE / "shots"
SHOTS.mkdir(exist_ok=True)

PAGES = [
    ("领用报表", "/admin/3hfh2zfihov", "req-report"),
    ("库存流水", "/admin/jxpmhho71dy", "inv-log"),
]

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))

        page.goto(BASE + "/sign-in", wait_until="domcontentloaded")
        page.wait_for_selector("input", timeout=60000)
        page.locator("input[type='text'], input:not([type])").first.fill("leader_test")
        page.locator("input[type='password']").first.fill("dx123456")
        page.locator("button:has-text('登 录'), button:has-text('登录'), button[type='submit']").first.click()
        page.wait_for_load_state("networkidle")

        ok_all = True
        for title, url, shot in PAGES:
            page.goto(BASE + url, wait_until="networkidle")
            page.wait_for_timeout(6000)
            page.screenshot(path=str(SHOTS / f"{shot}.png"), full_page=True)
            info = page.evaluate("""() => ({
                hasCanvas: !!document.querySelector('canvas'),
                canvases: document.querySelectorAll('canvas').length,
                tableRows: document.querySelectorAll('.ant-table-tbody tr').length,
                bodyText: document.body.innerText.slice(0, 400),
            })""")
            has_chart = info["canvases"] > 0
            has_rows = info["tableRows"] > 0
            blank = ("页面不存在" in info["bodyText"]) or (len(info["bodyText"].strip()) < 30)
            status = "✓" if (has_chart or has_rows) and not blank else "✗"
            if status == "✗":
                ok_all = False
            print(f"{status} {title}: canvas={info['canvases']} 表格行={info['tableRows']} 空白={blank}")
            print(f"   页面文本片段: {info['bodyText'][:150]!r}")

        print(f"\nconsole/pageerror: {errors if errors else '无'}")
        print("结果:", "全部通过 ✓" if ok_all and not errors else "存在问题 ✗")
        browser.close()

main()
