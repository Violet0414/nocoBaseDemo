"""验证综合门户"各班次学员数"图表：柱顶数量标签 + 中文图例（Violet 反馈 2026-11-09）。"""
import pathlib
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:13000"
HERE = pathlib.Path(__file__).parent
SHOTS = HERE / "shots"

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))

        page.goto(BASE + "/sign-in", wait_until="domcontentloaded")
        page.wait_for_selector("input", timeout=60000)
        page.locator("input[type='text'], input:not([type])").first.fill("organizer_test")
        page.locator("input[type='password']").first.fill("dx123456")
        page.locator("button:has-text('登 录'), button:has-text('登录'), button[type='submit']").first.click()
        page.wait_for_load_state("networkidle")

        page.goto(BASE + "/admin/dl676l12ru6", wait_until="networkidle")
        page.wait_for_timeout(6000)
        page.screenshot(path=str(SHOTS / "portal-chart.png"), full_page=True)

        canvas_info = page.evaluate("""() => {
          const cards = [...document.querySelectorAll('.ant-card, [class*="block"]')];
          const card = cards.find(c => c.textContent.includes('各班次学员数') && c.querySelector('canvas'));
          if (!card) return null;
          const echarts = card.querySelector('canvas').__echarts__ || window.echarts && null;
          // 从 canvas 无法直接取 instance，改抓 legend/label 文本由截图判读
          return { hasCanvas: true };
        }""")
        print("CHART_CARD =", canvas_info)
        print("JS_ERRORS =", errors[:5])
        browser.close()

if __name__ == "__main__":
    main()
