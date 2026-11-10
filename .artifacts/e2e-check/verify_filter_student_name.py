"""验证：审批待办-请假待审 筛选「学员姓名 包含 张」发 student.name 条件且返回数据（2026-11-10）。"""
import pathlib, urllib.parse
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:13000"
HERE = pathlib.Path(__file__).parent
SHOTS = HERE / "shots"


def login(page):
    page.goto(BASE + "/sign-in", wait_until="domcontentloaded")
    page.wait_for_timeout(5000)
    for attempt in range(3):
        if "/admin" in page.url:
            return True
        try:
            page.wait_for_selector("input", timeout=20000)
            page.locator("input[type='text'], input:not([type])").first.fill("organizer_test", timeout=10000)
            page.locator("input[type='password']").first.fill("dx123456")
            page.locator("button[type='submit'], button:has-text('登录'), button:has-text('登 录')").first.click()
            page.wait_for_timeout(8000)
        except Exception:
            page.goto(BASE + "/sign-in", wait_until="domcontentloaded")
            page.wait_for_timeout(3000)
    return "/admin" in page.url


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        print("LOGIN_OK =", login(page), page.url)

        filters_seen = []
        def on_request(req):
            if "nb_dx_leave" in req.url and ":list" in urllib.parse.unquote(req.url):
                u = urllib.parse.urlparse(req.url)
                filters_seen.append(urllib.parse.unquote(urllib.parse.parse_qs(u.query).get("filter", [""])[0]))
        page.on("request", on_request)

        page.goto(BASE + "/admin/fkrtrtchlkj", wait_until="domcontentloaded")
        page.wait_for_timeout(12000)

        # 打开筛选，学员姓名行填「张」，提交
        page.locator("button:has-text('筛选')").first.click(timeout=8000)
        page.wait_for_timeout(2000)
        page.locator("input[placeholder='输入值']").first.fill("张", timeout=5000)
        page.wait_for_timeout(1000)
        page.screenshot(path=str(SHOTS / "verify_filter_filled.png"), full_page=True)
        filters_seen.clear()
        page.locator("button:has-text('提 交'), button:has-text('提交')").last.click(timeout=5000)
        page.wait_for_timeout(6000)
        page.screenshot(path=str(SHOTS / "verify_filter_result.png"), full_page=True)

        print("== 提交筛选后的 filter ==")
        for f in filters_seen:
            print(f)
        body = page.locator(".ant-table-tbody").first.inner_text(timeout=8000)
        print("TABLE =", body[:300].replace("\n", " | "))
        print("HAS_ZHANG =", "张" in body)
        print("HAS_PENDING_HINT = 暂无数据 ->", "暂无数据" in body)

        # 重置筛选，确认表格恢复空（0 条 pending）
        try:
            page.locator("button:has-text('筛选')").first.click(timeout=5000)
            page.wait_for_timeout(1500)
            page.locator("button:has-text('重 置'), button:has-text('重置')").last.click(timeout=5000)
            page.wait_for_timeout(5000)
            body2 = page.locator(".ant-table-tbody").first.inner_text(timeout=8000)
            print("AFTER_RESET =", body2[:120].replace("\n", " | "))
        except Exception as e:
            print("RESET_ERR:", e)
        browser.close()


if __name__ == "__main__":
    main()
