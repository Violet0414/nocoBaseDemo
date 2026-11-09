"""验证移动端扫码报名页已下线：旧链接 404 / 菜单不再出现「扫码报名」。"""
import pathlib
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:13000"
SHOTS = pathlib.Path(__file__).parent / "shots"

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 390, "height": 844})
        page = ctx.new_page()

        page.goto(BASE + "/sign-in", wait_until="domcontentloaded")
        page.wait_for_selector("input", timeout=60000)
        page.locator("input[type='text'], input:not([type])").first.fill("student_test")
        page.locator("input[type='password']").first.fill("dx123456")
        page.locator("button:has-text('登 录'), button:has-text('登录'), button[type='submit']").first.click()
        page.wait_for_load_state("networkidle")

        # 1. 旧链接不应再渲染报名表单（NocoBase 回退到移动端首页）
        page.goto(BASE + "/v/mobile/3cfhfajaa4x", wait_until="domcontentloaded")
        page.wait_for_timeout(5000)
        page.screenshot(path=str(SHOTS / "retired-signup-404.png"))
        old_text = page.locator("body").inner_text()
        gone = "扫码报名" not in old_text and "报名登记" not in old_text

        # 2. 移动端首页菜单不应再有「扫码报名」
        page.goto(BASE + "/v/mobile", wait_until="domcontentloaded")
        page.wait_for_timeout(5000)
        page.screenshot(path=str(SHOTS / "retired-mobile-menu.png"))
        menu_text = page.locator("body").inner_text()
        no_menu = "扫码报名" not in menu_text

        print(f"旧链接已失效(404/页面不存在): {gone}")
        print(f"移动端菜单已无「扫码报名」: {no_menu}")
        print("PASS" if (gone and no_menu) else "FAIL")

if __name__ == "__main__":
    main()
