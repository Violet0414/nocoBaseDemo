#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""C1 站内提醒 e2e：学员提交请假 → organizer_test 审批通过 → 验证通知落库（notificationInAppMessages 给 user 6）。
认证：OAuth token 管理动作 + organizer_test/student_test 账密登录（users:signin）。"""
import json, subprocess, time, urllib.request, urllib.parse

def oauth_token():
    return subprocess.run(["python3", "-c",
        'import json;print(json.load(open("/home/mxr/.nocobase/config.json"))["envs"]["dx-demo"]["auth"]["accessToken"])'],
        capture_output=True, text=True).stdout.strip()

ADMIN_H = {"Authorization": "Bearer " + oauth_token(), "X-Authenticator": "basic",
           "Content-Type": "application/json"}
BASE = "http://127.0.0.1:13000/api"

def req(headers, method, path, body=None):
    r = urllib.request.Request(BASE + path,
                               data=json.dumps(body).encode() if body else None,
                               headers=headers, method=method)
    try:
        with urllib.request.urlopen(r, timeout=15) as resp:
            return resp.status, json.loads(resp.read().decode())
    except Exception as e:
        b = e.read().decode()[:300] if hasattr(e, "read") else str(e)
        return getattr(e, "code", 0), b

def signin(account):
    s, d = req({"Content-Type": "application/json"}, "POST", "/auth:signIn",
               {"account": account, "password": "dx123456"})
    if s != 200:
        raise SystemExit(f"{account} 登录失败: {s} {d}")
    tok = (d.get("data") or {}).get("token")
    return {"Authorization": "Bearer " + tok, "X-Authenticator": "basic",
            "Content-Type": "application/json"}

# 1. student_test 提交请假（user 6 / 学员1 / 班1）
st_h = signin("student_test")
esc = urllib.parse.quote
s, d = req(st_h, "POST", "/nb_dx_leave:create",
           {"student_id": 1, "class_id": 1, "type": "事假", "reason": "站内提醒链路验证（C1）",
            "start_time": "2026-11-11 08:00:00", "end_time": "2026-11-11 18:00:00",
            "duration_days": 1, "status": "pending"})
print("1. 学员提交请假:", s)
if s != 200: raise SystemExit(d)
leave_id = d["data"]["id"]
print("   leave id:", leave_id)

# 2. organizer_test 审批通过
time.sleep(5)
org_h = signin("organizer_test")
s, d = req(org_h, "GET", "/workflowManualTasks:listMine?filter=" +
           esc(json.dumps({"status": 0, "workflowId": 396908352176128})))
tasks = d.get("data", [])
task = tasks[0] if tasks else None  # 新版本流当前唯一待办即本次提交（标题含张明远）
if not task:
    raise SystemExit("未找到新流待办")
print("2. 待办:", task["id"], task.get("title"))
# 读 manual 节点 forms key
s, d = req(org_h, "GET", f"/flow_nodes:get?filterByTk={task['nodeId']}")
node = (d.get("data") or {})
form_key = list((node.get("config", {}).get("forms") or {}).keys())[0]
s, d = req(org_h, "POST", "/workflowManualTasks:submit?filterByTk=" + str(task["id"]),
           {"result": {form_key: {"approved_remark": "同意"}, "_": "approve"}})
print("3. 审批提交:", s)

# 3. 验证站内消息
time.sleep(4)
s, d = req(ADMIN_H, "GET", "/notificationInAppMessages?filter=" +
           esc(json.dumps({"userId": 6})) + "&sort=-id&page=1&pageSize=5")
msgs = d.get("data", []) if isinstance(d, dict) else []
print("4. user6 站内消息最新 5 条:")
for m in msgs[:5]:
    mm = m.get("content", "")[:60]
    print("   -", m.get("title") or m.get("subject"), "|", mm)
hit = [m for m in msgs if "请假审批结果" in json.dumps(m, ensure_ascii=False)]
print("结果:", "✓ 请假审批站内提醒已送达 user 6" if hit else "✗ 未发现审批提醒消息")
s, d = req(ADMIN_H, "GET", "/notificationSendLogs?sort=-id&page=1&pageSize=3")
logs = d.get("data", []) if isinstance(d, dict) else []
print("5. 发送日志:", [(l.get("status"), str(l.get("channelName") or "")) for l in logs])
