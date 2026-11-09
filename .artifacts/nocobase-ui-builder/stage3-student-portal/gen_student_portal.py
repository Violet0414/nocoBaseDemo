# 生成阶段3-5 学员管理(5页) + 综合门户(3页) 蓝本 JSON
# 复用 s3-class-admin 的 defaults 分组方案(student/class),新增 excellent 进分组
import json, os

OUT = os.path.dirname(os.path.abspath(__file__))

STU_POPUPS = {
    "view": {"name": "查看学员", "description": "查看一条学员详情"},
    "addNew": {"name": "新增学员", "description": "新增一条学员记录"},
    "edit": {"name": "编辑学员", "description": "编辑一条学员记录"},
}
CLASS_POPUPS = {
    "view": {"name": "查看班次", "description": "查看一条班次详情"},
    "addNew": {"name": "新增班次", "description": "新增一条班次记录"},
    "edit": {"name": "编辑班次", "description": "编辑一条班次记录"},
}
ANN_POPUPS = {
    "view": {"name": "查看通知", "description": "查看一条通知公告详情"},
    "addNew": {"name": "新增通知", "description": "新增一条通知公告"},
    "edit": {"name": "编辑通知", "description": "编辑一条通知公告"},
}

STU_GROUPS = [
    {"key": "stuBasic", "title": "基本信息", "fields": [
        "name", "student_no", "gender", "birth_date", "political_status", "phone", "photo"]},
    {"key": "stuWork", "title": "单位与分工", "fields": [
        "work_unit", "duty", "group_no", "excellent"]},
    {"key": "stuStatus", "title": "学籍与状态", "fields": [
        "status", "enroll_status", "remark", "klass", "user"]},
]
CLASS_GROUPS = [
    {"key": "classBasic", "title": "基本信息", "fields": [
        "name", "code", "category", "train_type", "status", "organizer"]},
    {"key": "classPeriod", "title": "报名与学习周期", "fields": [
        "enroll_start", "enroll_end", "start_date", "end_date", "total_days", "total_hours"]},
    {"key": "classOther", "title": "教室与其他", "fields": [
        "default_room", "room_locked", "qr_token", "description", "students",
        "teaching_plans", "course_schedules", "elective_plans", "seats"]},
]

DEF_STUDENT = {"popups": STU_POPUPS, "fieldGroups": STU_GROUPS}
DEF_CLASS = {"popups": CLASS_POPUPS, "fieldGroups": CLASS_GROUPS}
DEF_ANN = {"popups": ANN_POPUPS}


def chart(collection, dim, alias, ctype="pie"):
    return {
        "query": {
            "mode": "builder",
            "resource": {"dataSourceKey": "main", "collectionName": collection},
            "measures": [{"field": "id", "aggregation": "count", "alias": alias}],
            "dimensions": [{"field": dim}],
        },
        "visual": {
            "mode": "basic",
            "type": ctype,
            "mappings": ({"x": dim, "y": alias} if ctype == "bar"
                         else {"category": dim, "value": alias}),
        },
    }


def table(key, title, collection, fields, record_actions, settings=None):
    b = {
        "key": key, "type": "table", "title": title, "collection": collection,
        "fields": fields, "recordActions": record_actions,
    }
    if settings:
        b["settings"] = settings
    return b


def page(nav_group, item_title, item_icon, page_title, tab_title, blocks, defaults, assets=None):
    d = {
        "version": "1",
        "mode": "create",
        "navigation": {
            "layoutUid": "admin-layout-model",
            "group": nav_group,
            "item": {"title": item_title, "icon": item_icon},
        },
        "page": {"title": page_title},
        "tabs": [{
            "key": "main", "title": tab_title, "blocks": blocks,
            "layout": {"rows": [[{"key": b["key"], "span": 24} for b in blocks]]},
        }],
        "defaults": {"collections": defaults},
    }
    if assets:
        d["assets"] = assets
    return d


GROUP_STU = {"title": "学员管理", "icon": "TeamOutlined"}
GROUP_PORTAL = {"title": "综合门户", "icon": "AppstoreOutlined"}

pages = {}

# ---------- 学员管理 5 页 ----------
pages["page1-student-info"] = page(
    GROUP_STU, "学员信息", "ProfileOutlined", "学员信息", "学员信息",
    [table("stuTable", "学员信息", "nb_dx_student",
           ["name", "student_no", "gender", "klass.name", "duty", "work_unit", "phone", "status", "enroll_status"],
           ["view", "edit", "delete"])],
    {"nb_dx_student": DEF_STUDENT, "nb_dx_class": DEF_CLASS},
)

pages["page2-student-album"] = page(
    GROUP_STU, "学员相册", "TeamOutlined", "学员相册", "学员相册",
    [table("albumTable", "学员相册", "nb_dx_student",
           ["photo", "name", "gender", "work_unit", "duty", "klass.name", "excellent"],
           ["view"])],
    {"nb_dx_student": DEF_STUDENT, "nb_dx_class": DEF_CLASS},
)

pages["page3-student-status"] = page(
    GROUP_STU, "学籍管理", "IdcardOutlined", "学籍管理", "学籍管理",
    [
        {"key": "statusPie", "type": "chart", "title": "学籍状态分布", "chart": "stuByStatus"},
        table("statusTable", "学籍明细", "nb_dx_student",
              ["name", "student_no", "klass.name", "status", "enroll_status", "remark"],
              ["view", "edit"]),
    ],
    {"nb_dx_student": DEF_STUDENT, "nb_dx_class": DEF_CLASS},
    assets={"charts": {"stuByStatus": chart("nb_dx_student", "status", "stuCount")}},
)

pages["page4-student-archive"] = page(
    GROUP_STU, "学员档案", "FileTextOutlined", "学员档案", "学员档案",
    [table("archiveTable", "学员档案", "nb_dx_student",
           ["name", "gender", "political_status", "phone", "work_unit", "klass.name", "status", "excellent"],
           ["view"])],
    {"nb_dx_student": DEF_STUDENT, "nb_dx_class": DEF_CLASS},
)

pages["page5-training-record"] = page(
    GROUP_STU, "培训记录", "HistoryOutlined", "培训记录", "培训记录",
    [
        {"key": "trainBar", "type": "chart", "title": "各班次学员数", "chart": "stuByClass"},
        table("trainTable", "参训记录", "nb_dx_student",
              ["name", "klass.name", "status", "enroll_status", "excellent"],
              ["view"]),
    ],
    {"nb_dx_student": DEF_STUDENT, "nb_dx_class": DEF_CLASS},
    assets={"charts": {"stuByClass": chart("nb_dx_student", "klass.name", "stuCount", ctype="bar")}},
)

# ---------- 综合门户 3 页 ----------
pages["page6-portal-home"] = page(
    GROUP_PORTAL, "综合门户", "HomeOutlined", "综合门户", "综合门户",
    [
        {"key": "portalBar", "type": "chart", "title": "各班次学员数", "chart": "stuByClassHome"},
        {"key": "portalPie", "type": "chart", "title": "请假状态分布", "chart": "leaveByStatus"},
        table("annTable", "通知公告", "nb_dx_announcement",
              ["title", "kind", "publisher.nickname", "published_at", "top"],
              ["view"]),
    ],
    {"nb_dx_student": DEF_STUDENT, "nb_dx_class": DEF_CLASS,
     "nb_dx_announcement": DEF_ANN},
    assets={"charts": {
        "stuByClassHome": chart("nb_dx_student", "klass.name", "stuCount", ctype="bar"),
        "leaveByStatus": chart("nb_dx_leave", "status", "leaveCount"),
    }},
)

pages["page7-class-home"] = page(
    GROUP_PORTAL, "班级主页", "BookOutlined", "班级主页", "班级主页",
    [table("classTable", "班次列表", "nb_dx_class",
           ["name", "code", "category", "status", "start_date", "end_date", "organizer.nickname"],
           ["view"])],
    {"nb_dx_class": DEF_CLASS, "nb_dx_student": DEF_STUDENT},
)

pages["page8-student-home"] = page(
    GROUP_PORTAL, "学员主页", "UserOutlined", "学员主页", "学员主页",
    [table("homeTable", "我的信息", "nb_dx_student",
           ["photo", "name", "klass.name", "duty", "status", "excellent"],
           ["view"])],
    {"nb_dx_student": DEF_STUDENT, "nb_dx_class": DEF_CLASS},
)

for name, d in pages.items():
    path = os.path.join(OUT, f"{name}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
    print("written", path)
