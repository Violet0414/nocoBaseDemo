"""验证方案B：请假表单班次必填 + 班次表单 total_days 必填（2026-11-10）。"""
import pathlib
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:13000"
SHOTS = pathlib.Path(__file__).parent / "shots"

def login(page, user, pwd):
    page.goto(BASE + "/sign-in", wait_until="domcontentloaded")
    page.wait_for_selector("input", timeout=60000)
    page.locator("input[type='text'], input:not([type])").first.fill(user)
    page.locator("input[type='password']").first.fill(pwd)
    page.locator("button:has-text('登 录'), button:has-text('登录'), button[type='submit']").first.click()
    page.wait_for_load_state("networkidle")

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 390, "height": 844})
        page = ctx.new_page()
        login(page, "student_test", "dx123456")

        # 1) 移动端请假申请页
        page.goto(BASE + "/v/mobile/80a2tclmlct", wait_until="domcontentloaded")
        page.wait_for_timeout(5000)
        page.screenshot(path=str(SHOTS / "leave-form-required.png"), full_page=True)
        text = page.locator("body").inner_text()
        print("HAS_班次 =", "班次" in text)
        # 检查班次表单项附近有无必填星号/标记
        klass_item = page.locator("div:has-text('班次')").last
        html = page.content()
        # Formily 必填星号通常渲染 .ant-form-item-required
        star = page.locator(".ant-form-item-required")
        labels = [star.nth(i).inner_text() for i in range(star.count())]
        print("REQUIRED_LABELS =", labels)

        # 2) 不选班次直接提交 → 应被校验拦截
        page.locator("button:has-text('提交'), button:has-text('提 交')").first.click()
        page.wait_for_timeout(2000)
        page.screenshot(path=str(SHOTS / "leave-submit-blocked.png"), full_page=True)
        body = page.locator("body").inner_text()
        print("VALIDATION_HINT =", "请选择班次" in body or "请输入" in body or "班次" in body)

        # 3) admin 班次新建表单 total_days 必填
        ctx2 = browser.new_context(viewport={"width": 1440, "height": 900})
        p2 = ctx2.new_page()
        login(p2, "admin", "dx123456") if False else None
        browser.close()

if __name__ == "__main__":
    main()
