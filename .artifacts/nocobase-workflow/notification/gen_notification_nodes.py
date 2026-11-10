#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""C1 站内提醒：4 条审批流 revision + workflow-notification 节点（通道 in-app）。
挂载规则（D54a）：分支首节点才带 branchIndex（false/驳回=0）；已执行流须 revision（D58a 三步法）。
receivers 进 message.receivers（in-app channel 解析：id 字符串或 UserRepo find 对象）。
"""
import json, subprocess, re, sys, pathlib, tempfile, os

def nb(args):
    r = subprocess.run(["nb", "api", "workflow"] + args + ["-j", "-e", "dx-demo"],
                       capture_output=True, text=True)
    raw = re.sub(r"\x1b\[[0-9;]*m", "", r.stdout + r.stderr)
    i = raw.find("{")
    if i < 0:
        print("FAIL:", " ".join(args), raw[:300]); sys.exit(1)
    return json.loads(raw[i:])

def body_file(obj):
    f = pathlib.Path(tempfile.mkstemp(suffix=".json")[1])
    f.write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")
    return str(f)

def notice_cfg(content, receivers):
    return {"channelName": "in-app", "ignoreFail": True, "content": content, "receivers": receivers}

RECEIVER_STUDENT_USER = ["{{$context.data.student.user_id}}"]
RECEIVER_PAYMENT = [{"filter": {"student": {"id": {"$eq": "{{$context.data.student_id}}"}}}}]

FLOWS = [
    {
        "key": "3jjgxfrwd3l", "id": 396816229400576, "name": "请假",
        "nodes": [
            {"match": ("update", "标记超 1/7 提醒"), "title": "站内提醒（已通过，累计请假超限）",
             "config": notice_cfg("请假审批结果：你的请假申请已审批通过。注意：你的累计请假天数已超过总学习天数的1/7。", RECEIVER_STUDENT_USER)},
            {"branch": ("condition", "累计是否超过 1/7"), "title": "站内提醒（已通过）",
             "config": notice_cfg("请假审批结果：你的请假申请已审批通过。", RECEIVER_STUDENT_USER)},
            {"branch": ("condition", "审批是否通过"), "title": "站内提醒（未通过）",
             "config": notice_cfg("请假审批结果：你的请假申请未通过，请联系组织员了解详情。", RECEIVER_STUDENT_USER)},
        ],
    },
    {
        "key": "w5fd81cfoyg", "id": 396816562847744, "name": "退学",
        "nodes": [
            {"match": ("update", "学员学籍状态改为已退学"), "title": "站内提醒（退学已通过）",
             "config": notice_cfg("退学审批结果：你的退学申请已审批通过，学籍状态已更新。", RECEIVER_STUDENT_USER)},
            {"branch": ("condition", "审批是否通过"), "title": "站内提醒（退学未通过）",
             "config": notice_cfg("退学审批结果：你的退学申请未通过。", RECEIVER_STUDENT_USER)},
        ],
    },
    {
        "key": "re5oyih3tpo", "id": 396799131385856, "name": "报名",
        "nodes": [
            {"match": ("update", "回写报名关联"), "title": "站内提醒（报名通过，已开账号）",
             "config": notice_cfg("报名审核结果：恭喜，你的报名申请已通过，系统已为你开通学员账号（用户名为报名手机号，初始密码 dx123456）。", RECEIVER_STUDENT_USER)},
            {"match": ("update", "关联已有档案"), "title": "站内提醒（报名通过，已关联档案）",
             "config": notice_cfg("报名审核结果：你的报名申请已通过，已关联你的学员档案。", RECEIVER_STUDENT_USER)},
            {"branch": ("condition", "审核是否通过"), "title": "站内提醒（报名未通过）",
             "config": notice_cfg("报名审核结果：很遗憾，你的报名申请未通过。", RECEIVER_STUDENT_USER)},
        ],
    },
    {
        "key": "728jz0ss65a", "id": 396743055048704, "name": "缴费",
        "nodes": [
            {"match": ("manual", "缴费审核（教务）"), "title": "站内提醒（缴费审核完成）",
             "config": notice_cfg("缴费审核结果：你的缴费凭证已完成审核，请前往查看审核结果。", RECEIVER_PAYMENT)},
        ],
    },
]

new_ids = {}
for fl in FLOWS:
    print(f"\n===== {fl['name']}流 =====")
    rev = nb(["workflows", "revision", "--filter-by-tk", str(fl["id"]),
              "--filter", json.dumps({"key": fl["key"]})])
    new_id = rev["data"]["id"]
    new_ids[fl["name"]] = new_id
    print(f"revision: {fl['id']} -> {new_id}")

    wf = nb(["workflows", "get", "--filter-by-tk", str(new_id), "--appends", "nodes"])
    nodes = wf["data"]["nodes"]
    by_title = {(n["type"], n["title"]): n for n in nodes}

    for spec in fl["nodes"]:
        if "match" in spec:
            anchor = by_title[spec["match"]]
            body = {"type": "notification", "title": spec["title"],
                    "upstreamId": anchor["id"], "config": spec["config"]}
        else:
            anchor = by_title[spec["branch"]]
            body = {"type": "notification", "title": spec["title"],
                    "upstreamId": anchor["id"], "branchIndex": 0, "config": spec["config"]}
        d = nb(["workflows", "nodes", "create", "--workflow-id", str(new_id),
                "--body-file", body_file(body)])
        print(f"  + {spec['title']}: id={d['data']['id']}")

    nb(["workflows", "update", "--filter-by-tk", str(new_id),
        "--body-file", body_file({"enabled": True})])
    print("  enabled ✓")

print("\nNEW IDS:", json.dumps(new_ids, ensure_ascii=False))
