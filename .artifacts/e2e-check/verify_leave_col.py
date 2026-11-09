"""验证请假待审列表/弹窗学员姓名修复（Violet 反馈 2026-11-09）。"""
import json, pathlib
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:13000"
HERE = pathlib.Path(__file__).parent
SHOTS = HERE / "shots"

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        api_fail = []
        page.on("response", lambda r: api_fail.append(f"{r.status} {r.url[-80:]}") if r.status >= 400 else None)

        page.goto(BASE + "/sign-in", wait_until="domcontentloaded")
        page.wait_for_selector("input", timeout=60000)
        page.locator("input[type='text'], input:not([type])").first.fill("organizer_test")
        page.locator("input[type='password']").first.fill("dx123456")
        page.locator("button:has-text('登 录'), button:has-text('登录'), button[type='submit']").first.click()
        page.wait_for_load_state("networkidle")

        page.goto(BASE + "/admin", wait_until="networkidle")
        page.wait_for_timeout(3000)
        page.locator("text=综合门户").first.click()
        page.wait_for_timeout(1500)
        page.locator("text=审批待办").first.click()
        page.wait_for_timeout(6000)
        page.screenshot(path=str(SHOTS / "verify-leave-list.png"), full_page=True)

        # 读取「学员姓名」列内容
        cells = page.locator(".ant-table-tbody td:nth-child(2)").all_inner_texts()
        print("LIST_COL2 =", json.dumps(cells, ensure_ascii=False))

        # 点「吴建军」行的查看弹窗
        row = page.locator("tr:has-text('吴建军')").first
        row.locator("text=查看").first.evaluate("el => el.click()")
        page.wait_for_timeout(4000)
        page.screenshot(path=str(SHOTS / "verify-leave-view.png"), full_page=True)
        drawer_text = page.locator(".ant-drawer, .ant-modal").last.inner_text()
        print("DRAWER_HAS_WU =", "吴建军" in drawer_text)
        print("DRAWER_STUDENT_ITEM_COUNT =", drawer_text.count("学员"))
        print("HTTP4XX =", api_fail[:5], "JS_ERRORS =", errors[:3])
        browser.close()

if __name__ == "__main__":
    main()
