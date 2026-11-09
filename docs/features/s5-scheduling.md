# s5-scheduling — AI Portal 课表/排课/排座页面

> 阶段5：AI Portal（Portal main）内用 React 实现的三页：周课表、排课画布、座位表。源码在 `main/src/features/scheduling/`，路由挂 `/schedule/*`（「教学排课」菜单组）。

## 为什么用 AI Portal 而不是无代码页面

排课画布（拖拽）与座位图（网格拖拽）这类交互无代码蓝本做不了，PLAN 阶段5 即定义为 React 源码页。承载机制见决策 D36（升级 2.4.0-alpha.17 才有 Portal 机制）。

## 信息架构

- 菜单组「教学排课」（`/schedule`，meta.group）下三页：
  - 周课表 `/schedule/week`（只读视图 + 冲突提示卡）
  - 排课画布 `/schedule/board`（拖拽排课/调课入口）
  - 座位表 `/schedule/seats`
- `registryRoutesEnabled=false` 关闭模板 demo 路由，三页 lazy import

## 业务规则

### 时间模型

- 课表格子由 `week_no`（周次）+ `day_of_week`（1–7，权威字段）+ 时段（TIME_SLOTS 5 节：08:30–10:10 / 10:30–12:10 / 14:00–15:40 / 16:00–17:40 / 19:00–20:40）定位。
- `start_time`/`end_time` 仅作展示占位：写入时统一用 `2026-01-04`（周一）起的固定日期 + 时段起止。**理由**：模型里 day_of_week 与 start_time 双轨并存（阶段1 YAML 既定），前端以 day_of_week 为准，避免日期换算引入时区坑。
- 时段反推：`slotFromTime` 按 start_time 的 hh:mm 落在哪个时段区间判定；跨天兜底 `dayFromTime`（getDay 0 → 7）。

### 排课与调课

- 拖专题进格子 = create `nb_dx_course_schedule`（kind=lecture、eval_enabled=true、status=pending、place=班次 default_room）。
- 拖已有课到新格子 = update + 写一条 `nb_dx_change_log`（summary「调课：X 原时段 → 新时段」、old_values/new_values JSON、reason=画布拖拽调课、notified=false）。**调课历史必须落库**，通知（notified 置 true）后置。
- 「智能排课（简化版）」= 贪心：未排专题按顺序填第一个空格子，不保证最优，只保证不冲突。

### 冲突检测（前端本地）

- 同周次内两记录同时段（week_no + day + slot 全同）且满足其一即冲突：同教师（teacher_id 相同）、同教室（place 字符串相同）。
- 冲突格子红色高亮 + 顶部 Badge + 周课表页冲突提示卡。**仅前端检测**，服务端 workflow pre-action 校验后置（见 decisions D38）。

### 排座

- 座位初始化：按教室布局 6 排 × 8 列逐格 create `nb_dx_seat`（label=r-c，kind=normal），已有座位不再重复初始化。
- 自动排座：空座位按 row_no→col_no 排序，学员按学号（localeCompare numeric）或出生日期（早=年长在前）排序，顺序填充；只填空位，不动已排学员。生成的是本地方案，点「保存排座」diff 后才写库。
- 手动拖拽：座位↔座位交换、未分配学员→空位、座位→未分配区清空，均先改本地 state，统一保存。

## 数据契约（关键，迭代改字段先看这）

2.4 alpha REST 形态与旧版不同（决策 D37）：

- create/update body **平铺**（不收 `{"values": {...}}` 包装）
- update 走 `?filterByTk=<id>`，响应是数组取 `[0]`
- filter 用 FK 列名（`class_id`），appends 用关联名（`class`/`topic`/`teacher`/`student`）——YAML 里的 `klass` 字段名在 REST 层不存在
- 写入 m2o 可直接给 FK 列（`class_id: 1`）或关联名（`student: 1`）

通用封装在 `api.ts`：`listResource` / `createRecord` / `updateRecord` / `resolveId`；纯逻辑（`detectConflicts` / `autoAssignSeats`）与 UI 分离，vitest 单测在 `main/tests/logic/scheduling.test.ts`。

## 验证方式

- 自动化：typecheck + eslint + 逻辑单测通过；模板自带 route-overlay-viewport 测试因 portal-sdk 版本上下文不兼容持续失败（与本次改动无关，模板问题）。
- 浏览器端走查（拖拽手感、冲突高亮、保存反馈）由 Violet 验证——芒果怪无浏览器环境。

## 修复记录：AI Portal 页面班次下拉为空（2026-11-09，D47）

Violet 走查发现 AI Portal 页面（/qr 及排课三页）下拉框选不出班次。无头浏览器（Playwright）复现并定位：

- **根因**：`nocobaseClient.action` 默认 `unwrap: "data"`——返回值已经是 `payload.data` 本体；而 `api.ts` 的 `listResource` 又取了一层 `res.data`，永远是 `undefined`，最终 `return res.data ?? []` 返回空数组。**API 请求本身 200 且有 4 条数据，组件拿到的永远是 `[]`**。`createRecord` / `updateRecord` 同样多包一层。
- **修复**：三个 helper 统一适配 unwrap 后的返回形态（数组/单对象/含 data 包装三种兼容）。业务代码全部走这三个 helper，一处修复覆盖 /qr + 排课三页（周课表/排课画布/座位表此前在浏览器端同样坏，阶段5 只验证过 API 层）。
- **验证方式升级**：本机有 Playwright + Chrome（此前"无浏览器环境"不成立），已用无头浏览器回归：/qr 下拉 4 班次、选中生成二维码；周课表选班次后课节与冲突提示正常。后续走查先用无头浏览器自测再交 Violet。

## 修复记录：排课画布拖拽落点错位（2026-11-09，D49）

Violet 反馈"课程拖拽释放后，新位置不是鼠标所释放的位置"。数据取证（调课日志 + 库存值交叉比对）定位根因：

- **根因 = 旧构建的时间写入格式错误**。Violet 走查时浏览器加载的是 18:07 构建（commit 5a45189），其拖拽写入 `2026-01-${4+day-1}T08:30:00.000Z`——两个错：①日期基准 `4+day-1` 把周一写成 1 月 4 日（周日），差一天；②**`.000Z` 后缀把北京钟面值直接当 UTC 存**，UTC+8 浏览器回读解析成 16:30 等 → `slotFromTime` 反算出错误的节次行（08:30Z → 16:30 → "下午第2节"），显示位置与释放格不符。
- 当前构建已用 `slotTimes`（`4+day` + `+08:00` 语义，服务器正确换算为 UTC），CLI 实测 create/update 均正确转换；但 **`slotFromTime`/`dayFromTime` 此前依赖浏览器本地时区解析**——演示机时区若非东八区仍会错位。本次改为显式东八区（`beijingClock` = UTC+8h 固定偏移 + `getUTC*` 取钟面），任何时区浏览器反算结果一致。
- **存量数据修复**：被旧构建写坏的 11 条（UTC 钟面恰等于时段起点 08:30/10:30/14:00/16:00/19:00，判据与好行零重合）按 `day_of_week`（权威列）+ UTC 钟面还原节次重写；另对齐 14 条种子数据的日期基准（`4+day-1` 同源错位）。修复后全表 29 条 start_time/end_time 与 day_of_week/节次全部自洽。
- 部署：pnpm build + `nb portal deploy main`（bundle index-DN4vEZiv.js）。**Violet 需强刷（Ctrl+Shift+R）再走查**，否则浏览器缓存旧 bundle 仍会复现。
- 备份 `backups/nocobase_20261109_fix_schedule_tz.sql`。
