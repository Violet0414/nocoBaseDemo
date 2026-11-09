#!/usr/bin/env python3
# 生成阶段3 教学评估+投票问卷+统计图表 6 页蓝本
import json, os

OUT = os.path.dirname(os.path.abspath(__file__))

BASE_DEFAULTS = {
    "nb_dx_student": {
        "popups": {"view": {"name": "查看学员", "description": "查看一条学员详情"},
                   "addNew": {"name": "新增学员", "description": "新增一条学员记录"},
                   "edit": {"name": "编辑学员", "description": "编辑一条学员记录"}},
        "fieldGroups": [
            {"key": "stuBasic", "title": "基本信息", "fields": ["name", "student_no", "gender", "birth_date", "political_status", "phone", "photo"]},
            {"key": "stuWork", "title": "单位与分工", "fields": ["work_unit", "duty", "group_no"]},
            {"key": "stuStatus", "title": "学籍与状态", "fields": ["status", "enroll_status", "remark", "klass", "user"]},
        ],
    },
    "nb_dx_class": {
        "popups": {"view": {"name": "查看班次", "description": "查看一条班次详情"},
                   "addNew": {"name": "新增班次", "description": "新增一条班次记录"},
                   "edit": {"name": "编辑班次", "description": "编辑一条班次记录"}},
        "fieldGroups": [
            {"key": "classBasic", "title": "基本信息", "fields": ["name", "code", "category", "train_type", "status", "organizer"]},
            {"key": "classPeriod", "title": "报名与学习周期", "fields": ["enroll_start", "enroll_end", "start_date", "end_date", "total_days", "total_hours"]},
            {"key": "classOther", "title": "教室与其他", "fields": ["default_room", "room_locked", "qr_token", "description"]},
        ],
    },
    "nb_dx_topic": {
        "popups": {"view": {"name": "查看专题", "description": "查看一条教学专题详情"},
                   "addNew": {"name": "新增专题", "description": "新增一条教学专题记录"},
                   "edit": {"name": "编辑专题", "description": "编辑一条教学专题记录"}},
        "fieldGroups": [
            {"key": "topicBasic", "title": "专题信息", "fields": ["name", "category", "attribute", "teach_form", "hours", "status"]},
            {"key": "topicOther", "title": "主讲与说明", "fields": ["teacher", "eval_scheme", "description", "remark"]},
        ],
    },
    "nb_dx_course_schedule": {
        "popups": {"view": {"name": "查看排课", "description": "查看一条排课记录详情"},
                   "addNew": {"name": "新增排课", "description": "新增一条排课记录"},
                   "edit": {"name": "编辑排课", "description": "编辑一条排课记录"}},
        "fieldGroups": [
            {"key": "csBasic", "title": "课程安排", "fields": ["topic_name", "kind", "week_no", "day_of_week", "start_time", "end_time", "place", "status"]},
            {"key": "csRelate", "title": "关联对象", "fields": ["klass", "topic", "activity", "teacher"]},
            {"key": "csOther", "title": "其他设置", "fields": ["merged", "unit_name", "eval_enabled"]},
        ],
    },
    "users": {
        "popups": {"view": {"name": "查看用户", "description": "查看一条用户详情"},
                   "addNew": {"name": "新增用户", "description": "新增一条用户记录"},
                   "edit": {"name": "编辑用户", "description": "编辑一条用户记录"}},
    },
    "nb_dx_eval_scheme": {
        "popups": {"view": {"name": "查看评估方案", "description": "查看一条评估方案详情"},
                   "addNew": {"name": "新增评估方案", "description": "新增一条评估方案记录"},
                   "edit": {"name": "编辑评估方案", "description": "编辑一条评估方案记录"}},
        "fieldGroups": [
            {"key": "esBasic", "title": "方案信息", "fields": ["name", "kind", "method", "merged_eval"]},
            {"key": "esRule", "title": "评分规则", "fields": ["min_score", "max_score", "items_text", "remark"]},
        ],
    },
    "nb_dx_eval_record": {
        "popups": {"view": {"name": "查看评估记录", "description": "查看一条评估记录详情"},
                   "addNew": {"name": "新增评估记录", "description": "新增一条评估记录"},
                   "edit": {"name": "编辑评估记录", "description": "编辑一条评估记录"}},
    },
    "nb_dx_vote": {
        "popups": {"view": {"name": "查看投票", "description": "查看一条投票详情"},
                   "addNew": {"name": "新增投票", "description": "新增一条投票记录"},
                   "edit": {"name": "编辑投票", "description": "编辑一条投票记录"}},
        "fieldGroups": [
            {"key": "voteBasic", "title": "投票信息", "fields": ["name", "kind", "scope", "status", "end_time"]},
            {"key": "voteContent", "title": "问题与选项", "fields": ["question", "options_text"]},
            {"key": "voteRelate", "title": "关联对象", "fields": ["klass", "creator"]},
        ],
    },
    "nb_dx_vote_record": {
        "popups": {"view": {"name": "查看投票明细", "description": "查看一条投票明细详情"},
                   "addNew": {"name": "新增投票明细", "description": "新增一条投票明细记录"},
                   "edit": {"name": "编辑投票明细", "description": "编辑一条投票明细记录"}},
        "fieldGroups": [
            {"key": "vrAll", "title": "投票明细", "fields": ["vote", "option_selected", "voter", "score_value", "voted_at"]},
        ],
    },
    "nb_dx_survey": {
        "popups": {"view": {"name": "查看问卷", "description": "查看一条问卷详情"},
                   "addNew": {"name": "新增问卷", "description": "新增一条问卷记录"},
                   "edit": {"name": "编辑问卷", "description": "编辑一条问卷记录"}},
        "fieldGroups": [
            {"key": "svBasic", "title": "问卷信息", "fields": ["name", "kind", "status", "end_time", "limit_per_day"]},
            {"key": "svContent", "title": "问卷内容", "fields": ["description"]},
            {"key": "svRelate", "title": "关联对象", "fields": ["klass", "creator"]},
        ],
    },
    "nb_dx_survey_answer": {
        "popups": {"view": {"name": "查看答卷", "description": "查看一条答卷详情"},
                   "addNew": {"name": "新增答卷", "description": "新增一条答卷记录"},
                   "edit": {"name": "编辑答卷", "description": "编辑一条答卷记录"}},
    },
}

GROUP = {"title": "教学评估", "icon": "FileDoneOutlined"}

# survey_answer 带描述字段（简化存储说明），需声明 Description Review 出口
SURVEY_ANSWER_DEFAULTS = {
    "nb_dx_survey_answer": dict(
        BASE_DEFAULTS["nb_dx_survey_answer"],
        formBehaviorDescriptionReview={
            "fields": {
                "answers_json": {"decision": "unsupported", "reasonCode": "ambiguous-description"},
                "device_tag": {"decision": "unsupported", "reasonCode": "ambiguous-description"},
            }
        },
    ),
}


def table(key, title, coll, fields, data_scope=None, actions=("view", "edit", "delete")):
    blk = {"key": key, "type": "table", "title": title, "collection": coll,
           "fields": fields, "recordActions": list(actions)}
    if data_scope:
        blk["settings"] = {"dataScope": {"filter": data_scope}}
    return blk


def page(fname, item_title, item_icon, tabs, charts=None, defaults_extra=None):
    d = {
        "version": "1", "mode": "create",
        "navigation": {"layoutUid": "admin-layout-model",
                       "group": dict(GROUP),
                       "item": {"title": item_title, "icon": item_icon}},
        "page": {"title": item_title},
        "tabs": tabs,
    }
    if charts:
        d["assets"] = {"charts": charts}
    cols = dict(BASE_DEFAULTS)
    if defaults_extra:
        cols.update(defaults_extra)
    d["defaults"] = {"collections": cols}
    with open(os.path.join(OUT, fname), "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    print("wrote", fname)


# 页1 评估方案
page("page1-eval-scheme.json", "评估方案", "FileDoneOutlined",
     [{"key": "main", "title": "评估方案",
       "blocks": [table("esTable", "评估方案", "nb_dx_eval_scheme",
                        ["name", "kind", "method", "min_score", "max_score", "merged_eval", "items_text", "remark"])],
       "layout": {"rows": [[{"key": "esTable", "span": 24}]]}}])

# 页2 专题评估
page("page2-topic-eval.json", "专题评估", "StarOutlined",
     [{"key": "main", "title": "专题评估",
       "blocks": [table("topicEvalTable", "专题评估记录", "nb_dx_eval_record",
                        ["student_name", "klass.name", "scheme.name", "topic.name", "schedule.topic_name", "kind", "score", "items_json", "opinion", "anonymous"],
                        data_scope={"logic": "$and", "items": [{"path": "kind", "operator": "$eq", "value": "topic"}]})],
       "layout": {"rows": [[{"key": "topicEvalTable", "span": 24}]]}}])

# 页3 综合评估
page("page3-comprehensive-eval.json", "综合评估", "TrophyOutlined",
     [{"key": "main", "title": "综合评估",
       "blocks": [table("compEvalTable", "综合评估记录", "nb_dx_eval_record",
                        ["student_name", "klass.name", "scheme.name", "kind", "score", "items_json", "opinion", "anonymous"],
                        data_scope={"logic": "$and", "items": [{"path": "kind", "operator": "$eq", "value": "comprehensive"}]})],
       "layout": {"rows": [[{"key": "compEvalTable", "span": 24}]]}}])

# 页4 投票管理（vote 单表；投票明细不在此页，organizer 无 vote_record 权限）
page("page4-vote.json", "投票管理", "CheckSquareOutlined",
     [{"key": "main", "title": "投票管理",
       "blocks": [table("voteTable", "投票列表", "nb_dx_vote",
                        ["name", "klass.name", "question", "kind", "scope", "status", "end_time", "creator.nickname"])],
       "layout": {"rows": [[{"key": "voteTable", "span": 24}]]}}])

# 页5 不记名问卷（survey + survey_answer 双 tab）
page("page5-survey.json", "不记名问卷", "FormOutlined",
     defaults_extra=SURVEY_ANSWER_DEFAULTS,
     tabs=
     [{"key": "main", "title": "问卷列表",
       "blocks": [table("surveyTable", "问卷列表", "nb_dx_survey",
                        ["name", "klass.name", "kind", "status", "end_time", "limit_per_day", "creator.nickname"])],
       "layout": {"rows": [[{"key": "surveyTable", "span": 24}]]}},
      {"key": "answers", "title": "答卷明细",
       "blocks": [table("surveyAnswerTable", "答卷明细", "nb_dx_survey_answer",
                        ["survey.name", "answers_text", "answers_json", "device_tag", "submitted_at"])],
       "layout": {"rows": [[{"key": "surveyAnswerTable", "span": 24}]]}}])

# 页6 统计图表（4 chart）
CHARTS = {
    "evalAvgByKind": {
        "query": {"mode": "builder",
                  "resource": {"dataSourceKey": "main", "collectionName": "nb_dx_eval_record"},
                  "measures": [{"field": "score", "aggregation": "avg", "alias": "avgScore"}],
                  "dimensions": [{"field": "kind"}]},
        "visual": {"mode": "basic", "type": "bar", "mappings": {"x": "kind", "y": "avgScore"}},
    },
    "evalCountByKind": {
        "query": {"mode": "builder",
                  "resource": {"dataSourceKey": "main", "collectionName": "nb_dx_eval_record"},
                  "measures": [{"field": "id", "aggregation": "count", "alias": "evalCount"}],
                  "dimensions": [{"field": "kind"}]},
        "visual": {"mode": "basic", "type": "pie", "mappings": {"category": "kind", "value": "evalCount"}},
    },
    "voteCountByOption": {
        "query": {"mode": "builder",
                  "resource": {"dataSourceKey": "main", "collectionName": "nb_dx_vote_record"},
                  "measures": [{"field": "id", "aggregation": "count", "alias": "voteCount"}],
                  "dimensions": [{"field": "option_selected"}]},
        "visual": {"mode": "basic", "type": "bar", "mappings": {"x": "option_selected", "y": "voteCount"}},
    },
    "surveyAnswerCount": {
        "query": {"mode": "builder",
                  "resource": {"dataSourceKey": "main", "collectionName": "nb_dx_survey_answer"},
                  "measures": [{"field": "id", "aggregation": "count", "alias": "answerCount"}],
                  "dimensions": [{"field": "survey.name"}]},
        "visual": {"mode": "basic", "type": "bar", "mappings": {"x": "survey.name", "y": "answerCount"}},
    },
}
page("page6-statistics.json", "统计图表", "PieChartOutlined",
     [{"key": "main", "title": "统计图表",
       "blocks": [
           {"key": "avgChart", "type": "chart", "title": "评估类型平均分", "chart": "evalAvgByKind"},
           {"key": "evalPie", "type": "chart", "title": "评估记录分布", "chart": "evalCountByKind"},
           {"key": "voteChart", "type": "chart", "title": "投票选项分布", "chart": "voteCountByOption"},
           {"key": "surveyChart", "type": "chart", "title": "各问卷答卷数", "chart": "surveyAnswerCount"},
       ],
       "layout": {"rows": [[{"key": "avgChart", "span": 12}, {"key": "evalPie", "span": 12}],
                           [{"key": "voteChart", "span": 12}, {"key": "surveyChart", "span": 12}]]}}],
     charts=CHARTS)

print("done")
