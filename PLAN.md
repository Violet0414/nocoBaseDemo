# 党校智慧管理平台 Demo — NocoBase + AI Agent 实施计划

## Context

依据 `dx.xlsx` 功能清单(177 行,"党校智慧管理平台":综合门户 / 智慧教务 / 学员服务 / 移动应用 四大块)做 demo。

选型结论(已与用户确认):
- **NocoBase v2 稳定版(≥2.1.0,当前 2.2.40)**。v3 已转代码优先、生态未补齐,不选
- 审批流用**免费版 workflow Manual 节点 DIY**(正规审批节点是 Professional $8000 商业插件)
- 排课/排座**真做,走 AI Portal 写 React 代码**(不写插件,避开插件 client-v2 开发中风险)
- 移动端内置 ui-layout(免费):学员端核心页配置,教职工端 PC 响应式兜底
- **全流程由 AI Agent(Claude Code)驱动**:NocoBase v2 官方支持 Agent 接入(`nb` CLI + Skills),数据建模/页面搭建/workflow 编排/权限配置/AI Portal 前端代码全部 agent 干,人做决策和验收
- License:demo 内部演示可用,不可去 logo、不可对外销售

## 工具链与接入方式

环境决策(2026-11-08 修正,与实际状态对齐):**Docker 只跑 PostgreSQL 数据库,NocoBase 应用本地跑**(nb CLI 管理);数据库 PostgreSQL;旧 test 配置已不存在(`~/.nocobase/` 空),无需清理。

实际状态核实(2026-11-08):
- `nb` CLI **未安装**,需 `npm install -g @nocobase/cli`(registry 最新 stable 2.2.41;原记录"已装 3.0.0-alpha.9"不实)
- Docker Desktop 已安装于 Windows,但 **WSL 集成未启用**(需用户在 Settings → Resources → WSL Integration 勾选)

```bash
# 1. Docker 起 PostgreSQL(应用数据库)
docker run -d --name dx-demo-pg \
  -e POSTGRES_PASSWORD=<密码> \
  -e POSTGRES_DB=dx_demo \
  -p 5432:5432 -v dx-demo-pgdata:/var/lib/postgresql/data \
  postgres:16

# 2. nb CLI 安装与初始化
npm install -g @nocobase/cli         # 2.2.x stable
nb init --ui --locale zh-CN          # 浏览器可视化向导(此步需用户配合点选):
                                     #   选"新安装"、应用版本 2.2.x stable、
                                     #   自定义数据库 localhost:5432/dx_demo、管理员账号
# nb init 自动安装 NocoBase Skills(github.com/nocobase/skills)
# 之后重启 Claude Code 会话,agent 即可操作 NocoBase(http://localhost:13000)
```

跨电脑续做:见 `README.md` / `docs/SETUP.md`;数据备份存 `backups/`(pg_dump),进度快照见 `STATE.md`。

Skills 提供:环境管理 / 数据建模 / 界面配置 / 工作流管理 / ACL / **dsl-reconciler(YAML 批量搭建)** / 插件管理 / 发布 / 版本控制 / AI Portal 搭建。

## 搭建模式分工

| 模式 | 入口 | 用在哪 |
|---|---|---|
| 无代码 Portal(agent 改配置,存 DB,版本快照可回退) | `/v/admin` | 管理后台全部标准页面:各库 CRUD、教材、教务、统计图表 |
| AI Portal(agent 写 React 源码,进 Git) | `/x/main` | 重交互页面:周视图课表、排课画布、拖拽排座、座位表 |
| workflow(agent 编排节点链) | — | 4 条 DIY 审批流 |
| dsl-reconciler(YAML 批量) | — | 按 dx.xlsx 清单批量建数据模型 |

两 Portal 共用同一套 collection + 用户体系,学员端 = 混合(标准页配置 + 课表/座位表走 AI Portal)。

## 功能拆分(对照清单四大块)

### A 类:agent 无代码配置(约 70%)

| 清单模块 | 做法 |
|---|---|
| 教学资源 7 库(师资/专题/活动/基地/拟开发/案例/校外宣讲) | collection + CRUD 区块 + 导入导出 |
| 教材管理全套(信息/采购/领用/退库/荐书/库存报表) | 关联表 + workflow 库存联动 + 图表区块 |
| 班次管理、教学通知(阅读统计)、教学计划 | collection + 区块 |
| 学员管理(信息/相册/档案/学籍/培训记录) | 多对多关联 + 数据范围按角色 |
| 材料"带来留下"、申报信息、纪律承诺 | public forms + collection |
| 作业管理(布置/提交/批阅/转批) | collection + 关联 |
| 教学评估(方案/专题/综合) | 配置表 + 表单 + 统计;先只做分数制,等级/混合制简化 |
| 投票、不记名问卷 | public forms + 统计区块 |
| 考勤统计、社区活跃度 | 图表区块 |
| 综合门户、班级主页、学员主页 | 页面按角色出菜单 |
| 学员社区 | 评论区块 |

### B 类:workflow DIY 审批(约 10%)

统一模式:状态字段 + workflow(提交触发 → Manual 节点审批 → 条件分支改状态 → 通知节点站内提醒)。门户放"待办列表"页凑消息/待办。

| 流程 | 特殊点 |
|---|---|
| 请假申请 | 累计请假 ≤ 总学时 1/7:workflow 变量聚合已批时长,超限标提醒 |
| 退学申请 | 通过后改学员状态 + 账号禁用(简化) |
| 报名审核 | public forms 扫码报名 → 审核;"自动开账号"简化为状态流转,demo 不真开账号 |
| 缴费审核 | 凭证上传 + 审核状态 |

### C 类:AI Portal 写代码(约 15%)

`/x/main` Portal,React 源码进 Git:

- **周视图课表组件**(格子 + 拖拽):PC 主入口,组件响应式,移动端菜单挂 Link
- **排课画布 + 调课**(拖拽专题进格子、拖拽调课,记录调课历史)
- **座位表组件**(教室布局 + 拖拽排座 + 按学号/年龄自动排座)
- 冲突检测/智能排课简化版:调 NocoBase collection API,服务端逻辑用 workflow 或 AI Portal 请求前校验;数据照存 NocoBase collection
- 三维排课视图:有余力再做

已知坑:AI Portal 页面(`/x/`)与移动布局的整合靠 Link 路由(打开 PC 风格页),组件必须做响应式。

### D 类:砍掉 / 静态替代

智能语音(砍)、学业证书 PDF(降级为数据+模板展示,后置)、自助一体机报到(砍,硬件)、短信通知(站内通知代替)、智慧简报(砍或后置)、企微/钉钉/SSO(商业版,砍,用账号密码)。

## 核心数据模型(collections)

组织:users / roles / departments(内置)
教务:class(班次)、student、topic、teacher、activity、base、teaching_plan
教材:textbook、purchase、requisition、return、recommendation、inventory_log
插件/AI Portal 用:course_schedule、change_log、seat
事务:attendance、leave、go_out、dropout、material、declaration
学习:assignment、submission、eval_scheme、eval_record、vote、survey
内容:announcement、news、comment、registration、payment

## 实施阶段(agent 驱动,人做决策验收)

| 阶段 | 内容 | 验证 |
|---|---|---|
| 0 接入 | 装 nb CLI(alpha)→ `nb init --ui`(用户配合向导)→ 重启 Claude Code 会话确认 Skills 生效 | agent 能列出应用环境、执行环境检查 |
| 1 建模 | dx.xlsx 清单 → YAML → dsl-reconciler 批量建 collections + 关联 | 数据模型页可查看,数量与设计一致 |
| 2 ACL | 5 角色(校领导/组织员/教务/教师/学员)+ 数据范围 | 各角色登录,数据边界正确 |
| 3 PC 管理端 | 无代码 Portal 分模块配页面(7 库/教材/教务/班务/评估/统计),**每模块完成存版本快照** | CRUD + 图表可操作,改坏可回退 |
| 4 workflow | 4 条审批流 + 待办列表页 | 请假全流程走通,1/7 占比提醒生效 |
| 5 AI Portal | 课表/排座 React 页面(dev → deploy 循环) | 拖拽排课无冲突,排座自动分配 |
| 6 移动端 | 移动布局配学员核心页:扫码报名/请假/材料/课表(Link)/学员录/作业 | 手机浏览器全流程可操作 |
| 7 收尾 | 造演示数据 + 按角色演示脚本走查 | 脚本完整过一遍 |

每阶段产出可验收、可回退(版本快照),AI 搭建质量不稳时人工介入点在验收环节。

## 风险

- `nb` CLI 与 AI Portal 均为 **alpha** 能力,搭建质量待实战验证;兜底 = 版本快照回退 + 无代码 Portal 手工改配置
- AI 生成代码不保证 100% 正确,报错回喂 agent 排查修复
- 移动端页面仍需单独配一遍(agent 干,人工验收)

## 验证方式(整体)

演示脚本按角色走查:组织员建班 → 学员扫码报名 → 审核通过 → 学员请假(超 1/7 提醒)→ 排课拖拽 → 学员手机看课表 → 评估打分 → 统计出图。
