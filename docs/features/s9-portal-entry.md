# s9-portal-entry — admin 排课入口页（iframe 嵌 AI Portal）

> 2026-11-10（D71）。解决"排课三页在 `/x/main` 独立门户，教务用户要开两个地址"的体验割裂问题（Violet 提出并拍板方案 A）。

## 为什么做

- dx.xlsx 需求里「排课管理 / 课表查询」属**智慧教务→教务管理**，「排座管理」属**班务管理**——都是同一个系统的内部菜单，没有"独立排课子系统"的说法。
- 实现上它们是 AI Portal（`/x/main`，React 代码页，拖拽交互无代码做不了），与 admin 无代码门户是两套渲染体系，页面**搬不进** admin。
- 折中：**菜单归位（admin 出入口）+ 渲染留在原地（iframe 嵌 /x/main）**。用户全程只用 `/admin` 一个地址；`/x/main` 保留作直连兜底。

## 规则是什么

| 页 | 位置 | iframe src | routeId |
|---|---|---|---|
| 排课管理 | 教务管理组（教学计划之后） | `/x/main/schedule/board` | 396915888357376 |
| 课表查询 | 教务管理组（排课管理之后） | `/x/main/schedule/week` | 396915913523200 |
| 排座管理 | 班务管理组（退学管理之后） | `/x/main/schedule/seats` | 396915917717504 |

- 页面结构 = flowPage + 单个 jsBlock（key `entryIframe`），代码只做一件事：`ctx.render(<div style={{margin:-24}}><iframe src=... style={{width:'100%',height:'calc(100vh - 64px)',border:0}}/></div>)`。`margin:-24` 抵消 admin 内容区 padding 让 iframe 铺满。
- **蓝本校验器直接放行 iframe 代码**（无 API 调用/自定义 action，D56 的占位+SQL 绕过法这次不需要）。
- 菜单顺序按 dx-requirements 需求层级插入（SQL 直改 `desktopRoutes.sort`，见 D59 排序规则），不是组末尾追加。
- 授权：leader/organizer/academic/teacher 4 角色各授 5 条（教务管理组 + 2 新页 + 班务管理组 + 1 新页）。**纯 iframe 页不涉集合数据，无需 rolesResourcesActions。**
- iframe 与 admin 同源（同 127.0.0.1:13000），cookie 会话互通，无二次登录。
- 学员不用这三个入口（学员视角走 /v/mobile 我的课表直出）。

## 改动影响面与坑

- **embed 模式（D75，2026-11-10 Violet 拍板方案一）**：main Portal `layout.tsx` 加 `?embed=1` 判断——带参时只渲染页面本体（h-svh 全幅，无侧栏/顶栏/内边距）。3 个入口页 iframe src 均已加 `?embed=1`，**已 build+deploy**（bundle index-BbSxP8n6.js）。直连 /x/main 不带参不受影响（侧栏仍在）。jsBlock 模型 uid：s96hi0xk166/ykhawbr91vm/6nia4y84u97，SQL 改法见 D75 坑（转义引号走 SQL 文件 + dollar-quote + docker exec -i）。
- iframe 内不再有 portal 侧栏——**切三页回 admin 菜单**（这正是需求层级本意：三页本是三个独立菜单项）。
- **蓝本校验器直接放行 iframe 代码**（无 API 调用/自定义 action，D56 的占位+SQL 绕过法这次不需要）。
- 菜单顺序按 dx-requirements 需求层级插入（SQL 直改 `desktopRoutes.sort`，见 D59 排序规则），不是组末尾追加。
- 授权：leader/organizer/academic/teacher 4 角色各授 5 条（教务管理组 + 2 新页 + 班务管理组 + 1 新页）。**页面本身不涉集合权限，但 iframe 内 Portal 页会调 7 个业务集合的 API**——organizer 曾因此连环报 403，已补齐（D72/D73/D74，矩阵见 s5-scheduling.md）；leader/academic/teacher 原有权限覆盖。
- iframe 与 admin 同源（同 127.0.0.1:13000），cookie 会话互通，无二次登录。
- 学员不用这三个入口（学员视角走 /v/mobile 我的课表直出）。
- admin 菜单组默认折叠——无头验证时必须先点开组才能看到子项（脚本误判过一次）。
- 产物：蓝本 `.artifacts/nocobase-ui-builder/schedule-entry/`（gen_schedule_entry.py + 3 个 JSON + embed-mode.sql）；验证 `.artifacts/e2e-check/verify_schedule_entry.py`（菜单展开 + iframe 挂载/src 带 embed=1 + 内页渲染且无侧栏 + 直连回归，全绿 pageerror=0）。
- 服务器同步：**dump（3 条 jsBlock + sort）+ main Portal 重 build+deploy（embed 模式）**，两件都要。
