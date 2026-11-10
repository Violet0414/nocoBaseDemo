#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B1-B6 管理端新页蓝本生成（apply-blueprint 用）。
B1 作业管理（批阅/转批走 edit 弹窗） B2 材料回复 B3 申报信息 B4 纪律承诺 B5 调课记录 B6 通知阅读统计。
"""
import json, pathlib

ART = pathlib.Path(__file__).parent

CLASS_GROUPS = [
    {"key": "classBasic", "title": "基本信息",
     "fields": ["name", "code", "category", "train_type", "status", "organizer"]},
    {"key": "classPeriod", "title": "报名与学习周期",
     "fields": ["enroll_start", "enroll_end", "start_date", "end_date", "total_days", "total_hours"]},
    {"key": "classOther", "title": "其他信息",
     "fields": ["default_room", "qr_token", "description"]},
]
STUDENT_GROUPS = [
    {"key": "studentBasic", "title": "基本信息",
     "fields": ["name", "student_no", "gender", "birth_date", "political_status", "phone", "photo"]},
    {"key": "studentWork", "title": "单位与班级",
     "fields": ["work_unit", "duty", "group_no", "klass", "user"]},
    {"key": "studentStatus", "title": "学籍状态",
     "fields": ["status", "enroll_status", "excellent", "remark"]},
]

def popups_view(name):
    return {"popups": {"view": {"name": name, "description": f"查看一条{name}详情"}}}

def popups_ve(name):
    return {"popups": {"view": {"name": f"查看{name}", "description": f"查看一条{name}详情"},
                       "edit": {"name": f"编辑{name}", "description": f"编辑一条{name}记录"}}}

def pie(key, coll, field, alias):
    return {key: {
        "query": {"mode": "builder",
                  "resource": {"dataSourceKey": "main", "collectionName": coll},
                  "measures": [{"field": "id", "aggregation": "count", "alias": alias}],
                  "dimensions": [{"field": field}]},
        "visual": {"mode": "basic", "type": "pie",
                   "mappings": {"category": field, "value": alias}}}}

def page(coll_groups, group_route, title, icon, blocks, rows, charts=None):
    d = {"version": "1", "mode": "create"}
    if charts:
        d["assets"] = {"charts": charts}
    d["defaults"] = {"collections": coll_groups}
    d["navigation"] = {"portalUid": "__default_admin__",
                       "group": {"routeId": group_route},
                       "item": {"title": title, "icon": icon}}
    d["page"] = {"title": title}
    d["tabs"] = [{"key": "main", "title": title,
                  "layout": {"rows": rows}, "blocks": blocks}]
    return d

def table(key, coll, fields, actions):
    return {"key": key, "type": "table", "title": None, "collection": coll,
            "fields": fields, "recordActions": actions}

def chart_block(key, title, chart_key):
    return {"key": key, "type": "chart", "title": title, "chart": chart_key}

pages = {}

# ---------- B1 作业管理（教务管理组） ----------
pages["B1-assignment.json"] = page(
    {
        "nb_dx_assignment": popups_ve("作业"),
        "nb_dx_submission": popups_ve("作业提交"),
        "nb_dx_topic": {"popups": {"view": {"name": "查看专题", "description": "查看一条教学专题详情"},
                                   "associations": {"teacher": {"view": {"name": "查看教师", "description": "查看教师详情"}}}}},
        "nb_dx_class": {"popups": {"view": {"name": "查看班次", "description": "查看一条班次记录详情"}}, "fieldGroups": CLASS_GROUPS},
        "nb_dx_student": {"popups": {"view": {"name": "查看学员", "description": "查看一条学员详情"}}, "fieldGroups": STUDENT_GROUPS},
        "users": popups_view("用户"),
    },
    "396723346014208", "作业管理", "FileDoneOutlined",
    [table("assignmentTable", "nb_dx_assignment",
           ["name", "topic.name", "klass.name", "teacher.nickname", "due_date", "review_mode", "status"],
           ["view", "edit"]),
     chart_block("subChart", "作业提交情况统计", "subByStatus"),
     table("submissionTable", "nb_dx_submission",
           ["assignment.name", "student.name", "submitted_at", "score", "review", "status"],
           ["view", "edit"])],
    [[{"key": "assignmentTable", "span": 24}],
     [{"key": "subChart", "span": 12}, {"key": "submissionTable", "span": 12}]],
    charts=pie("subByStatus", "nb_dx_submission", "status", "subCount"),
)

# ---------- B2 材料回复（教务管理组） ----------
pages["B2-material.json"] = page(
    {
        "nb_dx_material": popups_ve("材料"),
        "nb_dx_class": {"popups": {"view": {"name": "查看班次", "description": "查看一条班次记录详情"}}, "fieldGroups": CLASS_GROUPS},
        "nb_dx_student": {"popups": {"view": {"name": "查看学员", "description": "查看一条学员详情"}}, "fieldGroups": STUDENT_GROUPS},
        "users": popups_view("用户"),
    },
    "396723346014208", "材料回复", "MessageOutlined",
    [chart_block("matChart", "材料类型分布", "matByKind"),
     table("matTable", "nb_dx_material",
           ["student.name", "klass.name", "kind", "question", "content", "status", "reply"],
           ["view", "edit"])],
    [[{"key": "matChart", "span": 12}, {"key": "matTable", "span": 12}]],
    charts=pie("matByKind", "nb_dx_material", "kind", "matCount"),
)

# ---------- B3 申报信息（教务管理组） ----------
pages["B3-declaration.json"] = page(
    {
        "nb_dx_declaration": popups_view("申报信息"),
        "nb_dx_class": {"popups": {"view": {"name": "查看班次", "description": "查看一条班次记录详情"}}, "fieldGroups": CLASS_GROUPS},
        "nb_dx_student": {"popups": {"view": {"name": "查看学员", "description": "查看一条学员详情"}}, "fieldGroups": STUDENT_GROUPS},
    },
    "396723346014208", "申报信息", "ProfileOutlined",
    [chart_block("declChart", "申报类型分布", "declByType"),
     table("declTable", "nb_dx_declaration",
           ["student.name", "klass.name", "type", "content", "date"],
           ["view"])],
    [[{"key": "declChart", "span": 12}, {"key": "declTable", "span": 12}]],
    charts=pie("declByType", "nb_dx_declaration", "type", "declCount"),
)

# ---------- B4 纪律承诺（班务管理组） ----------
pages["B4-commitment.json"] = page(
    {
        "nb_dx_commitment": popups_view("纪律承诺"),
        "nb_dx_class": {"popups": {"view": {"name": "查看班次", "description": "查看一条班次记录详情"}}, "fieldGroups": CLASS_GROUPS},
        "nb_dx_student": {"popups": {"view": {"name": "查看学员", "description": "查看一条学员详情"}}, "fieldGroups": STUDENT_GROUPS},
    },
    "396730107232256", "纪律承诺", "SafetyCertificateOutlined",
    [chart_block("signChart", "签署情况统计", "signByStatus"),
     table("signTable", "nb_dx_commitment",
           ["title", "klass.name", "student.name", "signed", "signed_at"],
           ["view"])],
    [[{"key": "signChart", "span": 12}, {"key": "signTable", "span": 12}]],
    charts=pie("signByStatus", "nb_dx_commitment", "signed", "signCount"),
)

# ---------- B5 调课记录（教务管理组） ----------
CS_GROUPS = [
    {"key": "csBasic", "title": "课程信息",
     "fields": ["topic_name", "klass", "topic", "activity", "kind", "week_no", "day_of_week"]},
    {"key": "csTime", "title": "时间与地点",
     "fields": ["start_time", "end_time", "place", "unit_name"]},
    {"key": "csOther", "title": "其他",
     "fields": ["teacher", "merged", "eval_enabled", "status"]},
]
pages["B5-change-log.json"] = page(
    {
        "nb_dx_change_log": popups_view("调课记录"),
        "nb_dx_course_schedule": {"popups": {"view": {"name": "查看课节", "description": "查看一条课节详情"}}, "fieldGroups": CS_GROUPS},
        "users": popups_view("经办人"),
    },
    "396723346014208", "调课记录", "HistoryOutlined",
    [table("changeTable", "nb_dx_change_log",
           ["summary", "old_values", "new_values", "reason", "notified", "operator.nickname"],
           ["view"])],
    [[{"key": "changeTable", "span": 24}]],
)

# ---------- B6 通知阅读统计（教务管理组） ----------
# through 集合无关联字段，改用 announcement 主表 + readers m2m 列展示已读人员
pages["B6-notice-readers.json"] = page(
    {
        "nb_dx_announcement": popups_view("教学通知"),
        "nb_dx_class": {"popups": {"view": {"name": "查看班次", "description": "查看一条班次记录详情"}}, "fieldGroups": CLASS_GROUPS},
        "users": popups_view("阅读人"),
    },
    "396723346014208", "通知阅读统计", "ReadOutlined",
    [table("readTable", "nb_dx_announcement",
           ["title", "kind", "publisher.nickname", "published_at", "readers.nickname"],
           ["view"])],
    [[{"key": "readTable", "span": 24}]],
)

for fn, d in pages.items():
    # 清理 title: None
    for t in d["tabs"]:
        for b in t["blocks"]:
            if b.get("title") is None:
                b.pop("title")
    (ART / fn).write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    print("written", fn)
print("done")
