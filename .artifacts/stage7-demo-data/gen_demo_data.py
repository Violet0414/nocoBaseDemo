#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""阶段7 全套演示数据生成（幂等保护：teacher/seat/textbook 非空即退出）"""
import json, os, sys, urllib.request, urllib.error, datetime

CONF = os.path.expanduser("~/.nocobase/config.json")
cfg = json.load(open(CONF))
env = cfg["envs"]["dx-demo"]
TOKEN = env["auth"]["accessToken"]
BASE = (env.get("baseUrl") or "http://127.0.0.1:13000").rstrip("/")

def _call(url, method, body=None):
    req = urllib.request.Request(url, method=method,
        headers={"Authorization": f"Bearer {TOKEN}", "X-Authenticator": "basic",
                 "Content-Type": "application/json", "X-Locale": "zh-CN"})
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

def upd(res, rid, body):
    return _call(f"{BASE}/api/{res}:update?filterByTk={rid}", "POST", body)

def count(res):
    return len(_call(f"{BASE}/api/{res}?pageSize=1", "GET"))

# ---------- 幂等保护 ----------
for r in ["nb_dx_teacher", "nb_dx_seat", "nb_dx_textbook"]:
    if count(r) > 0:
        sys.exit(f"已存在演示数据（{r} 非空），如需重灌请先恢复备份")

SLOTS = [("08:30", "10:10"), ("10:30", "12:10"), ("14:00", "15:40"), ("16:00", "17:40"), ("19:00", "20:40")]

def slot_dt(day, si):
    d0 = datetime.date(2026, 1, 4) + datetime.timedelta(days=day - 1)
    s, e = SLOTS[si]
    return f"{d0.isoformat()} {s}:00", f"{d0.isoformat()} {e}:00"

# ========== 1. 补全现有班1 / 学员1-3 ==========
upd("nb_dx_class", 1, {
    "code": "ZQ2601", "category": "youth", "train_type": "fulltime", "status": "ongoing",
    "enroll_start": "2025-11-01", "enroll_end": "2025-12-20",
    "start_date": "2026-01-05", "end_date": "2026-02-06",
    "total_days": 21, "total_hours": 240, "organizer_id": 3,
    "default_room": "第一报告厅", "room_locked": True, "qr_token": "ZQ2601-REG",
    "description": "第1期中青年干部培训班，学制21天，全脱产培训。"})
print("✓ 班1 补全")

upd("nb_dx_student", 1, dict(name="张明远", student_no="ZQ2601-01", gender="male", birth_date="1979-03-12",
    political_status="cpc", phone="13808510001", work_unit="贵阳市云岩区委组织部 副部长",
    duty="leader", group_no=1, status="active", enroll_status="yes", user_id=6))
upd("nb_dx_student", 2, dict(name="王丽娟", student_no="ZQ2601-02", gender="female", birth_date="1982-07-05",
    political_status="cpc", phone="13808510002", work_unit="遵义市汇川区教育局 副局长",
    duty="deputy", group_no=1, status="active", enroll_status="yes"))
upd("nb_dx_student", 3, dict(name="李勇强", student_no="ZQ2601-03", gender="male", birth_date="1980-11-23",
    political_status="cpc", phone="13808510003", work_unit="安顺市平坝区政府办 主任",
    duty="study", group_no=2, status="active", enroll_status="yes"))
print("✓ 学员1-3 改真名（学员1 绑定 student_test 账号）")

# ========== 2. 师资 ==========
teachers = [
    ("王振华", "male", "中共贵州省委党校", "教授", "马克思主义理论", 0, 0),
    ("李慧敏", "female", "中共贵州省委党校", "副教授", "党的建设", 0, 0),
    ("张国栋", "male", "贵州大学", "教授", "区域经济学", 0, 1),
    ("刘燕", "female", "中共贵州省委党校", "副教授", "宪法与行政法", 0, 0),
    ("陈立", "male", "贵州省委组织部", "副部长", "干部能力建设", 1, 0),
    ("赵秀英", "female", "中共贵州省委党校", "教授", "公共管理", 0, 0),
    ("周涛", "male", "贵州财经大学", "副教授", "乡村振兴", 0, 1),
    ("吴明远", "male", "中共贵州省委党校", "讲师", "党性教育", 0, 0),
]
tids = {}
for i, (n, g, u, t, ra, il, ie) in enumerate(teachers, 1):
    tids[i] = create("nb_dx_teacher", dict(name=n, gender=g, unit=u, title=t, political_status="cpc",
        research_area=ra, is_leader=bool(il), is_external=bool(ie),
        phone=f"1390851{i:04d}", email=f"teacher{i}@gzdx.cn"))
print("✓ 师资 8 人:", tids)

# ========== 3. 评估方案 ==========
scheme_topic = create("nb_dx_eval_scheme", dict(name="专题课教学质量评估", kind="topic", method="score",
    items_text="政治立场,内容深度,案例质量,讲授表达,课堂互动", min_score=60, max_score=100))
scheme_comp = create("nb_dx_eval_scheme", dict(name="综合评估（结业）", kind="comprehensive", method="grade",
    items_text="理论学习,党性修养,能力提升,作风表现", min_score=1, max_score=5))
scheme_party = create("nb_dx_eval_scheme", dict(name="党性考核", kind="party", method="mixed",
    items_text="理想信念,宗旨意识,纪律作风,学习态度", min_score=60, max_score=100))
print("✓ 评估方案 3 条")

# ========== 4. 专题 ==========
topics = [
    (1, "党性教育专题", "spirit", "required", "lecture", 8, 2, "scheduled"),
    (2, "乡村振兴政策解读", "theory", "required", "lecture", 6, 7, "scheduled"),
    (3, "现场教学：案例研讨", "field", "required", "field", 4, 8, "scheduled"),
    (4, "习近平新时代中国特色社会主义思想概论", "theory", "required", "lecture", 12, 1, "excellent"),
    (5, "党章党规党纪教育", "spirit", "required", "lecture", 4, 8, "scheduled"),
    (6, "新质生产力与贵州高质量发展", "ability", "elective", "lecture", 6, 3, "scheduled"),
    (7, "依法行政与法治思维", "ability", "elective", "lecture", 4, 4, "scheduled"),
    (8, "领导干部压力管理与心理调适", "ability", "elective", "seminar", 3, 6, "approved"),
    (9, "红色遵义现场教学", "field", "elective", "field", 6, 8, "approved"),
    (10, "基层治理现代化", "theory", "required", "lecture", 6, 6, "scheduled"),
    (11, "数字经济与产业转型", "ability", "elective", "lecture", 6, 3, "approved"),
    (12, "党风廉政建设专题", "spirit", "required", "lecture", 4, 5, "scheduled"),
]
for tid, name, cat, attr, form, hours, t, st in topics:
    body = dict(name=name, category=cat, attribute=attr, teach_form=form, hours=hours,
        teacher_id=tids[t], status=st, eval_scheme_id=scheme_topic,
        description=f"{name}（{hours}学时，主讲：{teachers[t-1][0]}）")
    if tid <= 3:
        upd("nb_dx_topic", tid, body)
    else:
        create("nb_dx_topic", body)
print("✓ 专题 12 个")

# ========== 5. 活动 / 基地 / 拟开发专题 / 案例 / 校外宣讲 ==========
a1 = create("nb_dx_activity", dict(name="党性分析交流会", category="partyday", hours=3, place="第一讨论室", description="对照党章找差距"))
a2 = create("nb_dx_activity", dict(name="主题党日活动", category="partyday", hours=3, place="党性教育基地"))
a3 = create("nb_dx_activity", dict(name="素质拓展训练", category="military", hours=4, place="训练基地"))
a4 = create("nb_dx_activity", dict(name="学员文艺晚会", category="culture", hours=3, place="大礼堂"))
create("nb_dx_activity", dict(name="分组研讨：乡村振兴路径", category="practice", hours=3, place="第二讨论室"))
print("✓ 教学活动 5 项")

for n, c, addr in [("遵义会议纪念馆", "red", "遵义市红花岗区子尹路96号"),
                   ("塘约村（农村改革示范村）", "rural", "安顺市平坝区乐平镇"),
                   ("贵州国家大数据综合试验区展示中心", "economy", "贵阳市观山湖区"),
                   ("贵州省文化馆", "culture", "贵阳市云岩区北京路"),
                   ("廉政警示教育基地", "other", "贵阳市南明区")]:
    create("nb_dx_base", dict(name=n, category=c, address=addr, contact="基地联络办",
        phone="0851-80000000", description="现场教学合作基地"))
print("✓ 现场教学基地 5 个")

for n, dep, st, td in [("《习近平经济思想在贵州的实践》课程包", "经济学教研部", "developing", "2026-06-30"),
                       ("案例课程：息烽集中营革命精神", "党史教研部", "done", "2026-03-31"),
                       ("现场教学点：花江峡谷大桥（超级工程）", "公共管理教研部", "developing", "2026-09-30"),
                       ("微党课系列：一分钟党史", "党史教研部", "paused", "2026-12-31")]:
    create("nb_dx_planned_topic", dict(name=n, department=dep, proposer_id=4, target_date=td,
        status=st, description="拟开发专题"))
print("✓ 拟开发专题 4 个")

for n, c, src, y in [("新时代“枫桥经验”的贵州实践", "基层治理", "省委组织部", 2025),
                     ("脱贫攻坚与乡村振兴有效衔接案例", "乡村振兴", "省农业农村厅", 2024),
                     ("基层党建“双联双促”工作机制", "基层党建", "本校党建教研部", 2025),
                     ("大数据赋能政府治理现代化", "数字经济", "贵阳市大数据局", 2023)]:
    create("nb_dx_teaching_case", dict(name=n, category=c, source=src, year=y, content="教学案例库"))
print("✓ 教学案例 4 个")

for n, ln, t, d, place, aud, cnt in [("市（州）委党校开学典礼讲话", "陈立", 5, "2025-12-15", "省委党校大礼堂", "全市党校系统", 260),
                                     ("学习贯彻党的二十届四中全会精神宣讲", "王振华", 1, "2025-11-20", "贵阳市南明区", "区直机关干部", 180),
                                     ("乡村振兴政策形势报告", "周涛", 7, "2025-12-02", "毕节市", "县乡干部", 320)]:
    create("nb_dx_external_lecture", dict(name=n, lecturer_name=ln, teacher_id=tids[t], date=d,
        place=place, audience=aud, audience_count=cnt, description="校外宣讲记录"))
print("✓ 校外宣讲 3 场")

# ========== 6. 新班次 2/3/4 ==========
class2 = create("nb_dx_class", dict(name="2026年乡村振兴专题培训班", code="ZT2602", category="special",
    train_type="onjob", status="enrollable", enroll_start="2026-11-10", enroll_end="2026-11-30",
    start_date="2026-12-01", end_date="2026-12-05", total_days=5, total_hours=30,
    organizer_id=3, default_room="第二教室", qr_token="ZT2602-REG",
    description="专题培训班，扫码报名，学制5天。"))
class3 = create("nb_dx_class", dict(name="第2期中青班", code="ZQ2701", category="youth",
    train_type="fulltime", status="planned", start_date="2027-03-01", end_date="2027-04-10",
    total_days=30, total_hours=360, organizer_id=3, default_room="第一报告厅",
    description="计划班次，待招生。"))
class4 = create("nb_dx_class", dict(name="2025年秋季进修班", code="JX2503", category="improve",
    train_type="fulltime", status="finished", start_date="2025-09-01", end_date="2025-11-28",
    total_days=60, total_hours=600, organizer_id=3, default_room="第三教室",
    description="历史班次（已结业）。"))
print("✓ 新班次 3 个:", class2, class3, class4)

# ========== 7. 学员 ==========
roster1 = [
    ("陈晓红", "female", "1985-05-18", "六盘水市钟山区民政局 副局长", "life", 2),
    ("刘志远", "male", "1983-09-08", "铜仁市碧江区政法委副书记", "group", 2),
    ("杨帆", "male", "1986-02-14", "黔东南州凯里市发改局 副局长", "none", 3),
    ("周静", "female", "1984-12-01", "黔南州都匀市委党校 讲师", "none", 3),
    ("吴建军", "male", "1978-06-25", "毕节市七星关区政府办 副主任", "none", 3),
    ("郑雪梅", "female", "1987-08-19", "贵安新区行政审批局 科长", "none", 4),
    ("冯国华", "male", "1981-04-11", "安顺市西秀区委统战部 副部长", "none", 4),
    ("许文博", "male", "1988-10-30", "贵阳市白云区工信局 副局长", "none", 4),
    ("何雨欣", "female", "1989-01-22", "遵义市红花岗区文旅局 副局长", "none", 1),
    ("罗天成", "male", "1985-07-07", "黔西南州兴义市委办 副主任", "none", 1),
    ("高婷婷", "female", "1990-03-15", "六盘水市水城区教育局 股长", "none", 2),
    ("孙浩然", "male", "1987-11-09", "铜仁市沿河县政府办 科员", "none", 2),
    ("马俊杰", "male", "1984-05-28", "毕节市威宁县委组织部 科长", "none", 2),
]
n1 = 4
for name, g, bd, unit, duty, grp in roster1:
    create("nb_dx_student", dict(name=name, student_no=f"ZQ2601-{n1:02d}", gender=g,
        birth_date=bd, political_status="cpc", phone=f"1380851{n1:04d}", work_unit=unit,
        duty=duty, group_no=grp, klass_id=1, status="active", enroll_status="yes"))
    n1 += 1
# 班2 学员（待报到）
s17 = create("nb_dx_student", dict(name="谢明轩", student_no="ZT2602-01", gender="male",
    birth_date="1986-06-06", political_status="cpc", phone="13808520001",
    work_unit="贵阳市修文县农业局 副局长", klass_id=class2, status="pending", enroll_status="no"))
s18 = create("nb_dx_student", dict(name="蒋雨桐", student_no="ZT2602-02", gender="female",
    birth_date="1989-09-14", political_status="cpc", phone="13808520002",
    work_unit="遵义市凤冈县乡村振兴局 科长", klass_id=class2, status="pending", enroll_status="no"))
# 班4 历史学员
create("nb_dx_student", dict(name="唐建国", student_no="JX2503-01", gender="male",
    birth_date="1977-04-02", political_status="cpc", phone="13808530001",
    work_unit="省直机关 处长", klass_id=class4, status="finished", enroll_status="yes"))
create("nb_dx_student", dict(name="秦岚", student_no="JX2503-02", gender="female",
    birth_date="1980-12-08", political_status="cpc", phone="13808530002",
    work_unit="省属国企 党委副书记", klass_id=class4, status="finished", enroll_status="yes"))
create("nb_dx_student", dict(name="白志强", student_no="JX2503-03", gender="male",
    birth_date="1982-02-17", political_status="cpc", phone="13808530003",
    work_unit="黔东南州榕江县 副县长", klass_id=class4, status="dropout", enroll_status="yes"))
print("✓ 学员 18 人（班1 共16 / 班2 2 / 班4 3）")

# ========== 8. 教学计划 / 选修 ==========
create("nb_dx_teaching_plan", dict(name="第1期中青班教学计划", klass_id=1, status="published",
    purpose="提高中青年干部政治素质和专业能力",
    assessment="平时考核30% + 党性考核30% + 结业综合评估40%",
    books="《习近平谈治国理政》第五卷、《党章》",
    arrangement="第1周理论学习，第2周党性教育与现场教学，穿插选修与研讨"))
create("nb_dx_teaching_plan", dict(name="乡村振兴专题班教学计划", klass_id=class2, status="draft",
    purpose="解读乡村振兴政策，交流实践经验", assessment="结业研讨汇报",
    arrangement="5天：政策解读2天、现场教学2天、研讨1天"))
ep = create("nb_dx_elective_plan", dict(name="中青班选修课（第一轮）", klass_id=1, mode="own",
    round="first", status="selecting", start_time="2026-01-04 20:00:00", end_time="2026-01-05 22:00:00"))
for sid, tno, st in [(4, 6, "chosen"), (5, 7, "chosen"), (6, 8, "chosen"), (7, 9, "chosen"),
                     (8, 11, "chosen"), (9, 6, "opened"), (10, 7, "opened")]:
    tname = topics[tno - 1][1]
    create("nb_dx_elective_choice", dict(topic_name=tname, plan_id=ep, student_id=sid,
        topic_id=tno, round="first", status=st))
print("✓ 教学计划 2 份 + 选修计划 1 个（7 条选课）")

# ========== 9. 课表（班1 两周 + 冲突演示 + 班2 一节） ==========
schedules = []
def sched(week, day, si, kind, tname, topic_id=None, activity_id=None, teacher_id=None,
          place=None, merged=False, unit_name=None, eval_on=False, status="scheduled", klass_id=1):
    st, et = slot_dt(day, si)
    rid = create("nb_dx_course_schedule", dict(topic_name=tname, class_id=klass_id,
        topic_id=topic_id, activity_id=activity_id, kind=kind, week_no=week,
        day_of_week=day, start_time=st, end_time=et, place=place,
        teacher_id=teacher_id, merged=merged, unit_name=unit_name,
        eval_enabled=eval_on, status=status))
    schedules.append(rid)
    return rid

R1 = "第一报告厅"
# 第1周
sc_a1 = sched(1, 1, 0, "topic", topics[3][1], topic_id=4, teacher_id=tids[1], place=R1, unit_name="理论武装单元", eval_on=True)
sc_a2 = sched(1, 1, 1, "topic", topics[0][1], topic_id=1, teacher_id=tids[2], place=R1, unit_name="党性教育单元", eval_on=True)
sched(1, 1, 2, "topic", topics[9][1], topic_id=10, teacher_id=tids[6], place=R1, unit_name="理论武装单元")
sched(1, 1, 3, "activity", "党性分析交流会", activity_id=a1, place="第一讨论室")
sched(1, 2, 0, "topic", topics[1][1], topic_id=2, teacher_id=tids[7], place=R1, unit_name="政策解读单元", eval_on=True)
sched(1, 2, 1, "topic", topics[4][1], topic_id=5, teacher_id=tids[8], place=R1, unit_name="党性教育单元")
sched(1, 2, 2, "topic", topics[5][1], topic_id=6, teacher_id=tids[3], place=R1, unit_name="能力素养单元")
sched(1, 2, 3, "activity", "主题党日活动", activity_id=a2, place="党性教育基地")
# 冲突演示：第1周周三第1节 同教室两节
conflict_a = sched(1, 3, 0, "topic", topics[6][1], topic_id=7, teacher_id=tids[4], place=R1, unit_name="能力素养单元", eval_on=True)
conflict_b = sched(1, 3, 0, "topic", topics[7][1], topic_id=8, teacher_id=tids[6], place=R1, unit_name="能力素养单元")
sched(1, 3, 1, "topic", topics[10][1], topic_id=11, teacher_id=tids[3], place=R1, unit_name="能力素养单元")
sched(1, 3, 2, "video", "视频课：警示教育片", place=R1)
sched(1, 4, 0, "topic", topics[11][1], topic_id=12, teacher_id=tids[5], place=R1, unit_name="党性教育单元", eval_on=True)
sched(1, 4, 1, "topic", topics[8][1], topic_id=9, teacher_id=tids[8], place="遵义会议纪念馆", unit_name="现场教学单元")
sched(1, 5, 0, "topic", topics[2][1], topic_id=3, teacher_id=tids[8], place=R1, unit_name="现场教学单元")
sched(1, 5, 1, "elective", topics[10][1] + "（选修）", topic_id=11, teacher_id=tids[3], place=R1)
# 第2周
sched(2, 1, 0, "topic", topics[9][1], topic_id=10, teacher_id=tids[6], place=R1, unit_name="理论武装单元")
sched(2, 1, 1, "topic", topics[5][1], topic_id=6, teacher_id=tids[3], place=R1, unit_name="能力素养单元")
sched(2, 1, 2, "activity", "素质拓展训练", activity_id=a3, place="训练基地")
sched(2, 2, 0, "topic", topics[0][1], topic_id=1, teacher_id=tids[2], place=R1, unit_name="党性教育单元")
sched(2, 2, 1, "topic", topics[3][1], topic_id=4, teacher_id=tids[1], place=R1, unit_name="理论武装单元")
sched(2, 2, 2, "elective", topics[7][1] + "（选修）", topic_id=8, teacher_id=tids[6], place=R1)
sched(2, 3, 0, "topic", topics[1][1], topic_id=2, teacher_id=tids[7], place=R1, unit_name="政策解读单元")
sched(2, 3, 1, "topic", topics[4][1], topic_id=5, teacher_id=tids[8], place=R1, unit_name="党性教育单元")
sched(2, 3, 2, "video", "视频课：形势与政策", place=R1)
sched(2, 4, 0, "topic", topics[11][1], topic_id=12, teacher_id=tids[5], place=R1, unit_name="党性教育单元")
sched(2, 4, 2, "activity", "学员文艺晚会", activity_id=a4, place="大礼堂")
sc_chg = sched(2, 5, 0, "topic", topics[10][1] + "（调课）", topic_id=11, teacher_id=tids[3],
    place=R1, unit_name="能力素养单元", status="changed")
# 班2 一节（冲突跨班可见）
sched(1, 1, 0, "topic", topics[1][1], topic_id=2, teacher_id=tids[7], place=R1, klass_id=class2, unit_name="政策解读单元")
print(f"✓ 课表 {len(schedules)} 节（含冲突演示对 + 调课 1 节）")

create("nb_dx_change_log", dict(
    summary="「数字经济与产业转型」由第2周周五第2节调至第1节",
    schedule_id=sc_chg,
    old_values=json.dumps({"week_no": 2, "day_of_week": 5, "slot": 1}, ensure_ascii=False),
    new_values=json.dumps({"week_no": 2, "day_of_week": 5, "slot": 0}, ensure_ascii=False),
    reason="教师公务调整", operator_id=3, notified=True))
print("✓ 调课日志 1 条")

# ========== 10. 座位（班1 6×8=48，学员1-16 就座） ==========
seat_rows, seat_cols = 6, 8
seat_ids = []
for r in range(1, seat_rows + 1):
    for c in range(1, seat_cols + 1):
        sid_ = create("nb_dx_seat", dict(label=f"R{r}-C{c}", class_id=1, room=R1,
            area="A", row_no=r, col_no=c, kind="seat"))
        seat_ids.append(sid_)
for i in range(1, 17):  # 学员1-16 按学号坐 1-2 排
    upd("nb_dx_seat", seat_ids[i - 1], {"student_id": i})
print("✓ 座位 48 个（学员1-16 已就座）")

# ========== 11. 通知公告 / 新闻 / 评论 ==========
create("nb_dx_announcement", dict(title="关于开展2026年春季班次报名工作的通知", kind="campus",
    content="各处室、各教研部：2026年春季班次报名工作即将启动，请做好宣传与组织工作。",
    publisher_id=2, published_at="2026-01-02 09:00:00", top=True))
create("nb_dx_announcement", dict(title="第1期中青班第一周课程安排公布", kind="teaching", class_id=1,
    content="第1周以理论武装与党性教育为主，请学员按时参加，做好预习。",
    publisher_id=3, published_at="2026-01-03 17:00:00"))
create("nb_dx_announcement", dict(title="学员请假流程及纪律要求提醒", kind="student", class_id=1,
    content="学员请假须通过平台提交申请，组织员审批；累计请假超过总学习天数七分之一的将予以提醒。",
    publisher_id=3, published_at="2026-01-04 08:00:00"))
create("nb_dx_announcement", dict(title="新生报到指引", kind="guide",
    content="请携带身份证、单位介绍信到学员楼一层报到，扫码即可完成报到登记。",
    publisher_id=3, published_at="2025-12-28 10:00:00"))
nws = []
for t, c, at, top in [("我校举办2025年秋季学期结业典礼", "2025年秋季学期各班次顺利结业，校领导出席典礼并为优秀学员颁奖。", "2025-11-29 10:00:00", False),
                      ("省委党校（贵州行政学院）召开教学工作座谈会", "会议强调要坚持以习近平新时代中国特色社会主义思想为指导，全面提升办学质量。", "2025-12-15 09:00:00", True),
                      ("我校教师在全省党校系统精品课比赛中获奖", "我校两个专题课分获一等奖、二等奖。", "2026-01-05 11:00:00", False)]:
    nws.append(create("nb_dx_news", dict(title=t, content=c, publisher_id=2, published_at=at, top=top)))
create("nb_dx_comment", dict(title="学习体会", content="这次培训课程安排非常充实，收获很大！",
    author_id=6, kind="post", news_id=nws[2]))
create("nb_dx_comment", dict(title="支持", content="附议，现场教学环节印象深刻。", author_id=3,
    kind="reply", news_id=nws[2]))
print("✓ 公告 4 条 + 新闻 3 条 + 评论 2 条")

# ========== 12. 教材模块 ==========
books = {}
for n, pub, auth, yr, price, isbn, cat, stock in [
        ("《习近平谈治国理政》第五卷", "外文出版社", "习近平", 2025, 80.0, "9787119134567", "theory", 200),
        ("《中国共产党章程》", "人民出版社", "中共中央", 2022, 8.0, "9787010245678", "party", 500),
        ("《乡村振兴战略规划与实践》", "中共中央党校出版社", "李慧敏 编", 2024, 56.0, "9787503567890", "manage", 120),
        ("《法治政府建设十讲》", "法律出版社", "刘燕 著", 2023, 45.0, "9787519765432", "law", 80),
        ("《数字经济概论》", "高等教育出版社", "张国栋 等", 2024, 62.0, "9787040587654", "manage", 60),
        ("《党性教育读本》", "中共中央党校出版社", "本校编写组", 2025, 38.0, "9787503578901", "party", 150)]:
    books[n] = create("nb_dx_textbook", dict(name=n, publisher=pub, authors=auth, pub_year=yr,
        price=price, isbn=isbn, category=cat, stock=stock))
b1name, b2name = list(books)[0], list(books)[1]
b1, b2 = books[b1name], books[b2name]
p1 = create("nb_dx_purchase", dict(textbook_name=b1name, textbook_id=b1, quantity=200, unit_price=80.0,
    amount=16000.0, supplier="贵州新华书店", date="2025-12-20", status="received", operator_id=4))
create("nb_dx_purchase", dict(textbook_name="《党性教育读本》", textbook_id=books["《党性教育读本》"],
    quantity=150, unit_price=38.0, amount=5700.0, supplier="贵州新华书店", date="2025-12-28",
    status="ordered", operator_id=4))
create("nb_dx_purchase", dict(textbook_name="《数字经济概论》", textbook_id=books["《数字经济概论》"],
    quantity=60, unit_price=62.0, amount=3720.0, supplier="贵阳书城", date="2026-01-06",
    status="draft", operator_id=4))
r1 = create("nb_dx_requisition", dict(textbook_name=b1name, textbook_id=b1, class_id=1,
    batch_no="LL-2026-001", quantity=16, date="2026-01-04", status="done", operator_id=3))
create("nb_dx_requisition", dict(textbook_name=b2name, textbook_id=b2, class_id=class2,
    batch_no="LL-2026-002", quantity=2, date="2026-11-25", status="submitted", operator_id=3))
create("nb_dx_textbook_return", dict(textbook_name=b2name, textbook_id=b2, class_id=class4,
    requisition_id=r1, quantity=3, date="2025-11-20", operator_id=3))
for i, nm in enumerate(["李勇强", "郑雪梅", "何雨欣"], 1):
    create("nb_dx_recommendation", dict(book_name=f"学员荐书{i}：《之江新语》", authors="习近平",
        publisher="浙江人民出版社", reason="实践性强，适合干部阅读", student_id=i + 2, class_id=1,
        date="2026-01-05"))
for tname, ttype, chg, before, after, ref in [
        (b1name, "in", 200, 0, 200, "CG-2025-001"), (b1name, "out", 16, 200, 184, "LL-2026-001"),
        (b2name, "in", 500, 0, 500, "CG-2025-002"), (b2name, "out", 3, 500, 497, "TK-2025-003")]:
    create("nb_dx_inventory_log", dict(textbook_name=tname, textbook_id=books[tname], type=ttype,
        qty_change=chg, before_qty=before, after_qty=after, ref_no=ref, operator_id=4,
        happened_at="2025-12-20 10:00:00"))
print("✓ 教材 6 本 + 采购 3 / 领用 2 / 退库 1 / 荐书 3 / 库存流水 4")

# ========== 13. 请假 / 外出 / 退学 / 打卡 / 承诺书 / 材料表 ==========
create("nb_dx_leave", dict(student_name="王丽娟", student_id=2, class_id=1, type="sick",
    reason="感冒发烧，需居家休息", start_time="2026-01-06 08:30:00", end_time="2026-01-06 17:40:00",
    duration_days=1, status="approved", approved_remark="注意休息，补齐课程", over_ratio=False))
create("nb_dx_leave", dict(student_name="吴建军", student_id=8, class_id=1, type="duty",
    reason="本单位有紧急公务需返回处理", start_time="2026-01-08 14:00:00", end_time="2026-01-09 17:40:00",
    duration_days=2, status="pending", over_ratio=False))
create("nb_dx_leave", dict(student_name="许文博", student_id=11, class_id=1, type="withdrawn" if False else "personal",
    reason="家中有事", start_time="2026-01-10 08:30:00", end_time="2026-01-10 17:40:00",
    duration_days=1, status="withdrawn", over_ratio=False))
create("nb_dx_go_out", dict(student_name="杨帆", student_id=6, class_id=1, type="half_day",
    reason_place="前往市发改委对接工作", start_time="2026-01-05 14:00:00", end_time="2026-01-05 17:40:00",
    status="acked"))
create("nb_dx_go_out", dict(student_name="周静", student_id=7, class_id=1, type="leave_campus",
    reason_place="外出就医", start_time="2026-01-06 09:00:00", end_time="2026-01-06 12:00:00",
    status="submitted"))
create("nb_dx_dropout", dict(student_name="白志强", student_id=21, class_id=class4,
    reason="工作调动，无法继续参加培训", status="approved", approved_remark="同意退学，按结业前退学办理"))
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
print("✓ 请假 3 / 外出 2 / 退学 1 / 打卡 3 / 承诺书 1 / 材料表 2")

# ========== 14. 考勤（第1周前两节课 × 16 学员） ==========
att_stat = {1: "normal", 2: "normal", 3: "late", 4: "normal", 5: "normal", 6: "goout",
            7: "normal", 8: "leave", 9: "normal", 10: "normal", 11: "absent", 12: "normal",
            13: "normal", 14: "normal", 15: "late", 16: "absent"}
for scid, day in [(schedules[0], 1), (schedules[1], 1)]:
    for sid_, stt in att_stat.items():
        create("nb_dx_attendance", dict(student_name=STD_NAMES[sid_], student_id=sid_, class_id=1,
            schedule_id=scid, topic_id=4 if scid == schedules[0] else 1, date="2026-01-05",
            status="normal" if scid == schedules[0] else stt,
            checkin_time=f"2026-01-05 08:2{sid_ % 10}:00", location=R1,
            method="mobile" if sid_ % 3 else "rollcall"))
print("✓ 考勤 32 条")

# ========== 15. 评估 / 党性考核 / 投票 / 问卷 ==========
STD_NAMES = ["张明远", "王丽娟", "李勇强", "陈晓红", "刘志远", "杨帆", "周静", "吴建军",
             "郑雪梅", "冯国华", "许文博", "何雨欣", "罗天成", "高婷婷", "孙浩然", "马俊杰"]
scores = [92, 88, 95, 78, 84, 90, 86, 93, 81, 89]
for i, sc in enumerate(scores):
    sid_ = i + 1
    tno = [4, 4, 2, 2, 12, 12, 4, 2, 12, 4][i]
    create("nb_dx_eval_record", dict(student_name=STD_NAMES[sid_ - 1], student_id=sid_, class_id=1,
        scheme_id=scheme_topic, schedule_id=sc_a1 if tno == 4 else (sc_a2 if tno == 1 and False else schedules[4]),
        topic_id=tno, kind="topic", score=sc,
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
print("✓ 评估记录 30 条（专题10 / 综合8 / 党性自评8 / 党性考评4）")

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

# ========== 16. 报名 / 缴费（班2） ==========
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
print("✓ 报名 6 条（待审4/通过2）+ 缴费 4 条")

# ========== 17. 作业 / 提交 ==========
asg = create("nb_dx_assignment", dict(name="党性分析材料撰写", class_id=1, topic_id=1,
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

print("\n全部完成 ✅  班次4 / 学员21 / 师资8 / 专题12 / 课表28 / 座位48 / 各业务表已灌入")
