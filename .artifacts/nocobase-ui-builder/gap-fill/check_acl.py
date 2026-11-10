#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""查 4 角色对 B 组相关表的 collection 权限（acl data-source-resources get）。"""
import json, subprocess, re

ROLES = ["r_leader", "r_organizer", "r_academic", "r_teacher", "r_student"]
TABLES = ["nb_dx_assignment", "nb_dx_submission", "nb_dx_material",
          "nb_dx_declaration", "nb_dx_commitment", "nb_dx_change_log",
          "nb_dx_announcement", "nb_dx_comment"]

def nb(args):
    r = subprocess.run(["nb", "api", "acl"] + args + ["-j", "-e", "dx-demo"],
                       capture_output=True, text=True)
    raw = re.sub(r"\x1b\[[0-9;]*m", "", r.stdout)
    i = raw.find("{")
    return json.loads(raw[i:]) if i >= 0 else {}

MAP = {"view": "R", "list": "R", "get": "R", "create": "C", "update": "U",
       "destroy": "D", "delete": "D", "export": "X", "import": "I"}
for role in ROLES:
    row = [role]
    for t in TABLES:
        d = nb(["roles", "data-source-resources", "get",
                "--role-name", role, "--name", t, "--data-source-key", "main", "--appends", "actions"])
        res = d.get("data") or {}
        acts = res.get("actions") or {}
        names = sorted(str(a) for a in acts) if isinstance(acts, dict) else sorted(str(acts))
        key = "".join(MAP.get(n, n[0].upper()) for n in names) or "-"
        row.append(f"{t.split('_', 2)[-1]}:{key}")
    print(" ".join(row))
