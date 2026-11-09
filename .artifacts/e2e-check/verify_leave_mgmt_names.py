"""验证请假管理页学员姓名列回显（D60 批量修复 student_name→student.name）。"""
import pathlib
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:13000"
SHOTS = pathlib.Path(__file__).parent / "shots"

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        page.goto(BASE + "/sign-in", wait_until="domcontentloaded")
        page.wait_for_selector("input", timeout=60000)
        page.locator("input[type='text'], input:not([type])").first.fill("organizer_test")
        page.locator("input[type='password']").first.fill("dx123456")
        page.locator("button:has-text('登 录'), button:has-text('登录'), button[type='submit']").first.click()
        page.wait_for_load_state("networkidle")

        page.goto(BASE + "/admin/aj0sy2ux0wc", wait_until="domcontentloaded")
        page.wait_for_timeout(6000)
        page.screenshot(path=str(SHOTS / "leave-mgmt-names.png"), full_page=True)
        text = page.locator("body").inner_text()
        print("HAS_张明远 =", "张明远" in text)
        print("HAS_吴建军 =", "吴建军" in text)
        print("HAS_许文博 =", "许文博" in text)
        print("HAS_学员姓名表头 =", "学员姓名" in text)
        browser.close()

if __name__ == "__main__":
    main()
