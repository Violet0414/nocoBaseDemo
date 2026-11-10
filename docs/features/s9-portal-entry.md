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

- **零代码改动**：main Portal 源码不动，无需 build+deploy；纯 DB 配置，前端刷新即生效。
- iframe 内保留 portal 自身侧栏（教学排课：周课表/排课画布/座位表），好处是**一个入口内可切三页**不用回 admin 菜单；代价是双层侧栏观感。若要去侧栏需改 main 源码支持 embed 模式（后置可选）。
- admin 菜单组默认折叠——无头验证时必须先点开组才能看到子项（脚本误判过一次）。
- 产物：蓝本 `.artifacts/nocobase-ui-builder/schedule-entry/`（gen_schedule_entry.py + 3 个 JSON）；验证 `.artifacts/e2e-check/verify_schedule_entry.py`（菜单展开检查 + iframe 挂载/src/内页文本三重校验）。
- 服务器同步：纯 DB 配置，随下次 fresh dump 重灌自动带走。
