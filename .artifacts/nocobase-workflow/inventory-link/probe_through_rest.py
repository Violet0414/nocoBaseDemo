#!/usr/bin/env python3
"""B6 前置验证：nb_dx_announcement_readers through 集合 REST 可用性与字段形态。"""
import json, subprocess, urllib.request, urllib.parse

tok = subprocess.run(["python3", "-c",
    'import json;print(json.load(open("/home/mxr/.nocobase/config.json"))["envs"]["dx-demo"]["auth"]["accessToken"])'],
    capture_output=True, text=True).stdout.strip()
BASE = "http://127.0.0.1:13000/api"
H = {"Authorization": "Bearer " + tok, "X-Authenticator": "basic"}

def get(path):
    try:
        with urllib.request.urlopen(urllib.request.Request(BASE + path, headers=H), timeout=10) as r:
            return r.status, r.read().decode()[:600]
    except Exception as e:
        body = ""
        if hasattr(e, "read"):
            try: body = e.read().decode()[:300]
            except Exception: pass
        return getattr(e, "code", 0), body

s, b = get("/nb_dx_announcement_readers?pageSize=1&appends=announcement,users")
print("GET collection:", s, b)
s, b = get("/nb_dx_announcement_readers?pageSize=1")
print("GET list:", s, b)
