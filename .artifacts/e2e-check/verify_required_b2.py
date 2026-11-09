"""方案B最终回归：请假表单必填拦截 + 正常提交成功（2026-11-10）。"""
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

def pick(page, index, option_text):
    page.locator(".ant-select-selector").nth(index).click(force=True)
    page.wait_for_timeout(1500)
    page.evaluate("""(text) => {
        const els = [...document.querySelectorAll('div,li,span')].filter(
            e => e.children.length === 0 && e.textContent.trim() === text);
        const el = els[els.length - 1];
        if (!el) throw new Error('option not found: ' + text);
        ['pointerdown','mousedown','pointerup','mouseup','click'].forEach(t =>
            el.dispatchEvent(new MouseEvent(t, {bubbles: true, cancelable: true})));
    }""", option_text)
    page.wait_for_timeout(1000)

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 390, "height": 844})
        page = ctx.new_page()
        login(page, "student_test", "dx123456")
        page.goto(BASE + "/v/mobile/80a2tclmlct", wait_until="domcontentloaded")
        page.wait_for_timeout(5000)

        # 1) 空提交 → 必填拦截
        page.locator("button:has-text('提交'), button:has-text('提 交')").first.click()
        page.wait_for_timeout(2000)
        body = page.locator("body").inner_text()
        print("EMPTY_SUBMIT_BLOCKED =", "保存失败" in body)
        print("REQUIRED_HINTS =", body.count("该字段是必填字段"))
        page.screenshot(path=str(SHOTS / "b2-empty-blocked.png"), full_page=True)

        # 2) 正常填写提交 → 成功
        pick(page, 0, "张明远")   # 学员
        pick(page, 1, "第1期中青班")  # 班次
        pick(page, 2, "事假")     # 类型
        page.locator("textarea").first.fill("方案B回归测试请假")
        for i in (0, 1):
            page.locator("input[placeholder*='日期']").nth(i).click(force=True)
            page.wait_for_timeout(1200)
            page.evaluate("""() => {
                const el = [...document.querySelectorAll('button,div,span')].find(
                    e => e.textContent.trim() === '确定');
                if (!el) throw new Error('确定 not found');
                ['pointerdown','mousedown','pointerup','mouseup','click'].forEach(t =>
                    el.dispatchEvent(new MouseEvent(t, {bubbles: true, cancelable: true})));
            }""")
            page.wait_for_timeout(600)
        page.locator("input[type='number'], input").last.fill("0.5")
        page.locator("button:has-text('提交'), button:has-text('提 交')").first.click()
        page.wait_for_timeout(3000)
        body2 = page.locator("body").inner_text()
        print("VALID_SUBMIT_OK =", "保存成功" in body2)
        page.screenshot(path=str(SHOTS / "b2-valid-ok.png"), full_page=True)
        browser.close()

if __name__ == "__main__":
    main()
