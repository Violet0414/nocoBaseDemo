# s3-academic — 教务管理模块业务逻辑（阶段3）

> 完成：2026-11-09。5 页挂「教务管理」菜单组（routeId `396723346014208`）。
> 蓝本：`.artifacts/nocobase-ui-builder/stage3-academic/`；备份：`nocobase_20261109_stage3_academic.sql`。

## 页面清单与定位

| 页面 | 集合 | routeId | 主要使用者 |
|---|---|---|---|
| 班次管理 | nb_dx_class | 396723346014209 | 教务人员/组织员维护班次生命周期；全员可看 |
| 通知公告 | nb_dx_announcement | 396723947896832 | 教务人员发布；全员可看 |
| 教学计划 | nb_dx_teaching_plan | 396723966771200 | 教务人员编写；全员可看 |
| 选修计划 | nb_dx_elective_plan | 396723979354112 | 教务人员设选修轮次；教师不授 |
| 教学资料 | nb_dx_teaching_material | 396723994034176 | 教务人员上传；仅领导/教务/学员可见 |

5 页均为单 tab + table 结构，recordActions = view/edit（班次页多 delete），新增走表格默认 addNew 按钮。

## 业务规则（为什么这样配）

1. **班次是全系统的主轴**：class 被 announcement/teaching_plan/elective_plan/teaching_material 以 m2o 引用，也通过 o2m 挂 students/teaching_plans/course_schedules/elective_plans/seats。班次管理页 view 弹窗因此带 6 个关联弹窗三件套（organizer/students/teaching_plans/course_schedules/elective_plans/seats）。
2. **请假占比提醒依赖 total_days**：class 的 `total_days`（总学习天数）字段描述即"累计请假不超过总学习天数的 1/7"，阶段4 workflow 请假审批将聚合该值做超限提醒——建模阶段已留好字段。
3. **通知公告 klass 为空 = 全校通知**：`klass` m2o 可空，指定班级则只有该班学员可见（学员端过滤逻辑阶段6/7 实现）。
4. **选修计划三轮流转**：round（第一轮/第二轮/已结束）+ status（选课中/已截止/已定开课）双状态字段；mode 区分本班选修/合班选修。选课明细在 `nb_dx_elective_choice`（学员端产生，管理端经计划 view 弹窗查看）。
5. **教学资料分本班/全校**：category 区分；klass 在"本班资料"时必填——该校验留待阶段4/7 演示，页面不加硬约束（demo 口径）。

## route 权限矩阵（页面可见性）

| 角色 | 班次 | 通知 | 计划 | 选修计划 | 教学资料 | 依据 |
|---|---|---|---|---|---|---|
| r_leader | ✓ | ✓ | ✓ | ✓ | ✓ | 全库 view+export |
| r_organizer | ✓ | ✓ | ✓ | ✓ | ✗ | 无 teaching_material 独立配置 |
| r_academic | ✓ | ✓ | ✓ | ✓ | ✓ | 5 表全 CRUD |
| r_teacher | ✓ | ✓ | ✓ | ✗ | ✗ | elective_plan/material 无独立配置 |
| r_student | ✓ | ✓ | ✓ | ✓ | ✓ | 5 表均 view |

每页授权粒度 = 组 1 条 + 页面 1 条 + tab 1 条。leader/academic/student 11 条、organizer 9 条、teacher 7 条。

## 踩坑（继承 + 新增）

- **复用教材模块 4 条踩坑**（fieldGroups/date 字段/descriptionReview/layout），详见 `s3-textbook.md` 末节。本模块全部预防性规避：nb_dx_class/nb_dx_student/nb_dx_topic 直接给 fieldGroups。
- **`desktop-routes list` 默认分页 20 条**：验证授权时若总数 >20 会漏看新授权，必须用 `--filter {"id":{"$in":[...]}}` 精确验证，否则会误判授权失败。
- **desktop-routes add 是纯增量**：授错了要用 `remove` 命令回撤（本次 teacher 多授了选修计划 2 条，remove 后验证剩余 0 条）。
- **`nb api data-source-resources get` 不存在**：正确命令是 `nb api acl roles data-source-resources get --role-name <r> --name <表> --data-source-key main --appends actions`（STATE.md 旧速查写法有误，已按本次实际命令修正）。
