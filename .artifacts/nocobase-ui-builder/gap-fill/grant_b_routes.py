#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B 组 6 页 route 授权（页 + hidden tab 子行），按阶段3 业务规则。"""
import json, subprocess, re

PAGES = {
    "作业管理":   [396906271408128, 396906271408129],
    "材料回复":   [396906292379648, 396906292379649],
    "申报信息":   [396906304962560, 396906304962561],
    "纪律承诺":   [396906321739776, 396906321739777],
    "调课记录":   [396906552426496, 396906552426497],
    "通知阅读统计": [396906680352768, 396906680352769],
}
GRANT = {  # 角色 -> 页面列表
    "r_leader":   list(PAGES.values()),
    "r_academic": list(PAGES.values()),
    "r_organizer": [PAGES["作业管理"], PAGES["材料回复"], PAGES["申报信息"], PAGES["纪律承诺"], PAGES["通知阅读统计"]],
    "r_teacher":  [PAGES["作业管理"]],
}

def nb(args):
    r = subprocess.run(["nb", "api", "acl"] + args + ["-j", "-e", "dx-demo"],
                       capture_output=True, text=True)
    raw = re.sub(r"\x1b\[[0-9;]*m", "", r.stdout + r.stderr)
    i = raw.find("{")
    return json.loads(raw[i:]) if i >= 0 else {}

import pathlib, tempfile
tmp = pathlib.Path(tempfile.mkdtemp())

for role, groups in GRANT.items():
    ids = sorted({i for g in groups for i in g})
    f = tmp / f"{role}.json"
    f.write_text(json.dumps(ids))
    d = nb(["roles", "desktop-routes", "add", "--role-name", role, "--body-file", str(f)])
    ok = "data" in d or d.get("status") != 400
    print(role, "授权", len(ids), "条 ->", "OK" if ok else json.dumps(d)[:200])
print("done")
