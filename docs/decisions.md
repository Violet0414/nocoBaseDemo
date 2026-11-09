# decisions.md — 关键决策记录

> 新决策随时补录。避免后续会话重复讨论已定事项。

## 2026-11-08 及之前（迁自 test_demo/PLAN.md）

| # | 决策 | 原因 |
|---|---|---|
| D1 | NocoBase **v2 stable（2.2.41）**，不选 v3 | v3 已转代码优先、生态未补齐 |
| D2 | 审批流用**免费版 workflow Manual 节点 DIY** | 正规审批节点是 Professional $8000 商业插件 |
| D3 | 排课/排座**真做，走 AI Portal 写 React** | 不写插件，避开插件 client-v2 开发中风险 |
| D4 | 移动端用内置 ui-layout（免费） | 学员端核心页配置，教职工端 PC 响应式兜底 |
| D5 | 全流程 AI Agent 驱动（nb CLI + Skills） | 人做决策和验收 |
| D6 | License 约束 | demo 内部演示可用，不可去 logo、不可对外销售 |
| D7 | 砍掉/降级项 | 智能语音、自助一体机（硬件）、短信通知（站内代替）、学业证书 PDF（后置）、企微/钉钉/SSO（商业版） |

## 2026-11-08（本会话新增）

| # | 决策 | 原因 |
|---|---|---|
| D8 | **管理端优先**：阶段0→1→2→3→4 先行，5/6/7 后置 | Violet 指示优先做管理端功能 |
| D9 | 工作目录迁至 `F:\顺拓\demo`，test_demo 保留为存档 | Violet 要求所有工作内容输出在 demo 文件夹 |
| D10 | **不用 git，纯文件夹拷贝**做同步；可移植性靠文档（CLAUDE/STATE/SETUP）+ pg_dump 备份 | Violet 确认；不依赖本机状态是续做关键 |
| D11 | PostgreSQL 用 Docker Desktop（启用 WSL 集成）而非 WSL 直装 | Violet 确认；与原方案一致 |
| D12 | nb CLI 装 registry 最新 stable 2.2.41 | 原记录"已装 3.0.0-alpha.9"与实际不符，已修正 |
| D13 | 环境事实修正：`~/.nocobase/` 不存在，旧配置清理项跳过 | 2026-11-08 实测 |
| D14 | NocoBase 实际安装方式：**Docker 源 + 内置数据库 + OAuth 认证**（nb 托管容器 nb-dx-demo-app/nb-dx-demo-postgres），替代原计划的 npm 本地跑 + 自建 dx-demo-pg | Violet 在 nb init 向导中的实际选择；数据全在 PG volume，pg_dump 备份可覆盖，可移植性不受影响 |
| D15 | Docker 镜像加速源换为 1ms.run + daocloud | 原 USTC 源已停止服务；Docker Hub 直连在本网络不通 |
| D16 | demo/ 文件夹内不放应用本体（应用在容器内），只放文档/备份/产物 | Violet 确认目录隔离优先；换电脑按 SETUP.md 重建容器并恢复备份 |

## 2026-11-08（阶段1 数据建模）

| # | 决策 | 原因 |
|---|---|---|
| D17 | 数据模型定为 **42 个 collections**（PLAN 原 33 个）：教务 13 / 课表座位 3 / 教材 6 / 事务 7 / 学习 8 / 内容 5 | 按 TASKS.md 阶段3 模块清单与 dx.xlsx 功能清单补齐 PLAN 漏列项：拟开发专题/教学案例/校外宣讲（凑齐 7 库）、选修计划+选课记录、教学资料、纪律承诺、投票明细、问卷答卷；阅读统计用 m2m readers 实现（不建独立流水表） |
| D18 | dsl-reconciler workspace 放 `demo/models/`，skill 侧用 symlink 接入；统一命名前缀 `nb_dx_`、字段 snake_case | 所有产物必须落 demo 文件夹（CLAUDE.md 纪律）；前缀避免与系统表冲突 |
| D19 | 教材退库 collection 命名 `nb_dx_textbook_return`（不用 `return`） | RETURN 是 SQL 关键字风险 |
| D20 | 学员培训记录简化：每次参训建一条 student 记录（klass m2o），不做独立培训记录表 | demo 粒度；档案追溯按姓名/手机号查历史班级即可 |
| D21 | 请假 1/7 规则的数据支撑：class.total_days（总学习天数）+ leave.duration_days（支持小数）+ leave.over_ratio（超限标记，workflow 写入） | dx.xlsx 明确"累计请假不超过总学习天数 1/7" |
| D22 | 推送认证走 `NB_TOKEN`（取自 nb 的 OAuth accessToken），不依赖账密 | 应用为 OAuth 设备登录；token 过期用 `nb env auth dx-demo` 刷新 |

## 2026-11-09（阶段2 ACL）

| # | 决策 | 原因 |
|---|---|---|
| D23 | **阶段2 权限矩阵定稿**：r_leader 全 45 表 view+export；r_organizer CRUD 10 表（student/class/registration/事务7表）+ view 11 表；r_academic CRUD 23 表（教学资源7库+教材6表+教务类）+ view 9 表；r_teacher CRUD 11 表（考勤/作业/评估/问卷/投票）+ view 7 表；r_student create+view 11 表 + view 24 表。 Violet 确认的矩阵方案 | 全部走 `apply-data-permissions` 一次批量写入，显式全字段 + 显式 scope 绑定 |
| D24 | **菜单 route 权限推迟到阶段3**，随每个页面创建同步配置 | 阶段2 时 desktop 菜单尚未建立，先配会返工（Violet 确认） |
| D25 | **学员数据范围严格版实现**：S1 本人记录 scope=`student.user.id = {{$user.id}}`（13 张带 student 字段表共用）；S2 本班 scope=`klass.students.user.id = {{$user.id}}`（11 张带 klass 字段表共用）；S2b 班次专用 scope=`students.user.id`（nb_dx_class）；答卷表(nb_dx_survey_answer)无学员字段用内置 own。scope id：S1=396708890345472 / S2=396708894539776 / S2b=396708898734080 | Violet 选严格版；filter 走 ID 组 $eq + ACL 上下文变量，符合 Filter Authoring Gate |
| D26 | **「学员只见本班」数据级验证待补**：阶段2 已验证允许/拒绝边界（200/403/create/destroy），演示数据（阶段7）入库后需补测 scope 过滤结果 | 当前库内无业务数据，scope 过滤结果集为空无法断言 |
| D27 | 5 个测试账号：leader_test/organizer_test/academic_test/teacher_test/student_test，密码 dx123456（user id 2–6） | 各角色登录验证与后续演示用 |
| D28 | NocoBase 越权 destroy 返回 HTTP 500 包体 `{"errors":[{"message":"No permissions"}]}`（非 403），以响应体为准判断拦截成功 | 实测现象，避免误判为服务器错误 |
| D29 | **测试账号必须解绑内置 `member` 角色**：新建用户自动绑定 member（default 角色），登录时优先用 member 导致「全菜单只读」假象；已用 `acl roles users remove --filter-by-tk "2,3,4,5,6"` 把 5 个测试账号的 member 解绑，各账号只留 r_* 角色。以后新建测试账号都要检查并解绑 member | 2026-11-09 实测：member 遮蔽 r_* 角色的菜单与数据权限 |

## 2026-11-09（阶段3-5 学员管理 + 门户）

| 编号 | 决策 | 理由 |
|---|---|---|
| D30 | **r_student 补 nb_dx_student view（全 16 字段）+ 新建 S1b scope**（id 396733982769152，filter `user.id = {{$user.id}}`，仅绑 student 表）。注意与 S1 区别：S1 的 filter 是 `student.user.id`（适用于带 student m2o 字段的 13 张表），student 表自身无 student 字段，必须用 `user.id` 直达的 S1b，不可混用。Violet 确认选"补 view + 本人 scope"方案 | dx.xlsx 学员端需要学员主页/相册/培训记录；D23 矩阵原未授 student 表 |
| D31 | **评估/投票问卷模块页面拆分**：①投票管理页只放 vote 主表不放 vote_record（organizer 无 vote_record 权限，避免整页授不了 route）；②vote_record 查看收敛到「统计图表」页（仅 leader/teacher）；③不记名问卷双 tab 整页不授 organizer（无 survey_answer 权限）；④统计图表页仅 leader/teacher（管理视角）；⑤评估记录四类 kind 拆两页过滤 topic/comprehensive，party 两类留在班务模块 | 按实测 collection ACL 反推 route 授权，避免"授了 route 块却报错" |
| D32 | **chart 块配置存在 `flowModels.options.stepParams.chartSettings`（use=ChartBlockModel），不在 uiSchemas**；avg 聚合写法 `{"field":"score","aggregation":"avg","alias":...}` 与 count 同构有效；survey_answer 描述字段需 `formBehaviorDescriptionReview`（decision=unsupported/reasonCode=ambiguous-description，同教材 stock 字段） | chart 用 uiSchemas/schema 读回会扑空；验证走 SQL `select count(*) from "flowModels" where options::text like '%<alias>%'` |

## 2026-11-09（阶段4 workflow 审批流）

| 编号 | 决策 | 理由 |
|---|---|---|
| D33 | **manual 节点审批结果写法**：form 类型=update 定位触发记录，通过/驳回两个 action 按钮各带 `values:{"status":...}` 预设值（审批人只点按钮），两个 action 的 job status 均用 1(RESOLVED) 保证驳回不中断流程，驳回报错风险归零；"账号禁用"简化为学员学籍状态流转（D27 任务描述既定） | 商业 approval 插件不可用（D2），手写 forms 结构已验证可行（结构记录见 s4-workflow.md 踩坑1） |
| D34 | **审批操作入口用 legacy page 挂 WorkflowTodo 块**（工作台待办，routeId 396748572852224），查看入口用 flowPage（审批待办，396747054514176，dataScope status=pending）；两页均授 leader/organizer/academic | flowPage 蓝本只支持 table/chart/jsBlock/markdown 四种块，挂不了 manual 插件的 WorkflowTodo 组件；flowPage schema 在 flowModels 不走 uiSchemas 树 |
| D35 | **审批人分配**：请假→组织员 r_organizer（班主任职能）、退学→校领导 r_leader（重决策）、报名/缴费→教务 r_academic（教务职能）；manual assignees 写死测试账号 user id（3/2/4），换正式账号时需 revision 更新节点 | dx.xlsx 业务常规；manual 节点 assignees 仅支持具体 user id 数组（不支持角色变量） |

## 2026-11-09（阶段5 AI Portal：升级 + 课表/排课/排座页）

| 编号 | 决策 | 理由 |
|---|---|---|
| D36 | **为启用 AI Portal 升级到 NocoBase 2.4.0-alpha.17**：Violet 两次拍板（先选"升 2.3.0-beta"，实测无 Portal 后选"走真 Portal"）。调研结论：Portal 机制（multiPortal + `nb portal` 命令面）真实存在于 2.4.0-alpha.17，portal-template-default 包本身只在 3.x 发布，2.4 alpha 运行时即够用，不必跳 3.0。两次升级前均 pg_dump 全库备份；升级后验证 45 表/4 workflow/90 路由无损（页面类型改名 flowPage） | AI Portal 课表/排课/排座拖拽页无代码做不了（PLAN 阶段5 既定） |
| D37 | **2.4 alpha REST API 形态三要点**：①create/update body 必须平铺，`{"values":{...}}` 包装被静默忽略（字段全 null 写入）；②update 用 `?filterByTk=<id>`（非 `:update/<id>` 路径），响应是数组取 [0]；③filter 用 FK 列名（`class_id`）、appends 用关联名（`class`/`topic`/`teacher`/`student`）——YAML 字段名 `klass` 在 REST 层既非 association 也非 attribute。写入 m2o 给 FK 列或关联名均可 | 2026-11-09 逐项 curl 实测，见 docs/features/s5-scheduling.md 数据契约节 |
| D38 | **课表时间模型：day_of_week 为权威字段**，start_time/end_time 仅展示占位（固定 2026-01-04 周一起的日期 + 时段起止）；冲突检测（同教师/同教室同时段）**仅前端本地实现**，服务端 workflow pre-action 校验后置 | 避免双轨字段日期换算引入时区坑；demo 阶段前端检测够用，正式版需服务端兜底 |
| D39 | **阶段5 AI 交互未落地，如实报告**：运行时有 AI 员工（Atlas）但 LLM 服务配置为 0（无任何模型 key），AI 交互无法真实运行。候选交互（排课冲突智能解读、课表自然语言查询）待 Violet 提供 LLM key 后补做 | nocobase-ai-builder 规范要求：缺运行时能力须诊断并报告，不得静默跳过或假装完成 |

## 2026-11-09（阶段7 演示数据）

| 编号 | 决策 | 理由 |
|---|---|---|
| D26 | **「学员只见本班」数据级验证通过，决策关闭**（原遗留项）：student_test 登录实测——学员表只见本人（S1b）、请假/考勤只见本人记录（S1）、座位/班次只见本班（S2）、新闻全员可见 | 演示数据入库后 scope 过滤结果集非空，可断言；全部符合预期 |
| D40 | **演示数据全集以脚本生成、幂等保护、一次灌入**：4 班次（覆盖 ongoing/enrollable/planned/finished 四态）/ 21 学员 / 8 师资 / 12 专题 / 29 课节（预置 1 对冲突演示 + 1 条调课记录）/ 48 座位 / 41 表全覆盖；班1 学员1 张明远绑 student_test 供全流程演示；REST 写入认证头必须 `Authorization: Bearer` + `X-Authenticator: basic`（仅 X-Token 401），destroy 带 filter 须放 query | 脚本可复用于环境重建；6 条踩坑记录在 docs/features/s7-demo-data.md |
| D41 | **演示数据附刻意冲突演示对**：第1周周三第1节「依法行政」「压力管理」两节同占第一报告厅（不同教师）——单班课表即可触发冲突高亮，无需跨班操作 | Violet 走查阶段5 冲突检测时零准备成本 |

## 2026-11-09（服务器部署）

| 编号 | 决策 | 理由 |
|---|---|---|
| D42 | **服务器部署走 compose 双容器、不装 nb CLI**：内网机 10.10.40.44（Ubuntu 24.04，ops 用户，Docker 已装）上以 docker-compose 起 `nocobase:2.4.0-alpha.17-full` + `postgres:16`，本机 dump + storage（portals/uploads/apps）随迁，`APP_KEY` 原样保留。纯 pg_dump 不够——Portal 产物与上传文件均落 storage bind mount 不在库内；`apps/main` 下 root 权限文件须 `docker cp` 从容器取出。restart 策略 `unless-stopped`（优于本机 nb 托管的 no 策略） | 内网试用最快路径：复刻本机容器拓扑，避免服务器装 Node/nb CLI/向导交互；compose 文件与迁移包沉淀在 `.artifacts/server-deploy/`，步骤见 SETUP.md 第 8 节 |

## 2026-11-09（走查问题修复：图表中文 / 板块高度 / logo）

| 编号 | 决策 | 理由 |
|---|---|---|
| D43 | **chart 英文分类改 custom visual + raw 中文映射**：6 个按 select 字段 value 分组的 chart（库存报表 category / 学籍 status / 考勤 status / 请假 status / 评估 kind×2）`visual.mode` 改 `custom`，raw 里用 labelMap 把 value→中文 label 后 return ECharts option（ChartOptionModel：直接 return，数据取 `ctx.data.objects`）。投票选项分布不动（option_selected 本身存中文文本）。localized `configure` 的 chart 合法键：title/description/height/heightMode/query/visual/events（直接放 `changes` 下，不包 settings） | builder basic 模式不翻译 select value；custom 是唯一可控渲染路径。系统 locale 本就是 zh-CN，内置按钮文案无需处理 |
| D44 | **附件匿名读 + logo 走公开路径**：①给 `anonymous` 角色授 main.attachments view（files 路由 302 通过）；②`/storage/uploads/*` 由 nginx `auth_request`（nb env proxy 的 legacy file auth）拦截，匿名永远 401，因此 logo 不走 uploads：文件放 nginx public 目录 `storage/.nocobase/proxy/nginx/default/public/logo.png`（无鉴权），`attachments.id=1.url` 改为 `/logo.png`。admin 账号 nickname 顺手改「管理员」 | 登录页左上角 logo 破图的根因是匿名 401；不动 nginx 托管配置（会被 `nb env proxy` 重渲染覆盖）。**服务器同步时须：把 logo.png 复制进服务器同路径 public 目录 + dump 里的 url 改动随迁**，否则服务器登录页 logo 仍破图 |
| D45 | **并排两块高度对齐用 specifyValue**：库存报表页 chart+table（12/12 并排）统一 `height: 380 + heightMode: "specifyValue"`（cardSettings.blockHeight） | 后端读回主标准是 cardSettings.blockHeight；默认高度两块不一致导致错位 |

## 2026-11-09（补做：班次报名二维码）

| 编号 | 决策 | 理由 |
|---|---|---|
| D46 | **二维码链路：AI Portal `/x/main/qr` 生成页 + admin 班次行操作 + 移动报名页 URL 自动带班次**。①`/x/main/qr`（main 源码 `src/features/qr/class-qr.tsx`，路由 `hidden: true` 不进侧边栏，sidebar 过滤 `meta?.hidden`）用 qrcode npm 包本地生成 PNG（内网无 CDN 依赖），origin 自适应，支持下载；②班次管理页 JSRecordActionModel 行操作 `window.open('/x/main/qr?token='+ctx.record.qr_token)`（JS action ctx 合法 root 是 `ctx.record`，不支持 `ctx.flowCtx`）；③报名表单 fieldValue 规则 `autoKlassFromUrl`：`urlSearchParams.class` 非空时 klass 默认值 = runjs `Number(v)` | Violet 走查反馈"班次的二维码在哪"——qr_token 字段有数据但从未生成展示。**二维码 URL 带班次 id 而非 qr_token**：fieldValue runjs 是同步取值场景查不了 token→id；qr_token 保留作行操作入口参数。公开未登录报名仍需 public forms，后置 |
| D47 | **AI Portal 页面下拉空 = api.ts 双 unwrap bug**：`nocobaseClient.action` 默认 `unwrap:"data"` 返回的已是 `payload.data` 本体，`listResource` 再取 `res.data` 永远 undefined → 返回 `[]`（请求 200 有数据但组件拿空）。三个 helper（listResource/createRecord/updateRecord）统一适配；业务调用全走 helper，一处修复覆盖 /qr + 排课三页。**验证方式升级：本机有 Playwright+Chrome（此前"无浏览器环境"不成立），走查先用无头浏览器自测** | Violet 走查暴露；阶段5 当时只验证了 API 层。无头浏览器复现链：popup 打开但高 0 → fiber 里 classes=ARR(0) → 抓响应体 4 条 → 定位双 unwrap |
| D48 | **AI Portal 角色授权**：阶段2 create-blank 角色基线带 `!ui.*` snippet，所有非 admin 角色访问 `/x/main/` 被 multi-portal 插件 `roles:check` 拒（PORTAL_ACCESS_DENIED）→ 移动端「课程表」入口对学员是死链。修复 = 5 角色各插一条 `rolesMultiPortals`（multiPortalUid=`__default_portal__`）。学员进 Portal 后 S2 scope 使班次下拉只有本班、自动选中即正确班次 | Violet 走查副发现；无头浏览器实测学员登录直达周课表、课节/冲突正常 |
| D49 | **排课画布拖拽落点错位**：走查时浏览器加载旧构建（18:07），其拖拽写入 `2026-01-${4+day-1}T…:00.000Z`——日期基准差一天 + 北京钟面当 UTC 存，回读在 UTC+8 浏览器解析成 16:30 等 → 节次反算错位。修复：①代码已用 `slotTimes`（+08:00 语义）且 `slotFromTime`/`dayFromTime` 改显式东八区（beijingClock 固定偏移），不再依赖浏览器时区；②存量 25 条坏数据按 day_of_week（权威列）+钟面还原重写，全表 29 条自洽；③build+deploy 后 **Violet 必须强刷**。教训：时间字段写入统一走 slotTimes，任何"钟面当 UTC"写法都会在回读时错位 | Violet 走查反馈；取证靠 nb_dx_change_log 的调课时间线 + 库存 UTC 值交叉比对 |

## 2026-11-09（走查问题修复：报名待审空数据 / 操作栏列序）

| 编号 | 决策 | 理由 |
|---|---|---|
| D51 | **移动端 createForm 状态字段默认值必须用 fieldValue 规则补齐**：扫码报名（status=pending）此前漏配 → UI 提交落库 status 为空，报名待审 tab 按 `status=pending` 过滤查不到（此前测试数据是 API 直接带 status 造的，掩盖了 bug）。同类修复请假（pending）/材料（submitted）/作业提交（submitted）三个表单；存量 2 条空 status 记录已 UPDATE 回 pending。写法：`set-field-value-rules` 是**全量替换** slot，已有规则（如 autoKlassFromUrl）必须先读出原文一并回写；静态默认值用 runjs 形态 `{"code":"return 'pending';","version":"v2"}`（项目内已验证的形态，未采用未知静态 shape） | Violet 报障「提交报名后待审页无数据」；表单级默认值比 DB 列默认值更直观可控，且不动建模 |
| D52 | **全站表格操作栏（TableActionsColumnModel）统一移到最后一列**：45 处 flow-surfaces 表格块的操作栏原本全在第一列（sort=1），用 `flowSurfaces:moveNode`（source=操作栏列 uid，target=当时行末列 uid，position=after）逐一移至末位。列序存在 `flowModelTreePath.sort`（depth=1 的父子边），SQL 可全量定位；纯服务端配置改动，前端刷新即生效，无构建部署 | Violet 要求「所有板块的操作栏放最后一列」；no-code 页面统一规范，AI Portal（main 源码）三页表格为自绘 React 表格无操作栏列，不在本次范围 |

## 2026-11-09（公开扫码报名：自制静态页 + 机器人 API key）

| 编号 | 决策 | 理由 |
|---|---|---|
| D53 | **未登录扫码报名 = nginx public 静态页 `/signup.html` + 窄权限机器人 API key**（Violet 拍板方案B）。①机制取证：本版本 auth 中间件只放行代码级 public action 白名单（`acl.allowManager.isPublic`），**anonymous 角色的资源授权不能让无 token 请求通过**（一律 EMPTY_TOKEN 401），public forms 是商业插件不装；②方案：静态页放 nginx public 目录（D44 同款路径），建 `r_signup_bot` 角色（仅 `nb_dx_registration` create 带字段白名单 + `nb_dx_class` view）、`signup_bot` 用户（user id 7），用 apiKeys 插件签 10 年期 JWT 当 `Authorization: Bearer`（API key 本质是带 roleName 的长期 JWT，走标准认证链），页面 fetch 提交 `status=pending` → 触发报名审批流；③越权实测 list/destroy 403；二维码改指公开页（class-qr.tsx 已改**未部署**）；真实 key 留 `backups/` 不入库，提交版为占位符 | Violet 问"扫码时学员未登录怎么办"；公开表单商业插件不值得买。API key 权限面收窄到"只能刷报名垃圾数据"，demo 可接受；机器人角色 snippet 额外带 `pm.api-keys.configuration`（生成 key 必需） |

## 2026-11-09（报名闭环：审核通过自动建档+开账号，方案 A）

| 编号 | 决策 | 理由 |
|---|---|---|
| D54 | **报名审核流 v2（revision key re5oyih3tpo，id 396799131385856）：manual 审批 → cond[approved] → query(按手机号查学员档案) → cond[无档案] → true 分支（create users(username=手机号, nickname=姓名, password=dx123456, roles=[r_student]) → create nb_dx_student(挂班次+user_id+status=active+enroll_status=yes) → update registration 回写 student_id/user_id）/ false 分支（update registration 只挂已有 student_id）**。同手机号二次报名不重复开号、不重建档案，只把新报名挂到已有档案 | Violet 确认方案 A。新学员登录口径：**用户名=报名手机号，密码统一 dx123456**（与测试账号一致，演示友好）；S2/S1b scope 自动生效（student.user_id 关联是 scope 生效的关键） |
| D54a | **workflow 节点链三条硬规则**（本次 4 轮实测踩坑）：①f-string 生成 `{{$...}}` 变量须写 `{{\$...`，多一个 `$` 变量解析失败→condition 恒 false；②**分支节点的直接下游才带 branchIndex（true=1 / false=0），分支内后续节点 branchIndex=NULL**，且**分支节点自身 downstreamId 必须为空**（填了会导致分支首节点被重复执行，如 create user 二次执行撞 username 唯一约束）；③**SQL 直改 flow_nodes 配置后必须 `workflows sync`（或重启应用）**，内存节点图不会自动刷新；④query/create 节点结果是 record 本体，引用 `{{$jobsMapByNodeKey.<key>.id}}`（无 .data 前缀）；⑤basic engine 没有 `empty` calculator，判空用 `equal` 与 null 比较 | nodes:create API 创建的节点不自动填 downstreamId（请假流是填的），缺了会断链；补 downstreamId 到分支节点又会重复执行——分支语义靠 upstreamId+branchIndex 表达 |
| D54b | **registration 集合补 note 字段（报名附言）**：公开页/移动页提交的 note 此前被静默丢弃（集合无此列，API 忽略不报错），dsl-reconciler push 新增，signup_bot 字段白名单本就含 note，落库即通 | Violet 公开报名页有「报名附言」输入框；附言进报名记录供教务审核参考 |
