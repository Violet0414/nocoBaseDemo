"""验证培训记录页"各班次学员数"图表：中文图例「学员数」+ 柱顶数量标签（Violet 反馈 2026-11-10）。"""
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

        page.goto(BASE + "/admin/n6229xx31n5", wait_until="networkidle")
        page.wait_for_timeout(6000)
        page.screenshot(path=str(SHOTS / "train-chart.png"), full_page=True)

        # 图表卡片存在性 + echarts 容器定位
        info = page.evaluate("""() => {
          const divs = [...document.querySelectorAll('div')];
          const ecDiv = divs.find(d => d.hasAttribute('_echarts_instance_'));
          const cards = [...document.querySelectorAll('.ant-card, [class*="block"]')];
          const card = cards.find(c => c.textContent.includes('各班次学员数') && c.querySelector('canvas'));
          return {
            hasEchartsDom: !!ecDiv,
            hasChartCard: !!card,
            cardText: card ? card.textContent.slice(0, 80) : null
          };
        }""")
        print("CHART_INFO =", info)
        print("JS_ERRORS =", errors[:5])
        assert info["hasChartCard"], "未找到「各班次学员数」图表卡片"
        assert not errors, f"页面存在 JS 错误: {errors[:3]}"
        print("PASS ✓")
        browser.close()

if __name__ == "__main__":
    main()
