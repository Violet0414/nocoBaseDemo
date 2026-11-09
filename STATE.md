# STATE.md — 当前进度快照

> 新会话/换电脑续做入口。每完成任务更新本文件。最后更新：2026-11-09（**D51/D52 走查修复**：移动端表单状态默认值 + 全站操作栏移末列，均已自测通过；此前：二维码改版 D50，main 待 deploy；D49 排课拖拽修复走查须强刷）

## 跨电脑续做流程（换电脑时按序执行）

1. 把本文件夹整体拷到新电脑（任意位置，如 `E:\贵州顺拓\demo`）
2. 文件夹内启动 Claude Code（新会话会自动读 CLAUDE.md → 本文件）
3. 按 `docs/SETUP.md` 第 1–6 节重建环境：Node 22 → Docker WSL 集成 → `nb init`（选择同款配置）→ 恢复 backups/ 最新 dump → dsl-reconciler 依赖与 symlink
4. 验证：`nb env list` 显示 dx-demo、应用 HTTP 200、models/collections 42 个 YAML 在位
5. 回到下方"当前位置"继续干活（所有进度以本文件 + TASKS.md checkbox 为准）

> 2026-11-09 已在新电脑（Windows 用户 Violet，路径 `E:\贵州顺拓\demo`）完成整套重建并验证：nb init + 恢复 stage1 备份 + push 幂等全通过。

## 当前位置

**公开扫码报名页上线（2026-11-09，D53）** — Violet 问「学员扫码时未登录怎么办」→ 拍板方案B 自制公开页。**本版本 anonymous 角色授权不能让无 token API 通过**（auth 中间件只认代码级 public 白名单，一律 EMPTY_TOKEN；public forms 是商业插件），故走「nginx public 静态页 `/signup.html?class=<id>` + `r_signup_bot` 窄权限角色（仅报名 create 字段白名单 + 班次 view，越权 403 实测）+ signup_bot 用户（id 7）10 年期 API key（apiKeys 插件 JWT，Bearer 走标准认证链）」：无头浏览器实测未登录全流程通——班次卡片显示班名+状态 → 填表 → 落库 pending → 触发报名审批流 ✓。产物 `.artifacts/public-signup/`（提交版占位符，真实 key `backups/public-signup-api-key.txt`）；备份 `nocobase_20261109_pre_public_signup.sql`；决策 D53。**待办：①main class-qr.tsx 二维码已改指公开页但未 build+deploy（`cd main && nb portal deploy main`，Violet 说了算）；②服务器重部署时 signup.html 须复制进服务器 nginx public 目录。**

**走查 bug 修复：报名待审空数据 + 操作栏列序（2026-11-09，D51/D52）** — Violet 报障两项已修并自测通过：①**报名待审页无新数据**根因 = 移动端 createForm 均未给 status 设默认值（此前测试数据是 API 带 status 造的，掩盖 bug），UI 提交落库 status 为空，待审 tab 按 status=pending 过滤查不到 → 4 个移动表单（报名/请假/材料/作业提交）各加 fieldValue 默认值规则（set-field-value-rules 全量替换，已有规则须一并回写），存量 2 条空 status 已 UPDATE 回 pending，无头浏览器闭环回归：UI 提交 POST 带 status:"pending" → 报名待审页可见 ✓；②**全站操作栏移最后一列**：45 处 flow-surfaces 表格块的 TableActionsColumnModel 原本全在第一列，moveNode 逐一移至末位（列序在 flowModelTreePath.sort，SQL 可全量定位），admin 报名待审页 + mobile 学员录实测表头操作栏已在末列 ✓。纯服务端配置改动，**前端刷新即生效**；备份 `nocobase_20261109_fix_status_actions.sql`；决策 D51/D52，逻辑见 docs/features/s6-mobile.md 补充节。

**阶段5 收口：周课表补拖拽 + 座位表自动排座修复（2026-11-09）** — Violet 修改 TASKS 阶段5 清单（不接入 AI）后逐项核对：排课画布/座位表/冲突检测+智能排课均满足，唯周课表缺拖拽 → 已补（拖课程卡到其他格调课，写 change_log「周课表拖拽调课」，与画布逻辑一致；调课不改 place）；座位表「按学号/年龄自动排座」按钮不生效根因 = applyAutoAssign filter 误用 `klass`（REST 层应为 `class_id`，400 被静默吞），连带把"全部学员往空位排"改为"只排未分配学员"避免一人两座。typecheck+7 单测过，build+deploy 完成（index-DVCDMnva.js，**走查须强刷**）；逻辑见 docs/features/s5-scheduling.md 补充节。**浏览器端走查待 Violet，通过后阶段5 可标 ✅。**

**二维码交互改版：弹窗直出 + 建班即得码（2026-11-09，D50）** — Violet 需求「点报名二维码直接展示、不跳转；创建班次时二维码一同创建好」。①admin 班次管理行操作改版：删旧 JSRecordActionModel（s5w1ecobnf2 window.open），建原生 popup 行操作 PopupCollectionActionModel（uid `d84vmbh85ma`，dialog 模式）+ 弹窗内 JSBlock（uid `d6jsr0yfxhv`，iframe 加载 `/x/main/qr?class=<id>`），点击当前页直接弹码（flow-system 禁止 runjs 直接 DOM 造弹窗，必须走 popup host + ctx.render，正规路径）；②/qr 页支持 `?class=<id>` 直查班次出码（保留 ?token 兼容），二维码只依赖班次 id → 新建班次保存后立即可弹码，不再依赖 qr_token；③修正报名页路径 bug：二维码内容改 `/v/mobile/3cfhfajaa4x?class=<id>`（mobile Portal 具体页面必须带 /v 前缀，此前拼 /mobile/... 会应用内 404「页面不存在」，Violet 实测发现）。配置产物 `.artifacts/qr-dialog/`。**待办：main Portal 改动（class-qr.tsx）需 `cd main && nb portal deploy main` 后生效（Violet 自测前部署）；弹窗行操作为服务端配置已即时生效。**

**排课画布拖拽落点 bug 修复完成（2026-11-09，D49）** — Violet 反馈"课程拖拽释放后，新位置不是鼠标所释放的位置"。数据取证定位：走查时浏览器加载的是旧构建（18:07），其拖拽写入 `2026-01-${4+day-1}T08:30:00.000Z`（日期基准差一天 + 北京钟面当 UTC 存）→ 回读解析成 16:30 → 节次/星期反算全错。修复三件套：①存量 25 条坏数据按 day_of_week（权威列）+ UTC 钟面还原节次重写，全表 29 条 start_time 与 day_of_week/节次全部自洽（含 14 条种子数据同源日期错位对齐 + 2 条 TZTEST 测试记录清理）；②api.ts `slotFromTime`/`dayFromTime` 改显式东八区（beijingClock 固定 +8h），不再依赖浏览器时区，演示机时区不同也不会错位；③pnpm build + `nb portal deploy main` 完成（bundle index-DN4vEZiv.js），typecheck + 7 单测过。**Violet 走查前必须 Ctrl+Shift+R 强刷**（浏览器缓存旧 bundle 会复现）。备份 `nocobase_20261109_fix_schedule_tz.sql`；逻辑见 docs/features/s5-scheduling.md 修复记录节。

**AI Portal 走查 bug 修复（2026-11-09，D47/D48）** — Violet 反馈"AI 模式页面无法选择班次"。无头浏览器（本机有 Playwright+Chrome，验证方式升级）复现定位：①**api.ts 双 unwrap bug**（D47）——`nocobaseClient.action` 默认 unwrap:"data" 已返回 data 本体，`listResource` 再取 `.data` 永远 undefined → 页面拿空数组；三个 helper 统一修复，覆盖 /qr + 周课表/排课画布/座位表（此前排课三页浏览器端同样坏，阶段5 只验证过 API 层）。②**AI Portal 角色授权**（D48）——阶段2 create-blank 基线 `!ui.*` 使非 admin 全部 403「无权访问此门户」，移动端课程表入口对学员是死链；5 角色各插 `rolesMultiPortals`（uid `__default_portal__`）打通。回归实测：/qr 下拉 4 班次 + 二维码生成 ✓；学员登录直达周课表、S2 scope 下自动选中本班、课节/冲突正常 ✓。main 已重新 build+deploy；备份 `nocobase_20261109_qr_signup.sql`（含授权记录）。

**班次报名二维码补做完成（2026-11-09，D46）** — 回应 Violet「班次的二维码在哪」：①AI Portal 新增 `/x/main/qr` 二维码页（main 源码 `src/features/qr/class-qr.tsx` + routes.tsx 注册 hidden 路由，qrcode npm 包本地生成、origin 自适应、可下载 PNG，依赖已装进 package.json）；②admin 班次管理页新增「报名二维码」行操作（JSRecordActionModel uid s5w1ecobnf2，window.open `/x/main/qr?token=<qr_token>`）；③移动报名页 createForm 加 fieldValue 规则 autoKlassFromUrl（uid mgyr71ht7sj）：URL `?class=<班次id>` 时自动选班次。typecheck/build/deploy 全过，/qr 与报名页均 200。备份 `nocobase_20261109_qr_signup.sql`；链路逻辑见 docs/features/s6-mobile.md 补充节。**服务器重部署时**：main Portal 源码已含 qr 功能，重新 build+deploy 或随 storage/portals 同迁即可。

**走查问题修复完成（2026-11-09，D43-D45）** — Violet 走查反馈 3 项已修：①6 个按 select value 分组的 chart（库存报表/学籍/考勤/请假/评估×2）改 custom visual + raw 中文映射（评估平均分 bar 含坐标轴中文化）；投票选项分布本身中文未动；②库存报表 chart+table 并排块统一 height 380 specifyValue；③logo 破图根因 = 附件匿名 401（nginx auth_request 拦 /storage/uploads），已给 anonymous 授 attachments view + logo 改走公开路径 /logo.png（attachments.id=1.url 已改，文件在 nginx public 目录），admin nickname 改「管理员」。配置改动备份 `nocobase_20261109_fix_charts_logo.sql`；蓝本产物 `.artifacts/nocobase-ui-builder/fix-charts/`。**服务器重部署时**：logo.png 须复制进服务器 nginx public 目录（D44），否则登录页 logo 仍破图。

**阶段6 移动端完成（2026-11-09）** — Portal `mobile`（no-code，/v/mobile，portalUid `__default_mobile__`）配学员核心 6 页：扫码报名（396774382895104）/请假申请（396774621970432）/材料提交（396774414352384）/学员录（396774630359040）/我的作业（396774636650496）/课程表 jsBlock 入口卡（396774655524864，window.open → /x/main/schedule/week）。r_student 补 12 条 route 授权 + nb_dx_material create；学员 API 实测 5 项全过（请假/材料/作业/报名/本班 scope）。蓝本 `.artifacts/nocobase-ui-builder/stage6-mobile/`；逻辑档案 `docs/features/s6-mobile.md`；备份 `nocobase_20261109_stage6_mobile.sql`。遗留：①公开扫码报名（未登录态）需 public forms，后置；②手机浏览器走查待 Violet。

**服务器部署完成（2026-11-09，D42）** — 内网机 `10.10.40.44`（Ubuntu 24.04，ops 用户）整体迁移：compose 双容器（nocobase 2.4.0-alpha.17-full + postgres:16）+ fresh dump + storage（portals/uploads/apps）随迁，`APP_KEY` 原样保留。验证全过：HTTP 200、Portal `/x/main/` hash 一致（index-Bcd5rqc0.js）、leader_test 登录 OK、班次 4/学员 21 数据无损。访问地址 **http://10.10.40.44:13000/**（账号密码与本机完全一致）。部署目录 `/home/ops/dx-demo/pkg`，步骤沉淀 SETUP.md 第 8 节，迁移包 `.artifacts/server-deploy/`。注意：服务器另有他人业务容器（5173/8080/28080），勿动。**阶段6 六页只在本机，服务器尚未同步（重部署时随 fresh dump 一并带走）。**

**并行待走查**：阶段5 三页（周课表 /schedule/week、排课画布 /schedule/board、座位表 /schedule/seats）已部署 http://127.0.0.1:13000/x/main/ ，拖拽走查待 Violet。**AI 交互未落地**：LLM 服务 0 配置，需 Violet 提供 key（D39）。

## 已完成

- [x] 确定方案：NocoBase v2 stable（2.2.41）+ Docker Desktop WSL 集成
- [x] demo 工作目录建立（本文件夹），PLAN/TASKS/dx.xlsx 从 test_demo 迁入并修正
- [x] 核实旧 test 配置不存在（`~/.nocobase/` 空），清理项跳过
- [x] 可移植性文档齐备（CLAUDE.md / README.md / SETUP.md / decisions.md）
- [x] nb CLI 2.2.41 安装成功（Node 升级至 v22.23.4 + 全局预装 skills 包，踩坑记录见 SETUP.md）
- [x] Docker Desktop WSL 集成启用；镜像加速源更换（USTC 已停服 → 1ms.run + daocloud，见 SETUP.md）
- [x] **nb init 完成**：应用运行于 http://127.0.0.1:13000（HTTP 200）
- [x] 首次备份：backups/nocobase_20261108_initial.sql（283KB）
- [x] 自建容器 dx-demo-pg（含 volume dx-demo-pgdata）已删除（Violet 确认）
- [x] **新会话验证通过**：`nb env list` / `nb env info dx-demo` 确认 app+DB running、OAuth 有效；Skills 加载正常
- [x] 修复：nvm default 原为 v20（v22 下其实装好了 nb），已 `nvm alias default 22` 固化
- [x] **阶段1 完成（2026-11-08）**：42 个 collections YAML 写入 `models/collections/` → dsl-reconciler 一次 push 成功 → 共 45 张表（含 3 个自动 m2m through），API 验证通过，备份 `nocobase_20261108_stage1_models.sql`
- [x] **新电脑重建完成（2026-11-09）**：Node 22.23.4 + nb 2.2.41 + nb init（env 仍名 dx-demo，Docker 源 + 内置库）→ 恢复 stage1 备份（无 error）→ dsl-reconciler 依赖 + symlink（新路径）→ push 幂等全 "="；镜像源换为 1ms.run + daocloud。注意：恢复备份后管理员账号回到旧电脑那套（Violet 保管），nb init 时新设的 admin 被覆盖
- [x] **阶段2 完成（2026-11-09）**：5 角色（r_leader/r_organizer/r_academic/r_teacher/r_student）+ 学员 3 个自定义 scope（S1 本人/S2 本班/S2b 班次，见 decisions D25）+ 5 测试账号（D27）；边界实测：学员 leave/news 200、purchase/student 403、越权 destroy 被拦、校领导 create 403；备份 `nocobase_20261109_stage2_acl.sql`。菜单 route 权限推迟阶段3（D24）；「只见本班」数据级验证待有演示数据后补（D26）
- [x] **阶段3-1 教学资源 7 库完成（2026-11-09）**：7 页挂「教学资源」组（routeId 396710905708544）——师资库/专题库/活动库/基地库/拟开发专题/教学案例/校外宣讲，均为 table + view/edit 弹窗；route 权限 leader/academic/student 各 15 条（组+页+tab），organizer/teacher 不授（无该 7 表权限）；蓝本 `.artifacts/nocobase-ui-builder/stage3-teaching-resources/`；备份 `nocobase_20261109_stage3_teaching_resources.sql`。踩坑：①`nb portal` 命令面 2.2.41 不存在，走 flow-surfaces legacy lane；②users m2o 显示列用 `.nickname` 不是 `.name`（apply-blueprint 会报 field-path-unknown）
- [x] **阶段3-2 教材管理 6 页完成（2026-11-09）**：「教材管理」组（routeId 396714401660928）——教材信息/教材采购/教材领用/教材退库/学员荐书/库存报表（chart 饼图 + 明细表，读回已确认 ChartBlockModel）；route 权限 leader/academic 各 13 条、student 5 条（组+教材信息+学员荐书），organizer/teacher 不授；蓝本 `.artifacts/nocobase-ui-builder/stage3-textbook/`；业务逻辑见 `docs/features/s3-textbook.md`；备份 `nocobase_20261109_stage3_textbook.sql`。新踩坑：①关联目标集合 >10 字段须给 defaults fieldGroups（nb_dx_class/nb_dx_student 15 字段）；②字段名 `date` 在生成 details 弹窗不计有效字段，标量 <4 的集合要给 view 动作显式 popup+fieldGroups（关联字段对象形式带 titleField）；③带 description 字段（stock）须 formBehaviorDescriptionReview，合法出口 `unsupported/ambiguous-description`；④多块 layout 各占一行被拒，须同 rows 数组；⑤测试账号须解绑内置 member 角色（decisions D29，否则 member 遮蔽 r_* 导致全菜单只读）
- [x] **阶段3-3 教务管理 5 页完成（2026-11-09）**：「教务管理」组（routeId 396723346014208）——班次管理/通知公告/教学计划/选修计划/教学资料，apply-blueprint 全部一次通过（教材模块 fieldGroups 方案预防性复用）；route 权限 leader/academic/student 各 11 条、organizer 9 条、teacher 7 条（选修计划/教学资料无 collection view 不授）；蓝本 `.artifacts/nocobase-ui-builder/stage3-academic/`；业务逻辑见 `docs/features/s3-academic.md`；备份 `nocobase_20261109_stage3_academic.sql`。新踩坑：①`desktop-routes list` 默认分页 20 条，验证须用 `--filter {"id":{"$in":[...]}}` 精确查；②`desktop-routes add` 纯增量，授错用 `remove` 回撤；③collection 权限查询正确命令是 `nb api acl roles data-source-resources get --role-name <r> --name <表> --data-source-key main --appends actions`（旧速查的 `data-source-resources get` 独立命令不存在）
- [x] **阶段3-4 班务管理 6 页完成（2026-11-09）**：「班务管理」组（routeId 396730107232256）——请假/外出报备/退学/考勤统计（chart 饼图+明细表）/党性考核（eval_record dataScope 过滤 party_self/party_review）/优秀学员（vote+vote_record）；route 权限 leader/student 各 13 条、organizer 11 条（无 vote_record 权限不授优秀学员）、academic 9 条（无 eval/vote 权限）、teacher 7 条（仅考勤/党性/优秀学员）；蓝本 `.artifacts/nocobase-ui-builder/stage3-class-admin/`（含生成脚本 gen_class_admin.py）；业务逻辑见 `docs/features/s3-class-admin.md`；备份 `nocobase_20261109_stage3_class_admin.sql`。新踩坑：①块级 defaultFilter 强制 `{logic,items}` 结构且 ≥3 个 filterable 字段，单字段过滤改用 `settings.dataScope.filter`；②chart 块必须显式 `assets.charts.<key>.query/visual`，count 聚合 `{"field":"id","aggregation":"count"}` 有效；③菜单树查询用 `nb api resource list --resource 'desktopRoutes:listAccessible' --no-paginate -j`（desktop-routes list 命令面不存在）
- [x] **阶段3-5 学员管理 5 页 + 综合门户 3 页完成（2026-11-09）**：「学员管理」组（routeId 396734674829312）——学员信息/学员相册/学籍管理（status 饼图）/学员档案/培训记录（各班次学员数柱状图，dimension 用关联路径 klass.name 一次通过）；「综合门户」组（routeId 396734888738816）——综合门户（双 chart+公告表）/班级主页/学员主页；8 页全部基于 nb_dx_student/class/announcement 单表多视角（D20）；**D30（Violet 确认）**：r_student 补 nb_dx_student view+S1b scope（id 396733982769152，filter user.id，与 S1 的 student.user.id 语义不同不可混用）；route 权限 leader/organizer/academic 各 18 条、teacher 16 条（无 leave 权限不授综合门户页）、student 12 条；蓝本 `.artifacts/nocobase-ui-builder/stage3-student-portal/`（含 gen_student_portal.py）；逻辑档案 `docs/features/s3-student-portal.md`；备份 `nocobase_20261109_stage3_student_portal.sql`。新踩坑：①bar 图 mappings 键是 x/y（pie 才是 category/value），报错 expectedShape 有提示；②rolesResourcesScopes 无 nb api 命令面，用 `curl POST /api/dataSources/main/rolesResourcesScopes:create`，绑定必须 `scopeId`，resource update 必须 `--filter-by-tk`

- [x] **阶段3-6 教学评估+投票问卷+统计图表 6 页完成（2026-11-09）**：「教学评估」组（routeId 396739781394432）——评估方案/专题评估（eval_record dataScope kind=topic）/综合评估（kind=comprehensive）/投票管理（仅 vote 主表，D31）/不记名问卷（survey+survey_answer 双 tab）/统计图表（4 chart：avg 评估均分柱图+count 评估分布饼图+投票选项柱图+问卷答卷数柱图）；route 权限 leader/teacher 各 14 条、organizer 9 条、student 10 条、academic 不授（6 表全无权限）；蓝本 `.artifacts/nocobase-ui-builder/stage3-eval-survey/`（含 gen_eval_survey.py）；逻辑档案 `docs/features/s3-eval-survey.md`；备份 `nocobase_20261109_stage3_eval_survey.sql`。新踩坑（D32）：①chart 块配置落 `flowModels.options.stepParams.chartSettings`（ChartBlockModel），uiSchemas 读不到，验证走 SQL like；②avg 聚合与 count 同构有效；③survey_answer 描述字段需 formBehaviorDescriptionReview（同教材 stock）

- [x] **阶段4 workflow 4 条审批流 + 待办 2 页完成（2026-11-09）**：请假（organizer 审批，approved 分支聚合 sum(duration_days) 超 class.total_days/7 → over_ratio=true）/退学（leader 审批，approved → 学员 status=dropout）/报名（academic）/缴费（academic），manual 节点 update 表单 + action 按钮预设 status（D33）；「审批待办」flowPage（396747054514176，4 tab dataScope status=pending）+「工作台待办」legacy page（396748572852224，WorkflowTodo 块，D34）；route 授权 leader/organizer/academic 各 6 条（两页）；请假全流程 + 超限提醒 API 实测通过；脚本 `.artifacts/nocobase-workflow/s4-workflows/gen_workflows.py` + 蓝本 `s4-todo-page.json`；逻辑档案 `docs/features/s4-workflow.md`；备份 `nocobase_20261109_stage4_workflow.sql`。新踩坑：①manual forms 手写结构（type=update + filter 变量 + action values 预设 + job status 恒 1）；②manual task submit 在 execution 刚创建几秒内会 400，重启应用可解（正常节奏不复现）；③已执行 workflow 节点锁死，须 revision（带 key）改新版；④测试审批把 assignees 临时换 admin(1)，测完 revision 改回

- [x] **升级至 NocoBase 2.4.0-alpha.17 启用 AI Portal（2026-11-09，D36）**：决策链 2.2.41（无 Portal）→ 2.3.0-beta（也无，Portal 是 3.x 功能）→ Violet 拍板走真 Portal → 实测 2.4.0-alpha.17 即有完整 `nb portal` 命令面 + multiPortal=true，不必跳 3.0。两次升级前 pg_dump（`nocobase_20261109_pre_upgrade_2_3_beta.sql` / `nocobase_20261109_pre_upgrade_3_alpha.sql`）；`nb app upgrade --version X --force` 已知坑：--version 只拉镜像不切容器，须再跑一次 `--skip-download --force` 才切换；**--skip-download 的后遗症**：入口 index.html 嵌入的 publicPath 残留旧版本号（/dist/2.4.0-alpha.17/dist/2.3.0-beta.21/ 全 404），表现为升级后 /admin 所有页面卡 Loading 打不开，`nb app restart` 重新生成入口 HTML 即修复（2026-11-09 实测，无需重装 dist）。升级后 45 表/4 workflow/90 路由无损；`nb portal pull main` 拉源码到 `demo/main/`（pnpm install 约 8 分钟）。undici@8 与 node20 坑：jsdom 30 需 Node 22+，bash 前必 `source ~/.nvm/nvm.sh && nvm use 22`（钉了 pnpm override undici=7.30.2 无害）

- [x] **部署内网服务器（2026-11-09，D42）**：10.10.40.44 compose 双容器整体迁移，全量验证通过；地址 http://10.10.40.44:13000/ ；步骤见 SETUP.md 第 8 节

- [x] **阶段5 课表/排课/排座三页代码完成（2026-11-09）**：Portal main「教学排课」组（/schedule）——周课表（7×5 表格+冲突高亮+冲突提示卡）、排课画布（拖专题排课、拖课调课写 nb_dx_change_log、智能排课贪心版）、座位表（6×8 初始化、拖拽换座/清座、按学号/年龄自动排座 diff 保存）；`registryRoutesEnabled=false` 关模板 demo 路由。纯逻辑（detectConflicts/autoAssignSeats）与 UI 分离，单测 7 用例全过 + typecheck + eslint 通过；API 形态对齐 D37（body 平铺/filterByTk/class_id+class 关联名）。已 deploy（页面 hash 读回确认）；逻辑档案 `docs/features/s5-scheduling.md`；备份 `nocobase_20261109_stage5_scheduling.sql`。遗留：①浏览器拖拽走查待 Violet；②AI 交互未落地（无 LLM key，D39）；③服务端冲突校验 workflow 后置

## 实际安装方式与原计划的差异（重要）

Violet 在 nb init 向导中实际选择了 **Docker 源 + 内置数据库**（原计划 npm 本地跑 + 自建 dx-demo-pg）：

| 项 | 实际状态 |
|---|---|
| 应用运行时 | Docker 容器 `nb-dx-demo-app`（nocobase/nocobase:latest-full，端口 13000） |
| 应用数据库 | Docker 容器 `nb-dx-demo-postgres`（用户/库/密码均为 `nocobase`，端口不映射宿主机，nb 托管） |
| 认证方式 | OAuth 设备登录（非账密）；CLI 已建 env `dx-demo`（auth=oauth） |
| demo/ 内应用目录 | **无**（应用在容器内；demo/ 只放文档/备份/产物，可移植性不受影响） |
| 自建容器 dx-demo-pg | **已删除**（Violet 确认清理，含 volume dx-demo-pgdata） |

## 下一步（按序）

1. **Violet 浏览器走查**（三项一起）：①阶段6 移动端 6 页（手机浏览器开 http://127.0.0.1:13000/v/mobile 或 /mobile，学员 student_test 登录，逐页点；课表入口应打开 /x/main/schedule/week）；②阶段5 三页拖拽（冲突演示对在第1周周三第1节）；③演示脚本走查（组织员建班→学员扫码报名→审核→请假→排课→评估→统计，测试账号见 D27，密码 dx123456）。发现问题回报芒果怪修
2. **服务器同步阶段6**：走查通过后按 SETUP.md 第 8 节重打包（fresh dump 含阶段6 页面）
3. AI 交互（D39）：Violet 提供 LLM key（任意 OpenAI 兼容/Anthropic 服务）后，用 `nb api ai llm-services` 配置，再给排课画布加"冲突智能解读"类交互
4. （可选后置）公开扫码报名：public forms 未登录报名链接（班次 qr_token 已备）

### 阶段7 速查（续做直接用）

- 演示数据脚本：`.artifacts/stage7-demo-data/gen_demo_data.py`（幂等保护：teacher/seat/textbook 非空即退）；重灌须先恢复备份
- 演示数据全景与约定：`docs/features/s7-demo-data.md`（冲突演示对位置、请假超限闭环、workflow 联动、REST 认证头等 6 条踩坑）
- REST API 认证：`Authorization: Bearer <token>` + `X-Authenticator: basic`（仅 X-Token 会 401）
- 测试账号（D27）：leader_test/organizer_test/academic_test/teacher_test/student_test，密码 dx123456；学员1 张明远绑 student_test
- 阶段2 遗留 D26 已关闭（2026-11-09 实测）

### 阶段6 速查（续做直接用）

- 移动端入口：http://127.0.0.1:13000/v/mobile（/mobile 也通）；6 页 routeId 见 docs/features/s6-mobile.md 表格
- mobile Portal 蓝本规则：navigation 只带 `portalUid: "__default_mobile__"` + `item.icon`；omit group/layoutUid
- 蓝本新踩坑：①关联目标 >10 字段的 fieldGroups 挂**目标表**键下且须覆盖全部生成字段（student 15 字段含 user）；②m2o 字段须对象形式 `{"field","titleField"}`（users 用 nickname）；③多块 layout 不许每块独占一行（同行 span 12）；④蓝本不支持 js action `clickSettings`，JS 逻辑用 jsBlock（settings.code，strict render 必须 ctx.render）
- 学员验证数据：leave#8（pending，进审批流）、material/submission/registration 各 1 条（2026-11-09 实测产生，可当演示数据用）
- 公开扫码报名未做（登录态报名页替代，public forms 后置）

### 阶段5 速查（续做直接用）

- Portal 源码 `demo/main/`（developmentPath）；改完 `cd main && pnpm build && nb portal deploy main`（deploy 会重跑 build）
- 验证部署版本：`curl -s http://127.0.0.1:13000/x/main/ | grep -o 'assets/index-[^"]*\.js'` 对比本地 dist 的 index-*.js hash
- API 形态（D37）：body 平铺 / update `?filterByTk=` / filter `class_id` / appends `class,topic,teacher,student`；CLI 侧 `nb api resource list --resource nb_dx_xxx --filter '{"class_id":1}' --appends class -j`
- 课表占位日期固定 2026-01-04（周一）起；day_of_week 权威
- 跑测试/构建前必 `source ~/.nvm/nvm.sh && nvm use 22`（jsdom 需 Node 22+）
- 模板测试 `tests/components/route-overlay-viewport.test.tsx` 持续失败 = portal-sdk 与模板版本上下文不兼容，非本次代码问题，可忽略
- 演示数据现状（2026-11-09 阶段7 灌入）：4 班次（班1 中青班 ongoing / 班2 可报名 / 班3 计划 / 班4 历史）、班1 学员 16 人、专题 12、课表 29 节、座位 48（学员 1-16 已就座）；冲突演示对 = 第1周周三第1节同占第一报告厅两节
- 座位初始化已加保护：未选班次不允许初始化（Violet 实测踩中，48 个 class_id=0 废座位已清理）

### 阶段4 速查（续做直接用）

- workflow 列表/读回：`nb api workflow workflows list --filter '{"current":true}' -j`；节点链 `workflows get --appends nodes`
- 当前启用版本：请假流 v2 `396745412444160`（assignees [3]）、退学流 v2 `396746379231232`（[2]）、报名流 `396743046660096`（[4]）、缴费流 `396743055048704`（[4]）
- manual task API：待办 `workflowManualTasks:listMine`；提交 `workflowManualTasks:submit`（filterByTk=taskId，body `{"result":{"<formKey>":{...},"_":"<actionKey>"}}`）；submit 400 → 重启 nb-dx-demo-app
- 测试数据：班次 1「第1期中青班」total_days=21；学员 1 挂班 1；leave#3/#4 为已批演示记录

### 阶段3 建页速查（续做直接用）

- 菜单组 routeId：教学资源 `396710905708544`、教材管理 `396714401660928`、教务管理 `396723346014208`、班务管理 `396730107232256`、学员管理 `396734674829312`、综合门户 `396734888738816`、教学评估 `396739781394432`（自建组写法 `group:{title,icon}` 不带 routeId）
- 命令模板：`nb api flow-surfaces apply-blueprint --body-file <json> -j`（legacy lane 用 `navigation.layoutUid: "admin-layout-model"`，已有组用 `navigation.group.routeId`）
- 蓝本踩坑详见 `docs/features/s3-textbook.md` 末节（fieldGroups/date 字段/descriptionReview/layout 四条）+ `docs/features/s3-academic.md` 末节
- route 授权：`nb api acl roles desktop-routes add --role-name <r> --body-file <ids数组json> -j`（纯增量，授错用 `remove` 回撤）；读回验证必须加 `--filter '{"id":{"$in":[...]}}'`（默认分页 20 条会漏）
- 角色实测放行不能用 X-Role 覆盖（会报 ROLE_NOT_FOUND_FOR_USER，admin 无该角色），要用 `data-source-resources get --role-name <r> --data-source-key main --name <表> --appends actions -j` 查配置

### 阶段2 遗留（不阻塞阶段3）

- 「学员只见本班」数据级验证：阶段7 造演示数据后补测（decisions D26）
- 菜单 route 权限：阶段3 每页面同步配（decisions D24）

## 阶段1 产物位置（重要）

| 项 | 位置 |
|---|---|
| 42 个 collections YAML（源） | `models/collections/*.yaml` |
| dsl-reconciler workspace | `~/.agents/skills/nocobase-dsl-reconciler/workspaces/dx-demo` → **symlink 指向 demo/models/**（state.yaml 落在 demo/models/） |
| push 命令 | `cd ~/.claude/skills/nocobase-dsl-reconciler/src && NB_TOKEN=$(取自 ~/.nocobase/config.json envs.dx-demo.auth.accessToken) NB_URL=http://127.0.0.1:13000 npx tsx cli/cli.ts push dx-demo --force --copy`（需 Node 22：先 `source ~/.nvm/nvm.sh && nvm use 22`；src 需先 `npm install`） |
| 注意 | token 过期后先跑 `nb env auth dx-demo` 刷新 |

## 本机环境差异记录（换电脑时对照 SETUP.md 重建）

| 项 | 本机状态 |
|---|---|
| OS | Windows + WSL2（Ubuntu，WSL 用户 mxr；Windows 用户 Violet） |
| 项目路径 | `E:\贵州顺拓\demo`（WSL `/mnt/e/贵州顺拓/demo`） |
| Node | v22.23.4（nvm default；nb 要求 Node 22+） |
| nb CLI | ✅ 2.4.0-alpha.17（alpha 渠道；2.2.41→2.3.0-beta→2.4.0-alpha.17，D36）；已全局预装 skills 包 |
| npm registry | 官方源（访问偏慢，Node 22 下载约 10 分钟） |
| Docker Desktop | WSL 集成已启用；镜像加速源 1ms.run + daocloud（2026-11-09 替换旧源） |
| NocoBase | ✅ 2.4.0-alpha.17，容器 nb-dx-demo-app @ http://127.0.0.1:13000（Portal main 部署于 /x/main/，源码 demo/main/） |
| 应用数据库 | 容器 nb-dx-demo-postgres（nocobase/nocobase/nocobase） |
| 管理员账号 | 来自 stage1 备份恢复（旧电脑 Violet 自设，账号密码由 Violet 保管） |
| 备份命令 | `docker exec nb-dx-demo-postgres pg_dump -U nocobase nocobase > backups/<文件名>.sql` |

## 阶段完成总览

| 阶段 | 状态 | 备份文件 |
|---|---|---|
| 0 接入 | ✅ | nocobase_20261108_initial.sql |
| 1 建模 | ✅ | nocobase_20261108_stage1_models.sql |
| 2 ACL | ✅ | nocobase_20261109_stage2_acl.sql |
| 3 PC 管理端 | ✅ 38 页全完成（教学资源 7 + 教材 6 + 教务 5 + 班务 6 + 学员 5 + 门户 3 + 评估问卷统计 6） | nocobase_20261109_stage3_eval_survey.sql |
| 4 workflow | ✅ 4 条审批流 + 待办 2 页（请假/退学/报名/缴费 + 审批待办 + 工作台待办） | nocobase_20261109_stage4_workflow.sql |
| 5 AI Portal | 🔄 代码完成待浏览器走查（三页已部署 /x/main/；AI 交互待 LLM key） | nocobase_20261109_stage5_scheduling.sql |
| 6 移动端 | ✅ 学员核心 6 页完成（手机浏览器走查待 Violet；公开扫码后置） | nocobase_20261109_stage6_mobile.sql |
| 7 收尾 | 🔄 演示数据 ✅（41 表全覆盖 + D26 关闭）；演示脚本走查待 Violet | nocobase_20261109_stage7_demo_data.sql |
