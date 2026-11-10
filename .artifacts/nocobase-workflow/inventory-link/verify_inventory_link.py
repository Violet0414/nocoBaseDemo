#!/usr/bin/env python3
"""A1 库存联动闭环验证：分别插入采购/领用/退库各 1 条，验证 execution resolved + stock 变动 + 流水正确。
认证：nb OAuth accessToken（STATE 既定形态）+ X-Authenticator: basic（s7-demo-data 沉淀规则）。
"""
import json, subprocess, re, sys, time
import urllib.request

def get_token():
    out = subprocess.run(["python3", "-c",
        'import json;print(json.load(open("/home/mxr/.nocobase/config.json"))["envs"]["dx-demo"]["auth"]["accessToken"])'],
        capture_output=True, text=True)
    return out.stdout.strip()

TOKEN = get_token()
BASE = "http://127.0.0.1:13000/api"
HEADERS = {"Authorization": f"Bearer {TOKEN}", "X-Authenticator": "basic",
           "Content-Type": "application/json"}

def req(method, path, body=None):
    r = urllib.request.Request(BASE + path, data=json.dumps(body).encode() if body else None,
                               headers=HEADERS, method=method)
    with urllib.request.urlopen(r, timeout=15) as resp:
        return json.loads(resp.read().decode())

def esc(s):  # filter 的 URL 编码
    return urllib.parse.quote(s)

import urllib.parse

def fail(msg):
    print("✗ " + msg); sys.exit(1)

# ===== 每种业务各插 1 条 =====
TID = req("GET", "/nb_dx_textbook?fields=id,name,stock&pageSize=1")["data"][0]["id"]
print(f"测试教材 id={TID}")
CASES = [
    # (集合, 类型, 教材id, 数量, 额外字段)
    ("nb_dx_purchase", "采购", TID, 5, {"date": "2026-11-10", "status": "approved"}),
    ("nb_dx_requisition", "领用", TID, 3, {"date": "2026-11-10", "batch_no": "LY-TEST-01", "status": "approved"}),
    ("nb_dx_textbook_return", "退库", TID, 2, {"date": "2026-11-10", "status": "approved"}),
]

for coll, ltype, tid, qty, extra in CASES:
    # 前置库存
    before = req("GET", f"/nb_dx_textbook?filter={esc(json.dumps({'id': tid}))}&fields=id,name,stock")["data"][0]
    stock0 = before["stock"]
    body = {"textbook_id": tid, "textbook_name": before["name"], "quantity": qty, **extra}
    created = req("POST", f"/{coll}:create", body)["data"]
    rid = created["id"]
    print(f"\n[{ltype}] 已插入 {coll}#{rid}（教材{tid} 数量{qty}，stock {stock0}）")
    time.sleep(3)  # async workflow 执行窗口
    # execution
    wf_map = {"采购": "教材采购库存联动流", "领用": "教材领用库存联动流", "退库": "教材退库库存联动流"}
    exs = req("GET", "/executions?filter=" + esc(json.dumps(
        {"workflow": {"key": {"$in": []}}, "id": {"$gt": 0}})))  # 占位，下面直接取最新
    # 直接查最新 execution by workflow title
    wf_list = req("GET", "/workflows?filter=" + esc(json.dumps({"title": wf_map[ltype]})))["data"]
    wfid = wf_list[0]["id"]
    exs = req("GET", "/executions?filter=" + esc(json.dumps({"workflowId": wfid})) +
              "&sort=-id&page=1&pageSize=1")["data"]
    if not exs:
        fail(f"{ltype} 无 execution")
    ex = exs[0]
    print(f"  execution#{ex['id']} status={ex['status']}", end=" ")
    if ex["status"] != 1:
        print(f"（非 resolved！jobs: " + json.dumps([{k: j.get('status')} for k, j in
              {j['nodeKey']: j for j in ex.get('jobs', {}).get('data', []) or []}.items()] if ex.get('jobs') else []) + "）")
        fail(f"{ltype} execution 未 resolved")
    print("✓")
    # 库存
    after = req("GET", f"/nb_dx_textbook?filter={esc(json.dumps({'id': tid}))}&fields=id,stock")["data"][0]
    expect = stock0 + (qty if ltype in ("采购", "退库") else -qty)
    if abs(after["stock"] - expect) > 1e-9:
        fail(f"{ltype} stock={after['stock']} 期望 {expect}")
    print(f"  stock {stock0} → {after['stock']}（期望 {expect}）✓")
    # 流水
    logs = req("GET", "/nb_dx_inventory_log?filter=" + esc(json.dumps({"ref_no": str(created.get('batch_no', rid))})) +
               "&appends=&sort=-id&page=1&pageSize=5")["data"]
    log = None
    for r_ in logs:
        if r_["type"] == ltype and abs((r_["qty_change"] or 0) - qty) < 1e-9 and r_["textbook_id"] == tid:
            log = r_; break
    if not log:
        # 兜底：按 textbook+type 取最新
        logs = req("GET", "/nb_dx_inventory_log?filter=" + esc(json.dumps({"textbook_id": tid, "type": ltype})) +
                   "&sort=-id&page=1&pageSize=1")["data"]
        log = logs[0] if logs else None
        if not log or abs((log["qty_change"] or 0) - qty) > 1e-9:
            fail(f"{ltype} 流水未找到")
    ok_after = log["after_qty"] == after["stock"]
    print(f"  流水#{log['id']} before={log['before_qty']} after={log['after_qty']} "
          f"qty_change={log['qty_change']} type={log['type']} ref_no={log['ref_no']} "
          f"happened_at={log['happened_at']} {'✓' if ok_after else '✗ after_qty 不一致'}")
    if not ok_after:
        fail("after_qty 与教材 stock 不一致")

print("\n=== 全部 3 条联动流闭环验证通过 ✓ ===")
