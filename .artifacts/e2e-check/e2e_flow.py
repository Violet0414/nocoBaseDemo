"""E2E 链路 UI 验证（阶段7 演示脚本自动化走查）。
用法: python3 e2e_flow.py step
step: login-student | mobile-signup | week-table | stats
"""
import sys, json, pathlib
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:13000"
HERE = pathlib.Path(__file__).parent
STATE = HERE / "state_student.json"
SHOTS = HERE / "shots"
SHOTS.mkdir(exist_ok=True)

def ui_login(page, account, password):
    page.goto(BASE + "/sign-in", wait_until="domcontentloaded")
    page.wait_for_selector("input", timeout=60000)
    # 账号框: 第一个文本输入框; 密码框: type=password
    user_input = page.locator("input[type='text'], input:not([type])").first
    user_input.fill(account)
    page.locator("input[type='password']").first.fill(password)
    btn = page.locator("button:has-text('登 录'), button:has-text('登录'), button[type='submit']").first
    btn.click()
    page.wait_for_load_state("networkidle")
    return page

def main(step):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 420, "height": 860})
        page = ctx.new_page()
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        api_fail = []
        page.on("response", lambda r: api_fail.append(f"{r.status} {r.url[-80:]}") if r.status >= 400 else None)

        if step == "login-student":
            ui_login(page, "student_test", "dx123456")
            ctx.storage_state(path=str(STATE))
            print("LOGIN_OK url=", page.url)

        elif step == "mobile-signup":
            ctx = browser.new_context(storage_state=str(STATE), viewport={"width": 420, "height": 860})
            page = ctx.new_page()
            page.goto(f"{BASE}/v/mobile/3cfhfajaa4x?class=8", wait_until="networkidle")
            page.wait_for_timeout(4000)
            page.screenshot(path=str(SHOTS / "mobile-signup.png"), full_page=True)
            # 找班次下拉的显示值
            content = page.content()
            has_klass = "E2E链路测试班" in content
            has_title = "报名" in content or "扫码报名" in content
            print(json.dumps({"page_loaded": "页面不存在" not in content, "klass_auto_selected": has_klass, "title_ok": has_title, "http4xx": api_fail[:5], "js_errors": errors[:3]}, ensure_ascii=False))

        browser.close()

if __name__ == "__main__":
    main(sys.argv[1])
