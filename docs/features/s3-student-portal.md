# s3-学员管理与综合门户 — 8 页逻辑说明(阶段3-5)

> 完成日期:2026-11-09。对应蓝本:`.artifacts/nocobase-ui-builder/stage3-student-portal/`(生成脚本 `gen_student_portal.py`)。
> 数据模型:`models/collections/nb_dx_student|class|announcement|leave.yaml`(阶段1 已建)。

## 业务范围

两个菜单组共 8 页:

| 组 | 页面 | 集合 | routeId | 用途 |
|---|---|---|---|---|
| 学员管理(396734674829312) | 学员信息 | nb_dx_student | 396734674829313 | 学员主档维护(组织员以班级维度管理,分配班级职务/学号) |
| | 学员相册 | nb_dx_student | 396734704189440 | 头像卡片式名录(photo 列 + 姓名/单位/职务),便于互相认识 |
| | 学籍管理 | nb_dx_student | 396734710480896 | 学籍状态分布饼图 + 明细(在读/待审核/退学/结业 + 报到状态) |
| | 学员档案 | nb_dx_student | 396734716772352 | 档案视角完整详情(政治面貌/联系方式/参训班次) |
| | 培训记录 | nb_dx_student | 396734882447360 | 各班次学员数柱状图 + 参训记录明细 |
| 综合门户(396734888738816) | 综合门户 | student/leave/announcement | 396734888738817 | 门户首页:各班次学员数 + 请假状态分布 + 通知公告列表 |
| | 班级主页 | nb_dx_class | 396734895030272 | 班次列表(类别/状态/起止日期/组织员),详情弹窗看班次全貌 |
| | 学员主页 | nb_dx_student | 396734901321728 | 学员个人页(本人信息;学员角色经 S1b scope 只见本人) |

## 业务规则

1. **dx.xlsx 的 5 项学员功能映射到 1 表 5 视角**:dx.xlsx 的学员信息/相册/学籍/档案/培训记录在 demo 中不做 5 张独立表,统一基于 `nb_dx_student`(D20:每次参训建一条 student 记录,`klass` m2o 指向班次)。5 页 = 同一集合的 5 个业务视角(维护/名录/状态统计/详情/参训历史),各有不同的列组合与图表,避免建无意义的平行表。
2. **学籍状态机**:student.status ∈ {pending 待审核, active 在读, dropout 已退学, finished 已结业} + enroll_status 报到状态;退学流转由阶段4 退学审批流驱动,本期人工维护;学籍管理页的饼图即该状态的分布视图。
3. **学员主页与 S1b scope**:学员角色登录学员主页只见本人记录(见权限节)。管理员/组织员/教务看全部学员。「多次参训学员切换班级」等高级场景按 demo 粒度省略(培训记录页可见本人各条参训记录即覆盖)。
4. **综合门户待办预告**:dx.xlsx 门户要求"待办推送",待办数据要等阶段4 workflow 才有;本期综合门户放统计图表 + 通知公告,待办列表页是阶段4 独立任务(TASKS 阶段4 第 5 条)。
5. **班级主页 demo 简化**:dx.xlsx 的班级主页要场景化展示通知/课表/评估/材料/资料/优秀学员;demo 阶段以班次列表 + 详情弹窗(fieldGroups 三组:基本信息/周期/其他)覆盖,课表场景在阶段5 AI Portal,班级维度数据页可视需要后续在详情弹窗加关联块。

## 权限设计(D23 矩阵 + 本次 D30 变更)

**D30(Violet 确认)**:r_student 原本无 nb_dx_student 权限,但 dx.xlsx 学员端需要学员主页/相册/培训记录,故补 `nb_dx_student` view(全 16 字段)+ 新建 **S1b-本人学员记录** scope(id 396733982769152,filter `user.id = {{$user.id}}`)。注意 S1(396708890345472)的 filter 是 `student.user.id`,只适用于**带 student 字段的表**;nb_dx_student 表自身没有 student 字段,必须用 S1b(`user.id` 直达),两条 scope 语义不同不可混用。

| 角色 | route 条数 | 授予页面 | 依据 |
|---|---|---|---|
| r_leader | 18 | 全 8 页 | 全表 view+export |
| r_organizer | 18 | 全 8 页 | student/class CRUD、announcement view、leave/attendance view(图表可查) |
| r_academic | 18 | 全 8 页 | class/announcement CRUD、student/leave/attendance view |
| r_teacher | 16 | 学员管理 5 页 + 班级主页 + 学员主页 | **不授综合门户页**:请假 chart 依赖 leave 表,teacher 无 leave 权限(chart 会 403);class/student/announcement view 满足其余页 |
| r_student | 12 | 学员相册 + 培训记录 + 综合门户 3 页 | 学员信息/学籍/档案是管理视角不授;相册经 S1b 只见本人头像(demo 粒度);统计图经 S1b 只统计本人 |

## 蓝本阶段踩坑(新增一条,接续 s3-class-admin)

1. **bar 图 mappings 键是 x/y 不是 category/value**:pie 用 `{category, value}`,bar 用 `{x, y}`,写错报 `chart-visual-required-mappings-missing`(报错信息会给出 expectedShape)。饼图/柱状图混用时容易踩。
2. **关联路径可直接作 chart dimension**:`klass.name` 作柱状图维度一次通过(无需物化处理),count 聚合 `{"field":"id","aggregation":"count"}` 沿用。
3. **rolesResourcesScopes 只能走 REST**:`nb api` 命令面没有 `data-sources:main:roles-resources-scopes`,创建 scope 用 `curl POST /api/dataSources/main/rolesResourcesScopes:create`(body 只传 name/resourceName/scope);绑定 action 必须用 `scopeId`(不能传 scope 对象);resource update 必须带 `--filter-by-tk`。
4. 复用:student/class fieldGroups 三组方案(s3-textbook 定稿)继续有效,本次把 excellent 补进 stuWork 组。

## 补充：各班次学员数图表口径（D56，2026-11-09；D77 补修培训记录，2026-11-10）

- **规则**：综合门户与培训记录页的「各班次学员数」柱状图，计数口径 = 学员档案条数（含未挂班的，显示为「未分班」一栏），不是活跃学员数；数量来源 = raw visual 前端按 `klass.name` 分组计数。
- **为什么前端计数**：`charts:queryData` 对关联维度（`klass.name`）不聚合，返回每学员一行明细且不含 measure 别名列，builder 模式拿不到数量（详见 decisions D56）。
- **D77 补充（2026-11-10）**：D56 实际只改了综合门户的图表实例（arheyvzxnw1）；培训记录页是**独立的 ChartBlockModel 实例**（73fclpvn4nr），当时仍为 builder 模式图例显示英文 stuCount——已用同款 custom raw 方案补修（蓝本 `.artifacts/nocobase-ui-builder/fix-train-chart/`）。两页图表互不影响，改一处不等于改一类。
- **数据现状**：18 名学员 class_id 为 NULL（多为历史导入/报名建档测试数据），仅第1期中青班 4 人挂班；演示若需柱状图好看，需先给学员补挂班次。
