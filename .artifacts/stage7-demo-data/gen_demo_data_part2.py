#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""续跑：declaration 起的剩余部分（依赖 id 从库里查回）"""
import json, os, urllib.request, urllib.parse, urllib.error

CONF = os.path.expanduser("~/.nocobase/config.json")
env = json.load(open(CONF))["envs"]["dx-demo"]
TOKEN = env["auth"]["accessToken"]
BASE = "http://127.0.0.1:13000"

def _call(url, method="GET", body=None):
    req = urllib.request.Request(url, method=method,
        headers={"Authorization": f"Bearer {TOKEN}", "X-Authenticator": "basic",
                 "Content-Type": "application/json"})
    data = json.dumps(body).encode() if body is not None else None
    try:
        with urllib.request.urlopen(req, data) as r:
            out = json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"{method} {url} -> HTTP {e.code}: {e.read().decode()[:500]}")
    if out.get("errors"):
        raise RuntimeError(f"{method} {url} -> {out['errors']}")
    return out.get("data")

def create(res, body):
    d = _call(f"{BASE}/api/{res}:create", "POST", body)
    return d["id"] if isinstance(d, dict) else d

def one(res, flt):
    q = urllib.parse.quote(json.dumps(flt))
    d = _call(f"{BASE}/api/{res}?filter={q}&pageSize=1")
    if not d:
        raise RuntimeError(f"{res} 查不到 {flt}")
    return d[0]

# ---- 依赖 id ----
STD_NAMES = ["张明远", "王丽娟", "李勇强", "陈晓红", "刘志远", "杨帆", "周静", "吴建军",
             "郑雪梅", "冯国华", "许文博", "何雨欣", "罗天成", "高婷婷", "孙浩然", "马俊杰"]
topic_ids = {}
for t in _call(f"{BASE}/api/nb_dx_topic?pageSize=100"):
    topic_ids[t["name"]] = t["id"]
class2 = one("nb_dx_class", {"code": "ZT2602"})["id"]
class4 = one("nb_dx_class", {"code": "JX2503"})["id"]
R1 = "第一报告厅"

sched_t4 = one("nb_dx_course_schedule", {"class_id": 1, "topic_id": topic_ids["习近平新时代中国特色社会主义思想概论"], "week_no": 1, "day_of_week": 1})["id"]
sched_t1 = one("nb_dx_course_schedule", {"class_id": 1, "topic_id": topic_ids["党性教育专题"], "week_no": 1, "day_of_week": 1})["id"]
sched_t2 = one("nb_dx_course_schedule", {"class_id": 1, "topic_id": topic_ids["乡村振兴政策解读"], "week_no": 1, "day_of_week": 2})["id"]
scheme_topic = one("nb_dx_eval_scheme", {"kind": "topic"})["id"]
scheme_comp = one("nb_dx_eval_scheme", {"kind": "comprehensive"})["id"]
scheme_party = one("nb_dx_eval_scheme", {"kind": "party"})["id"]

# ---- 打卡 ----
create("nb_dx_declaration", dict(student_name="张明远", student_id=1, class_id=1, type="daily",
    content="本人今日无发热等症状，健康打卡（健康码绿码，无中高风险区旅居史）", date="2026-01-05"))
create("nb_dx_declaration", dict(student_name="王丽娟", student_id=2, class_id=1, type="daily",
    content="健康打卡（健康码绿码）", date="2026-01-05"))
create("nb_dx_declaration", dict(student_name="李勇强", student_id=3, class_id=1, type="trip",
    content="周末返黔途中经长沙转车，已报备（健康码绿码，48小时核酸阴性）", date="2026-01-05"))
create("nb_dx_commitment", dict(title="学员廉洁自律承诺书", class_id=1, student_id=1,
    content="本人承诺在培训期间严守校规校纪，廉洁自律……", signed=True, signed_at="2026-01-05 09:10:00"))
create("nb_dx_material", dict(question="结业论文格式模板哪里下载？", student_id=3, class_id=1,
    kind="bring", content="请问教务处", status="submitted"))
create("nb_dx_material", dict(question="请假条纸质版交到哪里？", student_id=2, class_id=1,
    kind="leave", content="已在线提交请假申请", reply="线上审批即可，无需交纸质版。", reply_by_id=3,
    status="replied"))
print("✓ 打卡 3 / 承诺书 1 / 材料表 2")

# ---- 考勤 ----
att_stat = {1: "normal", 2: "normal", 3: "late", 4: "normal", 5: "normal", 6: "goout",
            7: "normal", 8: "leave", 9: "normal", 10: "normal", 11: "absent", 12: "normal",
            13: "normal", 14: "normal", 15: "late", 16: "absent"}
for scid, tno in [(sched_t4, topic_ids["习近平新时代中国特色社会主义思想概论"]), (sched_t1, topic_ids["党性教育专题"])]:
    for sid_, stt in att_stat.items():
        create("nb_dx_attendance", dict(student_name=STD_NAMES[sid_ - 1], student_id=sid_, class_id=1,
            schedule_id=scid, topic_id=tno, date="2026-01-05",
            status="normal" if scid == sched_t4 else stt,
            checkin_time=f"2026-01-05 08:2{sid_ % 10}:00", location=R1,
            method="mobile" if sid_ % 3 else "rollcall"))
print("✓ 考勤 32 条")

# ---- 评估 ----
scores = [92, 88, 95, 78, 84, 90, 86, 93, 81, 89]
tno_names = [4, 4, 2, 2, 12, 12, 4, 2, 12, 4]
tn_map = {4: "习近平新时代中国特色社会主义思想概论", 2: "乡村振兴政策解读", 12: "党风廉政建设专题"}
for i, sc in enumerate(scores):
    sid_ = i + 1
    tno = tno_names[i]
    create("nb_dx_eval_record", dict(student_name=STD_NAMES[i], student_id=sid_, class_id=1,
        scheme_id=scheme_topic,
        schedule_id=sched_t4 if tno == 4 else (sched_t2 if tno == 2 else None),
        topic_id=topic_ids[tn_map[tno]], kind="topic", score=sc,
        items_json=json.dumps({"政治立场": 95, "内容深度": sc, "案例质量": 90, "讲授表达": 88, "课堂互动": 92},
            ensure_ascii=False),
        opinion="课程内容充实，建议增加案例互动。", anonymous=True))
grades = [5, 4, 5, 4, 5, 3, 4, 5]
for i, g in enumerate(grades):
    create("nb_dx_eval_record", dict(student_name=STD_NAMES[i], student_id=i + 1, class_id=1,
        scheme_id=scheme_comp, kind="comprehensive", score=g,
        items_json=json.dumps({"理论学习": g, "党性修养": 5, "能力提升": 4, "作风表现": 5}, ensure_ascii=False),
        opinion="综合表现良好。", anonymous=True))
for i in range(8):
    create("nb_dx_eval_record", dict(student_name=STD_NAMES[i], student_id=i + 1, class_id=1,
        scheme_id=scheme_party, kind="party_self", score=85 + i,
        items_json=json.dumps({"理想信念": 90, "宗旨意识": 88, "纪律作风": 85, "学习态度": 92}, ensure_ascii=False),
        opinion="自我剖析：理论学习还需深入。", anonymous=False))
for i in range(4):
    create("nb_dx_eval_record", dict(student_name=STD_NAMES[i], student_id=i + 1, class_id=1,
        scheme_id=scheme_party, kind="party_review", score=80 + i * 3,
        items_json=json.dumps({"理想信念": 85, "宗旨意识": 82, "纪律作风": 80, "学习态度": 88}, ensure_ascii=False),
        opinion="支部考核意见：合格。", anonymous=False))
print("✓ 评估记录 30 条")

# ---- 投票 / 问卷 ----
vote1 = create("nb_dx_vote", dict(name="第1期中青班优秀学员评选", class_id=1,
    question="请从以下学员中评选你心中的优秀学员（单选）",
    options_text="张明远,王丽娟,李勇强,陈晓红,周静",
    kind="single", scope="class", status="open", end_time="2026-01-20 17:00:00", creator_id=3))
votes = [("张明远", 1), ("张明远", 2), ("王丽娟", 3), ("王丽娟", 4), ("李勇强", 5), ("张明远", 6),
         ("陈晓红", 7), ("周静", 8), ("王丽娟", 9), ("李勇强", 10), ("张明远", 11), ("周静", 12)]
for opt, vid in votes:
    create("nb_dx_vote_record", dict(option_selected=opt, vote_id=vote1, voter_id=vid,
        voted_at="2026-01-06 12:00:00"))
print("✓ 投票 1 个 + 票 12 张")

sv = create("nb_dx_survey", dict(name="第1期中青班教学质量不记名问卷", class_id=1,
    description="本问卷匿名填写，用于改进教学工作", kind="mixed", limit_per_day=1,
    status="open", end_time="2026-01-18 17:00:00", creator_id=3))
ans = [{"course": "A", "teacher": "B", "advice": "希望增加现场教学比重"},
       {"course": "A", "teacher": "A", "advice": "整体很好"},
       {"course": "B", "teacher": "A", "advice": "自习时间可以再多一点"},
       {"course": "B", "teacher": "C", "advice": "建议开设更多选修课"},
       {"course": "A", "teacher": "B", "advice": "无"},
       {"course": "C", "teacher": "A", "advice": "课程节奏稍快"},
       {"course": "A", "teacher": "A", "advice": "非常满意"},
       {"course": "B", "teacher": "B", "advice": "希望组织跨班交流"}]
for i, a in enumerate(ans, 1):
    create("nb_dx_survey_answer", dict(answers_text=json.dumps(a, ensure_ascii=False),
        survey_id=sv, answers_json=json.dumps(a, ensure_ascii=False),
        device_tag=f"ANON-{i:03d}", submitted_at=f"2026-01-06 1{i}:00:00"))
print("✓ 问卷 1 个 + 匿名答卷 8 份")

# ---- 报名 / 缴费 ----
s17 = one("nb_dx_student", {"student_no": "ZT2602-01"})["id"]
s18 = one("nb_dx_student", {"student_no": "ZT2602-02"})["id"]
for nm, ph, g, unit in [("林芳", "13808540001", "female", "安顺市农业农村局 副局长"),
                        ("杜文韬", "13808540002", "male", "贵阳市乌当区 政法委副书记"),
                        ("苟小明", "13808540003", "male", "毕节市纳雍县 副县长"),
                        ("梅婷", "13808540004", "female", "黔南州龙里县 教育局副局长")]:
    create("nb_dx_registration", dict(name=nm, class_id=class2, phone=ph, gender=g,
        political_status="cpc", work_unit=unit, status="pending"))
for nm, sid_, ph in [("谢明轩", s17, "13808520001"), ("蒋雨桐", s18, "13808520002")]:
    create("nb_dx_registration", dict(name=nm, class_id=class2, phone=ph,
        gender="male" if sid_ == s17 else "female", political_status="cpc",
        work_unit="见学员档案", status="approved", review_by_id=4, review_remark="符合报名条件",
        student_id=sid_))
create("nb_dx_payment", dict(payer_name="谢明轩", student_id=s17, class_id=class2, amount=600.0,
    method="personal", channel="qrcode", status="approved", review_by_id=4,
    review_remark="已到账核对", date="2026-11-15"))
create("nb_dx_payment", dict(payer_name="蒋雨桐", student_id=s18, class_id=class2, amount=600.0,
    method="personal", channel="voucher", status="pending", date="2026-11-16"))
create("nb_dx_payment", dict(payer_name="林芳", class_id=class2, amount=600.0,
    method="unit", channel="offline", status="pending", date="2026-11-16"))
create("nb_dx_payment", dict(payer_name="唐建国", class_id=class4, amount=1200.0,
    method="unit", channel="offline", status="approved", review_by_id=4, review_remark="历史记录",
    date="2025-08-20"))
print("✓ 报名 6 条 + 缴费 4 条")

# ---- 作业 ----
asg = create("nb_dx_assignment", dict(name="党性分析材料撰写", class_id=1, topic_id=topic_ids["党性教育专题"],
    teacher_id=5, requirement="结合学习体会撰写个人党性分析材料，不少于2000字",
    due_date="2026-01-15", review_mode="teacher", status="assigned"))
create("nb_dx_submission", dict(student_name="张明远", assignment_id=asg, student_id=1,
    content="通过第一周学习，深刻认识到……（正文略）", submitted_at="2026-01-07 20:00:00", status="submitted"))
create("nb_dx_submission", dict(student_name="王丽娟", assignment_id=asg, student_id=2,
    content="对照党章找差距，本人存在……（正文略）", submitted_at="2026-01-07 21:30:00", status="submitted"))
create("nb_dx_submission", dict(student_name="李勇强", assignment_id=asg, student_id=3,
    content="党性分析：一、存在问题……（正文略）", submitted_at="2026-01-08 09:00:00",
    score=92, review="剖析深刻，整改措施具体", reviewer_id=5, status="reviewed"))
print("✓ 作业 1 个 + 提交 3 份")
print("\n续跑完成 ✅")
