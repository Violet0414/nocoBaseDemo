# -*- coding: utf-8 -*-
"""补缺功能统一无头回归：A/B/D 组 9 个新页 + 既有页回归（库存报表/请假管理/工作台待办）。
admin 页 leader_test；移动社区 student_test；待办 organizer_test。"""
import pathlib
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:13000"
HERE = pathlib.Path(__file__).parent
SHOTS = HERE / "shots"
SHOTS.mkdir(exist_ok=True)

ADMIN_PAGES = [
    ("领用报表", "/admin/3hfh2zfihov"),
    ("库存流水", "/admin/jxpmhho71dy"),
    ("作业管理", "/admin/xq4npakitcp"),
    ("材料回复", "/admin/yraxqhxmo8g"),
    ("申报信息", "/admin/ok0ifwkpsge"),
    ("纪律承诺", "/admin/oni1jpvmd9o"),
    ("调课记录", "/admin/a57pctvjrbv"),
    ("通知阅读统计", "/admin/bxn38fqyt9z"),
    ("学员社区", "/admin/8kdal76v8ea"),
    ("回归:库存报表", "/admin/g8277c0m2zd"),
    ("回归:请假管理", "/admin/aj0sy2ux0wc"),
]
MOBILE_PAGES = [("移动端:学员社区", "/v/mobile")]

def check(page, label, url, shot, errors):
    page.goto(BASE + url, wait_until="networkidle")
    page.wait_for_timeout(6000)
    page.screenshot(path=str(SHOTS / shot), full_page=True)
    info = page.evaluate("""() => ({
        canvases: document.querySelectorAll('canvas').length,
        rows: document.querySelectorAll('.ant-table-tbody tr').length,
        forms: document.querySelectorAll('form').length,
        text: document.body.innerText.slice(0, 200),
    })""")
    bad = ("页面不存在" in info["text"]) or ("403" in info["text"][:60] and not info["rows"])
    has_content = info["canvases"] > 0 or info["rows"] > 0 or info["forms"] > 0
    status = "✗" if bad or not has_content else "✓"
    print(f"{status} {label}: canvas={info['canvases']} 行={info['rows']} 表单={info['forms']}"
          + ("" if status == "✓" else f" 文本={info['text'][:80]!r}"))
    return status == "✓"

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
        # --- admin 页（leader_test） ---
        ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        login(page, "leader_test")
        for label, url in ADMIN_PAGES:
            ok = check(page, label, url, f"gap_{label.split(':')[-1]}.png", errors) and ok
        # --- 待办（organizer_test，验证 jsBlock 新 id 兼容） ---
        ctx2 = browser.new_context(viewport={"width": 1440, "height": 900})
        page2 = ctx2.new_page()
        login(page2, "organizer_test")
        page2.goto(BASE + "/admin/lv96gv4zgoq", wait_until="networkidle")
        page2.wait_for_timeout(6000)
        page2.screenshot(path=str(SHOTS / "gap_todo.png"), full_page=True)
        todo_text = page2.evaluate("() => document.body.innerText.slice(0, 400)")
        todo_ok = ("请假审批" in todo_text) and ("张明远" in todo_text)
        print(("✓" if todo_ok else "✗") + " 回归:工作台待办（新流 id 待办可见）")
        ok = todo_ok and ok
        # --- 移动端社区（student_test） ---
        ctx3 = browser.new_context(viewport={"width": 390, "height": 844})
        page3 = ctx3.new_page()
        login(page3, "student_test")
        page3.goto(BASE + "/v/mobile", wait_until="networkidle")
        page3.wait_for_timeout(5000)
        menu_text = page3.evaluate("() => document.body.innerText.slice(0, 600)")
        has_community = "学员社区" in menu_text
        print(("✓" if has_community else "✗") + " 移动端:学员社区入口在菜单")
        ok = has_community and ok
        page3.screenshot(path=str(SHOTS / "gap_mobile_menu.png"), full_page=True)
        print(f"\npageerror 合计: {len(errors)}" + (f" -> {errors[:3]}" if errors else ""))
        print("总体:", "✓ 全部通过" if ok and not errors else "✗ 存在问题")
        browser.close()

main()
