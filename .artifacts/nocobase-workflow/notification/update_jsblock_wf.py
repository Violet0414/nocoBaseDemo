#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""C1 收尾：jsBlock 72hgyrjlwza 补 4 条流新 revision id（ENABLED_WF/WF_TITLE/FALLBACK_ACTIONS）。
读-改-写（dollar-quote），先备份原 options 到 backups/。"""
import json, subprocess, re, pathlib, sys

UID = "72hgyrjlwza"
NEW = {  # 新 revision id: (标题, 动作对形态)
    396908352176128: ("请假审批", "approve"),
    396908373147648: ("退学审批", "approve"),
    396908392022016: ("报名审核", "pass"),
    396908412993536: ("缴费审核", "pass"),
}
ACTIONS = {
    "approve": "[]({key:'approve',title:'通过',values:{status:'approved'}},{key:'reject',title:'驳回',values:{status:'rejected'}})".replace("[]", "[{...}]"),
}
ACT_STR = {
    "approve": "[{key:'approve',title:'通过',values:{status:'approved'}},{key:'reject',title:'驳回',values:{status:'rejected'}}]",
    "pass": "[{key:'pass',title:'审核通过',values:{status:'approved'}},{key:'deny',title:'拒绝',values:{status:'rejected'}}]",
}

def psql(sql):
    r = subprocess.run(["docker", "exec", "nb-dx-demo-postgres", "psql", "-U", "nocobase", "nocobase",
                        "-t", "-A", "-c", sql], capture_output=True, text=True)
    if r.returncode != 0:
        print("PSQL FAIL:", r.stderr[:300]); sys.exit(1)
    return r.stdout.strip()

# 1. 读原 options
raw = psql(f"SELECT options::text FROM \"flowModels\" WHERE uid='{UID}';")
code = json.loads(raw)["code"] if isinstance(json.loads(raw), dict) and "code" in json.loads(raw) else raw

# 兼容：options 是 JSON，code 字段在哪层
obj = json.loads(raw)
code = (obj.get("stepParams", {}).get("jsSettings", {}).get("runJs", {}).get("code")
        or obj.get("code"))
if not code or "ENABLED_WF" not in code:
    print("code 字段定位失败，顶层键:", list(obj.keys())[:20]); sys.exit(1)

# 2. 备份
bdir = pathlib.Path("/mnt/e/贵州顺拓/demo/backups")
(bdir / "flowmodels_jsblock_wf_20261110.txt").write_text(raw, encoding="utf-8")

# 3. 改
assert "ENABLED_WF = [" in code
ids_str = ", ".join(str(i) for i in NEW)
code = code.replace("ENABLED_WF = [", f"ENABLED_WF = [{ids_str}, ", 1)

# 锚点精确替换（WF_TITLE 末行=退学映射，FALLBACK_ACTIONS 末行=退学 approve 映射）
TITLE_ANCHOR = "396816562847744: '退学审批',\n};"
ACT_ANCHOR = ("396816562847744: [{key:'approve',title:'通过',values:{status:'approved'}},"
              "{key:'reject',title:'驳回',values:{status:'rejected'}}],\n};")
assert code.count(TITLE_ANCHOR) == 1, f"TITLE 锚点数={code.count(TITLE_ANCHOR)}"
assert code.count(ACT_ANCHOR) == 1, f"ACT 锚点数={code.count(ACT_ANCHOR)}"

title_add = "".join(f"  {i}: '{t}',\n" for i, (t, _) in NEW.items())
act_add = "".join(f"  {i}: {ACT_STR[a]},\n" for i, (t, a) in NEW.items())
code = code.replace(TITLE_ANCHOR, "396816562847744: '退学审批',\n" + title_add + "};")
code = code.replace(ACT_ANCHOR, ACT_ANCHOR[:-len("\n};")] + "\n" + act_add + "};")

obj_new = dict(obj)
if "code" in obj:
    obj_new["code"] = code
else:
    obj_new["stepParams"]["jsSettings"]["runJs"]["code"] = code

# 4. 写回（dollar-quote）
payload = json.dumps(obj_new, ensure_ascii=False)
sql = 'UPDATE "flowModels" SET options = $jsb$' + payload + '$jsb$::json WHERE uid = \'' + UID + '\';'
psql(sql)

# 5. 验证
chk = psql(f"SELECT options::text FROM \"flowModels\" WHERE uid='{UID}';")
ok1 = all(str(i) in chk for i in NEW)
ok2 = chk.count("ENABLED_WF") == 1
print("写入完成：新 id 全部在位 =", ok1, "| JSON 合法 =", bool(json.loads(chk)))
print("ENABLED_WF 段:", chk[chk.find("ENABLED_WF"):chk.find("ENABLED_WF") + 180])
