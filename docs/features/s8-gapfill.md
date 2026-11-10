# s8-gapfill — PLAN 声明缺失功能补齐（2026-11-10）

> Violet 确认清单后执行：补齐 PLAN.md 声明但未落地的功能点。执行原则：只增不改（唯一例外 C1 走 revision）、全程中文文案、不影响现有功能。

## 业务规则与设计决策

### A. 教材库存闭环（PLAN A 类「workflow 库存联动 + 统计报表」）

- **三条联动流（提交即触发，Violet 拍板）**：采购/领用/退库各一条 collection 触发流（mode=1 create），链式：query 查教材当前 stock → calculation math.js 算变动后库存 → update `nb_dx_textbook.stock` → create `nb_dx_inventory_log` 流水（type=采购/领用/退库、before_qty/after_qty/qty_change、ref_no=领用批次号或触发记录 id、happened_at=触发记录 createdAt）。workflow id：采购 `396902662209536`、领用 `396902681083904`、退库 `396902702055424`。
- **变量引用形态**（报名流 v2 实存确认，修正 D54a 表述）：query/create 结果引用统一 `{{$jobsMapByNodeKey.<key>.<字段>}}`（无 `.data` 前缀）；calculation 结果整体引用（无字段名）。
- **防呆**：库存 stock 全表无空值（D60 math.js null TypeError 的教训前置核查）；API 直插不带 quantity 会致 calculation 失败——execution 报错不回写库存不写流水，属可接受 fail-fast。
- **领用报表页**（教材管理组，routeId 396903540916224）：各教材领用数量 bar chart 走 **D56 custom visual 方案**（`charts:queryData` 对关联维度 textbook.name 不聚合，前端 raw 分组 sum quantity）+ 领用明细表。
- **库存流水页**（396903549304832）：流水类型 pie（type 本表字段 builder 聚合正常，值本身中文无需翻译）+ 流水明细表（纯只读）。
- 联动流实测（验证脚本 `.artifacts/nocobase-workflow/inventory-link/verify_inventory_link.py`）：采购 200→205、领用 205→202、退库 202→204，流水 before/after/ref_no/happened_at 全对 ✓。测试数据保留作演示。

### B. 管理端缺失页 ×6（PLAN A/B 类散项）

| 页 | 组 | routeId | 要点 |
|---|---|---|---|
| 作业管理 | 教务管理 | 396906271408128 | 提交情况 pie + 作业列表 + 提交明细（批阅=edit 弹窗改 score/review；**转批**=edit 弹窗改 transferred_to 字段——建模时已预留） |
| 材料回复 | 教务管理 | 396906292379648 | 材料类型 pie + 列表（回复=edit 弹窗改 reply/reply_by） |
| 申报信息 | 教务管理 | 396906304962560 | 申报类型 pie + 列表 |
| 纪律承诺 | 班务管理 | 396906321739776 | 签署状态 pie + 列表（signed/signed_at 已预留） |
| 调课记录 | 教务管理 | 396906552426496 | change_log 只读表（summary/新旧值/原因/经办人） |
| 通知阅读统计 | 教务管理 | 396906680352768 | announcement 主表 + **readers m2m 列**直出已读人员；演示数据已灌 14 条 announcement_readers |

- **踩坑**：①bar 图蓝本 mappings 键必须是 `x`/`y`（pie 才是 category/value）——与 D56 踩坑同款，蓝本通道再次强制；②`createdAt` 不被蓝本 fields 接受（系统字段）；③蓝本 fields 引用关联路径会连带要求目标表的 popups/fieldGroups（change_log→course_schedule 13 字段、announcement→class 15 字段均需 fieldGroups，校验器报错会明确点名）；④through 集合（nb_dx_announcement_readers）无关联字段不可作块集合——阅读统计改走 announcement 主表 m2m 列。
- route 授权：leader/academic 全部 6 页；organizer 授作业/材料/申报/纪律承诺/阅读统计；teacher 授作业管理（页+hidden tab 子行两条一起授）。

### C. 站内提醒（PLAN B 类「通知节点站内提醒」）

- **通道**：`notificationChannels` 建 in-app 通道（name=in-app，title=站内消息），REST 直接创建。
- **4 条流全部 revision**（D58a 三步法）后接 `notification` 节点，ignoreFail=true 兜底。新 workflow id：请假 `396908352176128`、退学 `396908373147648`、报名 `396908392022016`、缴费 `396908412993536`。
- **receivers 形态**（源码取证）：workflow notification 节点 config 里 `receivers` 进 `message.receivers`，in-app channel 解析——元素为 id 字符串（如 `["{{$context.data.student.user_id}}"]`）或 UserRepo find 对象（缴费流按 student_id 查学员绑定的 user：`[{"filter":{"student":{"id":{"$eq":"{{$context.data.student_id}}"}}}}]`）。
- **挂载**：通过通知挂分支链尾（请假流的"通过"分超限/未超限两处），驳回通知挂 condition 的 branchIndex=0 分支；缴费流无分支直接挂 manual 后。
- **jsBlock 同步**（D58a 教训）：`72hgyrjlwza` 的 ENABLED_WF/WF_TITLE/FALLBACK_ACTIONS 补 4 个新 id（读-改-写，备份 `backups/flowmodels_jsblock_wf_20261110.txt`）。
- 实测（`.artifacts/e2e-check/verify_c1_notification.py`）：学员提交请假 → organizer 审批 202 → 站内消息「请假审批结果：…已审批通过。」送达学员 user 6，发送日志 success/in-app ✓。
- **坑**：manual task submit 的 `filterByTk` 必须放 URL query（放 body 400）；登录端点是 `/api/auth:signIn`（users:signin 404）。

### D. 学员社区 + 社区活跃度（PLAN A 类「学员社区 | 评论区块」「社区活跃度」）

- **零建模方案（D1）**：复用 `nb_dx_comment` 表——帖子 = `kind='post'`（parent_id 空），跟帖 = `kind='reply'` + parent_id 挂帖。表结构（parent_id/kind/hot）建模时已为此设计，不新增集合。
- **admin 社区管理页**（学员管理组，396909230882816）：活跃度 bar（按 author.nickname 分组计数，custom visual 前端计数，同 D56）+ 帖子列表（dataScope kind=post，编辑=精华标记 hot、删帖）+ 跟帖列表（kind=reply）。
- **移动端学员社区页**（mobile Portal，396909314768896）：发帖表单（author 手选 + kind 默认值规则 `defaultKindPost` setFieldValueRules，targetPath 形态）+ 帖子广场（dataScope kind=post）。r_student 授权 route 2 条 + **comment create 权限**（SQL 直插 `dataSourcesRolesResourcesActions`，r_student 原只有 view；ACL 表在 dataSource 维度，不在 rolesResources）。
- 演示数据：4 帖 + 4 跟帖（作者为测试账号，含 2 条 hot 精华）。
- **坑**：mobile Portal 蓝本多块不许每块独占一行（校验器强拒，须同行 span 12）——s6 踩坑③再次确认。

## 验证

统一无头回归（`.artifacts/e2e-check/verify_gapfill_all.py`，leader_test/organizer_test/student_test 三账号）：
- 9 新页全部渲染（chart canvas / 表格行数达标）✓
- 既有页回归：库存报表 / 请假管理 / 工作台待办（jsBlock 新 id 兼容，新流待办标题正常）✓
- 移动端学员社区菜单入口 ✓；pageerror=0 ✓
- 最终备份 `backups/nocobase_20261110_gapfill_done.sql`

## 服务器同步注意

本轮全部为 DB 配置（无 Portal 源码改动），下次 fresh dump 重灌即全量带走；`notificationChannels` 的 in-app 通道与演示数据随 dump 走，无需额外文件。
