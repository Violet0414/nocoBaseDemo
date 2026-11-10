# LLM-GUIDE.md — 项目导航地图（给 LLM/新会话用）

> 目的：让 LLM 在**不翻遍全库**的前提下，1) 快速定位菜单配置逻辑；2) 快速定位功能代码/配置；3) 快速梳理项目逻辑。
> 本文档讲"**去哪找、用什么查**"，业务规则细节不在这里（指向对应文档）。最后更新：2026-11-10（D62 后）。

---

## 0. 最重要的认知：这不是普通代码项目

本项目 = **NocoBase v2.4 低代码平台**。绝大多数"功能"不是源码，而是**存在 PostgreSQL 里的配置数据**：

| 你以为的 | 实际上 |
|---|---|
| 页面/菜单/表格/表单 | DB 表 `desktopRoutes` + `flowModels` + `flowModelTreePath` + `uiSchemas` 里的记录 |
| 业务逻辑（审批、联动） | DB 表 `workflows` + `flow_nodes` 里的工作流定义 |
| 字段/集合定义 | `models/collections/*.yaml`（源码）→ push 落库到 `collections`/`fields` |
| 权限 | `roles` / `rolesResourcesActions` / `rolesResourcesScopes` / `rolesDesktopRoutes` / `rolesMultiPortals` |

**真正的手写源码只有一处**：`demo/main/`（Portal main，React，含排课三页 + 二维码页）。
所以「改功能」只有两条路：**改 DB 配置**（SQL 直改 / `nb api` 命令 / 蓝本 apply-blueprint），或**改 Portal 源码**（build+deploy）。

### 容器与连接
- 应用：Docker 容器 `nb-dx-demo-app` @ http://127.0.0.1:13000（线上同构机 10.10.40.44:13000）
- 数据库：容器 `nb-dx-demo-postgres`（用户/库/密码均 `nocobase`）
- 备份：`docker exec nb-dx-demo-postgres pg_dump -U nocobase nocobase > backups/<名>.sql`
- CLI 鉴权：`nb` 命令走 env `dx-demo`（OAuth）；REST 调试走 `Authorization: Bearer <token>` + `X-Authenticator: basic`（仅 X-Token 会 401）

---

## 1. 快速定位菜单配置逻辑（问题 1）

### 1.1 菜单数据存在哪

| 层 | 存储位置 | 说明 |
|---|---|---|
| PC admin 菜单树 | `desktopRoutes` 表（type=group/page；`sort` 决定顺序；`hidden` 隐藏） | 多 Portal 版本另有 `desktopRoutesMultiPortals` |
| 移动端底栏/页面 | `mobileRoutes` 表 | 移动 Portal uid 固定 `__default_mobile__`，入口 `/v/mobile`（/mobile 也通） |
| 菜单可见性（角色） | `rolesDesktopRoutes`（PC）/ `rolesMobileRoutes`（移动）/ `rolesMultiPortals`（门户级开关） | 路由授权是**纯增量**：`add` 授、`remove` 撤 |
| 页面里挂的块 | `flowModels` + `flowModelTreePath`（块挂到哪个 route、排序、列序） | 菜单只是"壳"，页面内容在 flowModels |

### 1.2 菜单组 routeId 速查表（PC admin，全部已建成）

| 菜单组 | routeId |
|---|---|
| 综合门户 | `396734888738816` |
| 教学资源 | `396710905708544` |
| 教材管理 | `396714401660928` |
| 教务管理 | `396723346014208` |
| 班务管理 | `396730107232256` |
| 学员管理 | `396734674829312` |
| 教学评估 | `396739781394432` |
| 审批待办（flowPage） | `396747054514176` |
| 工作台待办（flowPage+jsBlock，D56b） | `396809741205504`（URL `/admin/lv96gv4zgoq`）；旧 legacy `396748572852224` 已 hidden |
| 排课管理 / 课表查询（教务管理组，iframe 嵌 /x/main，D71） | `396915888357376` / `396915913523200` |
| 排座管理（班务管理组，iframe 嵌 /x/main，D71） | `396915917717504` |

移动端底栏顺序（D59 后）：请假申请 / 学员录 / 我的作业 / 课程表 / 材料提交——**顺序只由 `mobileRoutes.sort` 决定**（见 1.4 坑②）。

### 1.3 菜单常用命令模板

```bash
# 查菜单树（角色可见视角，一次拉全）
nb api resource list --resource 'desktopRoutes:listAccessible' --no-paginate -j

# 查某角色被授了哪些路由（默认分页 20 条会漏，必须带 id 过滤）
nb api acl roles desktop-routes list --role-name r_leader -j
nb api acl roles desktop-routes add    --role-name r_leader --body-file <ids数组json> -j
nb api acl roles desktop-routes remove --role-name r_leader --body-file <ids数组json> -j

# 建页/改页（蓝本方式，含挂菜单组）
nb api flow-surfaces apply-blueprint --body-file <json> -j
# 已有组挂页时 navigation 写 {group:{routeId:<id>}}；新建组写 group:{title,icon}；legacy lane 加 layoutUid:"admin-layout-model"

# 删页面（含子树）——注意 target.uid 必须传 RootPageModel 的 uid，不是路由 schemaUid，传错报 popup-child 400
nb api flow-surfaces destroy-page ...
```

### 1.4 菜单四大坑（踩过的，别再踩）

1. **`desktop-routes list` 默认分页 20 条**——验证授权必须 `--filter '{"id":{"$in":[...]}}'` 精确查。
2. **菜单顺序只认 `desktopRoutes.sort`**——`move-node` 不支持跨页同级排序、`update-menu` 无排序参数，改顺序直接 UPDATE sort（D59 实证）。
3. **路由授权 ≠ 集合权限**——页面能看到但数据 403，是 `rolesResourcesActions`/`rolesResourcesScopes` 没授，两套要分开配。
4. **非 admin 角色要能用 Portal**——`rolesMultiPortals` 里必须有 `__default_portal__`（PC main）/ `__default_mobile__`（移动）记录，否则整个门户 403（D48）。

---

## 2. 快速定位功能代码/配置（问题 2）

### 2.1 按意图查：你想改什么 → 去哪改

| 想改什么 | 去哪 | 怎么改 |
|---|---|---|
| 加字段/改集合结构 | `models/collections/nb_dx_*.yaml` | 改 YAML → dsl-reconciler push（见 4.2）；**注意**：required 等 YAML 改动对存量字段 push 会跳过，须 SQL 直改 |
| 页面表格列（列名/绑定/列序） | `flowModels`（TableColumnModel 子模型） | 列序/绑定的 sort、associationPathName 在 `flowModelTreePath.sort` / flowModels 里，SQL 直改最快（D51/D55/D61 三次实证）；定位：`SELECT ... WHERE settings::text LIKE '%<关键字>%'` |
| 表单必填/默认值 | `flowModels` 的 `editItemSettings.required` / `set-field-value-rules` 规则 | **表单校验只认 flowModel 层 settings.required**——集合元数据 options.required / uiSchema.required 都不驱动 Formily 校验（D60 关键坑）；configure 命令不支持 settings，只能 SQL 直改（D62） |
| 弹窗表单结构 | `uiSchemas`（表单模板，形如 tfqyli…） | **多页共用模板会导致上下文字段互相污染**——新增弹窗必须 convert-template-to-copy 拆副本再各自配默认值（D62 根因） |
| 图表（chart） | `flowModels.options.stepParams.chartSettings` | uiSchemas 里读不到，验证只能 SQL like（D32）；关联维度不聚合，须 visual.mode=custom raw 前端自算（D56） |
| 审批流/联动逻辑 | `workflows` + `flow_nodes` | **已执行过的流节点锁死，必须 revision（带 key）出新版**；sync 后旧版自动停用 |
| Portal 页面代码（排课/课表/座位/二维码） | `demo/main/src/features/{scheduling,qr}/` | 改完 `cd main && pnpm build && nb portal deploy main`（deploy 自动 build）；验证 hash：`curl -s http://127.0.0.1:13000/x/main/ \| grep -o 'assets/index-[^"]*\.js'` |
| 权限（谁能看/谁能改数据） | `rolesResourcesActions`（动作）+ `rolesResourcesScopes`（数据范围） | scope 查询：`nb api acl roles data-source-resources get --role-name <r> --data-source-key main --name <表> --appends actions -j`；rolesResourcesScopes 无 CLI 命令面，用 `curl POST /api/dataSources/main/rolesResourcesScopes:create`，绑定用 `scopeId`、resource update 用 `--filter-by-tk` |
| 公开页（扫码报名） | `main/public` 侧 `/signup.html`（nginx public 静态页）+ `r_signup_bot` 窄权限角色 + signup_bot 用户 API key | 服务器重部署必须 docker cp signup.html/logo.png 进 nginx public（属 root，宿主 cp 会 Permission denied） |
| 移动端页面 | `mobileRoutes` + `flowModels`（no-code 配置） | 入口 `/v/mobile`；蓝本规则见 `docs/features/s6-mobile.md` |

### 2.2 按业务模块查：逻辑档案索引

**每模块的"为什么/规则是什么"在 `docs/features/`，这是改功能前必读的第一站：**

| 模块 | 档案 | 要点 |
|---|---|---|
| 教学资源 7 库 | s3-teaching-resources.md | users m2o 显示列用 `.nickname` 非 `.name` |
| 教材管理 | s3-textbook.md | fieldGroups 四大蓝本坑（>10 字段/date 字段/descriptionReview/layout） |
| 教务管理 | s3-academic.md | 同上蓝本坑预防性复用 |
| 班务管理 | s3-class-admin.md | defaultFilter 强制 `{logic,items}` 结构；chart 块必须显式 assets.charts |
| 学员管理+综合门户 | s3-student-portal.md | 单表多视角设计（D20）；S1/S1b/S2 scope 语义区别（D25/D30） |
| 评估/问卷/统计 | s3-eval-survey.md | chartSettings 只在 flowModels；**三页评估表单已拆副本 + kind 静态默认（D62）** |
| 审批流 4 条 | s4-workflow.md | **报名审批唯一入口 = 工作台待办提交**（改表 status 不推进 execution）；manual forms 手写结构；D54 建档开账号分支细节 |
| 排课三页 | s5-scheduling.md | 时区必须显式东八区（beijingClock +8h）；day_of_week 权威列；纯逻辑与 UI 分离 |
| 移动端 6 页 | s6-mobile.md | mobile 蓝本规则；jsBlock 必须 ctx.render；菜单排序坑 |
| 演示数据 | s7-demo-data.md | 41 表数据全景、冲突演示对位置、REST 认证头 |

### 2.3 产物与验证脚本索引（`.artifacts/`）

| 目录 | 内容 |
|---|---|
| `nocobase-ui-builder/` | 各阶段页面蓝本 JSON（stage3-* / stage6-mobile / fix-charts / d56-todo-flowpage / mobile-schedule-inline / fix-portal-chart）——**页面配置的"源码级"备份** |
| `nocobase-workflow/` | 工作流生成脚本（s4-workflows/gen_workflows.py、d51-signup-account/） |
| `e2e-check/` | 无头浏览器验证脚本（verify_*.py，Playwright+Chrome），回归复跑即验证 |
| `public-signup/`、`qr-dialog/` | 公开报名页、二维码弹窗配置 |
| `server-deploy/` | 服务器部署包 + fresh dump（`pkg/nocobase_20261110_server_deploy.sql` = 当前线上全量） |
| `stage7-demo-data/` | 演示数据脚本 gen_demo_data.py（幂等保护） |
| `eval-acl/`、`mobile-signup-page-retired/` | D57 授权补漏、扫码报名页删除前快照 |

### 2.4 备份即历史（`backups/`，不入 git）

每个改动前都有前置 dump：文件名 `nocobase_<日期>_<主题>.sql` 就是**改动时间线**。想知道"某功能什么时候、因什么改的"→ 先查 `STATE.md` 当前位置段（倒序事件流），再查 `docs/decisions.md`（编号决策 D1–D62）。

---

## 3. 快速梳理项目逻辑（问题 3）

### 3.1 分层架构（自下而上）

```
models/collections/*.yaml          ← 数据模型源码（42 集合，nb_dx_* 前缀）
      │ dsl-reconciler push
      ▼
PostgreSQL（容器 nb-dx-demo-postgres）
  ├─ collections/fields             ← 集合与字段（45 张表，含 3 个自动 m2m）
  ├─ desktopRoutes/mobileRoutes     ← 菜单树（7 大组 + 待办页 + 移动底栏）
  ├─ flowModels/flowModelTreePath   ← 页面块（表格/表单/图表/jsBlock），38+ 页面全在这
  ├─ uiSchemas                      ← 表单/弹窗 schema 模板
  ├─ workflows/flow_nodes           ← 4 条审批流
  └─ roles/rolesResources*/rolesDesktopRoutes/rolesMultiPortals  ← 权限
      │
      ├─ Portal main（demo/main/，React）  ← 唯一手写源码：/x/main/schedule/{week,board,seats} + /x/main/qr
      ├─ Portal mobile（no-code）          ← /v/mobile 学员 6 页
      └─ NocoBase admin（no-code）         ← /admin PC 管理端全部页面
```

### 3.2 角色体系（阶段2，D25/D27）

| 角色 | 定位 | 备注 |
|---|---|---|
| admin | 超管 | 密码 Violet 保管 |
| r_leader / r_organizer / r_academic / r_teacher / r_student | 5 业务角色 | 测试账号 *_test，密码 dx123456 |
| r_signup_bot | 公开报名机器人 | 仅报名 create 字段白名单 + 班次 view，配 signup_bot 用户（id 7）10 年 API key |

学员数据隔离 scope：S1 本人（student.user.id）/ S1b 本人（user.id，D30，语义不同不可混用）/ S2 本班 / S2b 班次。

### 3.3 四条审批流与联动（当前启用版本 id）

| 流 | workflow id | 联动逻辑 |
|---|---|---|
| 请假 | `396745412444160`（v2） | organizer 审批；approved 分支 sum(duration_days) 超 class.total_days/7 → over_ratio=true 提醒；**total_days/klass 空值会让 math.js 抛 TypeError 卡死整条 execution（D60 已加 required 防护）** |
| 退学 | `396746379231232`（v2） | leader 审批；approved → 学员 status=dropout |
| 报名 | `396799131385856`（key re5oyih3tpo，v2） | academic 审批；approved → 按手机号查档案 → 无则 create users（username=手机号/password=dx123456/roles=[r_student]）+ create student（挂班）+ 回写 registration |
| 缴费 | `396743055048704` | academic 审批，无特殊联动 |

branchIndex 只标分支首节点（true=1/false=0），分支节点 downstreamId 必须空，否则重复执行（D54a）。

### 3.4 业务主线（演示脚本顺序）

组织员建班 → 学员扫码报名（公开页 /signup.html?class=<id>，未登录可报）→ academic 在「工作台待办」审批 → 通过自动建档+开账号 → 学员登录 /v/mobile（请假申请首页）→ 请假走审批流（超 1/7 提醒）→ 教务排课（/x/main/schedule/board）→ 评估/投票/问卷 → 综合门户统计图表。

### 3.5 全局 Top 坑（改任何东西前先扫一遍）

1. **表单校验只认 flowModel 层 settings.required**（D60）——YAML required / uiSchema.required 都不管用；configure 命令改不了 settings，SQL 直改。
2. **共用表单模板是数据污染源**（D62）——多页共用一个 uiSchema 模板时，上下文字段（kind 等）无默认值 → 落库被列表过滤"吞掉"，表现为"提交了但数据没新增"。先拆副本。
3. **审批必须走「工作台待办」提交**（D54 规则）——直接 UPDATE 表 status 不推进 execution，下游联动（建档/开账号）全不跑。
4. **已执行 workflow 节点锁死**——改流必须 revision 出新版（带 key），新版自动 current+enabled，旧版自动停用；改完必须 sync。
5. **菜单/列顺序只认 sort 字段**——flowModelTreePath.sort（列序）、desktopRoutes.sort（菜单序），命令面都不支持排序。
6. **时区一律显式东八区**（D49）——课表占位日期固定 2026-01-04（周一）起，day_of_week 是权威列，start_time 曾大面积脏。
7. **REST 认证双头**：`Authorization: Bearer <token>` + `X-Authenticator: basic`。
8. **chart 配置只在 flowModels.options.stepParams.chartSettings**，且关联维度（klass.name）不聚合，要 custom raw 前端自算。
9. **desktop-routes / acl list 默认分页 20 条**，验证必须精确 filter。
10. **跑 nb/测试/构建前必 `source ~/.nvm/nvm.sh && nvm use 22`**（jsdom 需 Node 22+）。
11. **`nb api` 报 field-path-unknown**：users m2o 显示列是 `.nickname`。
12. **manual task submit 在 execution 刚创建几秒内会 400** → 重启 nb-dx-demo-app 可解。

---

## 4. 排障 SOP（现象 → 定位）

### 4.1 通用五步

1. **问清楚现象**：哪个页面/哪个角色/什么操作 → 先映射到层（菜单？页面块？工作流？权限？）
2. **查 STATE.md 当前位置段**：倒序事件流里搜关键字，大概率已有同款案例（本项目 62 天全是真实 bug 修复记录）
3. **取证**：
   - 页面配置 → SQL：`docker exec nb-dx-demo-postgres psql -U nocobase nocobase -c "SELECT id,\"assistantKey\",settings FROM \"flowModels\" WHERE settings::text LIKE '%<关键字>%' LIMIT 20;"`
   - 菜单/路由 → `SELECT id,title,type,\"parentId\",sort,hidden FROM desktopRoutes ORDER BY sort;`
   - 工作流 → `nb api workflow workflows list --filter '{"current":true}' -j`；节点链 `workflows get --filterByTk <id> --appends nodes -j`
   - 待办 → `workflowManualTasks:listMine`；execution 状态查 `flow_nodes` job
   - API 层 → `nb api resource list --resource nb_dx_<表> --filter '...' --appends ... -j`
4. **复现**：无头浏览器脚本（参照 `.artifacts/e2e-check/verify_*.py` 任一改）
5. **改完闭环**：改前 dump 备份 → 改 → 脚本验证 → 更新 STATE.md/docs/features → 服务器同步提醒

### 4.2 数据模型改动闭环

```
改 models/collections/*.yaml
→ source ~/.nvm/nvm.sh && nvm use 22
→ cd ~/.claude/skills/nocobase-dsl-reconciler/src
→ NB_TOKEN=$(cat ~/.nocobase/config.json | 取 envs.dx-demo.auth.accessToken) NB_URL=http://127.0.0.1:13000 npx tsx cli/cli.ts push dx-demo --force --copy
→ token 过期先跑 nb env auth dx-demo
→ 改动落 demo/models/state.yaml（push 幂等，重复 push 显示 "="）
```

### 4.3 Portal 代码改动闭环

```
改 demo/main/src/... → cd main && nb portal deploy main（自动 build）
→ 验证 hash：curl -s http://127.0.0.1:13000/x/main/ | grep -o 'assets/index-[^"]*\.js' 对比 dist
→ 浏览器强刷（Ctrl+Shift+R），旧 bundle 会缓存复现
```

### 4.4 服务器同步（10.10.40.44）

本地改动 ≠ 线上生效。每次收口按 `docs/SETUP.md` 第 8 节 fresh dump 重灌，注意：①signup.html/logo.png docker cp 进 nginx public；②main Portal 需重 build+deploy 或随 storage/portals 同迁；③超级用户角色是 `nocobase` 不是 postgres。

---

## 5. 入口文档优先级（读什么、按什么顺序）

| 场景 | 读 |
|---|---|
| 新会话续做 | CLAUDE.md → STATE.md → 本文件对应节 → TASKS.md 找未完成项 |
| 改某模块功能前 | docs/features/sX-<模块>.md（规则）+ STATE.md 该模块速查段（命令与坑） |
| 查某决策为什么 | docs/decisions.md（D1–D62 编号决策） |
| 查原始需求/功能清单 | docs/dx-requirements.md（dx.xlsx 177 行的结构化转录,四大块层级树） |
| 查某天改了什么 | STATE.md 当前位置段（倒序事件流）+ backups/ 文件名时间线 |
| 环境重建 | docs/SETUP.md（1–6 节本机、第 8 节服务器） |
