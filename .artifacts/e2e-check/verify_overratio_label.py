"""验证请假管理列表 over_ratio 列显示 是/否（2026-11-10）。"""
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
        page.wait_for_timeout(4000)
        page.wait_for_selector("input", timeout=60000)
        for attempt in range(3):
            if "/admin" in page.url or "/v/" in page.url:
                break
            page.wait_for_selector("input", timeout=60000)
            page.locator("input[type='text'], input:not([type])").first.fill("organizer_test", timeout=10000)
            page.locator("input[type='password']").first.fill("dx123456")
            page.locator("button:has-text('登 录'), button:has-text('登录'), button[type='submit']").first.click()
            try:
                page.wait_for_url("**/admin*", timeout=20000)
                break
            except Exception:
                page.goto(BASE + "/sign-in", wait_until="domcontentloaded")
                page.wait_for_timeout(3000)
        page.wait_for_load_state("networkidle")

        page.goto(BASE + "/admin/aj0sy2ux0wc", wait_until="networkidle")
        page.wait_for_timeout(8000)
        page.screenshot(path=str(SHOTS / "verify-overratio.png"), full_page=True)

        try:
            text = page.locator(".ant-table-tbody").first.inner_text(timeout=20000)
        except Exception as e:
            print("TABLE_NOT_FOUND:", e)
            text = ""
        print("HAS_TRUE = ", "true" in text.lower())
        print("HAS_FALSE =", "false" in text.lower())
        print("HAS_SHI   =", "是" in text)
        print("HAS_FOU   =", "否" in text)
        print("HTTP4XX =", api_fail[:5], "JS_ERRORS =", errors[:3])
        browser.close()

if __name__ == "__main__":
    main()
