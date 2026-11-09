"""验证移动课程表页直接展示本班课表（Violet 2026-11-09 需求）。"""
import json, pathlib
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:13000"
SHOTS = pathlib.Path(__file__).parent / "shots"

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 390, "height": 844})
        page = ctx.new_page()
        fails = []
        page.on("response", lambda r: fails.append(f"{r.status} {r.url[-80:]}") if r.status >= 400 else None)
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))

        page.goto(BASE + "/sign-in", wait_until="domcontentloaded")
        page.wait_for_selector("input", timeout=60000)
        page.locator("input[type='text'], input:not([type])").first.fill("student_test")
        page.locator("input[type='password']").first.fill("dx123456")
        page.locator("button:has-text('登 录'), button:has-text('登录'), button[type='submit']").first.click()
        page.wait_for_load_state("networkidle")

        page.goto(BASE + "/v/mobile/jxuptin8mn3", wait_until="domcontentloaded")
        page.wait_for_timeout(6000)
        page.screenshot(path=str(SHOTS / "mobile-schedule-inline.png"), full_page=True)
        text = page.locator("body").inner_text()
        checks = {
            "我的课程表": "我的课程表" in text,
            "班名": "第1期中青班" in text,
            "周一": "周一" in text,
            "专题课": "专题课" in text,
            "教师": "王振华" in text or "李慧敏" in text or "张国栋" in text,
            "无按钮": "打开课程表" not in text,
        }
        seg = page.locator(".ant-segmented-item:has-text('第2周')").first
        if seg.count() if hasattr(seg, "count") else True:
            try:
                seg.click()
                page.wait_for_timeout(2500)
                page.screenshot(path=str(SHOTS / "mobile-schedule-week2.png"), full_page=True)
                text2 = page.locator("body").inner_text()
                checks["第2周内容"] = "红色遵义现场教学" in text2 or "领导干部压力管理" in text2
            except Exception as e:
                checks["第2周内容"] = "ERR:" + str(e)[:80]
        print("CHECKS =", json.dumps(checks, ensure_ascii=False))
        print("HTTP4XX =", fails[:5], "JS_ERRORS =", errors[:3])
        browser.close()

if __name__ == "__main__":
    main()
