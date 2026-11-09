#!/usr/bin/env python3
"""阶段4：创建 4 条审批 workflow（manual 节点 DIY，D2 决策）。
审批人写死测试账号：请假→organizer(3) 退学→leader(2) 报名/缴费→academic(4)
按钮 action.values 预设 status，manual update form 直接把审批结果写回申请记录。
"""
import json, subprocess, sys, os

NB_ENV = "dx-demo"
ART = os.path.dirname(os.path.abspath(__file__))

def nb(args):
    cmd = ["nb", "api", "workflow"] + args + ["-j", "-e", NB_ENV]
    r = subprocess.run(cmd, capture_output=True, text=True)
    out = r.stdout
    import re
    out = re.sub(r"\x1b\[[0-9;]*m", "", out)
    if r.returncode != 0:
        print("FAIL:", " ".join(args), "\nSTDOUT:", out, "\nSTDERR:", r.stderr)
        sys.exit(1)
    return json.loads(out)

def create_node(wf_id, body):
    res = nb(["workflows", "nodes", "create", "--workflow-id", str(wf_id),
              "--body-file", _tmp(body)])
    return res  # node dict with id/key

_tmpfiles = []
def _tmp(body):
    p = os.path.join(ART, f"_tmp_{len(_tmpfiles)}.json")
    with open(p, "w") as f:
        json.dump(body, f, ensure_ascii=False)
    _tmpfiles.append(p)
    return p

def remark_field(coll, name, title, component="Input.TextArea"):
    return {
        name: {
            "type": "string",
            "title": title,
            "x-decorator": "FormItem",
            "x-component": "CollectionField",
            "x-component-props": {"field": {"title": title, "x-component": component}},
            "x-collection-field": f"{coll}.{name}",
        }
    }

def manual_config(coll, remark, assignees, title_tpl, actions, form_key="review"):
    return {
        "mode": 0,
        "assignees": assignees,
        "title": title_tpl,
        "forms": {
            form_key: {
                "type": "update",
                "title": "审批处理",
                "collection": coll,
                "dataSource": "main",
                "filter": {"$and": [{"id": {"$eq": "{{$context.data.id}}"}}]},
                "schema": {
                    "type": "object",
                    "properties": remark_field(coll, *remark),
                },
                "actions": actions,
            }
        },
    }

APPROVE_REJECT = [
    {"key": "approve", "title": "通过", "status": 1, "values": {"status": "approved"}},
    {"key": "reject", "title": "驳回", "status": 1, "values": {"status": "rejected"}},
]
PASS_REJECT = [
    {"key": "pass", "title": "审核通过", "status": 1, "values": {"status": "approved"}},
    {"key": "deny", "title": "拒绝", "status": 1, "values": {"status": "rejected"}},
]

def create_workflow(title, description, collection, appends):
    body = {
        "title": title,
        "type": "collection",
        "sync": False,
        "enabled": False,
        "description": description,
        "config": {
            "collection": collection,
            "mode": 1,
            "appends": appends,
            "condition": {"$and": [{"status": {"$eq": "pending"}}]},
        },
    }
    return nb(["workflows", "create", "--body-file", _tmp(body)])

def cleanup():
    for p in _tmpfiles:
        os.unlink(p)

# ============ W1 请假审批流 ============
wf = create_workflow(
    "请假审批流",
    "学员请假提交后由组织员审批；通过时聚合累计请假天数，超过班次总学习天数 1/7 置 over_ratio 提醒（D21）",
    "nb_dx_leave", ["student", "klass"])
wf_id = wf["data"]["id"]
print("W1 leave workflow id:", wf_id)

m1 = create_node(wf_id, {
    "type": "manual", "title": "请假审批（组织员）",
    "config": manual_config("nb_dx_leave", ("approved_remark", "审批意见"),
                            [3], "请假审批 - {{$context.data.student_name}}", APPROVE_REJECT),
})
mk = m1["data"]["key"]; m1id = m1["data"]["id"]
print("manual:", m1id, mk)

c1 = create_node(wf_id, {
    "type": "condition", "title": "审批是否通过",
    "upstreamId": m1id, "branchIndex": None,
    "config": {
        "rejectOnFalse": False, "engine": "basic",
        "calculation": {"group": {"type": "and", "calculations": [
            {"calculator": "equal",
             "operands": [f"{{{{$jobsMapByNodeKey.{mk}.review.status}}}}", "approved"]}
        ]}},
    },
})
c1id = c1["data"]["id"]
print("cond1:", c1id)

agg = create_node(wf_id, {
    "type": "aggregate", "title": "累计已批请假天数（含本次）",
    "upstreamId": c1id, "branchIndex": 1,
    "config": {
        "aggregator": "sum", "associated": False, "collection": "nb_dx_leave",
        "params": {
            "field": "duration_days",
            "filter": {"$and": [
                {"student": {"id": {"$eq": "{{$context.data.student.id}}"}}},
                {"status": {"$eq": "approved"}},
            ]},
        },
        "precision": 2,
    },
})
aggk = agg["data"]["key"]; aggid = agg["data"]["id"]
print("aggregate:", aggid, aggk)

calc = create_node(wf_id, {
    "type": "calculation", "title": "总学习天数 1/7 上限",
    "upstreamId": aggid, "branchIndex": None,
    "config": {
        "engine": "math.js",
        "expression": "{{$context.data.klass.total_days}}/7",
    },
})
calck = calc["data"]["key"]; calcid = calc["data"]["id"]
print("calc:", calcid, calck)

c2 = create_node(wf_id, {
    "type": "condition", "title": "累计是否超过 1/7",
    "upstreamId": calcid, "branchIndex": None,
    "config": {
        "rejectOnFalse": False, "engine": "basic",
        "calculation": {"group": {"type": "and", "calculations": [
            {"calculator": "gt",
             "operands": [f"{{{{$jobsMapByNodeKey.{aggk}}}}}",
                          f"{{{{$jobsMapByNodeKey.{calck}}}}}"]}
        ]}},
    },
})
c2id = c2["data"]["id"]
print("cond2:", c2id)

u1 = create_node(wf_id, {
    "type": "update", "title": "标记超 1/7 提醒",
    "upstreamId": c2id, "branchIndex": 1,
    "config": {
        "collection": "nb_dx_leave", "usingAssignFormSchema": False, "assignFormSchema": {},
        "params": {
            "individualHooks": False,
            "filter": {"$and": [{"id": {"$eq": "{{$context.data.id}}"}}]},
            "values": {"over_ratio": True},
        },
    },
})
print("update over_ratio:", u1["data"]["id"])

# ============ W2 退学审批流 ============
wf2 = create_workflow(
    "退学审批流",
    "退学申请由校领导审批；通过时把学员学籍状态改为已退学（账号禁用简化为状态流转）",
    "nb_dx_dropout", ["student"])
wf2_id = wf2["data"]["id"]
print("W2 dropout workflow id:", wf2_id)

m2 = create_node(wf2_id, {
    "type": "manual", "title": "退学审批（校领导）",
    "config": manual_config("nb_dx_dropout", ("approved_remark", "审批意见"),
                            [2], "退学审批 - {{$context.data.student_name}}", APPROVE_REJECT),
})
m2id = m2["data"]["id"]; m2k = m2["data"]["key"]
print("manual:", m2id, m2k)

c3 = create_node(wf2_id, {
    "type": "condition", "title": "审批是否通过",
    "upstreamId": m2id, "branchIndex": None,
    "config": {
        "rejectOnFalse": False, "engine": "basic",
        "calculation": {"group": {"type": "and", "calculations": [
            {"calculator": "equal",
             "operands": [f"{{{{$jobsMapByNodeKey.{m2k}.review.status}}}}", "approved"]}
        ]}},
    },
})
c3id = c3["data"]["id"]
print("cond:", c3id)

u2 = create_node(wf2_id, {
    "type": "update", "title": "学员学籍状态改为已退学",
    "upstreamId": c3id, "branchIndex": 1,
    "config": {
        "collection": "nb_dx_student", "usingAssignFormSchema": False, "assignFormSchema": {},
        "params": {
            "individualHooks": False,
            "filter": {"$and": [{"id": {"$eq": "{{$context.data.student.id}}"}}]},
            "values": {"status": "dropout"},
        },
    },
})
print("update student:", u2["data"]["id"])

# ============ W3 报名审核流 ============
wf3 = create_workflow(
    "报名审核流",
    "扫码报名登记后由教务审核（自动开账号简化为状态流转）；通过/拒绝结果由 manual 表单写回",
    "nb_dx_registration", [])
wf3_id = wf3["data"]["id"]
print("W3 registration workflow id:", wf3_id)

m3 = create_node(wf3_id, {
    "type": "manual", "title": "报名审核（教务）",
    "config": manual_config("nb_dx_registration", ("review_remark", "审核备注"),
                            [4], "报名审核 - {{$context.data.name}}", PASS_REJECT),
})
print("manual:", m3["data"]["id"], m3["data"]["key"])

# ============ W4 缴费审核流 ============
wf4 = create_workflow(
    "缴费审核流",
    "缴费凭证提交后由教务审核；凭证上传后通过/拒绝结果由 manual 表单写回",
    "nb_dx_payment", [])
wf4_id = wf4["data"]["id"]
print("W4 payment workflow id:", wf4_id)

m4 = create_node(wf4_id, {
    "type": "manual", "title": "缴费审核（教务）",
    "config": manual_config("nb_dx_payment", ("review_remark", "审核备注"),
                            [4], "缴费审核 - {{$context.data.payer_name}}", PASS_REJECT),
})
print("manual:", m4["data"]["id"], m4["data"]["key"])

cleanup()
print("\nALL DONE. workflow ids:", wf_id, wf2_id, wf3_id, wf4_id)
