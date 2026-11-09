# s6 — 移动端学员核心页（阶段6）

> 完成日期：2026-11-09。Portal：`mobile`（no-code，URL `/v/mobile`，portalUid `__default_mobile__`）。
> 蓝本：`.artifacts/nocobase-ui-builder/stage6-mobile/bp1~bp6*.json`。备份：`nocobase_20261109_stage6_mobile.sql`。

## 为什么做

dx.xlsx「移动应用」块的学员核心场景。按 PLAN 既定（D4），移动端用内置 no-code 移动 Portal 配置（免费），AI Portal 排课三页（`/x/main/`）组件本身响应式，移动端以 Link 打开 PC 页兜底，不重复实现。

## 页面清单（6 页，全部 mobile root 顶级入口）

| 页面 | routeId | pageSchemaUid | 主块 | 表 |
|---|---|---|---|---|
| 扫码报名 | 396774382895104 | 3cfhfajaa4x | createForm | nb_dx_registration |
| 请假申请 | 396774621970432 | 80a2tclmlct | createForm + 我的请假 table | nb_dx_leave |
| 材料提交 | 396774414352384 | xm89i0vlzcq | createForm | nb_dx_material |
| 学员录 | 396774630359040 | ru5tj20ddta | table（recordActions 仅 view） | nb_dx_student |
| 我的作业 | 396774636650496 | owx51rwfogb | 作业列表 table + 提交作业 createForm | nb_dx_assignment / nb_dx_submission |
| 课程表 | 396774655524864 | jxuptin8mn3 | jsBlock 入口卡（window.open → `/x/main/schedule/week`） | — |

## 规则与决策

1. **权限粒度**：r_student 新增 12 条 route 授权（6 页 + 6 个 hidden tabs 子 route）；表权限仅补了 `nb_dx_material` create（阶段2 已配齐其余 5 表）。`nb_dx_student` 学员录保持 view-only，recordActions 只留 view。
2. **数据范围继承阶段2 scope**：学员的"我的请假记录"和作业列表自动被 S1/S2 scope 过滤（实测 assignment count=1 只见本班作业）。
3. **课表挂 Link 而非重建**：移动端「课程表」页是 jsBlock 渲染的入口卡，点击 `window.open('/x/main/schedule/week')` 打开 AI Portal 周课表。不复制课表数据，单一数据源。
4. **审批闭环复用阶段4 workflow**：移动端请假 createForm 提交 status=pending，直接触发请假审批流（组织员待办）；报名记录由教务在 PC 端审核。移动端不配审核界面（审核是教职工场景，PC 响应式兜底）。
5. **表单字段裁剪**：所有 createForm 只放学员可填字段，状态/审核人/批阅分数等字段一律不放（由流程写回）。

## 踩坑记录（阶段6 新增）

1. **mobile 页 identity**：mobile-backed Portal 蓝本 `navigation` 只带 `portalUid`，omit `group` 和 `layoutUid`；`navigation.item.icon` 必填（页面入口图标）。
2. **关联目标 >10 字段必须 fieldGroups**（复现阶段3-2 坑）：本次 `nb_dx_class`（15 字段）与 `nb_dx_student`（15 字段）都要在 `defaults.collections.<目标表>.fieldGroups` 提供全字段分组，漏一个字段报 `default-field-groups-incomplete`（student 漏 user 报错过一次）。且 fieldGroups 必须挂在**被关联的目标表**键下，不是引用方表下。
3. **m2o 字段 titleField 必须显式对象形式**：`nb_dx_class` 的 YAML titleField=name 在 live 元数据里未生效（落到 id），蓝本报 `relation-titleField-unreadable`。所有 m2o（klass/student/topic/teacher/review_by/assignment）统一写 `{"field":"x","titleField":"name|nickname"}`（users 用 nickname）。
4. **多块 layout 不许每块独占一行**：`block-layout-single-column` 报错。两块（表单+表格）必须同行（各 span 12）。与阶段3 踩坑④同源。
5. **applyBlueprint 蓝本不支持 js action 的 `clickSettings`**：configureOptions 仅支持 title/tooltip/icon/iconOnly/type/color/htmlType/position。要放 JS 逻辑用 **jsBlock**（`settings.code`，strict render：必须 `ctx.render(...)` + `ctx.libs.antd` JSX）。

## 验证记录（2026-11-09）

- 学员账号 student_test API 实测：leave create（id=8，status=pending，进审批流）／material create／assignment list（count=1，本班 scope 生效）／submission create／registration create 全部 200。
- route 授权读回 12/12 命中（r_student）。
- `/v/mobile` 与 `/mobile` HTTP 200。
- 浏览器端手机走查待 Violet（芒果怪无浏览器环境）。

## 遗留

1. **公开扫码报名未做**：当前报名页在登录态下可用；真正的"未登录扫码报名"需 public forms 链接，demo 演示用登录态报名页替代，如需公开表单后置补。**2026-11-09 已补「班次报名二维码」入口链路，见下方补充节。**
2. 移动端页面在真机/窄屏的表现待 Violet 手机浏览器走查。

## 补充：班次报名二维码链路（2026-11-09）

「班次的二维码在哪」走查反馈补做。三段链路：

1. **AI Portal 二维码页 `/x/main/qr`**（main 源码 `src/features/qr/class-qr.tsx`，路由 hidden 不进侧边栏）：`?token=<qr_token>`（来自班次管理页行操作）或页内下拉选班次 → 用 qrcode 库本地生成 PNG（无外网 CDN 依赖）→ 可下载。二维码内容 = `window.location.origin + /mobile/3cfhfajaa4x?class=<班次id>`，origin 自适应，换部署地址无需改配置。
2. **admin 班次管理页「报名二维码」行操作**（JSRecordActionModel uid `s5w1ecobnf2`）：`window.open('/x/main/qr?token=' + ctx.record.qr_token)`。
3. **移动报名页自动带班次**：表单 `fieldValue` 规则（uid `mgyr71ht7sj`，key `autoKlassFromUrl`）——`urlSearchParams.class` 非空时 klass 字段默认值 = runjs `Number(参数)`。学员扫码打开报名页，班次字段自动选中对应班次，仍可手改。

设计取舍：二维码 URL 直接带班次 id 而非 `qr_token`，因为 fieldValue runjs 是同步取值场景，无法先查 `qr_token→id`；`qr_token` 仍保留在 `nb_dx_class` 作为行操作入口参数。公开（未登录）报名仍需 public forms，后置。
