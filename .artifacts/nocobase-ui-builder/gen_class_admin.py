#!/usr/bin/env python3
# 生成阶段3-4 班务管理 6 页蓝本 JSON
import json, os

OUT = os.path.dirname(os.path.abspath(__file__)) + '/stage3-class-admin'
os.makedirs(OUT, exist_ok=True)

# ---------- 公共 defaults 片段 ----------
def popups(name_view, name_add, name_edit, desc_prefix):
    return {
        'view': {'name': name_view, 'description': f'查看一条{desc_prefix}详情'},
        'addNew': {'name': name_add, 'description': f'新增一条{desc_prefix}记录'},
        'edit': {'name': name_edit, 'description': f'编辑一条{desc_prefix}记录'},
    }

CLASS_FG = [
    {'key': 'classBasic', 'title': '基本信息', 'fields': ['name', 'code', 'category', 'train_type', 'status', 'organizer']},
    {'key': 'classPeriod', 'title': '报名与学习周期', 'fields': ['enroll_start', 'enroll_end', 'start_date', 'end_date', 'total_days', 'total_hours']},
    {'key': 'classOther', 'title': '教室与其他', 'fields': ['default_room', 'room_locked', 'qr_token', 'description']},
]
STUDENT_FG = [
    {'key': 'stuBasic', 'title': '基本信息', 'fields': ['name', 'student_no', 'gender', 'birth_date', 'political_status', 'phone', 'photo']},
    {'key': 'stuWork', 'title': '单位与分工', 'fields': ['work_unit', 'duty', 'group_no']},
    {'key': 'stuStatus', 'title': '学籍与状态', 'fields': ['status', 'enroll_status', 'remark', 'klass', 'user']},
]
TOPIC_FG = [
    {'key': 'topicBasic', 'title': '专题信息', 'fields': ['name', 'category', 'attribute', 'teach_form', 'hours', 'status']},
    {'key': 'topicOther', 'title': '主讲与说明', 'fields': ['teacher', 'eval_scheme', 'description', 'remark']},
]
CS_FG = [
    {'key': 'csBasic', 'title': '课程安排', 'fields': ['topic_name', 'kind', 'week_no', 'day_of_week', 'start_time', 'end_time', 'place', 'status']},
    {'key': 'csRelate', 'title': '关联对象', 'fields': ['klass', 'topic', 'activity', 'teacher']},
    {'key': 'csOther', 'title': '其他设置', 'fields': ['merged', 'unit_name', 'eval_enabled']},
]

def assoc(field, v, a, e, prefix):
    return {field: {'view': {'name': v, 'description': f'查看一条{prefix}详情'},
                    'addNew': {'name': a, 'description': f'新增一条{prefix}记录'},
                    'edit': {'name': e, 'description': f'编辑一条{prefix}记录'}}}

STD = {
    'nb_dx_student': {'popups': popups('查看学员', '新增学员', '编辑学员', '学员'), 'fieldGroups': STUDENT_FG},
    'nb_dx_class': {'popups': popups('查看班次', '新增班次', '编辑班次', '班次'), 'fieldGroups': CLASS_FG},
    'nb_dx_topic': {'popups': popups('查看专题', '新增专题', '编辑专题', '教学专题'), 'fieldGroups': TOPIC_FG},
    'nb_dx_course_schedule': {'popups': popups('查看排课', '新增排课', '编辑排课', '排课记录'), 'fieldGroups': CS_FG},
    'users': {'popups': popups('查看用户', '新增用户', '编辑用户', '用户')},
}

def std(collections_extra=None, assoc_map=None):
    d = {k: json.loads(json.dumps(v)) for k, v in STD.items()}
    for k, v in (collections_extra or {}).items():
        d[k] = v
    for src, assocs in (assoc_map or {}).items():
        d.setdefault(src, {}).setdefault('popups', {})['associations'] = assocs
    return {'collections': d}

def page(fname, nav, page_title, tab_title, blocks, defaults, layout=None):
    tab = {'key': 'main', 'title': tab_title, 'blocks': blocks}
    if layout:
        tab['layout'] = layout
    doc = {'version': '1', 'mode': 'create', 'navigation': nav,
           'page': {'title': page_title}, 'tabs': [tab], 'defaults': defaults}
    with open(f'{OUT}/{fname}', 'w', encoding='utf-8') as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    print('written', fname)

LAYOUT_UID = {'layoutUid': 'admin-layout-model'}
GROUP_NEW = {'title': '班务管理', 'icon': 'SolutionOutlined'}

# P1 请假管理
page('page1-leave.json',
     {**LAYOUT_UID, 'group': GROUP_NEW, 'item': {'title': '请假管理', 'icon': 'FileDoneOutlined'}},
     '请假管理', '请假管理',
     [{'key': 'leaveTable', 'type': 'table', 'collection': 'nb_dx_leave',
       'fields': ['student_name', 'klass.name', 'type', 'start_time', 'end_time', 'duration_days', 'status', 'over_ratio'],
       'recordActions': ['view', 'edit', 'delete']}],
     std({'nb_dx_leave': {'popups': popups('查看请假申请', '新增请假申请', '编辑请假申请', '请假申请')}}))

# P2 外出报备
page('page2-goout.json',
     {**LAYOUT_UID, 'group': {'routeId': 'LEAVE_GROUP'}, 'item': {'title': '外出报备', 'icon': 'EnvironmentOutlined'}},
     '外出报备', '外出报备',
     [{'key': 'gooutTable', 'type': 'table', 'collection': 'nb_dx_go_out',
       'fields': ['student_name', 'klass.name', 'type', 'reason_place', 'start_time', 'end_time', 'status'],
       'recordActions': ['view', 'edit', 'delete']}],
     std({'nb_dx_go_out': {'popups': popups('查看外出报备', '新增外出报备', '编辑外出报备', '外出报备')}}))

# P3 退学管理
page('page3-dropout.json',
     {**LAYOUT_UID, 'group': {'routeId': 'LEAVE_GROUP'}, 'item': {'title': '退学管理', 'icon': 'UserDeleteOutlined'}},
     '退学管理', '退学管理',
     [{'key': 'dropoutTable', 'type': 'table', 'collection': 'nb_dx_dropout',
       'fields': ['student_name', 'klass.name', 'reason', 'status', 'approved_remark'],
       'recordActions': ['view', 'edit', 'delete']}],
     std({'nb_dx_dropout': {'popups': popups('查看退学申请', '新增退学申请', '编辑退学申请', '退学申请')}}))

# P4 考勤统计（chart + table）
page('page4-attendance.json',
     {**LAYOUT_UID, 'group': {'routeId': 'LEAVE_GROUP'}, 'item': {'title': '考勤统计', 'icon': 'ClockCircleOutlined'}},
     '考勤统计', '考勤统计',
     [{'key': 'attPie', 'type': 'chart', 'title': '考勤状态分布', 'chart': 'attByStatus'},
      {'key': 'attTable', 'type': 'table', 'title': '考勤明细', 'collection': 'nb_dx_attendance',
       'fields': ['student_name', 'klass.name', 'date', 'status', 'checkin_time', 'location', 'method'],
       'recordActions': ['view', 'edit', 'delete']}],
     std({'nb_dx_attendance': {'popups': popups('查看考勤记录', '新增考勤记录', '编辑考勤记录', '考勤记录')}}),
     layout={'rows': [[{'key': 'attPie', 'span': 24}, {'key': 'attTable', 'span': 24}]]})

# P5 党性考核（eval_record 过滤党性自评/复评）
page('page5-party-eval.json',
     {**LAYOUT_UID, 'group': {'routeId': 'LEAVE_GROUP'}, 'item': {'title': '党性考核', 'icon': 'AuditOutlined'}},
     '党性考核', '党性考核',
     [{'key': 'partyTable', 'type': 'table', 'collection': 'nb_dx_eval_record',
       'defaultFilter': {'$and': [{'kind': {'$in': ['party_self', 'party_review']}}]},
       'fields': ['student_name', 'klass.name', 'scheme.name', 'kind', 'score', 'items_json', 'opinion', 'anonymous'],
       'recordActions': ['view', 'edit', 'delete']}],
     std({'nb_dx_eval_scheme': {'popups': popups('查看评估方案', '新增评估方案', '编辑评估方案', '评估方案')},
          'nb_dx_eval_record': {'popups': popups('查看党性考核记录', '新增党性考核记录', '编辑党性考核记录', '党性考核记录')}},
         assoc_map={'nb_dx_eval_record': assoc('scheme', '查看评估方案', '新增评估方案', '编辑评估方案', '评估方案')}))

# P6 优秀学员（vote 投票/打分评选）
page('page6-excellent.json',
     {**LAYOUT_UID, 'group': {'routeId': 'LEAVE_GROUP'}, 'item': {'title': '优秀学员', 'icon': 'TrophyOutlined'}},
     '优秀学员', '优秀学员',
     [{'key': 'voteTable', 'type': 'table', 'collection': 'nb_dx_vote',
       'fields': ['name', 'klass.name', 'kind', 'scope', 'status', 'end_time', 'creator.nickname'],
       'recordActions': ['view', 'edit', 'delete']}],
     std({'nb_dx_vote': {'popups': popups('查看投票', '新增投票', '编辑投票', '投票')},
          'nb_dx_vote_record': {'popups': popups('查看投票明细', '新增投票明细', '编辑投票明细', '投票明细')}},
         assoc_map={'nb_dx_vote': assoc('records', '查看投票明细', '新增投票明细', '编辑投票明细', '投票明细')}))
