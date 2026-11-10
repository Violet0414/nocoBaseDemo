#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""方案A：admin 门户 3 个排课入口页蓝本（jsBlock iframe 嵌 /x/main，D50 已验证 iframe 模式）。
排课管理/课表查询 → 教务管理组；排座管理 → 班务管理组。
"""
import json, pathlib

ART = pathlib.Path(__file__).parent

ACADEMIC_GROUP = "396723346014208"   # 教务管理
CLASSADMIN_GROUP = "396730107232256"  # 班务管理


def page(title, icon, group_route, src):
    code = (
        "const { Spin } = ctx.libs.antd;\n"
        "ctx.render(\n"
        "  <div style={{ margin: -24 }}>\n"
        "    <iframe\n"
        f"      src=\"{src}\"\n"
        "      style={{ width: '100%', height: 'calc(100vh - 64px)', border: 0, display: 'block' }}\n"
        f"      title=\"{title}\"\n"
        "    />\n"
        "  </div>\n"
        ");\n"
    )
    return {
        "version": "1",
        "mode": "create",
        "navigation": {
            "portalUid": "__default_admin__",
            "group": {"routeId": group_route},
            "item": {"title": title, "icon": icon},
        },
        "page": {"title": title},
        "tabs": [
            {
                "key": "main",
                "title": title,
                "blocks": [
                    {
                        "key": "entryIframe",
                        "type": "jsBlock",
                        "settings": {"code": code},
                    }
                ],
            }
        ],
    }


pages = {
    "schedule-entry-board.json": page("排课管理", "LayoutOutlined", ACADEMIC_GROUP, "/x/main/schedule/board"),
    "schedule-entry-week.json": page("课表查询", "ClockCircleOutlined", ACADEMIC_GROUP, "/x/main/schedule/week"),
    "schedule-entry-seats.json": page("排座管理", "AppstoreOutlined", CLASSADMIN_GROUP, "/x/main/schedule/seats"),
}

for name, bp in pages.items():
    (ART / name).write_text(json.dumps(bp, ensure_ascii=False, indent=2), encoding="utf-8")
    print("written", name)
