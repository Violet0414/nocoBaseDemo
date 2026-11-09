# 阶段3-1：教学资源 7 库（PC 管理端）

> 完成日期：2026-11-09 ｜ 备份：`backups/nocobase_20261109_stage3_teaching_resources.sql`
> 蓝本：`.artifacts/nocobase-ui-builder/stage3-teaching-resources/page*.json`（重建/改版可直接参考）

## 业务范围

依据 dx.xlsx「教学资源」块：7 个资源库，均为"库管理"形态（增删改查 + 检索），无审批流、无统计图表（后者在评估/图表模块处理）。

## 页面与数据对应

| 菜单项 | collection | 表格列 | 权限要点 |
|---|---|---|---|
| 师资库 | nb_dx_teacher | name/gender/unit/title/research_area/is_leader/is_external/phone | academic 可维护；leader/student 只读 |
| 专题库 | nb_dx_topic | name/category/attribute/teach_form/hours/teacher.name/status | 同上；teacher 为 m2o→nb_dx_teacher |
| 活动库 | nb_dx_activity | name/category/hours/place | 同上 |
| 基地库 | nb_dx_base | name/category/address/contact/phone | 同上 |
| 拟开发专题 | nb_dx_planned_topic | name/proposer.nickname/department/target_date/status | 同上；proposer 为 m2o→users |
| 教学案例 | nb_dx_teaching_case | name/category/source/year | 同上 |
| 校外宣讲 | nb_dx_external_lecture | name/lecturer_name/teacher.name/date/place/audience_count | 同上 |

统一交互：每页一个 table 区块，动作为 筛选/新增/刷新/批量删除；行动作 查看/编辑/删除；筛选由后端按元数据自动生成（≤4 个可筛选字段）。

## 权限设计

- **collection 层**（阶段2 D23 定稿，本次只读核实）：academic=CRUD+export；leader=view+export；student=view；organizer/teacher=无（无独立权限记录）
- **route 层**（本次新增，D24 首次落地）：leader/academic/student 各 15 条 route（菜单组 + 7 页 + 每页 tab 子路由，后端自动补齐 tab id）；organizer/teacher 不授权
- 菜单组「教学资源」routeId=`396710905708544`；7 页 route id 见 STATE.md / 蓝本

## 迭代注意（踩坑与约定）

1. **users 关联字段显示列必须用 `proposer.nickname`**——users 表没有 `name` 字段，写 `proposer.name` 会被 apply-blueprint 拒绝（field-path-unknown）
2. **同组建页必须串行**：第 1 页用 `navigation.group.title` 创建组并取回 routeId，后续页一律用 `navigation.group.routeId` 引用，禁止再传 title
3. 本机 nb CLI 2.2.41 无 `nb portal` 命令面，建页走 legacy lane（`navigation.layoutUid: "admin-layout-model"`）
4. 改这 7 页的列/动作时改蓝本 JSON 后用 `apply-blueprint --mode replace --target '{"pageSchemaUid":"<uid>"}'` 重放，不要手工逐块点配
5. student 对 7 库只有 view，页面上的新增/编辑按钮对其自动隐藏（ACL 拦截），无需额外配置
