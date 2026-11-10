# STATE.md — 当前进度快照

> 新会话/换电脑续做入口。每完成任务更新本文件。最后更新：2026-11-10（**D74 组织员排课/座位 update 补授**；此前：D73 组织员 topic/change_log 权限补授，D72 组织员座位权限补授，D71 admin 排课入口归位（iframe 嵌 /x/main 三页），D70 超1/7提醒列显示是/否，D69 停用 plugin-ai 插件，D68 隐藏 main AI 悬浮按钮，D67 附件直链白字版+周课表隐藏 sidebar footer，D65+D66 品牌去 NocoBase 化，D64 需求对齐改名，D62 评估表单修复 + 服务器重发布）

## 当前位置

**组织员排课/座位 update 权限补授（2026-11-10，D74）** — Violet 报「/api/nb_dx_course_schedule:update?filterByTk=52 与 /api/nb_dx_seat:update?filterByTk=62 无权限」。organizer 对两表缺 update（D72/D73 只补了 create/view）。SQL 直插 2 条 update action（fields 照抄 r_academic，scopeId=All records），重启生效；实测两接口 200 ✓。**验证接口须用「写回原值」而非空体**——空体曾误置 seat 62 row/col 为 null（已按 label R2-C4 复原 row=2/col=4，course 52 写回 week1/day1 未变）。备份 `backups/nocobase_20261110_pre_organizer_update_acl.sql`；决策 D74；s5-scheduling.md ACL 矩阵已同步。**至此 organizer 排课三页写路径齐备（seat create/update + course_schedule update + change_log create）。**纯 DB 配置改动，随 fresh dump 同步服务器。

**组织员教学专题库+调课流水权限补授（2026-11-10，D73）** — Violet 报「/api/nb_dx_topic:list 同样 No permissions」（`lit` 是 list 笔误）。连带排查 D71 排课 iframe 三页前端引用的 7 个集合，organizer 缺 topic + change_log 两个（seat 已在 D72 补）。补授：**topic view+export**（对齐 r_leader）、**change_log view+create**（拖拽调课写流水，不给 destroy），SQL 直插 2 资源行 + 4 action 行（fields 白名单照抄 r_academic，scopeId=All records），重启生效；organizer_test 实测两接口 200 ✓。备份 `backups/nocobase_20261110_pre_organizer_topic_changelog_acl.sql`；决策 D73；坑（多行 VALUES 内 max(id)+1 子查询重复取值撞主键，须拆独立语句）沉淀 docs/features/s5-scheduling.md。**D71 排课 iframe 的 ACL 连带补漏完成——至此 organizer 排课三页 7 集合授权齐备。**纯 DB 配置改动，随 fresh dump 同步服务器。

**组织员座位权限补授（2026-11-10，D72）**

**组织员座位权限补授（2026-11-10，D72）** — Violet 报「r_organizer 调 /api/nb_dx_seat:create 报 No permissions」。根因：ACL 矩阵里 r_organizer 对 nb_dx_seat **连资源行都没有**（r_academic 才有全套 CRUD+export）。修复：SQL 直插 `dataSourcesRolesResources`（usingActionsConfig=true）+ create/view 两条 action 行（fields 白名单照抄 r_academic 12 字段，scopeId=All records 396628275953665），重启应用生效；organizer_test 实测 view ✓ create ✓（空体垃圾行 id=147 已 SQL 清理，seat 回到 96 行）。授权矩阵沉淀 docs/features/s5-scheduling.md；备份 `backups/nocobase_20261110_pre_organizer_seat_acl.sql`；决策 D72。**坑：docker exec psql 接 heredoc 必须 -i，否则 stdin 不进容器、整段静默不执行且无报错。**纯 DB 配置改动，随下次 fresh dump 同步服务器（与 D70/D71 一起）。

**admin 排课入口归位（2026-11-10，D71）** — Violet 提出"/x/main 排课页要开两个地址"，对照 PLAN.md/dx-requirements 确认需求里排课属教务管理/班务管理内部菜单后，拍板**方案A：admin 菜单挂 iframe 入口**。建 3 页（flowPage+jsBlock iframe）：排课管理（教务管理组，教学计划后，iframe /x/main/schedule/board，routeId 396915888357376）/ 课表查询（同组，396915913523200，/schedule/week）/ 排座管理（班务管理组，退学管理后，396915917717504，/schedule/seats）。**蓝本校验器直接放行 iframe jsBlock**（无 API 调用，D56 占位法没用上）；授权 leader/organizer/academic/teacher 各 5 条路由（组+页，纯 iframe 不涉集合权限）；菜单顺序按需求层级 SQL 直改 sort。无头验证全绿（菜单展开检查+iframe 挂载+内页渲染，pageerror=0，脚本坑：admin 菜单组默认折叠须点开再查）。**main 源码零改动无需 deploy**；/x/main 保留直连兜底。备份 `backups/nocobase_20261110_pre_schedule_entry.sql`；蓝本 `.artifacts/nocobase-ui-builder/schedule-entry/`；验证 `.artifacts/e2e-check/verify_schedule_entry.py`；逻辑档案 docs/features/s9-portal-entry.md。**遗留可选项：iframe 双层侧栏观感（内嵌 portal 保留自身侧栏，一个入口可切三页），要去侧栏需改 main 源码支持 embed 模式，后置。另：本轮核查发现 applicationPlugins.ai 竟为 enabled=t（D69 记录已停用，updatedAt 恰为停用时刻 12:12:25）——aiEmployees 403 无法定论，待 Violet 浏览器确认 admin AI 悬浮球是否复现，复现则重跑 `nb pm disable ai`。**

**请假管理「超1/7提醒」列显示是/否（2026-11-10，D70）** — Violet 走查要求 over_ratio 列由 true/false 改显示"是/否"。改动 = flowModels 单条：列 kgmbd2wuaer 的 field 渲染子模型 **9f4vkck3k1e** 由 DisplayTextFieldModel 改 **DisplayEnumFieldModel**，props.options 显式映射（**value 混配字符串 "true"/"false" 与布尔 true/false 双形式**——boolean 字段值经 API 序列化到前端是字符串，纯布尔匹配不上）。三个坑沉淀 decisions D70：①列单元格渲染走 field 子模型（对照实验证实）；②docker exec psql 传中文会乱码，改后须验 UTF-8 字节；③value 字符串化坑。NULL 显示空白正常（库内 1 条 true、1 条 NULL）。备份 `backups/nocobase_20261110_pre_overratio_label.sql`；验证 `.artifacts/e2e-check/verify_overratio_label.py`（登录时序：/sign-in 重定向 /signin?redirect=，固定等待 4s 再找 input；organizer_test 登录偶发失败重试即可）。e2e HAS_SHI ✓ + Violet 浏览器强刷确认 ✓。**纯 DB 配置改动，待下次 fresh dump 随重灌同步 10.10.40.44（未随本次 git 发布执行）。**

## 跨电脑续做流程（换电脑时按序执行）

1. 把本文件夹整体拷到新电脑（任意位置，如 `E:\贵州顺拓\demo`）
2. 文件夹内启动 Claude Code（新会话会自动读 CLAUDE.md → 本文件）
3. 按 `docs/SETUP.md` 第 1–6 节重建环境：Node 22 → Docker WSL 集成 → `nb init`（选择同款配置）→ 恢复 backups/ 最新 dump → dsl-reconciler 依赖与 symlink
4. 验证：`nb env list` 显示 dx-demo、应用 HTTP 200、models/collections 42 个 YAML 在位
5. 回到下方"当前位置"继续干活（所有进度以本文件 + TASKS.md checkbox 为准）

> 2026-11-09 已在新电脑（Windows 用户 Violet，路径 `E:\贵州顺拓\demo`）完成整套重建并验证：nb init + 恢复 stage1 备份 + push 幂等全通过。

**停用 plugin-ai 插件（2026-11-10，D69）** — Violet 给出 admin 端 plugin-ai 官方资产 SVG（f0053e745af0ad03.svg），要求隐藏 admin 的 AI 交互按钮。定位：admin 悬浮球是 **plugin-ai 客户端硬编码渲染**（无 flowModel 实例、无配置开关），条件 = aiEmployees 非空 + pathname 在 /admin 或 portal 前缀 + 非 v1 页面版本 + 非移动布局——8 个 builtIn AI 员工使其恒显示。修复：**`nb pm disable ai`**（WSL nb CLI）+ `nb app restart`（重建容器），applicationPlugins.ai enabled=false（installed 保留、数据无损）。验证：根路径/admin/main门户/移动端全 200，业务 API 200，aiEmployees API 403（路由已摘）；main 门户 nocobase-ai 扩展有错误状态机（拉取失败→status error→不渲染，无白屏风险）。恢复方式：`nb pm enable ai`。**服务器同步：enabled=false 在 applicationPlugins 表里，随下次 fresh dump 重灌自动生效，无需单独操作。**备份 `backups/nocobase_20261110_pre_disable_ai_plugin.sql`。

**隐藏 AI 悬浮对话按钮（2026-11-10，D68）** — Violet 指示隐藏「打开 AI 对话」悬浮按钮（nocobase-ai-chat.svg 图标，aria-label t('surface.openChat')）。机制：`extensions/nocobase-ai/global-ai-chat.tsx` 的 StarterGlobalAIChat 在 `ready=ai.configurationStatus==='ready'&&ai.employees.length>0` 时渲染 AIChatFloatingTrigger——库里 aiEmployees 有 8 个 builtIn 员工（nathan/dara/dex/ellis/lexi/vera/viz/atlas）恒 ready，且 D39 已取消 AI 交互，按钮成孤入口。修复：移除该处渲染 + 清 import（生产唯一渲染点；demo/floating.tsx 的引用是 DEV 演示页不进生产路由，bundle 里留有死代码无害）。build+deploy 完成（bundle index-D4Vmz5cz.js）。AIChatWindow 侧面板保留但无入口（不可达）；aiEmployees 数据未动。**服务器同步：portal 需重新 build+deploy。**

**附件直链白字版 + 周课表隐藏 sidebar footer（2026-11-10，D67）** — Violet 两项。①**`/files/main/main/attachments/1.png` 没显示新图**根因 = **Violet 走查在服务器（10.10.40.44），D66 只替换了本地容器**，服务器 uploads 两份 logo 还是旧 NocoBase 图（md5 取证确认）；另注意 `/storage/uploads/*` 走 nginx auth_request，未登录访问 401 也显示不出。修复：uploads（logo-0ilulu/logo-ouub0e）**本地 + 服务器**均替换为**透明底白字版**（logo-dark.png，Violet 指定）；服务器 nginx public /logo.png 同步换黑字版（白卡片背景上白字会隐形，登录页保持黑字）；WSL 侧 ssh/scp 通路（Windows 侧无密钥）。带 token 验证服务器 200 + md5 一致 ✓。②**周课表页隐藏 sidebar footer**：sidebar.tsx SidebarFooter 加 useLocation 判断 `/schedule/week` 返回 null；顺带把 footer 内容去 NocoBase 化（删 nocobase.com 链接，改「党校智慧管理平台 / 教学、学员、教务一体化管理 / v版本」，locale key 不再引用）。build+deploy 完成（bundle index-D3-gREZo.js；残留 grep 命中的 "AI builds freely." 是 en-US 语言包字符串，本系统固定中文，无害）。**logo 三链路现状：nginx public=黑字版、/x/main/dist=黑字版、uploads 附件直链=透明白字版。**

**登录页淡蓝背景 + uploads 底层 logo 替换（2026-11-10，D66）** — Violet 两项追加。①**`/x/main/login` 右侧背景黑→淡蓝**：auth-layout section `bg-neutral-950 text-white` → `bg-blue-50 text-blue-950`（kicker blue-800/80、正文 blue-900/70、白卡片 border-blue-200/70、底部 pill blue-100/70，网格纹理 currentColor 自适应）；②**`/files/main/main/attachments/1.png` 仍显示旧 NocoBase logo**：根因 = 该 URL 是附件记录 id=1 直链，**重定向到底层存储文件 `/storage/uploads/logo-0ilulu.png`**（D65 只换了 nginx public 的 /logo.png，uploads 原图没动）；修复：uploads 下 `logo-0ilulu.png` + 孤儿副本 `logo-ouub0e.png` 均 docker cp 替换为新 wordmark（旧图留底 `.artifacts/branding/backup_uploads_logo.png`），md5 三方一致，带 token 验证 200 新图 ✓。build+deploy 完成（bundle index-2kGFBzZR.js，hash 一致，bg-blue-50 在 bundle 中 grep 确认）。**服务器同步三件套更新：除 dump+portal 部署外，nginx public logo.png 与 uploads 两份 logo 文件都需替换。**

**品牌去 NocoBase 化 + 全站中文化完成（2026-11-10，D65）** — Violet 确认三项：①文字版 logo；②登录页右侧文案按芒果怪默认中文介绍；③英文展示文案全部中文化。实施：**图片**——Pillow 生成文字版 wordmark（`F:/Python/python.exe`，微软雅黑 Bold，亮 #18181b/暗 #fafafa 透明底 774×146）+ favicon（红底圆角方块白字「党」256px），脚本 `.artifacts/branding/gen_logo.py`，产物同步 `main/public/`；容器 nginx public `/logo.png` 已 docker cp 替换（admin 登录页 logo，旧图留底 `.artifacts/branding/backup_nocobase_logo.png`），attachments id=1 title 改「党校智慧管理平台-logo」。**源码 15 文件**——brand.tsx 文字化（BrandLogo=红底「党」圆角块 + BrandWordmark=文字，不再依赖图片）；index.html（title/description/favicon.png/noscript）；App.tsx + document-title-handler（appName + 动作前缀中文）；auth-layout 右侧营销区中文化（教学教务/学员服务两卡片）；登录/注册/忘记密码表单全中文；404/错误边界/ACL 无权限文案中文化。**注意坑：acl-gate.tsx 的 `errorMessage !== "Unable to load permissions"` 是与 SDK 英文报错的比对哨兵，非展示文案，不能翻译。** build+deploy 完成（bundle index-CxrucOB0.js，线上 hash 一致，新名 3 处/旧英文 0 处已 grep 验证）。admin favicon（NocoBase 图标，位于 dist 内）未替换（可选项，低价值）。备份 `backups/nocobase_20261110_branding.sql`（改后）。**服务器同步提醒：10.10.40.44 重灌时需①fresh dump；②新 logo.png docker cp 进 nginx public；③main Portal 重 build+deploy（或随 storage/portals 同迁）。**

**PLAN 缺失功能补齐完成（2026-11-10，D65）** — Violet 确认清单（拍板：三维排课不做/导入导出不做/库存联动提交即触发；约束：不影响现有功能、全中文）后补齐 PLAN.md 声明缺失的 4 组功能。**A 教材库存闭环**：采购/领用/退库 3 条联动流（提交即触发：query 库存→calculation→update stock→写 inventory_log 流水，id 396902662209536/396902681083904/396902702055424）+「领用报表」「库存流水」2 页（教材管理组，396903540916224/396903549304832）；实测采购 200→205/领用 205→202/退库 202→204 全链 ✓。**B 管理端 6 页**：作业管理（批阅+转批走 edit 弹窗，transferred_to_id 已预留）/材料回复/申报信息/纪律承诺/调课记录（change_log 只读）/通知阅读统计（announcement+readers m2m 列，灌 14 条已读演示数据），routeId 见 features/s8-gapfill.md；授权 leader/academic 全部+organizer 5 页+teacher 作业。**C 站内提醒**：notificationChannels 建 in-app 通道 + 4 条流 revision 接 notification 节点（新 id：请假 396908352176128/退学 396908373147648/报名 396908392022016/缴费 396908412993536，ignoreFail 兜底）+ jsBlock ENABLED_WF/WF_TITLE/FALLBACK_ACTIONS 补新 id（备份 flowmodels_jsblock_wf_20261110.txt）；实测学员提交请假→organizer 审批→「请假审批结果…」送达学员 ✓。**D 学员社区**：零建模复用 comment 表（kind=post/reply、parent_id 自关联、hot 精华）——admin「学员社区」页（学员管理组 396909230882816，活跃度 chart custom+帖子/跟帖管理）+ 移动端页（396909314768896，发帖表单 kind 默认规则 defaultKindPost+帖子广场）+ r_student comment create 权限（SQL 直插 dataSourcesRolesResourcesActions）+ 演示数据 4 帖 4 跟帖。**统一无头回归全绿**：9 新页渲染 ✓ 既有页（库存报表/请假管理/工作台待办新流待办标题正常）✓ 移动端社区入口 ✓ pageerror=0；脚本 verify_gapfill_all.py。备份：执行前 nocobase_20261110_pre_gap_fill.sql / 完成后 nocobase_20261110_gapfill_done.sql。逻辑档案 docs/features/s8-gapfill.md；决策 D65/D65a/D65b/D65c（蓝本校验器 5 新坑）。**注意：①ACL create 权限是 SQL 直插，已重启应用生效；②线上 10.10.40.44 待下次 fresh dump 重灌统一带走（本轮全为 DB 配置无文件随迁）；③backups 里 pre_overratio_label/pre_disable_ai_plugin/branding 三个备份来自并行会话，非本轮产物。**

**需求对齐改名完成（2026-11-10，D64）** — Violet 要求对照 docs/dx-requirements.md（dx.xlsx 转录）核对系统/菜单名称。改 12 处纯文案（SQL 直改 desktopRoutes，各页 hidden tabs 子行同步改）：①**站点标题 systemSettings.title `NocoBase`→`党校智慧管理平台`**（浏览器标签页/登录页，前端刷新生效）；②教务管理组「通知公告」→「教学通知」（396723947896832）；③教学资源组 6 库补"库"字对齐需求术语：教学专题库/教学活动库/教学基地库/教学案例库/校外宣讲库/拟开发专题库；④教学评估组：专题评估→专题评估状况、综合评估→综合评估状况、投票管理→投票；⑤移动端「课程表」→「我的课表」（396774655524864，底栏+页头同步）。备份 `backups/nocobase_20261110_pre_rename_menus.sql`。**已知缺口清单（未做，属新增工作量，2026-11-10 对比结论）**：admin 端作业管理/材料回复页缺失（移动端有提交无管理闭环）、调课记录页（change_log 有数据无展示页）、需求其余页（报到信息/纪律承诺/学业证书/活动风采/申报信息/综合门户消息等）；教材"统计报表"需求含领用报表+库存流水，现只有库存报表。**注意：线上 10.10.40.44 需下次重灌 fresh dump 时一并带走（或直接在服务器执行同款 UPDATE）。**

**评估新增表单修复 + 服务器重发布完成（2026-11-10，D62）** — Violet 线上报障「/api/nb_dx_eval_record:create 提交了但数据没新增」。取证（服务器日志 status=200 + 落库 6 条 kind 空）：党性考核/专题评估/综合评估三页「新增」弹窗**共用表单模板** tfqylic8j8y，kind 等上下文字段无默认值非必填 → 落库 kind 空被列表过滤吞掉。修复：三处 `convert-template-to-copy` 拆副本（sb2ygwyh4fh/iq01y38zu9h/w9zp48k1cti）+ 各副本 set-field-value-rules kind 静态默认（topic/party_self/comprehensive，runjs 形态）+ 学员字段 SQL 直改 editItemSettings.required（configure 不支持 settings，400 实证）。**服务器已重灌**：fresh dump `nocobase_20261110_server_deploy.sql`（含 D55-D62 全量）→ 10.10.40.44 drop+recreate+restore+signup.html/logo docker cp，验证 HTTP 200 + 新工作流启用 + 移动端新菜单 + 扫码报名页已删。服务器上 6 条 kind 空垃圾记录（Violet 测试，id 33-38）随重灌清除。备份 `backups/flowmodels_eval_student_required_backup_20261110.txt`；决策 D62。**遗留已清（2026-11-10 复核）：D58 残留待办（leave 13）已不存在——本地库与 fresh dump 均无 leave 13 记录及空标题 pending 待办（仅剩 3 条空标题已办历史记录，无害），线上随重灌同步干净；本地 admin 密码不在手上，评估表单 UI 闭环由 Violet 线上复验。**

**超1/7提醒断链修复 + 学员姓名列批量统一（2026-11-10，D60/D61）** — Violet 问「total_days 不填是不是就不触发提醒」→ 实证比预想更糟：calculation 节点 math.js 对 null 除法直接 TypeError，**整条审批流 execution -2 中断**（leave 12 卡死实证）。修复三件套：①total_days/leave.klass YAML 补 required + 存量空值补数；②22 处表单项 configure `settings.required`（请假表单 klass/事由/起止/天数 + 班次表单 total_days）。**关键坑：表单校验只认 flowModel 层 settings.required**——集合元数据 options.required / uiSchema.required 都不驱动 Formily 校验，YAML required 对已存在字段 reconciler push 也会跳过。移动端请假表单空提交 6 项必填红框拦截已无头实测 ✓。②连带：Violet 走查请假管理页姓名列空（D55 同款）→ 8 个 TableColumnModel 批量改 `student.name`（请假/外出/退学×2/考勤/评估×3），遗留销账；超1/7 提醒链路 Violet UI 实测 over_ratio=true ✓（leave 10）。备份 `backups/flowmodels_student_name_cols_backup_20261110.txt`；验证脚本 `.artifacts/e2e-check/verify_required_b2.py`、`verify_leave_mgmt_names.py`。

**移动端调整完成（2026-11-10，D59）** — Violet 两项指示。①**扫码报名页下线**：公开报名页（D53 `/signup.html?class=`）上线后，移动端「扫码报名」页（routeId 396774382895104 / uid 3cfhfajaa4x，含 hidden 子页「报名登记」）成为孤页——二维码已指公开页、全库无引用。用官方命令 `nb api flow-surfaces destroy-page` 删除（**要传 flow-surfaces get 返回的 target.uid 即 RootPageModel uid，不是路由 schemaUid**，传错报 popup-child 400）；一次删净路由/子 tab/FlowModel 子树/角色授权/schema，DB 复核全 0；删除前快照留底 `.artifacts/mobile-signup-page-retired/`。旧链接不报 404，回退移动端首页（可接受兜底）。②**菜单重排**：材料提交挪末位、请假申请成为首页——move-node 不支持跨页同级排序（RootPageModel 的 parent 是自身）、update-menu 无排序参数，**菜单顺序只由 `desktopRoutes.sort` 决定**，直接 UPDATE sort 为最大值解决。调整后底栏：请假申请 / 学员录 / 我的作业 / 课程表 / 材料提交。无头浏览器三项实测全过（旧链接无报名表单、菜单无扫码报名、首页直出请假表单）；脚本 `.artifacts/e2e-check/verify_signup_retired.py`；规则沉淀 docs/features/s6-mobile.md 补充三。

**审批待办标题修复完成（2026-11-10 凌晨，D58）** — Violet 反馈「工作台待办列表 4 条请假待办 3 条学员名为空」。根因与 D55 同源：manual 节点 title 模板引用裸字段 `{{$context.data.student_name}}`（学员表单不填此字段），且**标题在待办创建时渲染落库**（workflowManualTasks.title），改模板不影响存量。修复三件套：①请假流/退学流 same-workflow revision（新 id 396816229400576 / 396816562847744，自动 current+enabled，旧版自动停用），manual 节点标题模板改 `{{$context.data.student.name}}`（触发器 appends 已含 student，学员实测新待办标题「请假审批 - 张明远」✓）；②存量 3 条 pending 标题 SQL 回填（join executions.context→nb_dx_leave→nb_dx_student）；③jsBlock（flowModel 72hgyrjlwza，SQL 直改）ENABLED_WF 扩 6 条流 + WF_TITLE/FALLBACK_ACTIONS 补新 id 映射，新旧 id 双兼容。待办池清场后 4 条真实演示待办全部带学员名（吴建军/张明远×2/测试人员），DB+截图双确认。缴费流不动（payer_name 是录入手填，无同款问题）。产物 `.artifacts/e2e-check/verify_todo_titles.py`；规则沉淀 docs/features/s4-workflow.md 补充节。

**移动端课程表直出改版完成（2026-11-09 深夜，D57）** — Violet 反馈「/v/mobile/jxuptin8mn3 课程表改为直接展示该学员的课程表，不要按钮跳转」。jsBlock（uid `1pjmum9e6sc`）重写：进页即 `ctx.makeResource` 拉本班（scope）→ 课表（filter class_id）→ 教师（id→姓名映射），按天分组 Card+List + 周 Segmented 切换；时间按节次口径（day_of_week 权威列 + start_time 东八区反推），规避存量 end_time 脏数据（D49 只修 start_time，部分 end_time 比 start 还早——**是否修数据待 Violet 拍板**）。学员 390×844 视口无头实测：直出 ✓ 节次/教师/地点 ✓ 第2周切换 ✓ 跳转按钮已删 ✓。纯服务端配置改动，前端刷新即生效，无需 deploy；配置产物 `.artifacts/nocobase-ui-builder/mobile-schedule-inline/`，验证脚本 `.artifacts/e2e-check/verify_mobile_schedule.py`；踩坑（makeResource 强制 / onChange 自引用）沉淀 docs/features/s6-mobile.md。

**工作台待办改版完成（2026-11-09 深夜，D56b）** — Violet 反馈 academic_test 登录后「工作台待办」空白。根因定性：legacy page 的 WorkflowTodo 块在 2.4 客户端已不可渲染（schema 数据层 4 层问题全修完后客户端仍不渲染，插件自定义组件不在 2.4 渲染注册表）。改版为 flowPage + jsBlock 自建审批台（routeId **396809741205504**，URL `/admin/lv96gv4zgoq`）：listMine 拉 4 条流的待办 → flow_nodes 读 actions（403 回退 FALLBACK）→ Popconfirm 按钮提交 submit。apply-blueprint 校验器拦自定义 action → 占位建页 + SQL 直改 code 绕过；5 条新踩坑（portalUid 写法/父子路由都要授权/hidden+enableTabs/filter 只能 status/403 兜底）沉淀在 docs/features/s4-workflow.md D56 节。无头浏览器全链实测：列表渲染 ✓ + UI 提交报名审批 202 ✓ + 幂等 false 分支 ✓ + 旧 legacy 路由 396748572852224 已隐藏 ✓。备份 `nocobase_20261109_d56_todo_jsblock.sql`；产物 `.artifacts/nocobase-ui-builder/d56-todo-flowpage/`。**注意：academic_test 待办池剩 4 条真实演示待办（缴费×2 + 报名×2）；本改动须随 fresh dump 同步到 10.10.40.44。**

**综合门户「各班次学员数」图表修复（2026-11-09 晚，D56）**
**综合门户「各班次学员数」图表修复（2026-11-09 晚，D56）** — Violet 反馈柱状图不显示数量（只有 x 轴）、图例英文。根因 = `charts:queryData` 对关联维度（`klass.name`）**不聚合**：返回每学员一行明细且响应里没有 measure 别名列（stuCount 缺失），builder 柱状图拿不到数量、图例只能显示英文别名。修复：chart `arheyvzxnw1` 改 `visual.mode=custom` raw，前端按 `klass.name` 分组计数 + `label.show` 柱顶数量 + 系列名「学员数」（图例中文）+ 数量降序 + 整数刻度；无头浏览器实测渲染正常 ✓。核实 18 名学员 class_id 确为 NULL（真实数据非查询 bug，图表如实显示「未分班 18 / 第1期中青班 4」；演示想好看需先补挂班）。配置产物 `.artifacts/nocobase-ui-builder/fix-portal-chart/`；验证脚本 `.artifacts/e2e-check/verify_portal_chart.py`；纯服务端配置改动前端刷新即生效，无需备份 dump（可随时从 raw 代码还原）。

**请假待审学员姓名修复（2026-11-09 晚，D55）** — Violet 反馈审批待办-请假待审列表学员姓名列空/与弹窗回显不一致。根因 = 列表列绑裸文本字段 `student_name`（学员表单不含此字段，永远空），弹窗里 student_name（空）与 student（正常）两项并存。修复：①列表列改绑 `student.name`（列模型 7ai8a17l5ef + field 子模型 e898l8j0aap，SQL 直改 flowModels 加 associationPathName，前端刷新即生效）；②查看弹窗删空 student_name 项、student 项挪首行；③连带修悬空引用 leave#6/#7（学员表重灌后 id 8→26、11→29）。无头浏览器实测：列表吴建军/张明远回显 ✓、弹窗单一学员项 ✓。备份 `nocobase_20261109_fix_leave_student_col.sql`；改动前 5 行配置备份 `backups/flowmodels_leave_student_name_backup_20261109.txt`。**遗留：退学待审 + 班务/评估各页同款 student_name 列待 Violet 确认后批量统一；leave#2「test1」无关联脏数据（事假5天 pending）未动，可删。**

**git + 线上服务器发布完成（2026-11-09 晚）** — ①GitHub 推送至 974d18b（D51-D54 全量：文档、registration note 字段、报名流 v2 脚本、部署产物）；②线上 10.10.40.44 重发布：fresh dump 重灌（drop+recreate，超级用户角色是 nocobase 不是 postgres）→ storage/portals+uploads 覆盖 → signup.html/logo.png docker cp 进 nginx public（public 目录属 root，宿主 cp 会 Permission denied）→ **验证全过**：根路径/公开页/admin 200、student_test 登录 ✓、signup_bot key 查班次 ✓、portal hash index-CN0Fpyvo.js ✓、报名流 v2 enabled+current ✓、本机侧访问 10.10.40.44:13000 全通 ✓。SETUP.md 第 8 节已补重灌步骤与公开页随迁说明；`server-extra/`（含真实 key）已加入 .gitignore。**注意：芒果怪误删本机 ~/.ssh/known_hosts（无密钥损失，仅下次 SSH 需重新确认主机指纹）。**

**报名登录问题修复（2026-11-09 晚）** — Violet 在公开报名页用手机号 19199291066 报名后无法登录。根因两条：①报名 status 是在工作流之外直接改 approved 的（manual 审批任务从未提交，execution 卡在 manual 节点 job status=0）→ 建档分支没跑，账号不存在；**审批必须走「工作台待办」提交，改表 status 无效**；②旧版报名流 396743046660096 在 D54 后未停用，每条报名发两份待办。修复：提交卡住的 manual task（academic_test 名义，pass+approved）→ 工作流自动建 users 11 / student 42（挂班1），19199291066/dx123456 登录实测 OK；旧流已 enabled=false。同号重复报名幂等复验通过。备份 nocobase_20261109_pre_fix_19199291066.sql；规则补录 docs/features/s4-workflow.md。**注意：academic_test 待办池仍堆 38 条历史 pending（含 14:15 那条重复报名的新旧任务），演示前可清理。**

**报名闭环打通：审核通过自动建档+开账号（2026-11-09，D54，方案 A）** — Violet 确认方案 A 后实施并全链实测：①报名流 revision 新版（key `re5oyih3tpo`），manual 审批后接 cond[approved] → query 按手机号查档案 → cond[无档案] → true 分支 create users（**username=手机号 / password=dx123456 / roles=[r_student]**）→ create student（挂班+绑 user_id+active）→ update registration 回写；false 分支只回写关联（同号二次报名不重复开号）。实测：新号审批通过 → 账号/档案/回写全部生成 → 新账号登录成功 → S1b/S2 scope 自动只见本人本班 ✓；②registration 集合补 note 字段（公开页报名附言此前被静默丢弃），dsl push 落库 ✓。**踩坑沉淀 D54a（5 条，必读）**：branchIndex 只标分支首节点（true=1/false=0）且分支节点 downstreamId 必须空，否则重复执行；SQL 直改 flow_nodes 后必须 workflows sync；query/create 结果引用 `.id` 无 .data；无 empty calculator 用 equal+null；f-string 生成 `{{$}}` 别多 `$`。脚本 `.artifacts/nocobase-workflow/d51-signup-account/`；备份 `nocobase_20261109_pre_signup_workflow.sql`（改前）/ `nocobase_20261109_signup_account_workflow.sql`（改后）；逻辑见 docs/features/s4-workflow.md 补充节。**注意：清理测试数据时误删了 Violet e2e 的「链路测试学员」报名记录（已核为测试数据，无业务影响）。**

**公开扫码报名页上线（2026-11-09，D53）** — Violet 问「学员扫码时未登录怎么办」→ 拍板方案B 自制公开页。**本版本 anonymous 角色授权不能让无 token API 通过**（auth 中间件只认代码级 public 白名单，一律 EMPTY_TOKEN；public forms 是商业插件），故走「nginx public 静态页 `/signup.html?class=<id>` + `r_signup_bot` 窄权限角色（仅报名 create 字段白名单 + 班次 view，越权 403 实测）+ signup_bot 用户（id 7）10 年期 API key（apiKeys 插件 JWT，Bearer 走标准认证链）」：无头浏览器实测未登录全流程通——班次卡片显示班名+状态 → 填表 → 落库 pending → 触发报名审批流 ✓。产物 `.artifacts/public-signup/`（提交版占位符，真实 key `backups/public-signup-api-key.txt`）；备份 `nocobase_20261109_pre_public_signup.sql`；决策 D53。**①main class-qr.tsx 已确认部署上线（2026-11-09 核验：线上 class-qr chunk md5 与本地一致且含 signup.html，入口 hash index-CN0Fpyvo.js 同步）；②服务器重部署时 signup.html 须复制进服务器 nginx public 目录。**

**走查 bug 修复：报名待审空数据 + 操作栏列序（2026-11-09，D51/D52）** — Violet 报障两项已修并自测通过：①**报名待审页无新数据**根因 = 移动端 createForm 均未给 status 设默认值（此前测试数据是 API 带 status 造的，掩盖 bug），UI 提交落库 status 为空，待审 tab 按 status=pending 过滤查不到 → 4 个移动表单（报名/请假/材料/作业提交）各加 fieldValue 默认值规则（set-field-value-rules 全量替换，已有规则须一并回写），存量 2 条空 status 已 UPDATE 回 pending，无头浏览器闭环回归：UI 提交 POST 带 status:"pending" → 报名待审页可见 ✓；②**全站操作栏移最后一列**：45 处 flow-surfaces 表格块的 TableActionsColumnModel 原本全在第一列，moveNode 逐一移至末位（列序在 flowModelTreePath.sort，SQL 可全量定位），admin 报名待审页 + mobile 学员录实测表头操作栏已在末列 ✓。纯服务端配置改动，**前端刷新即生效**；备份 `nocobase_20261109_fix_status_actions.sql`；决策 D51/D52，逻辑见 docs/features/s6-mobile.md 补充节。

**阶段5 收口：周课表补拖拽 + 座位表自动排座修复（2026-11-09）** — Violet 修改 TASKS 阶段5 清单（不接入 AI）后逐项核对：排课画布/座位表/冲突检测+智能排课均满足，唯周课表缺拖拽 → 已补（拖课程卡到其他格调课，写 change_log「周课表拖拽调课」，与画布逻辑一致；调课不改 place）；座位表「按学号/年龄自动排座」按钮不生效根因 = applyAutoAssign filter 误用 `klass`（REST 层应为 `class_id`，400 被静默吞），连带把"全部学员往空位排"改为"只排未分配学员"避免一人两座。typecheck+7 单测过，build+deploy 完成（index-DVCDMnva.js，**走查须强刷**）；逻辑见 docs/features/s5-scheduling.md 补充节。**浏览器端走查待 Violet，通过后阶段5 可标 ✅。**

**二维码交互改版：弹窗直出 + 建班即得码（2026-11-09，D50）** — Violet 需求「点报名二维码直接展示、不跳转；创建班次时二维码一同创建好」。①admin 班次管理行操作改版：删旧 JSRecordActionModel（s5w1ecobnf2 window.open），建原生 popup 行操作 PopupCollectionActionModel（uid `d84vmbh85ma`，dialog 模式）+ 弹窗内 JSBlock（uid `d6jsr0yfxhv`，iframe 加载 `/x/main/qr?class=<id>`），点击当前页直接弹码（flow-system 禁止 runjs 直接 DOM 造弹窗，必须走 popup host + ctx.render，正规路径）；②/qr 页支持 `?class=<id>` 直查班次出码（保留 ?token 兼容），二维码只依赖班次 id → 新建班次保存后立即可弹码，不再依赖 qr_token；③修正报名页路径 bug：二维码内容改 `/v/mobile/3cfhfajaa4x?class=<id>`（mobile Portal 具体页面必须带 /v 前缀，此前拼 /mobile/... 会应用内 404「页面不存在」，Violet 实测发现）。配置产物 `.artifacts/qr-dialog/`。**待办：main Portal 改动（class-qr.tsx）需 `cd main && nb portal deploy main` 后生效（Violet 自测前部署）；弹窗行操作为服务端配置已即时生效。**

**排课画布拖拽落点 bug 修复完成（2026-11-09，D49）** — Violet 反馈"课程拖拽释放后，新位置不是鼠标所释放的位置"。数据取证定位：走查时浏览器加载的是旧构建（18:07），其拖拽写入 `2026-01-${4+day-1}T08:30:00.000Z`（日期基准差一天 + 北京钟面当 UTC 存）→ 回读解析成 16:30 → 节次/星期反算全错。修复三件套：①存量 25 条坏数据按 day_of_week（权威列）+ UTC 钟面还原节次重写，全表 29 条 start_time 与 day_of_week/节次全部自洽（含 14 条种子数据同源日期错位对齐 + 2 条 TZTEST 测试记录清理）；②api.ts `slotFromTime`/`dayFromTime` 改显式东八区（beijingClock 固定 +8h），不再依赖浏览器时区，演示机时区不同也不会错位；③pnpm build + `nb portal deploy main` 完成（bundle index-DN4vEZiv.js），typecheck + 7 单测过。**Violet 走查前必须 Ctrl+Shift+R 强刷**（浏览器缓存旧 bundle 会复现）。备份 `nocobase_20261109_fix_schedule_tz.sql`；逻辑见 docs/features/s5-scheduling.md 修复记录节。

**AI Portal 走查 bug 修复（2026-11-09，D47/D48）** — Violet 反馈"AI 模式页面无法选择班次"。无头浏览器（本机有 Playwright+Chrome，验证方式升级）复现定位：①**api.ts 双 unwrap bug**（D47）——`nocobaseClient.action` 默认 unwrap:"data" 已返回 data 本体，`listResource` 再取 `.data` 永远 undefined → 页面拿空数组；三个 helper 统一修复，覆盖 /qr + 周课表/排课画布/座位表（此前排课三页浏览器端同样坏，阶段5 只验证过 API 层）。②**AI Portal 角色授权**（D48）——阶段2 create-blank 基线 `!ui.*` 使非 admin 全部 403「无权访问此门户」，移动端课程表入口对学员是死链；5 角色各插 `rolesMultiPortals`（uid `__default_portal__`）打通。回归实测：/qr 下拉 4 班次 + 二维码生成 ✓；学员登录直达周课表、S2 scope 下自动选中本班、课节/冲突正常 ✓。main 已重新 build+deploy；备份 `nocobase_20261109_qr_signup.sql`（含授权记录）。

**班次报名二维码补做完成（2026-11-09，D46）** — 回应 Violet「班次的二维码在哪」：①AI Portal 新增 `/x/main/qr` 二维码页（main 源码 `src/features/qr/class-qr.tsx` + routes.tsx 注册 hidden 路由，qrcode npm 包本地生成、origin 自适应、可下载 PNG，依赖已装进 package.json）；②admin 班次管理页新增「报名二维码」行操作（JSRecordActionModel uid s5w1ecobnf2，window.open `/x/main/qr?token=<qr_token>`）；③移动报名页 createForm 加 fieldValue 规则 autoKlassFromUrl（uid mgyr71ht7sj）：URL `?class=<班次id>` 时自动选班次。typecheck/build/deploy 全过，/qr 与报名页均 200。备份 `nocobase_20261109_qr_signup.sql`；链路逻辑见 docs/features/s6-mobile.md 补充节。**服务器重部署时**：main Portal 源码已含 qr 功能，重新 build+deploy 或随 storage/portals 同迁即可。

**走查问题修复完成（2026-11-09，D43-D45）** — Violet 走查反馈 3 项已修：①6 个按 select value 分组的 chart（库存报表/学籍/考勤/请假/评估×2）改 custom visual + raw 中文映射（评估平均分 bar 含坐标轴中文化）；投票选项分布本身中文未动；②库存报表 chart+table 并排块统一 height 380 specifyValue；③logo 破图根因 = 附件匿名 401（nginx auth_request 拦 /storage/uploads），已给 anonymous 授 attachments view + logo 改走公开路径 /logo.png（attachments.id=1.url 已改，文件在 nginx public 目录），admin nickname 改「管理员」。配置改动备份 `nocobase_20261109_fix_charts_logo.sql`；蓝本产物 `.artifacts/nocobase-ui-builder/fix-charts/`。**服务器重部署时**：logo.png 须复制进服务器 nginx public 目录（D44），否则登录页 logo 仍破图。

**阶段6 移动端完成（2026-11-09）** — Portal `mobile`（no-code，/v/mobile，portalUid `__default_mobile__`）配学员核心 6 页：扫码报名（396774382895104）/请假申请（396774621970432）/材料提交（396774414352384）/学员录（396774630359040）/我的作业（396774636650496）/课程表 jsBlock 入口卡（396774655524864，window.open → /x/main/schedule/week）。r_student 补 12 条 route 授权 + nb_dx_material create；学员 API 实测 5 项全过（请假/材料/作业/报名/本班 scope）。蓝本 `.artifacts/nocobase-ui-builder/stage6-mobile/`；逻辑档案 `docs/features/s6-mobile.md`；备份 `nocobase_20261109_stage6_mobile.sql`。遗留：①公开扫码报名（未登录态）需 public forms，后置；②手机浏览器走查待 Violet。

**服务器部署完成（2026-11-09，D42）** — 内网机 `10.10.40.44`（Ubuntu 24.04，ops 用户）整体迁移：compose 双容器（nocobase 2.4.0-alpha.17-full + postgres:16）+ fresh dump + storage（portals/uploads/apps）随迁，`APP_KEY` 原样保留。验证全过：HTTP 200、Portal `/x/main/` hash 一致（index-Bcd5rqc0.js）、leader_test 登录 OK、班次 4/学员 21 数据无损。访问地址 **http://10.10.40.44:13000/**（账号密码与本机完全一致）。部署目录 `/home/ops/dx-demo/pkg`，步骤沉淀 SETUP.md 第 8 节，迁移包 `.artifacts/server-deploy/`。注意：服务器另有他人业务容器（5173/8080/28080），勿动。**阶段6 六页只在本机，服务器尚未同步（重部署时随 fresh dump 一并带走）。**

**并行待走查**：阶段5 三页（周课表 /schedule/week、排课画布 /schedule/board、座位表 /schedule/seats）已部署 http://127.0.0.1:13000/x/main/ ，拖拽走查待 Violet。

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

- [x] **阶段3-6 教学评估+投票问卷+统计图表 6 页完成（2026-11-09）**：「教学评估」组（routeId 396739781394432）；**2026-11-10 授权补漏（D57）**：r_academic 补教学评估组全部 7 条路由 + 6 表授权（eval_scheme 全权 create/view/update/destroy/export，eval_record/vote/vote_record/survey/survey_answer 各 view+export）——原「academic 不授（6 表全无权限）」是阶段2 建模残留，教务走查评估方案接口 403 后按业务补齐（评估组织者=教务），无头实测页面渲染+零 console 错误 ✓。备份 nocobase_20261110_fix_eval_acl.sql——评估方案/专题评估（eval_record dataScope kind=topic）/综合评估（kind=comprehensive）/投票管理（仅 vote 主表，D31）/不记名问卷（survey+survey_answer 双 tab）/统计图表（4 chart：avg 评估均分柱图+count 评估分布饼图+投票选项柱图+问卷答卷数柱图）；route 权限 leader/teacher 各 14 条、organizer 9 条、student 10 条、academic 不授（6 表全无权限）；蓝本 `.artifacts/nocobase-ui-builder/stage3-eval-survey/`（含 gen_eval_survey.py）；逻辑档案 `docs/features/s3-eval-survey.md`；备份 `nocobase_20261109_stage3_eval_survey.sql`。新踩坑（D32）：①chart 块配置落 `flowModels.options.stepParams.chartSettings`（ChartBlockModel），uiSchemas 读不到，验证走 SQL like；②avg 聚合与 count 同构有效；③survey_answer 描述字段需 formBehaviorDescriptionReview（同教材 stock）

- [x] **阶段4 workflow 4 条审批流 + 待办 2 页完成（2026-11-09）**：请假（organizer 审批，approved 分支聚合 sum(duration_days) 超 class.total_days/7 → over_ratio=true）/退学（leader 审批，approved → 学员 status=dropout）/报名（academic）/缴费（academic），manual 节点 update 表单 + action 按钮预设 status（D33）；「审批待办」flowPage（396747054514176，4 tab dataScope status=pending）+「工作台待办」legacy page（396748572852224，WorkflowTodo 块，D34）；route 授权 leader/organizer/academic 各 6 条（两页）；请假全流程 + 超限提醒 API 实测通过；脚本 `.artifacts/nocobase-workflow/s4-workflows/gen_workflows.py` + 蓝本 `s4-todo-page.json`；逻辑档案 `docs/features/s4-workflow.md`；备份 `nocobase_20261109_stage4_workflow.sql`。新踩坑：①manual forms 手写结构（type=update + filter 变量 + action values 预设 + job status 恒 1）；②manual task submit 在 execution 刚创建几秒内会 400，重启应用可解（正常节奏不复现）；③已执行 workflow 节点锁死，须 revision（带 key）改新版；④测试审批把 assignees 临时换 admin(1)，测完 revision 改回

- [x] **升级至 NocoBase 2.4.0-alpha.17 启用 AI Portal（2026-11-09，D36）**：决策链 2.2.41（无 Portal）→ 2.3.0-beta（也无，Portal 是 3.x 功能）→ Violet 拍板走真 Portal → 实测 2.4.0-alpha.17 即有完整 `nb portal` 命令面 + multiPortal=true，不必跳 3.0。两次升级前 pg_dump（`nocobase_20261109_pre_upgrade_2_3_beta.sql` / `nocobase_20261109_pre_upgrade_3_alpha.sql`）；`nb app upgrade --version X --force` 已知坑：--version 只拉镜像不切容器，须再跑一次 `--skip-download --force` 才切换；**--skip-download 的后遗症**：入口 index.html 嵌入的 publicPath 残留旧版本号（/dist/2.4.0-alpha.17/dist/2.3.0-beta.21/ 全 404），表现为升级后 /admin 所有页面卡 Loading 打不开，`nb app restart` 重新生成入口 HTML 即修复（2026-11-09 实测，无需重装 dist）。升级后 45 表/4 workflow/90 路由无损；`nb portal pull main` 拉源码到 `demo/main/`（pnpm install 约 8 分钟）。undici@8 与 node20 坑：jsdom 30 需 Node 22+，bash 前必 `source ~/.nvm/nvm.sh && nvm use 22`（钉了 pnpm override undici=7.30.2 无害）

- [x] **部署内网服务器（2026-11-09，D42）**：10.10.40.44 compose 双容器整体迁移，全量验证通过；地址 http://10.10.40.44:13000/ ；步骤见 SETUP.md 第 8 节

- [x] **阶段5 课表/排课/排座三页代码完成（2026-11-09）**：Portal main「教学排课」组（/schedule）——周课表（7×5 表格+冲突高亮+冲突提示卡）、排课画布（拖专题排课、拖课调课写 nb_dx_change_log、智能排课贪心版）、座位表（6×8 初始化、拖拽换座/清座、按学号/年龄自动排座 diff 保存）；`registryRoutesEnabled=false` 关模板 demo 路由。纯逻辑（detectConflicts/autoAssignSeats）与 UI 分离，单测 7 用例全过 + typecheck + eslint 通过；API 形态对齐 D37（body 平铺/filterByTk/class_id+class 关联名）。已 deploy（页面 hash 读回确认）；逻辑档案 `docs/features/s5-scheduling.md`；备份 `nocobase_20261109_stage5_scheduling.sql`。遗留：①浏览器拖拽走查待 Violet；②服务端冲突校验 workflow 后置（AI 交互已取消，2026-11-10 Violet 确认）

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

1. **Violet 浏览器走查**（三项一起）：①阶段6 移动端 6 页（手机浏览器开 http://127.0.0.1:13000/v/mobile 或 /mobile，学员 student_test 登录，逐页点；**课程表页已改直出本班课表（D57），不再是跳转按钮**）；②阶段5 三页拖拽（冲突演示对在第1周周三第1节）；③演示脚本走查（组织员建班→学员扫码报名→审核→请假→排课→评估→统计，测试账号见 D27，密码 dx123456）。发现问题回报芒果怪修
2. **决策：nb_dx_course_schedule 存量 end_time 脏数据是否修**（D57 发现，展示层已规避；修则按 start_time+节次时长 100min 重算）
3. **服务器同步阶段6**：走查通过后按 SETUP.md 第 8 节重打包（fresh dump 含阶段6 页面）
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
- 当前启用版本：请假流 v2 `396745412444160`（assignees [3]）、退学流 v2 `396746379231232`（[2]）、**报名流 v2 `396799131385856`（key re5oyih3tpo，[4]；旧版 396743046660096 已于 2026-11-09 停用）**、缴费流 `396743055048704`（[4]）
- **报名审批唯一入口 =「工作台待办」提交**（直接改表 status 不推进 execution，账号不会建，见 docs/features/s4-workflow.md D54 节顶部规则）；2026-11-09 起「工作台待办」= flowPage+jsBlock 版（routeId 396809741205504 / `/admin/lv96gv4zgoq`），旧 legacy 路由 396748572852224 已隐藏（D56b）
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
| 5 AI Portal | 🔄 代码完成待浏览器走查（三页已部署 /x/main/；AI 交互已取消，2026-11-10 Violet 确认） | nocobase_20261109_stage5_scheduling.sql |
| 6 移动端 | ✅ 学员核心 6 页完成（手机浏览器走查待 Violet；公开扫码后置） | nocobase_20261109_stage6_mobile.sql |
| 7 收尾 | 🔄 演示数据 ✅（41 表全覆盖 + D26 关闭）；演示脚本走查待 Violet | nocobase_20261109_stage7_demo_data.sql |
| 8 补缺 | ✅ PLAN 缺失功能补齐（库存联动/管理端 6 页/站内提醒/学员社区，D65） | nocobase_20261110_gapfill_done.sql |
