"""诊断 flowPage 工作台待办 lv96gv4zgoq 加载失败 400。"""
import json, pathlib
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:13000"
SHOTS = pathlib.Path(__file__).parent / "shots"

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        reqs = []
        page.on("request", lambda r: reqs.append((r.method, r.url, r.post_data)) if "api" in r.url else None)
        fails = []
        page.on("response", lambda r: fails.append((r.status, r.url, r.request.post_data)) if r.status >= 400 else None)
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))

        page.goto(BASE + "/sign-in", wait_until="domcontentloaded")
        page.wait_for_selector("input", timeout=60000)
        page.locator("input[type='text'], input:not([type])").first.fill("organizer_test")
        page.locator("input[type='password']").first.fill("dx123456")
        page.locator("button:has-text('登 录'), button:has-text('登录'), button[type='submit']").first.click()
        page.wait_for_load_state("networkidle")

        page.goto(BASE + "/admin/lv96gv4zgoq", wait_until="domcontentloaded")
        page.wait_for_timeout(8000)
        page.screenshot(path=str(SHOTS / "diag-flowpage-todo.png"), full_page=True)
        body_text = page.locator("body").inner_text()[:800]
        print("PAGE_TEXT_HEAD =", json.dumps(body_text, ensure_ascii=False))
        print("\nHTTP4XX:")
        for s, u, d in fails[:10]:
            print(f"  {s} {u}")
            if d: print(f"    body: {d[:500]}")
        print("\nJS_ERRORS =", errors[:3])
        browser.close()

if __name__ == "__main__":
    main()
