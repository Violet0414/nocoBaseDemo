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
| D39 | **阶段5 AI 交互未落地，如实报告**：运行时有 AI 员工（Atlas）但 LLM 服务配置为 0（无任何模型 key），AI 交互无法真实运行。候选交互（排课冲突智能解读、课表自然语言查询）待 Violet 提供 LLM key 后补做。**【已关闭 2026-11-10】Violet 确认系统不需要 AI 交互，此决策终止，见 D63** | nocobase-ai-builder 规范要求：缺运行时能力须诊断并报告，不得静默跳过或假装完成 |

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
| D55 | **表格列/详情弹窗绑定学员一律走关联字段 `student.name`，禁用裸文本字段 `student_name`**：审批待办-请假待审列表列（TableColumnModel + DisplayTextFieldModel，fieldPath 改 `student.name` + `associationPathName: "student"`）与查看弹窗（删 student_name 详情项、student 项挪至首行）已改；学员提交的表单不含 student_name，该列永远空导致回显缺失。连带修复悬空引用：leave#6 吴建军 student_id 8→26、leave#7 许文博 11→29（学员表重灌后 id 变段，旧引用悬空） | Violet 走查反馈「列表学员姓名与另一个空学员姓名字段不一致」；裸字段是建模冗余（titleField），显示口径统一走关联 |

## 2026-11-09（综合门户「各班次学员数」图表修复）

| 编号 | 决策 | 理由 |
|---|---|---|
| D56 | **各班次学员数 chart 改 custom visual raw + 前端分组计数**：`charts:queryData` 对关联维度（`klass.name`）不聚合——返回每学员一行明细且响应里根本没有 measure 别名列（stuCount 缺失），builder 柱状图因此「只有 x 轴没有数量」、图例显示英文别名。改 `visual.mode=custom`，raw 里取 `ctx.data.objects` 按 `klass.name` 分组计数后 return ECharts option：`label.show=true`（柱顶数量）、系列名「学员数」（图例中文）、按数量降序、`minInterval:1` 整数刻度、klass.name 空显示「未分班」。配置产物 `.artifacts/nocobase-ui-builder/fix-portal-chart/` | 与 D43 同一渲染路径，但 D43 是「翻译 select value」，本次是「接口不聚合只能前端数」；直接改接口查询不可控，前端计数对 demo 数据量完全够用。核实：18 名学员 class_id 确为 NULL（真实数据非查询 bug），图表如实反映 |
| D56b | **「工作台待办」放弃 legacy page（WorkflowTodo 块），改 flowPage + jsBlock 自建审批台**：Violet 反馈空白 → 排查四层根因（uiSchemas 根行错位/inline properties 丢弃/treePath.type NULL）全修完后客户端仍不渲染，定性 **2.4 客户端 legacy 通道已实质废弃**（拿到完整 schema 但 WorkflowTodo 等插件自定义组件不在渲染注册表，不可修复）。新页 routeId 396809741205504（/admin/lv96gv4zgoq），jsBlock 内 `workflowManualTasks:listMine`（filter 只能 status:0，加 type 报 Invalid SQL）+ `flow_nodes:get` 读 actions（403 回退 FALLBACK 映射）+ Popconfirm 提交 submit。**落地路径**：apply-blueprint runjs 校验器拦白名单外自定义 action → 占位代码过校验建页 + SQL 直改 flowModels 的 runJs.code（校验器只拦蓝本通道）；navigation 必须写 `portalUid:"__default_admin__"`（layoutUid 直拒）；**父路由与 tab 子路由是两条独立授权记录**，父缺→404、tab 缺→listAccessible 树 children 空页面只有标题；tab 行须 hidden=false 且父行 enableTabs=true 前端才拉 grid 渲染 | legacy WorkflowTodo 是 1.x 交互范式，2.4 不再投入；jsBlock 版视觉可控（Tag/Popconfirm/danger 红）且权限模型与 4 条流天然对齐。旧路由 396748572852224 hideInMenu+hidden 双置 true 保留可回滚 |

## 2026-11-09（移动端课程表直出改版）

| 编号 | 决策 | 理由 |
|---|---|---|
| D57 | **移动端「课程表」页（/v/mobile/jxuptin8mn3）jsBlock 直出本班课表，废除入口卡跳转**：进入页面即 `ctx.makeResource` 拉班次（scope 限本班）→ 课表（filter class_id）→ 教师（id→姓名映射替代 appends），按天分组 Card+List 展示，周 Segmented 切换；**时间口径与 main 周课表一致**：day_of_week 权威列 + start_time 东八区反推节次，显示固定节次表，**不显示原始 end_time 钟面**。配置产物 `.artifacts/nocobase-ui-builder/mobile-schedule-inline/` | Violet 反馈"直接展示该学员的课程表，而不是点击按钮跳转"；手机上再跳 PC 周课表体验割裂。**连带发现存量脏数据**：`nb_dx_course_schedule` 部分 end_time 比 start_time 还早/跨日回跳（D49 只重写了 start_time，end_time 未修，main 端只显示节次 label 所以从未暴露）——展示层已规避，是否修数据待 Violet 拍板；另 lesson：flow-surfaces 校验器强制 JSBlock 读集合用 `ctx.makeResource`（禁 `ctx.api.request`），且 JSX onChange 函数自引用报 unknown-global，需局部持有者变量绕过 |

## 2026-11-10（待办标题学员名修复）

| 编号 | 决策 | 理由 |
|---|---|---|
| D58 | **请假/退学审批流 manual 节点 task 标题改走关联字段**：`{{$context.data.student_name}}` → `{{$context.data.student.name}}`（trigger appends 含 student，实测 `请假审批 - 张明远` ✓）。已执行工作流节点禁止直接 reconfigure（400），必须走 same-workflow revision：请假流新版本 id **396816229400576**、退学流 **396816562847744**（均 enabled+current，旧版自动停用）；jsBlock ENABLED_WF/WF_TITLE/FALLBACK_ACTIONS 同时补新旧 id 兼容（SQL 直改，flowModel `72hgyrjlwza`）；存量 pending 待办标题按 execution.context→leave→student.name SQL 回填 3 条；两条测试垃圾待办（leave13/14，芒果怪造）走 UI 驳回清场，池子回到 4 条真实演示数据 | Violet 反馈待办列表 4 条里 3 条学员名空——同 D55 根因（学员表单不填裸文本 student_name），标题模板在待办创建时渲染落库，改节点后需回填存量；缴费流 payer_name 录入时手填无此问题，不动 |
| D58a | **已执行工作流改节点配置的三步法**：①`workflows revision --filter-by-tk <id> --filter '{"key":"<key>"}'` 建同工作流新版本（新 id 未执行可改）→ ②`flow-nodes update` 改新版本节点 → ③`workflows update --enabled` 启用（自动置 current、旧版自动停用）。**下游硬编码 workflowId 的（如 jsBlock ENABLED_WF）必须同步补新 id**，否则新版本产生的待办被过滤不显示 | API 对已执行工作流节点直接报 "Nodes in executed workflow could not be reconfigured" |
| D59 | **移动端扫码报名页下线 + 菜单顺序调整**：①公开报名页（D53）接管报名入口后，删除移动端「扫码报名」孤页（destroy-page 命令；**参数须传 flow-surfaces get 的 target.uid 即 RootPageModel uid**，传路由 schemaUid 报 popup-child 400）；②移动端菜单顺序只由 `desktopRoutes.sort` 决定（flowModels 无 sort 列；move-node 不支持跨页同级排序——RootPageModel 的 parent 是自身，update-menu 无排序参数），直接 UPDATE sort 调序。新底栏：请假申请（首页）/ 学员录 / 我的作业 / 课程表 / 材料提交（末位）。旧链接回退移动端首页不报错 | Violet 2026-11-10 指示「有公共报名页了，扫码报名页可以去掉」+「材料提交放最后、首页设成请假申请」；官方 surface API 不覆盖菜单排序，DB 直改是唯一路径且实测刷新即生效 |

## 2026-11-10（超1/7提醒防呆 + 学员姓名列批量统一）

| 编号 | 决策 | 理由 |
|---|---|---|
| D60 | **超1/7提醒断链修复（方案B 建模层防呆）**：根因链 = `nb_dx_class.total_days`（手填、无默认、非必填）为空时，请假审批流 calculation 节点 math.js `{{$context.data.klass.total_days}}/7` 抛 TypeError → execution -2 中断 → 提醒永不触发（实证 leave 12：365 天请假 execution 卡死在计算节点）。修复：①total_days 与 leave.klass YAML 补 `required: true`（dsl push）；②存量空值补数（testClass/测试班级 → 21）；③全部请假表单 klass 必填 + 全部班次表单 total_days 必填（22 处 flowModel configure `settings.required`）。**关键坑（必读）**：required 有三层——集合元数据 `options.required`、`uiSchema.required` 都**不驱动表单校验**，真正生效的是表单项模型的 `settings.required`（flowModel 层，flow-surfaces configure 落库）；YAML 模型层 required 只对 dsl push 新建集合生效，对已存在字段 reconciler 会跳过（只 diff select enum） | Violet 问「total_days 不填是不是就不触发」——实测比不触发更糟：整条审批流报错中断；建模层拦截最干净，工作流层容错（formula.js IF）不引入 |
| D61 | **全站「学员姓名」列批量统一走关联字段（D55 遗留销账）**：请假管理页（/admin/aj0sy2ux0wc）列表姓名列绑裸 `student_name` 显示为空（Violet 走查反馈），SQL 直改 8 个 TableColumnModel（请假管理 n67deltao4s + 外出报备 + 退学×2 + 考勤 + 评估×3）fieldPath → `student.name` + `associationPathName: "student"`，改前备份 `backups/flowmodels_student_name_cols_backup_20261110.txt`。无关联脏数据（leave 9/13）显示空属正常 | D55 只修了审批待办 flowPage，班务各页同款列当时待确认；Violet 实际踩到请假管理页，确认批量统一 |
| D62 | **评估新增表单 kind 静默丢字段修复**：党性考核/专题评估/综合评估三页的「新增」弹窗此前**共用同一表单模板**（tfqylic8j8y「新增党性考核记录」，usageCount=3），表单 kind/班级/课程全非必填且无默认值——用户只填学员提交时记录落库 kind 为空，被各页列表 kind 过滤（topic/comprehensive/party_*）吞掉，造成「提交了但数据没新增」。修复：`convert-template-to-copy` 三处各自拆副本 + 每副本 `set-field-value-rules` kind 静态默认值（runjs 形态）+ 学员选择器 SQL 直改 `stepParams.editItemSettings.required={required:true}`（configure 不支持 settings，D60 同款）+ 服务器 6 条 kind 空垃圾记录随重灌清除 | Violet 线上测试专题评估新增无数据显示；模板共享导致默认值无法按页差异化是根因，拆副本是官方 detach 路径 |
| D63 | **AI 交互取消 + D58 残留待办遗留销账**：①Violet 2026-11-10 确认**系统不需要 AI 交互**，D39 关闭——不配置 LLM 服务、不做排课冲突智能解读等候选交互，后续无 LLM key 依赖；②STATE.md D62 段记录的遗留「待办池 1 条 D58 验证残留『请假审批 - 』（leave 13）待 UI 驳回」经取证（本地库 + fresh dump 双查）**已不存在**——leave 13 行与空标题 pending 待办均无（D58 已走 UI 驳回清场，decisions D58 有记录），pending 待办池仅剩 4 条真实演示数据（吴建军/张明远×2/测试人员，标题正常） | Violet 指示去除待办遗留、去除 AI 交互记录；取证确认无需任何清理操作，避免误删演示数据 |
| D64 | **菜单/系统名称对齐 dx.xlsx 需求术语（纯文案 12 处）**：对照 docs/dx-requirements.md（dx.xlsx 转录）核对后 SQL 直改——①systemSettings.title `NocoBase`→`党校智慧管理平台`（登录页/浏览器标签）；②「通知公告」→「教学通知」；③教学资源 6 库补"库"字（教学专题库/教学活动库/教学基地库/教学案例库/校外宣讲库/拟开发专题库）；④专题评估→专题评估状况、综合评估→综合评估状况、投票管理→投票；⑤移动端「课程表」→「我的课表」。各页 hidden tabs 子行同步改，前端刷新生效。备份 `backups/nocobase_20261110_pre_rename_menus.sql`。已知缺口（未做）：admin 端作业管理/材料回复页、调课记录页、报到/纪律承诺/学业证书/活动风采/申报信息等需求页；教材"统计报表"需求含领用报表+库存流水，现只有库存报表 | Violet 要求对比需求清单与现系统名称差异并"按建议改"；改的是展示层标题，不动 routeId/flowModel，无功能风险；线上 10.10.40.44 待下次 fresh dump 重灌时一并带走 |
| D65 | **品牌去 NocoBase 化 + main 门户全站中文化**：D64 对比时发现的品牌残留按 Violet 三项指示清空——①logo：Pillow 生成文字版 wordmark（亮/暗透明底）+「党」字红底 favicon（脚本 `.artifacts/branding/gen_logo.py`，本机无 playwright 环境改用 `F:/Python/python.exe` + 微软雅黑 Bold 实现）；main 门户 brand.tsx 直接文字化不再依赖图片；admin 登录页 logo=容器 nginx public /logo.png，docker cp 替换（旧图留底）；②main 源码 15 文件中文化：登录页右侧营销区（原英文 AI 话术）改「教学教务/学员服务」中文介绍、登录/注册/忘记密码表单、404/错误边界/ACL 无权限、浏览器标题 appName；③build+deploy 验证：线上 bundle 新文案在旧英文 0 残留。**坑：acl-gate 的 "Unable to load permissions" 是 SDK 报错比对哨兵不可翻译**；admin favicon 未动（dist 内，低价值） | Violet 指示"其余地方的 NocoBase 图片也替换成系统名称"并确认文字版 logo + 全中文化；服务器同步需 dump + logo docker cp + portal 重部署三件套 |
| D66 | **登录页淡蓝背景 + 附件直链底层 logo 替换**：①`/x/main/login` 右侧深色区改淡蓝（bg-blue-50 系，文字/卡片/网格纹理全套适配浅底）；②Violet 发现 `/files/main/main/attachments/1.png` 仍是旧 NocoBase logo——该 URL 是 attachments 记录 id=1 直链，**重定向到底层存储 `/storage/uploads/logo-0ilulu.png`**（D65 只换 nginx public 不够），uploads 两份文件（logo-0ilulu + 孤儿副本 logo-ouub0e）docker cp 替换为新 wordmark，md5 核对 + 带 token 200 验证 | Violet 走查发现的两个漏网点；教训：logo 有三条服务链路——nginx public /logo.png（admin 登录页）、/x/main/logo.png（main 门户 public）、/storage/uploads/*.png（附件直链重定向终点），换 logo 三处都要换 |
| D67 | **附件直链白字版 + 周课表隐藏 sidebar footer**：①D66 的「没显示」根因 = 改动只在本地容器，Violet 走查的服务器 10.10.40.44 未同步（WSL 侧 ssh/scp 密钥可用，Windows 侧无）——uploads 两份 logo 本地+服务器换**透明底白字版**（Violet 指定），服务器 nginx public /logo.png 换黑字版防白卡背景隐形；`/storage/uploads/*` 走 auth_request，未登录 401 本来就显示不出；②SidebarFooter 加 useLocation 判断 /schedule/week 返回 null，顺带去 NocoBase 化（删 nocobase.com 链接改中文介绍） | logo 三链路版本分治：public/黑字（白底登录页）、dist/黑字（门户）、uploads/透明白字（Violet 指定）；服务器同步必须 SSH 走 WSL 侧 |
| D68 | **隐藏 AI 悬浮对话按钮**：「打开 AI 对话」悬浮球（nocobase-ai-chat.svg）由 nocobase-ai 扩展 global-ai-chat.tsx 渲染，条件 = AI 配置就绪且 aiEmployees 非空——库里 8 个 builtIn 员工恒 ready，按钮常显；D39 已取消 AI 交互故为孤入口。修复 = 移除 global-ai-chat.tsx 中 AIChatFloatingTrigger 渲染（生产唯一挂载点），AIChatWindow/aiEmployees 数据保留不动；demo/floating.tsx 仅 DEV 演示路由加载，bundle 死代码无害 | Violet 指示隐藏；只摘入口不拆扩展，未来若重启 AI 交互（D39 翻案）恢复一行渲染即可 |
| D69 | **停用 plugin-ai 插件（admin AI 悬浮球隐藏）**：admin/移动端的官方 AI 悬浮按钮由 plugin-ai 客户端硬编码渲染（条件 aiEmployees 非空 + /admin 或 portal 前缀，无配置开关、无 flowModel 实例可关），8 个 builtIn AI 员工使其恒显示。`nb pm disable ai` + `nb app restart` 停用；数据保留（installed=true），恢复 `nb pm enable ai`。验证四端 200 + 业务 API 正常 + aiEmployees API 403；main 门户 nocobase-ai 扩展拉取失败走 error 状态不渲染（白屏风险排除） | D39 取消 AI 交互后的彻底收尾（D68 摘了 main 自建扩展入口，D69 关掉官方插件入口）；enabled 状态随 fresh dump 同步服务器，无需额外操作 |
## 2026-11-10（PLAN 缺失功能补齐）

| 编号 | 决策 | 理由 |
|---|---|---|
| D65 | **补齐 PLAN.md 声明缺失功能（Violet 确认清单后执行）**：A 教材库存联动 workflow ×3（采购/领用/退库，**提交即触发**拍板）+ 领用报表/库存流水 2 页；B 管理端 6 页（作业管理含转批/材料回复/申报信息/纪律承诺/调课记录/通知阅读统计）；C 4 条审批流加站内提醒通知节点（in-app 通道）；D 学员社区（admin+移动端）+ 活跃度 chart。**拍板不做**：三维排课（PLAN「有余力再做」）、教学资源导入导出（A 类做法描述非独立功能点，builder 支持性未验证）。全程「只增不改」：唯一动现有流的是 C1 走 revision 三步法，jsBlock ENABLED_WF 补新 id。逻辑沉淀 docs/features/s8-gapfill.md | Violet 三点确认（排课视图不做/导入导出不做/提交即触发）+「不要影响现有功能、不要出现英文」约束 |
| D65a | **workflow notification 节点配置形态**（源码取证）：config={channelName, ignoreFail, content, receivers}——receivers 进 message.receivers，in-app channel 解析为 id 字符串数组或 UserRepo find 对象（缴费流用 student 查询对象绕无 user 直连）；in-app 通道先经 REST 建 notificationChannels（name=in-app）；**id 消息 title 为空正常，content 为正文** | PLAN B 类「通知节点站内提醒」落地；4 流全链实测「审批通过→消息送达学员」✓ |
| D65b | **学员社区零建模方案**：复用 nb_dx_comment（kind=post 帖/reply 跟帖、parent_id 自关联、hot 精华）——建模时字段即为此设计，不新增集合。移动端发帖表单 kind 默认值走 setFieldValueRules（**规则键是 targetPath 不是 field**）；r_student 补 comment create 权限走 SQL 直插 dataSourcesRolesResourcesActions（ACL 配置在 dataSource 维度表，rolesResources 表是空的） | PLAN A 类「学员社区|评论区块」「社区活跃度」；comment 表 9 字段无 fieldGroups 负担 |
| D65c | **蓝本校验器新踩坑（补缺批）**：①bar 图蓝本 mappings 必须 x/y（D56 同款再现）；②createdAt 不被蓝本 fields 接受；③关联路径 fields 连带要求目标表 popups/fieldGroups（change_log→course_schedule、announcement→class 均被点名）；④through 集合无关联字段不可作块集合；⑤mobile Portal 多块不许独占行（s6 踩坑③再现） | 6 页蓝本 4 轮报错修完；校验器报错信息会给 expectedShape 按提示改即可 |
| D70 | **请假管理「超1/7提醒」列显示是/否**：over_ratio 列单元格此前显示原始 true/false——列渲染走 TableColumnModel（kgmbd2wuaer）下的 field 子模型（uid 9f4vkck3k1e），原为 DisplayTextFieldModel。改为 **DisplayEnumFieldModel + props.options 显式映射**（不动集合定义，boolean 字段还要参与工作流判断）。三个坑：①列单元格渲染确实走 field 子模型（对照实验：临时换 DisplayDateTimeFieldModel 单元格即变，证实）；②`docker exec psql -c` 传中文被编码成乱码导致映射匹配失败渲染 fallback 回原值——中文须走 UTF-8 安全通道，改后验证字节（是=e698af/否=e590a6）；③**boolean 字段值经 API 序列化到前端为字符串 "true"**，纯布尔 value 映射匹配不上，options 须混配字符串与布尔两种 value（同一值只会命中一项，不重复渲染）。NULL 显示空白正常（现库 1 条 true、1 条 NULL）。备份 nocobase_20261110_pre_overratio_label.sql；验证 .artifacts/e2e-check/verify_overratio_label.py（脚本登录时序坑：/sign-in 会客户端重定向 /signin?redirect=，需固定等待后找 input） | Violet 走查要求"是/否"展示；e2e HAS_SHI 实测 ✓ + Violet 浏览器强刷确认 ✓ |

## 2026-11-10（admin 排课入口归位）

| 编号 | 决策 | 理由 |
|---|---|---|
| D71 | **排课三页 admin 菜单归位（方案A：iframe 入口）**：教务管理组新增「排课管理」（iframe `/x/main/schedule/board`）与「课表查询」（`/schedule/week`），班务管理组新增「排座管理」（`/schedule/seats`）——flowPage+jsBlock iframe 嵌 AI Portal 页（D50 弹窗 iframe 模式的整页版），同源免登录。菜单顺序按 dx-requirements 需求层级插入（排课管理/课表查询在教学计划后、排座管理在退学管理后，SQL 直改 sort）。授权 leader/organizer/academic/teacher 各 5 条路由；iframe 页无集合操作不涉 data-level 权限。**蓝本校验器直接放行 iframe jsBlock**（无 API 调用），D56 占位法未用上。/x/main 保留直连兜底，main 源码零改动。备份 nocobase_20261110_pre_schedule_entry.sql；蓝本 .artifacts/nocobase-ui-builder/schedule-entry/；验证 .artifacts/e2e-check/verify_schedule_entry.py 全绿（菜单展开+iframe 挂载+内页渲染，pageerror=0） | Violet 提出"两个地址体验割裂"，对照 PLAN.md/dx-requirements 确认需求里排课属教务管理/班务管理内部菜单后拍板方案A；B（link 型路由，desktopRoutes 未见先例）、C（重写进 no-code，丢拖拽交互）不选；iframe 双层侧栏为已知代价，去侧栏 embed 模式后置可选 |
| D72 | **组织员座位权限补授**：Violet 报「r_organizer 调 /api/nb_dx_seat:create 报 No permissions」——r_organizer 对 nb_dx_seat **连资源行都没有**（r_academic 有全套 CRUD+export）。SQL 直插 `dataSourcesRolesResources` 行（usingActionsConfig=true）+ **create/view** 两条 action 行（fields 白名单照抄 r_academic 12 字段，含 class_id/schedule_id/student_id 外键与 klass/schedule/student 关联字段；scopeId 用 All records=396628275953665，与 academic 一致；organizer 本就全量管理班次，不做班级过滤）。验证：organizer_test 实测 view ✓ create ✓（空体垃圾行 id=147 已 SQL 清理）。坑：`docker exec psql` 接 heredoc **必须加 -i**，否则 stdin 不进容器、整段静默不执行且无报错 | 座位表属排课三页（Portal /x/main/seats），organizer 建班后需自排座位；r_leader/teacher 仅 view/export 维持不动 |
| D73 | **组织员教学专题库+调课流水权限补授**：Violet 报「/api/nb_dx_topic:list 同样 No permissions」——r_organizer 对 nb_dx_topic 无授权（`lit` 是 list 笔误）。连带排查：D71 排课 iframe 三页前端共引用 7 个集合（course_schedule/class/student/seat/teaching_plan/topic/change_log），organizer 缺 **topic**（本次报障）+ **change_log**（拖拽调课要写流水，下次必撞）两个。补授：topic view+export（对齐 r_leader）、change_log view+create（organizer 可拖拽调课写流水，不给 destroy），fields 白名单照抄 r_academic，scopeId=All records。验证：organizer_test 实测两接口 200 ✓。**坑：INSERT 多行 VALUES 内 (SELECT max(id)+1) 子查询在语句内重复取值同 id 撞主键——多行插入必须拆独立语句** | 排课 iframe 入口的 ACL 连带补漏（D71 漏判"纯 iframe 不涉集合权限"——iframe 内 Portal 页调业务 API 需要集合权限） |
| D74 | **组织员排课/座位 update 权限补授**：Violet 报「/api/nb_dx_course_schedule:update 与 /api/nb_dx_seat:update（filterByTk 调行）No permissions」——organizer 对两表均缺 update（D72/D73 只补了 create/view）。SQL 直插 2 条 update action 行（fields 白名单照抄 r_academic：course_schedule 19 字段/seat 12 字段，scopeId=All records），重启生效；organizer_test 实测两接口 200 ✓（验证用写回原值方式，误置 seat 62 row/col null 已按 label R2-C4 复原）。**至此 organizer 排课三页写路径齐备（seat create/update + course_schedule update + change_log create）。**验证接口时用"写回原值"而非空体，避免造垃圾行或污染字段 | 排课 board 拖拽改 course_schedule 行 + 座位表调整改 seat 行是 organizer 本职 |
| D75 | **main Portal embed 模式（去 iframe 双层侧栏）**：layout.tsx（40 行壳组件）加 ~10 行——URL 带 `?embed=1` 时只渲染页面本体（h-svh 全幅，不挂 Sidebar/Header/内边距），其余路径渲染逻辑零改动。3 个 admin 入口页 jsBlock 的 iframe src 加 `?embed=1`（SQL replace options::text，**搜索串含 JSON 转义引号 \\" 必须走 SQL 文件 + dollar-quote + `docker exec -i psql <` 通路**——经 `docker exec psql -c` 传会被多层 shell 转义吃掉反斜杠静默不生效，实测踩中）。build+deploy main（bundle index-BbSxP8n6.js，线上 hash 一致）。验证全绿：3 入口页内层无侧栏纯直出 + 直连 /x/main 非 embed 侧栏仍在 + pageerror=0。jsBlock 模型 uid：s96hi0xk166(board)/ykhawbr91vm(week)/6nia4y84u97(seats) | Violet 在三方案（embed 模式/CSS 注入 hack/单菜单 tab）中拍板方案一——菜单层级对齐需求文档且实现正规可长期维护；CSS 注入依赖 DOM 结构属 hack 不取 |
| D76 | **全站筛选表单「学员姓名」字段批量改走 student.name 关联**：Violet 报「审批待办-请假待审（/admin/fkrtrtchlkj）/api/nb_dx_leave:list 查询条件不生效」。取证：①tab 自带固定过滤 `status=pending` **正常生效**（实际请求 filter 已带 `{"$and":[{"$and":[{"status":{"$eq":"pending"}}]}]}`，页面"暂无数据"是因为库内 3 条 leave 全为 approved 无 pending）；②API 层 filter 各形态（status eq / student.name includes / nested / type eq）均生效；③真正不生效的是**筛选表单交互**——按「学员姓名 包含 张」提交后请求带的是 `student_name`（裸文本字段，D55 已证实学员表单不填、库内恒空）→ 永远查不到。根因 = FilterActionModel 的 `stepParams.filterSettings.defaultFilter.defaultFilter.items`（筛选表单字段声明，权威层）绑了裸字段；D55 只修了列表列没修筛选行。修复：SQL replace `'"path":"student_name"'→'"path":"student.name"'` 批量修 **12 处 FilterActionModel**（请假待审 dfni5zl0h42 + 请假管理 ggkhfx9lomc + leave 第三处 momazfcihlh + 退学×2 pmfu2dzz1ze/cgf0fm22mvb + 外出 gjwz7g2b0aa + 考勤 1g1x4yfe5gi + 评估×3 3v6pu2gjgaj/1ozwtotueze/bq9pisg8o3d + 申报 tnzxspvyizf + 材料回复 iafdrtlkuaq），props.defaultFilterValue/filterValue/stepParams 三层 path 全部统一（与 D61 列统一同口径）。7 集合均有 student belongsTo 关联，API `student.name includes` 实测 count 正确 | D55/D58/D60/D61 同源问题的第五处遗漏面（这次是筛选层）；报障只点名请假待审，但 12 处同根因一次修净（D52/D61 批量先例）；备份 `backups/flowmodels_filter_student_name_backup_20261110.txt`（12 行改前快照）+ 全库 `nocobase_20261110_pre_filter_student_name_fix.sql`；验证脚本 `.artifacts/e2e-check/verify_filter_student_name.py`（Violet 浏览器复验）；纯 DB 配置改动，前端刷新生效，随 fresh dump 同步服务器。**补充（同日二轮）**：Violet 复验报「请假类型/请假事由筛选仍不生效」——取证结论：提交接口（移动端+admin 请假表单，SelectFieldModel 绑集合 enum）**存的是英文 code**（personal/sick/duty/other，用户验证时新提交的 leave 22 type='duty' 亦证实），type 筛选"不生效"的真因是**库内脏数据**：leave 18（D65 站内提醒链路测试用 API 手工造数）type 存了中文'事假'，UI 下拉选'事假'发 personal 永远查不到它——已修正 type='personal'；reason 筛选 API 实测正常（includes 链路 count=2/123 count=1），事由查不到大概率是输入片段与库内三条记录事由不匹配或残留姓名旧条件。**规则：API 直接造数必须传 enum value（code），传中文 label 会污染 select 字段且列表列恰好映射回中文显示、肉眼难察觉** |

## 2026-11-10（审批待办页放开已审数据）

| 编号 | 决策 | 理由 |
|---|---|---|
| D79 | **AI 悬浮球抑制：D69 的 `nb pm disable ai` 方案被实测推翻，新切断点 = aiEmployees 数据**：D76-D78 发布重灌后 Violet 报 admin AI 悬浮球复现。取证链：①本地 `applicationPlugins.ai` enabled=t（D71 段早发现的反常，本会话实验确证 **`nb pm disable ai` 写入 f 后 app 一旦 restart 启动逻辑必翻回 t——D69 的"停用成功"是热状态假象，该方案在 2.4.0-alpha.17 不可持久**）；②改清 `aiEmployees` 8 条内置员工（D68 实证的渲染条件 employees 非空）——对照实验：DELETE 不重启 → 悬浮球消失（aria-label 计数 0），restart → seed 重建 8 条 → 按钮回来。**最终状态：本地/服务器 aiEmployees 已清空、按钮消失（Violet 浏览器确认）；但应用重启会 seed 重建员工数据使按钮复现，属已知限制**——彻底持久方案（阻断启动 seed，需逆向 employeeManager 初始化条件或 PG trigger 拦截）未做完，Violet 确认现状可接受后中止。aiMessages/aiConversations 全空，清数据零功能损失；快照 `backups/aiemployees_snapshot_20261110.txt`（本地 8 行）+ `aiemployees_server_snapshot_20261110.txt`（服务器 8 行），恢复 = 重灌 dump 或手工回插 | D69 不可持久的根因不必深挖（启动 seed 机制在 server plugin-ai dist 内），务实选择"每次清数据"或后续做持久阻断；期间顺带确证 aiEmployees:list 对非授权角色（organizer_test）恒 403、对启动中应用瞬时返回 200 空（误导过一次判断，验证须在应用完全启动后） |
| D78 | **审批待办 4 tab 去掉 status=pending 固定过滤（Violet 拍板方案A）**：原设计（D34）4 个 tab（请假待审 02w8ejj8dqt/退学待审 x9qz8dhvcai/报名待审 gx32doksejc/缴费待审 56avsjgjhb4）表格块 dataScope 固定 `status=pending`，已审数据查不到；且筛选表单「审批状态」行选任何值都与固定 pending 叠加成恒空（pending AND approved）——这正是 Violet 报「查询条件不生效」的组成部分。改为清空 dataScope.filter.items（保留 `{logic,items:[]}` 结构），列表变全量，靠筛选表单「审批状态」行过滤（待审批/已批准/已驳回）。tab 文案不动；已审数据的另一查询路径「班务管理→请假管理」等业务页不受影响。SQL：`jsonb_set(...,'{stepParams,tableSettings,dataScope,filter,items}','[]')` | Violet 问"该页面能查到已审核的数据吗"→ 三方案（去固定过滤/加已审 tab/不改）拍板方案A；工作台待办（jsBlock listMine）仍是唯一审批操作入口，本页纯查看，放开无权限风险；备份 `backups/flowmodels_approval_tabs_datascope_backup_20261110.txt`；纯 DB 配置改动，前端刷新生效，随 fresh dump 同步服务器。**补充（同日三轮）**：Violet 要求请假待审列表加「审批状态」列——排查发现退学/报名/缴费待审 3 个 tab 已有 status 列（TableColumnModel+DisplayEnumFieldModel），仅请假待审漏配；SQL 直插列模型 c8fsk3wq2ne + field 子模型 d9mvk5xz7pt（照抄 dropout 待审列 wnbnqxybhvq/ig6v52edbtd 结构）+ treePath 9 行（列 self depth0 type=columns + 全祖先链），插「超1/7提醒」后（sort 9），操作列 p5wuk5r9ssv 顺延 sort 10；DisplayEnumFieldModel 按 status enum 自动映射中文（待审批/已批准/已驳回/已撤回）。备份 `backups/flowmodels_leave_status_col_backup_20261110.txt`。**加列套路（可复用）：flowModels 2 行（列+field 子模型）+ treePath = 子模型数×祖先链长度 + 各自 self 行** |
| D77 | **培训记录页「各班次学员数」图表图例改中文「学员数」**：Violet 报 /admin/n6229xx31n5 图例显示英文 "stuCount"。**D56 只修了综合门户一处（arheyvzxnw1），培训记录页的同款 builder 图（73fclpvn4nr）漏网**——两页各自持有独立 ChartBlockModel 实例，feature 文档 D56 节写「综合门户与培训记录页」口径时误以为两处都已改。修复 = 同款方案（flow-surfaces configure，changes.visual={mode:"custom", raw} 前端按 klass.name 分组计数 + 系列名「学员数」+ 柱顶 label），蓝本产物 `.artifacts/nocobase-ui-builder/fix-train-chart/`，验证 `.artifacts/e2e-check/verify_train_chart.py`（截图判读：图例学员数/柱顶 18·4·1/pageerror=0）。**定位坑：flowPage 的块模型在 flowModelTreePath 页面子树里查不全（页面根模型下无树行）——页面 URL slug = desktopRoutes.schemaUid，块归属须走 `nb api flow-surfaces get --uid <slug>` 的 tree（RootPageModel→tabs→grid→items）确认；desktopRoutes 里 hidden 的同名行（schemaUid=tjtk5icyiwh）是页面 tab 的路由表示，不是废弃页** | 同款问题第二处报障，说明逐实例配置模式下修一处≠修一类；全局搜 `stuCount` 现仅剩学籍管理 nzan9dg1i7c 为 builder 模式，但该图 2026-11-09 D43 已改 custom 中文映射无同款问题，暂无第三处 |
