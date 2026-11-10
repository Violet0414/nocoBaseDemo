"""诊断 workflow 手动待办弹窗为空（2026-11-10）。"""
import json, pathlib
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:13000"
HERE = pathlib.Path(__file__).parent
SHOTS = HERE / "shots"
URL = BASE + "/admin/workflow/tasks/manual/pending/396909008584706"

def login(page):
    page.goto(BASE + "/sign-in", wait_until="domcontentloaded")
    page.wait_for_timeout(4000)
    page.wait_for_selector("input", timeout=60000)
    for attempt in range(3):
        if "/admin" in page.url:
            break
        page.wait_for_selector("input", timeout=30000)
        page.locator("input[type='text'], input:not([type])").first.fill("organizer_test")
        page.locator("input[type='password']").first.fill("dx123456")
        page.locator("button:has-text('登 录'), button[type='submit']").first.click()
        try:
            page.wait_for_url("**/admin*", timeout=20000)
            break
        except Exception:
            page.goto(BASE + "/sign-in", wait_until="domcontentloaded")
            page.wait_for_timeout(3000)
    page.wait_for_load_state("networkidle")

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)[:300]))
        api_fail = []
        page.on("response", lambda r: api_fail.append(f"{r.status} {r.url[-90:]}") if r.status >= 400 else None)

        login(page)
        page.goto(URL, wait_until="networkidle")
        page.wait_for_timeout(6000)
        page.screenshot(path=str(SHOTS / "diag_task_pending.png"), full_page=True)
        print("URL_NOW =", page.url)
        print("PAGE_TEXT =", json.dumps(page.locator("body").inner_text()[:400], ensure_ascii=False))

        # 点击列表卡片（第一条待办卡片）
        cards = page.locator(".ant-list-item, .ant-card, [class*='task']")
        n = cards.count()
        print("CARD_CANDIDATES =", n)
        if n:
            cards.first.click()
            page.wait_for_timeout(4000)
            page.screenshot(path=str(SHOTS / "diag_task_popup.png"), full_page=True)
            modal = page.locator(".ant-modal, .ant-drawer")
            if modal.count():
                print("MODAL_TEXT =", json.dumps(modal.last.inner_text()[:500], ensure_ascii=False))
                print("MODAL_HTML_LEN =", len(modal.last.inner_html()))
            else:
                print("NO_MODAL")
        print("HTTP4XX =", api_fail[:8])
        print("JS_ERRORS =", errors[:5])
        browser.close()

if __name__ == "__main__":
    main()
