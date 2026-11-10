# -*- coding: utf-8 -*-
"""方案A验证：admin 3 个排课入口页（jsBlock iframe 嵌 /x/main）。
academic_test 登录 → 逐页访问 → 校验 iframe 挂载、src 正确、内页有内容；附菜单可见性检查。"""
import pathlib
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:13000"
HERE = pathlib.Path(__file__).parent
SHOTS = HERE / "shots"
SHOTS.mkdir(exist_ok=True)

PAGES = [
    ("排课管理", "/admin/aj8s3d0rqul", "/x/main/schedule/board", "se_board.png"),
    ("课表查询", "/admin/e3enf6pad6r", "/x/main/schedule/week", "se_week.png"),
    ("排座管理", "/admin/hsp9fs7nrzq", "/x/main/schedule/seats", "se_seats.png"),
]

def login(page, account):
    page.goto(BASE + "/sign-in", wait_until="domcontentloaded")
    page.wait_for_selector("input", timeout=60000)
    page.locator("input[type='text'], input:not([type])").first.fill(account)
    page.locator("input[type='password']").first.fill("dx123456")
    page.locator("button:has-text('登 录'), button:has-text('登录'), button[type='submit']").first.click()
    try:
        page.wait_for_url("**/admin/**", timeout=20000)
    except Exception:
        pass
    page.wait_for_load_state("networkidle")
    print(f"[login] {account} -> {page.url}")

def main():
    ok = True
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        login(page, "academic_test")
        page.goto(BASE + "/admin", wait_until="networkidle")
        page.wait_for_timeout(5000)

        # 菜单可见性（菜单组默认折叠，须展开后查）
        page.locator("a:has-text('教务管理'), li:has-text('教务管理')").first.click()
        page.wait_for_timeout(2000)
        menu_text = page.evaluate("() => document.body.innerText")
        for label in ("排课管理", "课表查询"):
            has = label in menu_text
            print(("✓" if has else "✗") + f" 教务管理组菜单含「{label}」")
            ok = has and ok
        page.locator("a:has-text('班务管理'), li:has-text('班务管理')").first.click()
        page.wait_for_timeout(2000)
        menu_text = page.evaluate("() => document.body.innerText")
        has = "排座管理" in menu_text
        print(("✓" if has else "✗") + " 班务管理组菜单含「排座管理」")
        ok = has and ok

        for label, url, expect_src, shot in PAGES:
            page.goto(BASE + url, wait_until="networkidle")
            page.wait_for_timeout(8000)  # iframe 内 portal bundle 加载
            page.screenshot(path=str(SHOTS / shot), full_page=True)
            info = page.evaluate("""(expect) => {
                const f = document.querySelector('iframe');
                if (!f) return { iframe: false };
                return {
                    iframe: true,
                    src: f.getAttribute('src'),
                    srcOk: (f.getAttribute('src') || '').indexOf(expect) !== -1,
                    h: f.getBoundingClientRect().height,
                    w: f.getBoundingClientRect().width,
                };
            }""", expect_src)
            # 同源 iframe 内页文本
            inner_text = ""
            inner_ok = False
            if info.get("iframe"):
                for fr in page.frames:
                    if expect_src in (fr.url or ""):
                        try:
                            inner_text = fr.evaluate("() => document.body.innerText.slice(0, 300)")
                        except Exception as e:
                            inner_text = f"<取帧失败 {e}>"
                        break
                inner_ok = len(inner_text.strip()) > 10 and "页面不存在" not in inner_text and "404" not in inner_text[:50]
            passed = info.get("iframe") and info.get("srcOk") and inner_ok
            print(("✓" if passed else "✗") + f" {label}: iframe={info.get('iframe')} srcOk={info.get('srcOk')} "
                  f"尺寸={info.get('w', 0):.0f}x{info.get('h', 0):.0f} 内页文本={inner_text[:60]!r}")
            ok = passed and ok

        print(f"\npageerror 合计: {len(errors)}" + (f" -> {errors[:3]}" if errors else ""))
        print("总体:", "✓ 全部通过" if ok and not errors else "✗ 存在问题")
        browser.close()

main()
