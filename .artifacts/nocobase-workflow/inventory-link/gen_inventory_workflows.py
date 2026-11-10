#!/usr/bin/env python3
"""A1 库存联动 workflow ×3（Violet 确认：提交即触发）。
采购/领用/退库 create 触发 → query 查教材当前库存 → calculation 算变动后库存
  → update textbook.stock → create inventory_log 流水（before/after/qty_change）。
引用形态（报名流 v2 实存确认）：query/create 结果引用 {{$jobsMapByNodeKey.<key>.字段}}（无 .data）。
"""
import json, subprocess, sys, os, re

NB_ENV = "dx-demo"
ART = os.path.dirname(os.path.abspath(__file__))

def nb(args):
    cmd = ["nb", "api", "workflow"] + args + ["-j", "-e", NB_ENV]
    r = subprocess.run(cmd, capture_output=True, text=True)
    out = re.sub(r"\x1b\[[0-9;]*m", "", r.stdout)
    if r.returncode != 0:
        print("FAIL:", " ".join(args), "\nSTDOUT:", out, "\nSTDERR:", r.stderr)
        sys.exit(1)
    return json.loads(out)

_tmpfiles = []
def _tmp(body):
    p = os.path.join(ART, f"_tmp_{len(_tmpfiles)}.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(body, f, ensure_ascii=False)
    _tmpfiles.append(p)
    return p

def node(wf_id, title, ntype, upstream, config):
    body = {"type": ntype, "title": title, "upstreamId": upstream, "config": config}
    d = nb(["workflows", "nodes", "create", "--workflow-id", str(wf_id),
            "--body-file", _tmp(body)])["data"]
    print(f"  {ntype:11s} {title}: id={d['id']} key={d['key']}")
    return d

def C(f):
    return f"{{{{$context.data.{f}}}}}"

def J(key, field=""):
    return f"{{{{$jobsMapByNodeKey.{key}{('.' + field) if field else ''}}}}}"

# (标题, 触发集合, 流水type, 库存运算符, ref_no 字段或 None)
FLOWS = [
    ("教材采购库存联动流", "nb_dx_purchase",        "采购", "+", None),
    ("教材领用库存联动流", "nb_dx_requisition",     "领用", "-", "batch_no"),
    ("教材退库库存联动流", "nb_dx_textbook_return", "退库", "+", None),
]

created = {}
for title, coll, ltype, op, ref_field in FLOWS:
    wf = nb(["workflows", "create", "--body-file", _tmp({
        "title": title,
        "type": "collection",
        "sync": False,
        "enabled": True,
        "description": f"{ltype}提交即触发：自动增减教材库存并写库存流水（PLAN A 类 workflow 库存联动）",
        "config": {"collection": coll, "mode": 1, "appends": []},
    })])
    wf_id = wf["data"]["id"]
    print(f"\n{title} workflow id={wf_id}")

    q = node(wf_id, "查询教材当前库存", "query", None, {
        "collection": "nb_dx_textbook", "multiple": False,
        "params": {"filter": {"$and": [{"id": {"$eq": C("textbook_id")}}]}},
    })
    calc = node(wf_id, "计算变动后库存", "calculation", q["id"], {
        "engine": "math.js", "expression": f"{J(q['key'], 'stock')} {op} {C('quantity')}",
    })
    upd = node(wf_id, "更新教材库存", "update", calc["id"], {
        "collection": "nb_dx_textbook", "usingAssignFormSchema": False, "assignFormSchema": {},
        "params": {
            "individualHooks": False,
            "filter": {"$and": [{"id": {"$eq": C("textbook_id")}}]},
            "values": {"stock": J(calc["key"])},
        },
    })
    ref = C(ref_field) if ref_field else C("id")
    node(wf_id, "写入库存流水", "create", upd["id"], {
        "collection": "nb_dx_inventory_log",
        "params": {"values": {
            "textbook_id": C("textbook_id"),
            "textbook_name": C("textbook_name"),
            "type": ltype,
            "qty_change": C("quantity"),
            "before_qty": J(q["key"], "stock"),
            "after_qty": J(calc["key"]),
            "ref_no": ref,
            "happened_at": C("createdAt"),
        }},
    })
    created[title] = wf_id

for p in _tmpfiles:
    os.unlink(p)
print("\nDONE. workflow ids:", json.dumps(created, ensure_ascii=False))
