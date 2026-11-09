"""学员登录态实测：nb_dx_student / nb_dx_course_schedule 可见范围。"""
import json
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:13000"

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context()
        page = ctx.new_page()
        page.goto(BASE + "/sign-in", wait_until="domcontentloaded")
        page.wait_for_selector("input", timeout=60000)
        page.locator("input[type='text'], input:not([type])").first.fill("student_test")
        page.locator("input[type='password']").first.fill("dx123456")
        page.locator("button:has-text('登 录'), button:has-text('登录'), button[type='submit']").first.click()
        page.wait_for_load_state("networkidle")

        token = page.evaluate("() => localStorage.getItem('NOCOBASE_TOKEN')")
        h = {"Authorization": "Bearer " + token}
        import urllib.request
        def api(url):
            req = urllib.request.Request(BASE + url, headers=h)
            return json.loads(urllib.request.urlopen(req).read())

        st = api("/api/nb_dx_student:list?pageSize=10")
        rows = st.get("data", []) if isinstance(st.get("data"), list) else st.get("data", {}).get("data", [])
        print("STUDENT_FULL =", json.dumps(rows, ensure_ascii=False)[:800])
        cid = 1
        import urllib.parse as up
        sc = api("/api/nb_dx_course_schedule:list?pageSize=100&filter=" + up.quote(json.dumps({"class_id": cid})))
        sdata = sc.get("data", [])
        if not isinstance(sdata, dict):
            sdata = {"data": sdata}
        print("SCHEDULE_COUNT =", sdata.get("count"), "class_id =", cid)
        if sdata.get("data"):
            print("SCHEDULE_SAMPLE =", json.dumps(sdata["data"][0], ensure_ascii=False)[:400])
        cl = api("/api/nb_dx_class:list?pageSize=20")
        cdata = cl.get("data", [])
        if not isinstance(cdata, list):
            cdata = cdata.get("data", [])
        try:
            th = api("/api/nb_dx_teacher:list?pageSize=5")
            tdata = th.get("data", [])
            if not isinstance(tdata, list):
                tdata = tdata.get("data", [])
            print("TEACHER_ROWS =", json.dumps([{k: r.get(k) for k in ("id", "name")} for r in tdata], ensure_ascii=False))
        except Exception as ex:
            print("TEACHER_ERR =", ex)
        print("CLASS_ROWS =", json.dumps([
            {k: r.get(k) for k in ("id", "name")} for r in cdata
        ], ensure_ascii=False))
        browser.close()

if __name__ == "__main__":
    main()
