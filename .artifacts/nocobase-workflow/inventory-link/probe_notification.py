#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""C1 前置：探 notification 通道 API 形态。"""
import json, subprocess, urllib.request, urllib.parse, re

tok = subprocess.run(["python3", "-c",
    'import json;print(json.load(open("/home/mxr/.nocobase/config.json"))["envs"]["dx-demo"]["auth"]["accessToken"])'],
    capture_output=True, text=True).stdout.strip()
BASE = "http://127.0.0.1:13000"
H = {"Authorization": "Bearer " + tok, "X-Authenticator": "basic", "Content-Type": "application/json"}

def req(method, path, body=None):
    r = urllib.request.Request(BASE + path, data=json.dumps(body).encode() if body else None,
                               headers=H, method=method)
    try:
        with urllib.request.urlopen(r, timeout=10) as resp:
            return resp.status, resp.read().decode()[:800]
    except Exception as e:
        b = ""
        if hasattr(e, "read"):
            try: b = e.read().decode()[:500]
            except Exception: pass
        return getattr(e, "code", 0), b

for p in ["/api/notificationManager/channels:list", "/api/notificationChannels:list",
          "/api/notificationManager/channels", "/api/notification/channels:list"]:
    s, b = req("GET", p)
    print(s, p, b[:200])
