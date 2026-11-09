"""验证 /admin/lv96gv4zgoq 待办列表标题回显学员名（Violet 2026-11-10 反馈）。"""
import json, pathlib
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:13000"
SHOTS = pathlib.Path(__file__).parent / "shots"

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))

        page.goto(BASE + "/sign-in", wait_until="domcontentloaded")
        page.wait_for_selector("input", timeout=60000)
        page.locator("input[type='text'], input:not([type])").first.fill("organizer_test")
        page.locator("input[type='password']").first.fill("dx123456")
        page.locator("button:has-text('登 录'), button:has-text('登录'), button[type='submit']").first.click()
        page.wait_for_load_state("networkidle")

        page.goto(BASE + "/admin/lv96gv4zgoq", wait_until="domcontentloaded")
        page.wait_for_timeout(6000)
        page.screenshot(path=str(SHOTS / "todo-titles.png"), full_page=True)
        text = page.locator("body").inner_text()
        names = ["吴建军", "张明远", "测试人员"]
        checks = {n: text.count(n) for n in names}
        empty_titles = text.count("请假审批 -\n") + text.count("请假审批 -（")
        print("NAME_COUNTS =", json.dumps(checks, ensure_ascii=False))
        print("HAS_请假TAG =", "请假审批" in text, "| HAS_报名TAG =", "报名审核" in text)
        print("JS_ERRORS =", errors[:3])
        browser.close()

if __name__ == "__main__":
    main()
