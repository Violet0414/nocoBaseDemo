#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""D 组：学员社区。D2 admin 社区管理页（学员管理组）；D3 移动端学员社区页（mobile Portal）。
复用 comment 表（D1 零建模）：kind=post 帖子 / kind=reply 跟帖，parent_id 自关联。"""
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

def ds(field, value):
    return {"settings": {"dataScope": {"filter": {"logic": "$and", "items": [
        {"path": field, "operator": "$eq", "value": value}]}}}}

# ---------- D2 admin 社区管理（学员管理组 396734674829312） ----------
d2 = {
    "version": "1", "mode": "create",
    "assets": {"charts": {"actByAuthor": {
        "query": {"mode": "builder",
                  "resource": {"dataSourceKey": "main", "collectionName": "nb_dx_comment"},
                  "measures": [{"field": "id", "aggregation": "count", "alias": "actCount"}],
                  "dimensions": [{"field": "author.nickname"}]},
        "visual": {"mode": "basic", "type": "bar",
                   "mappings": {"x": "author.nickname", "y": "actCount"}}}}},
    "defaults": {"collections": {
        "nb_dx_comment": {"popups": {
            "view": {"name": "查看帖子", "description": "查看一条帖子或跟帖详情"},
            "edit": {"name": "编辑帖子", "description": "编辑一条帖子或跟帖"}}},
        "users": {"popups": {"view": {"name": "查看用户", "description": "查看用户详情"}}},
        "nb_dx_class": {"popups": {"view": {"name": "查看班次", "description": "查看一条班次记录详情"}},
                        "fieldGroups": CLASS_GROUPS},
    }},
    "navigation": {"portalUid": "__default_admin__",
                   "group": {"routeId": "396734674829312"},
                   "item": {"title": "学员社区", "icon": "TeamOutlined"}},
    "page": {"title": "学员社区"},
    "tabs": [{"key": "main", "title": "学员社区",
              "layout": {"rows": [
                  [{"key": "actChart", "span": 12}, {"key": "postTable", "span": 12}],
                  [{"key": "replyTable", "span": 24}]]},
              "blocks": [
                  {"key": "actChart", "type": "chart", "title": "社区活跃度（发帖与回复排名）", "chart": "actByAuthor"},
                  {**{"key": "postTable", "type": "table", "title": "帖子列表", "collection": "nb_dx_comment",
                      "fields": ["title", "content", "author.nickname", "klass.name", "hot"],
                      "recordActions": ["view", "edit", "delete"]}, **ds("kind", "post")},
                  {**{"key": "replyTable", "type": "table", "title": "跟帖列表", "collection": "nb_dx_comment",
                      "fields": ["content", "author.nickname", "parent.title", "hot"],
                      "recordActions": ["view", "edit", "delete"]}, **ds("kind", "reply")},
              ]}],
}
(ART / "D2-community-admin.json").write_text(json.dumps(d2, ensure_ascii=False, indent=1), encoding="utf-8")

# ---------- D3 移动端学员社区（mobile Portal） ----------
d3 = {
    "version": "1", "mode": "create",
    "navigation": {"portalUid": "__default_mobile__", "item": {"title": "学员社区", "icon": "TeamOutlined"}},
    "page": {"title": "学员社区"},
    "tabs": [{"key": "main", "title": "学员社区",
              "layout": {"rows": [
                  [{"key": "postForm", "span": 12}, {"key": "postList", "span": 12}]]},
              "blocks": [
                  {"key": "postForm", "type": "createForm", "title": "发表帖子", "collection": "nb_dx_comment",
                   "fields": [{"field": "author", "titleField": "nickname"}, "title", "content",
                              {"field": "klass", "titleField": "name"}]},
                  {**{"key": "postList", "type": "table", "title": "帖子广场", "collection": "nb_dx_comment",
                      "fields": ["title", "content", "author.nickname", "hot"],
                      "recordActions": ["view"]}, **ds("kind", "post")},
              ]}],
    "defaults": {"collections": {
        "nb_dx_comment": {"popups": {
            "view": {"name": "帖子详情", "description": "查看帖子详情"},
            "addNew": {"name": "发表帖子", "description": "发表一条新帖子"}}},
        "users": {"popups": {"view": {"name": "用户详情", "description": "查看用户详情"},
                             "addNew": {"name": "新增用户", "description": "新增用户"},
                             "edit": {"name": "编辑用户", "description": "编辑用户"}}},
        "nb_dx_class": {"popups": {
            "view": {"name": "班次详情", "description": "查看班次详情"},
            "addNew": {"name": "新增班次", "description": "新增班次"},
            "edit": {"name": "编辑班次", "description": "编辑班次"}},
            "fieldGroups": CLASS_GROUPS},
    }},
}
(ART / "D3-community-mobile.json").write_text(json.dumps(d3, ensure_ascii=False, indent=1), encoding="utf-8")
print("written D2/D3")
