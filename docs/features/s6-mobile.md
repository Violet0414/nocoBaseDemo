# s6 — 移动端学员核心页（阶段6）

> 完成日期：2026-11-09。Portal：`mobile`（no-code，URL `/v/mobile`，portalUid `__default_mobile__`）。
> 蓝本：`.artifacts/nocobase-ui-builder/stage6-mobile/bp1~bp6*.json`。备份：`nocobase_20261109_stage6_mobile.sql`。

## 为什么做

dx.xlsx「移动应用」块的学员核心场景。按 PLAN 既定（D4），移动端用内置 no-code 移动 Portal 配置（免费），AI Portal 排课三页（`/x/main/`）组件本身响应式，移动端以 Link 打开 PC 页兜底，不重复实现。

## 页面清单（6 页，全部 mobile root 顶级入口）

| 页面 | routeId | pageSchemaUid | 主块 | 表 |
|---|---|---|---|---|
| ~~扫码报名~~（已下线 2026-11-10，见补充三） | ~~396774382895104~~ | ~~3cfhfajaa4x~~ | createForm | nb_dx_registration |
| 请假申请 | 396774621970432 | 80a2tclmlct | createForm + 我的请假 table | nb_dx_leave |
| 材料提交 | 396774414352384 | xm89i0vlzcq | createForm | nb_dx_material |
| 学员录 | 396774630359040 | ru5tj20ddta | table（recordActions 仅 view） | nb_dx_student |
| 我的作业 | 396774636650496 | owx51rwfogb | 作业列表 table + 提交作业 createForm | nb_dx_assignment / nb_dx_submission |
| 课程表 | 396774655524864 | jxuptin8mn3 | jsBlock 直出本班课表（2026-11-09 二次改版） | nb_dx_class / nb_dx_course_schedule / nb_dx_teacher |

## 规则与决策

1. **权限粒度**：r_student 新增 12 条 route 授权（6 页 + 6 个 hidden tabs 子 route）；表权限仅补了 `nb_dx_material` create（阶段2 已配齐其余 5 表）。`nb_dx_student` 学员录保持 view-only，recordActions 只留 view。
2. **数据范围继承阶段2 scope**：学员的"我的请假记录"和作业列表自动被 S1/S2 scope 过滤（实测 assignment count=1 只见本班作业）。
3. **课表直出而非跳转**（2026-11-09 二次改版，Violet 反馈"直接展示该学员的课程表，去掉按钮跳转"）：移动端「课程表」页 jsBlock（uid `1pjmum9e6sc`）改为进入页面即渲染本班课表——`ctx.makeResource('MultiRecordResource')` 依次拉 `nb_dx_class`（scope 自动限本班，取第一个班）→ `nb_dx_course_schedule`（filter class_id，pageSize 200）→ `nb_dx_teacher`（id→姓名映射，替代 appends）。按周 Segmented 切换（周集合从数据探测），按天分组 Card+List 展示：课名+kind Tag、节次+时间+教师+地点。数据仍单一数据源 `nb_dx_course_schedule`，不复制。旧入口卡（window.open → `/x/main/schedule/week`）已废弃。**时间口径与 main 一致**：`day_of_week` 权威列 + start_time 显式东八区（UTC 钟面 +8h）反推节次，显示固定节次表（第1~5节/晚间），不显示原始 end_time 钟面——存量 end_time 有脏数据（D49 只修了 start_time，部分 end_time 比 start 还早/跨日回跳），按节次口径展示可完全规避。
4. **审批闭环复用阶段4 workflow**：移动端请假 createForm 提交 status=pending，直接触发请假审批流（组织员待办）；报名记录由教务在 PC 端审核。移动端不配审核界面（审核是教职工场景，PC 响应式兜底）。
5. **表单字段裁剪**：所有 createForm 只放学员可填字段，状态/审核人/批阅分数等字段一律不放（由流程写回）。

## 踩坑记录（阶段6 新增）

1. **mobile 页 identity**：mobile-backed Portal 蓝本 `navigation` 只带 `portalUid`，omit `group` 和 `layoutUid`；`navigation.item.icon` 必填（页面入口图标）。
2. **关联目标 >10 字段必须 fieldGroups**（复现阶段3-2 坑）：本次 `nb_dx_class`（15 字段）与 `nb_dx_student`（15 字段）都要在 `defaults.collections.<目标表>.fieldGroups` 提供全字段分组，漏一个字段报 `default-field-groups-incomplete`（student 漏 user 报错过一次）。且 fieldGroups 必须挂在**被关联的目标表**键下，不是引用方表下。
3. **m2o 字段 titleField 必须显式对象形式**：`nb_dx_class` 的 YAML titleField=name 在 live 元数据里未生效（落到 id），蓝本报 `relation-titleField-unreadable`。所有 m2o（klass/student/topic/teacher/review_by/assignment）统一写 `{"field":"x","titleField":"name|nickname"}`（users 用 nickname）。
4. **多块 layout 不许每块独占一行**：`block-layout-single-column` 报错。两块（表单+表格）必须同行（各 span 12）。与阶段3 踩坑④同源。
5. **applyBlueprint 蓝本不支持 js action 的 `clickSettings`**：configureOptions 仅支持 title/tooltip/icon/iconOnly/type/color/htmlType/position。要放 JS 逻辑用 **jsBlock**（`settings.code`，strict render：必须 `ctx.render(...)` + `ctx.libs.antd` JSX）。
6. **flow-surfaces 强制资源 API（2026-11-09 补）**：JSBlock 里读集合禁止 `ctx.api.request({url: 'xxx:list'})`，校验器报 `runjs-resource-api-required`；必须用 `ctx.makeResource('MultiRecordResource')`（setResourceName/setPageSize/setFilter/refresh/getData）。appends 未在 resource API 文档中出现，关联名（如教师姓名）用第二次资源查询+前端映射替代。另外 JSX onChange 里函数自引用（drawWeek 递归）报 `runjs-global-unknown`，用局部持有者变量（`const self = { redraw: null }` + `self.redraw = drawWeek`）绕过。

## 验证记录（2026-11-09）

- 学员账号 student_test API 实测：leave create（id=8，status=pending，进审批流）／material create／assignment list（count=1，本班 scope 生效）／submission create／registration create 全部 200。
- route 授权读回 12/12 命中（r_student）。
- `/v/mobile` 与 `/mobile` HTTP 200。
- 浏览器端手机走查待 Violet（芒果怪无浏览器环境）。**（2026-11-09 起芒果怪已可用 Playwright+Chrome 无头自测，本节后续功能用无头验证）**
- 课程表直出改版（2026-11-09）：学员登录 390×844 手机视口实测，`/v/mobile/jxuptin8mn3` 进页直出"我的课程表 · 第1期中青班"，按天分组+节次口径（第1节 08:30–10:10 等）+教师/地点齐全，第1周/第2周 Segmented 切换正常，按钮跳转已移除；HTTP4XX 仅登录态注入初期的 401（正常），无 JS 错误。验证脚本 `.artifacts/e2e-check/verify_mobile_schedule.py`。

## 遗留

1. **公开扫码报名未做**：当前报名页在登录态下可用；真正的"未登录扫码报名"需 public forms 链接，demo 演示用登录态报名页替代，如需公开表单后置补。**2026-11-09 已补「班次报名二维码」入口链路，见下方补充节。**
2. 移动端页面在真机/窄屏的表现待 Violet 手机浏览器走查。

## 补充：班次报名二维码链路（2026-11-09）

「班次的二维码在哪」走查反馈补做。三段链路：

1. **AI Portal 二维码页 `/x/main/qr`**（main 源码 `src/features/qr/class-qr.tsx`，路由 hidden 不进侧边栏）：`?class=<班次id>`（来自班次管理页弹窗行操作）或 `?token=<qr_token>`（兼容旧链接）或页内下拉选班次 → 用 qrcode 库本地生成 PNG（无外网 CDN 依赖）→ 可下载。二维码内容 = `window.location.origin + /v/mobile/3cfhfajaa4x?class=<班次id>`，origin 自适应，换部署地址无需改配置。**注意 mobile Portal 具体页面路径必须带 `/v` 前缀**（`/mobile` 只是根入口，缺 `/v` 会应用内 404「页面不存在」）。
2. **admin 班次管理页「报名二维码」行操作**（2026-11-09 二次改版）：旧 JSRecordActionModel uid `s5w1ecobnf2`（window.open 跳转）已删除，改为原生 popup 行操作 **PopupCollectionActionModel uid `d84vmbh85ma`** + 弹窗内 **JSBlock uid `d6jsr0yfxhv`**——点击在当前页弹 dialog 直接展示二维码（iframe 加载 `/x/main/qr?class=<班次id>`），不跳转出应用；**建班即得码**（二维码只依赖班次 id，不依赖 qr_token，新建班次保存后立即可弹码）。配置产物 `.artifacts/qr-dialog/`。
3. **移动报名页自动带班次**：表单 `fieldValue` 规则（uid `mgyr71ht7sj`，key `autoKlassFromUrl`）——`urlSearchParams.class` 非空时 klass 字段默认值 = runjs：先 `fetch /api/nb_dx_class:get?filterByTk=<id>`（带 `ctx.token` 请求头）请求班次记录，成功后返回 id 赋值；请求失败降级为直接返回 id。**这样进入页面时班次数据先就绪，下拉才能正确显示班次名**（Violet 2026-11-09 反馈：同步裸赋 id 会导致班次显示异常）。学员仍可手改。
4. **AI Portal 访问授权（D48）**：5 个业务角色（r_leader/r_organizer/r_academic/r_teacher/r_student）各插一条 `rolesMultiPortals`（multiPortalUid=`__default_portal__`，即 main Portal）。此前阶段2 create-blank 基线的 `!ui.*` snippet 使所有非 admin 角色进 `/x/main/` 一律 403「无权访问此门户」，移动端「课程表」入口卡对学员是死链；授权后学员登录直接进周课表，且 S2 scope 使学员班次下拉只有本班、自动选中即正确班次。

设计取舍：二维码 URL 直接带班次 id 而非 `qr_token`，因为 fieldValue runjs 是同步取值场景，无法先查 `qr_token→id`；改版后行操作也不再依赖 `qr_token`（`?class=<id>` 直查班次），字段保留在 `nb_dx_class` 仅作旧链接兼容。公开（未登录）报名仍需 public forms，后置。

## 补充（2026-11-09 晚，D51）：状态字段默认值

**问题**：UI 实际提交报名后，报名待审页（admin 审批待办 flowPage 的报名 tab，过滤 `status=pending`）看不到新数据。

**根因**：移动端 createForm 均未给 `status` 设默认值——阶段6 的测试数据是 API 调用直接带 status 造的，掩盖了此缺口。UI 提交落库 status 为空串，待审过滤查不到。

**修复**（4 个表单各加一条 fieldValue 默认值规则，`flowSurfaces:setFieldValueRules`）：

| 表单 | 块 uid | 规则 key | 默认值 |
|---|---|---|---|
| 扫码报名 | mgyr71ht7sj | defaultStatusPending | pending |
| 请假申请 | wzt107tontk | defaultStatusPending | pending |
| 材料提交 | ux2ncmkqq35 | defaultStatusSubmitted | submitted |
| 我的作业·提交作业 | n67h5v3zos5 | defaultStatusSubmitted | submitted |

**踩坑**：`set-field-value-rules` 是 slot 全量替换——报名表单已有 `autoKlassFromUrl` 规则，必须先读原文一并回写，否则会被冲掉。静态默认值采用 runjs 形态（`return 'pending';`），项目内已验证。存量 2 条空 status 报名记录已 UPDATE 为 pending。无头浏览器闭环回归：UI 提交 → POST body 带 `status:"pending"` → 落库 → 报名待审页可见 ✓（测试记录已清理）。

## 补充二：公开扫码报名页（2026-11-09，D53）

**为什么**：演示主链路「学员扫码报名」时学员手机无登录态；此前方案 public forms 是商业插件，Violet 拍板自制（方案B）。

**机制取证**：本版本 auth 中间件只放行代码级 public 白名单（`acl.allowManager.isPublic`），anonymous 角色的资源授权**不能**让无 token API 通过（一律 EMPTY_TOKEN 401）——给 anonymous 授权的路走不通。

**方案**（三件套）：

1. **静态页 `/signup.html`**：放 nginx public 目录（`storage/.nocobase/proxy/nginx/default/public/`，D44 同款），纯原生 HTML/CSS/JS 无 CDN 依赖，窄屏适配。读 URL `?class=<班次id>`，用 API key fetch 班次显示卡片（班名+编号+状态标签），表单字段：姓名/手机号/性别/政治面貌（必填）+ 单位职务/附言（选填），前端必填校验，提交成功显示成功页。提交 body 固定 `status=pending` → 触发报名审批流。源码产物 `.artifacts/public-signup/signup.html`。
2. **机器人凭证**：`r_signup_bot` 角色（仅 `nb_dx_registration` create 且字段白名单 name/phone/gender/political_status/work_unit/note/class_id/status + `nb_dx_class` view 限班次展示字段）+ `signup_bot` 用户（id 7）+ apiKeys 插件签 10 年期 JWT（`{userId:7, roleName:"r_signup_bot"}`）。**API key 本质是带 roleName 的长期 JWT**，`Authorization: Bearer` 走标准认证链。角色 snippets 带 `pm.api-keys.configuration`（bot 自己签 key 必需）。越权实测：registration list / class destroy 均 403。
3. **二维码改指公开页**：`main/src/features/qr/class-qr.tsx` 二维码内容由 `/v/mobile/3cfhfajaa4x?class=` 改为 `/signup.html?class=`（已改并确认部署上线）。改版后扫码即达公开页；移动端报名页已于 2026-11-10 下线（见补充三）。

**安全边界**：key 硬编码在公开 HTML 中（任何访客可取），但权限面 = 只能 create 报名记录 + view 班次展示字段，最坏后果是刷报名垃圾数据（demo 可接受）；恶意 status=approved 提交只是记录状态、不触发流程不改他人数据，PC 审核员可见可改。真实 key 不入库：提交版为占位符，真 key 在 `backups/public-signup-api-key.txt`。

**踩坑**：①bot 用户绑角色用 `users.roles` 关联 create 会报「Role UID already exists」（它当新角色建），直接 INSERT `rolesUsers` 表；②apiKeys:create 需要 `pm.api-keys.configuration` snippet（默认 No permissions）；③loadKlass 的 fetch 忘带 API key 时显示「班次不存在」——公开页所有 /api 调用都必须带 Bearer key。

**验证**（无头浏览器未登录态）：班次卡片「E2E链路测试班（E2E2601）报名中」→ 填表提交 → 成功页 → 落库 pending + 报名流 execution 触发 ✓。

**服务器重部署注意**：signup.html 须复制进服务器 nginx public 目录（同 D44 logo.png 一起）；API key 随 HTML 携带，无需服务端配置；r_signup_bot/rolesResources 授权记录随 dump 迁移。

## 补充三：扫码报名页下线 + 菜单顺序调整（2026-11-10，D59）

**为什么下线**：D53 公开报名页 `/signup.html?class=` 上线并部署后，移动端「扫码报名」页（routeId 396774382895104 / uid 3cfhfajaa4x，含 hidden 子页「报名登记」）成为孤页——唯一入口二维码已改指公开页，全库 schema 无其他引用，main 源码无链接。Violet 确认移除。

**怎么删的**：官方命令 `nb api flow-surfaces destroy-page --uid <页面FlowModel uid>`（注意传 flow-surfaces get 返回的 target.uid，即 RootPageModel 的 uid，不是路由 schemaUid；直接传 schemaUid 会报「popup child page」400）。一次删除 = 路由 + 子 tab 路由 + FlowModel 子树 + 角色授权 + uiSchema，DB 复核三项全 0。删除前配置快照留底 `.artifacts/mobile-signup-page-retired/`。

**旧行为兜底**：旧链接 `/v/mobile/3cfhfajaa4x` 不报 404，NocoBase 回退到移动端首页——可接受，历史上若有人下载过旧二维码，扫了也只是落到移动端首页不会报错。

**菜单顺序（同日调整）**：材料提交挪到末位、请假申请成为第一位（即移动端首页）。flow-surfaces 的 move-node 不支持跨页同级排序（报 only-siblings 400，且 RootPageModel 的 parent 是自身，无共同父容器可传），update-menu 也无排序参数——**菜单顺序只由 `desktopRoutes.sort` 决定**（flowModels 表无 sort 列），直接 UPDATE 该页 sort 为最大值解决。调整后底栏顺序：请假申请 / 学员录 / 我的作业 / 课程表 / 材料提交。

**验证**（无头浏览器 390×844，学员 student_test）：①旧链接落到移动端首页且无报名表单 ✓；②菜单无「扫码报名」✓；③进 /v/mobile 直出「提交请假申请」表单，底栏 5 项顺序正确 ✓。脚本 `.artifacts/e2e-check/verify_signup_retired.py`。
