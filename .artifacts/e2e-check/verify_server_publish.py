"""验证服务器发布：admin AI 悬浮球是否消失 + 页面正常。

用法：python verify_server_publish.py <base_url>
默认 10.10.40.44:13000。
"""
import sys, pathlib
from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://10.10.40.44:13000"
TAG = "server" if "10.10.40.44" in BASE else "local"
SHOTS = pathlib.Path(__file__).parent / "shots"


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        page.goto(BASE + "/sign-in", wait_until="domcontentloaded")
        page.wait_for_timeout(5000)
        ok = False
        for attempt in range(3):
            if "/admin" in page.url:
                ok = True
                break
            try:
                page.wait_for_selector("input", timeout=20000)
                page.locator("input[type='text'], input:not([type])").first.fill("organizer_test", timeout=10000)
                page.locator("input[type='password']").first.fill("dx123456")
                page.locator("button[type='submit'], button:has-text('登录'), button:has-text('登 录')").first.click()
                page.wait_for_timeout(8000)
            except Exception:
                page.goto(BASE + "/sign-in", wait_until="domcontentloaded")
                page.wait_for_timeout(3000)
        print("LOGIN_OK =", ok, page.url)
        page.goto(BASE + "/admin", wait_until="domcontentloaded")
        page.wait_for_timeout(10000)
        page.screenshot(path=str(SHOTS / f"publish_{TAG}_admin.png"), full_page=True)

        # AI 悬浮球：aria-label 为「打开 AI 对话」/ openChat
        for sel in ["[aria-label='打开 AI 对话']", "[aria-label*='AI']", "[aria-label*='openChat']", ".nocobase-ai-chat-trigger"]:
            n = page.locator(sel).count()
            print(f"FLOATING_BALL [{sel!r}] =", n)
        # 审批待办页快照 + 请假待审内容
        page.goto(BASE + "/admin/fkrtrtchlkj", wait_until="domcontentloaded")
        page.wait_for_timeout(10000)
        page.screenshot(path=str(SHOTS / f"publish_{TAG}_fkr.png"), full_page=True)
        try:
            tb = page.locator(".ant-table-tbody").first.inner_text(timeout=10000)
            print("LEAVE_TABLE =", tb[:200].replace("\n", " | "))
            print("HAS_STATUS_COL =", ("审批状态" in page.locator(".ant-table-thead").first.inner_text(timeout=5000)))
        except Exception as e:
            print("TABLE_ERR:", e)
        browser.close()


if __name__ == "__main__":
    main()
