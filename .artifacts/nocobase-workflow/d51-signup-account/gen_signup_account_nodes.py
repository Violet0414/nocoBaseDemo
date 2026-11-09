#!/usr/bin/env python3
"""报名流 v2 追加「审核通过 → 自动建档+开账号」节点链（D54）。
链：manual(审批) → cond[approved] → query(按手机号查学员档案)
    → cond[无档案] → (create user → create student → update registration 回写)
                    → (update registration 只挂已有档案)
"""
import json, subprocess, sys, os, re

NB_ENV = "dx-demo"
ART = os.path.dirname(os.path.abspath(__file__))
WF = 396799131385856          # 报名流 v2
MANUAL_KEY = "y97wivn2i9u"    # 复制的审批节点 key

def nb(args):
    cmd = ["nb", "api", "workflow"] + args + ["-j", "-e", NB_ENV]
    r = subprocess.run(cmd, capture_output=True, text=True)
    out = re.sub(r"\x1b\[[0-9;]*m", "", r.stdout)
    if r.returncode != 0:
        print("FAIL:", " ".join(args), "\nSTDOUT:", out, "\nSTDERR:", r.stderr)
        sys.exit(1)
    return json.loads(out)

tmpfiles = []
def _tmp(body):
    p = os.path.join(ART, f"_tmp_{len(tmpfiles)}.json")
    json.dump(body, open(p, "w"), ensure_ascii=False)
    tmpfiles.append(p)
    return p

def node(title, ntype, upstream, branch, config):
    body = {"type": ntype, "title": title, "upstreamId": upstream,
            "branchIndex": branch, "config": config}
    r = nb(["workflows", "nodes", "create", "--workflow-id", str(WF),
            "--body-file", _tmp(body)])
    d = r["data"]
    print(f"  {ntype:9s} {title}: id={d['id']} key={d['key']}")
    return d

M = f"{{${{$jobsMapByNodeKey.{MANUAL_KEY}.review.status}}}}"   # manual 提交的 status
C = lambda f: f"{{${{$context.data.{f}}}}}"

# 1. cond: 审核是否通过
c1 = node("审核是否通过", "condition", 396799131385857, None, {
    "engine": "basic", "rejectOnFalse": False,
    "calculation": {"group": {"type": "and", "calculations": [
        {"calculator": "equal", "operands": [M, "approved"]}]}},
})

# 2. query: 按手机号查已有学员档案
q1 = node("按手机号查已有学员档案", "query", c1["id"], 0, {
    "collection": "nb_dx_student", "multiple": False,
    "params": {"filter": {"$and": [{"phone": {"$eq": C("phone")}}]}},
})
Q = f"{{${{$jobsMapByNodeKey.{q1['key']}}}}}"

# 3. cond: 是否无档案
c2 = node("是否无学员档案", "condition", q1["id"], 0, {
    "engine": "basic", "rejectOnFalse": False,
    "calculation": {"group": {"type": "and", "calculations": [
        {"calculator": "empty", "operands": [Q]}]}},
})

# 4a. true 分支: 开通学员账号
cu = node("开通学员账号", "create", c2["id"], 0, {
    "collection": "users",
    "params": {"values": {
        "username": C("phone"), "nickname": C("name"),
        "password": "dx123456", "roles": ["r_student"]}},
})
U = f"{{${{$jobsMapByNodeKey.{cu['key']}.data.id}}}}"

# 4b. 创建学员档案（挂班 + 绑账号）
cs = node("创建学员档案", "create", cu["id"], 0, {
    "collection": "nb_dx_student",
    "params": {"values": {
        "name": C("name"), "phone": C("phone"), "gender": C("gender"),
        "political_status": C("political_status"), "work_unit": C("work_unit"),
        "class_id": C("class_id"), "user_id": U,
        "status": "active", "enroll_status": "yes"}},
})
S = f"{{${{$jobsMapByNodeKey.{cs['key']}.data.id}}}}"

# 4c. 回写 registration 关联
node("回写报名关联", "update", cs["id"], 0, {
    "collection": "nb_dx_registration",
    "params": {"filter": {"$and": [{"id": {"$eq": C("id")}}]},
               "values": {"student_id": S, "user_id": U}},
})

# 5. false 分支: 已有档案，只回写关联
node("关联已有档案", "update", c2["id"], 1, {
    "collection": "nb_dx_registration",
    "params": {"filter": {"$and": [{"id": {"$eq": C("id")}}]},
               "values": {"student_id": f"{{{{Q.data.id}}}}" if False else Q + ".data.id"}},
})

for p in tmpfiles: os.unlink(p)
print("done")
