# 党校智慧管理平台 Demo — 执行任务清单

> 对应计划:`PLAN.md`。每阶段完成打 ✅ 并填验证结果。
> 状态:⬜ 未开始 / 🔄 进行中 / ✅ 完成
>
> **优先级(2026-11-08 Violet 确认):管理端优先 — 阶段0→1→2→3→4 先行,阶段5(AI Portal)/6(移动端)/7 后置。**
> **续做入口:换电脑/新会话先读 `STATE.md`。**

## 阶段0:清理旧配置 + Docker PG + nb init 初始化 ✅

- [x] 清理旧 test 环境配置 — **跳过:`~/.nocobase/` 不存在,无需清理**(2026-11-08 核实)
- [x] PostgreSQL — **实际与计划不同:Violet 向导选 Docker 源 + 内置数据库**,应用跑容器 `nb-dx-demo-app`(:13000),库在 nb 托管容器 `nb-dx-demo-postgres`(nocobase/nocobase/nocobase);自建 `dx-demo-pg` 闲置待处理
- [x] `nb init --ui --locale zh-CN` 向导完成 — Docker 源 / 2.2.41 / 内置库 / OAuth 设备登录(非账密)
- [x] 确认 Skills 已安装(nb init 自动同步)
- [x] 重启 Claude Code 会话,验证 — **✅ 通过(2026-11-08)**:`nb env list` 显示 dx-demo(当前,docker,oauth,2.2.41);`nb env info` 确认 app/DB 均 running,OAuth 会话有效至 2026-11-09;Skills 正常加载(env-manage skill 调用成功)。修复:nvm default 原为 v20,已 alias 到 22

## 阶段1:dx.xlsx 清单转数据模型(YAML 批量建 collections)✅

- [x] 按计划数据模型清单写 YAML — **✅ 2026-11-08:42 个 collections**(教务 13 / 课表座位 3 / 教材 6 / 事务 7 / 学习 8 / 内容 5),YAML 在 `models/collections/`,较 PLAN 33 个补齐 7 库 3 个、选修计划 2 个、教学资料、纪律承诺、投票明细、问卷答卷、阅读 m2m(见 decisions D17)
- [x] dsl-reconciler 批量建表 + 关联 — **✅ push 一次成功**,自动建 FK 与 3 个 m2m through 表,共 45 张表;state.yaml 记录部署状态
- 验证:**✅ 通过** — API 确认 45 张 nb_dx_* 表;抽查 class(22 字段)/leave(13)/course_schedule(19) 关联齐全;备份 nocobase_20261108_stage1_models.sql

## 阶段2:配置 5 角色 ACL 与数据范围 ✅

- [x] 角色:校领导 / 组织员 / 教务人员 / 教师 / 学员 — **✅ 2026-11-09**:`r_leader`/`r_organizer`/`r_academic`/`r_teacher`/`r_student`(均 create-blank 只读基线)
- [x] 菜单权限 + collection 权限 + 数据范围(学员只见本班) — **✅ 2026-11-09**:collection 权限 5 角色全配齐(leader 全库 view+export / organizer 21 表 / academic 32 表 / teacher 18 表 / student 35 表);数据范围:3 个自定义 scope(S1 本人=student.user.id、S2 本班=klass.students.user.id、S2b 班次=students.user.id)+ 答卷表内置 own;**菜单 route 权限经 Violet 确认推迟到阶段3 随页面同步配置**(见 decisions D24)
- 验证:**✅ 边界通过** — 5 测试账号(leader/organizer/academic/teacher/student_test,密码 dx123456)登录实测:学员 leave/news 200、purchase/student 403、越权 destroy 报 No permissions;校领导全库 200、create 403。「只见本班」数据级验证待阶段3/7 有演示数据后补测(见 decisions D26)

## 阶段3:无代码 Portal 配置 PC 管理端页面 ⬜

- [x] 教学资源 7 库(师资/专题/活动/基地/拟开发/案例/校外宣讲) — **✅ 2026-11-09**:7 页挂「教学资源」菜单组(routeId 396710905708544),blueprint 走 apply-blueprint,蓝本存 `.artifacts/nocobase-ui-builder/stage3-teaching-resources/`;route 权限:leader/academic/student 3 角色 ×15 条(组+7页+tab),organizer/teacher 无该 7 表权限故不授;踩坑:users 关联字段显示列须用 `proposer.nickname` 而非 `.name`
- [x] 教材管理全套(信息/采购/领用/退库/荐书/库存报表) — **✅ 2026-11-09**:「教材管理」组(routeId 396714401660928) 6 页 apply-blueprint 全过,库存报表 chart 饼图读回确认;route 权限 leader/academic 各13条、student 5条;蓝本 stage3-textbook/;逻辑档案 docs/features/s3-textbook.md;备份 nocobase_20261109_stage3_textbook.sql
- [x] 教务管理(班次/通知/计划/选修计划/教学资料) — **✅ 2026-11-09**:「教务管理」组(routeId 396723346014208) 5 页 apply-blueprint 全部一次通过,蓝本 stage3-academic/;route 权限 leader/academic/student 各11条、organizer 9条、teacher 7条(选修计划/教学资料不授);逻辑档案 docs/features/s3-academic.md;备份 nocobase_20261109_stage3_academic.sql
- [x] 班务管理(请假/外出报备/退学/考勤统计/党性考核/优秀学员) — **✅ 2026-11-09**:「班务管理」组(routeId 396730107232256) 6 页 apply-blueprint 通过(考勤统计 chart 饼图读回确认 ChartBlockModel;党性考核 eval_record 用 dataScope 过滤 kind=party_self/party_review);route 权限 leader/student 各13条、organizer 11条、academic 9条、teacher 7条(按实测 collection ACL);蓝本 stage3-class-admin/;逻辑档案 docs/features/s3-class-admin.md;备份 nocobase_20261109_stage3_class_admin.sql
- [x] 学员管理(信息/相册/档案/学籍/培训记录)+ 门户/班级主页/学员主页 — **✅ 2026-11-09**:「学员管理」组(routeId 396734674829312) 5 页(信息/相册/学籍+饼图/档案/培训记录+柱状图)+「综合门户」组(routeId 396734888738816) 3 页(综合门户双图表+公告/班级主页/学员主页);均基于 nb_dx_student/class/announcement 单表多视角(D20);r_student 补 student view+S1b scope(decisions D30,Violet 确认);route 权限 leader/organizer/academic 各18条、teacher 16条(无 leave 权限不授综合门户页)、student 12条;蓝本 stage3-student-portal/;逻辑档案 docs/features/s3-student-portal.md;备份 nocobase_20261109_stage3_student_portal.sql
- [x] 教学评估 + 投票问卷 + 统计图表 — **✅ 2026-11-09**:「教学评估」组(routeId 396739781394432) 6 页(评估方案/专题评估/综合评估/投票管理/不记名问卷双tab/统计图表4chart含 avg 聚合);route 权限 leader/teacher 各14条、organizer 9条、student 10条、academic 不授(6表全无权限);投票页只放 vote 主表(organizer 无 vote_record 权限,D31);蓝本 stage3-eval-survey/(含 gen_eval_survey.py);逻辑档案 docs/features/s3-eval-survey.md;备份 nocobase_20261109_stage3_eval_survey.sql
- [x] **每模块完成存版本快照(可回退)** — **✅ 2026-11-09**:7 个模块备份齐(教学资源/教材/教务/班务/学员门户/评估问卷,pg_dump 至 backups/;version-control 插件未启用,以 dump 为回退点)
- 验证:CRUD + 图表可操作 — **✅ 配置层验证通过**:6 页 route 读回 13 条齐;4 chart(dataScope avg/count 聚合)落库 flowModels 确认;kind 过滤 topic/comprehensive 各 1 条命中;浏览器实测留待阶段7 演示走查

## 阶段4:workflow DIY 4 条审批流 + 待办页 ✅

- [x] 请假申请(累计请假 ≤ 总学时 1/7:聚合已批时长,超限标提醒) — **✅ 2026-11-09**:请假审批流(collection 触发 status=pending→manual 组织员审批→approved 分支聚合 sum(duration_days) 与 class.total_days/7 比较→超限 update over_ratio=true);实测 0.5+2.6=3.1 > 21/7=3 → over_ratio=true ✓
- [x] 退学申请(通过后改学员状态 + 账号禁用简化) — **✅ 2026-11-09**:退学审批流(manual 校领导审批→approved 分支 update 学员 status=dropout);实测学员状态联动 ✓(测试数据学员已改回 active)
- [x] 报名审核(public forms 扫码报名 → 审核;"自动开账号"简化为状态流转) — **✅ 2026-11-09**:报名审核流(manual 教务审核,结果由按钮预设值写回 registration.status,无自动开账号)
- [x] 缴费审核(凭证上传 + 审核状态) — **✅ 2026-11-09**:缴费审核流(manual 教务审核,同上写回 payment.status)
- [x] 门户"待办列表"页(查询状态=待审批记录) — **✅ 2026-11-09**:双入口——①「审批待办」flowPage(routeId 396747054514176,综合门户组,4 tab 分别过滤 4 表 status=pending,仅 view 动作);②「工作台待办」legacy page(routeId 396748572852224,挂 WorkflowTodo 块,审批操作入口);均授 leader/organizer/academic
- 验证:请假全流程走通,占比提醒生效 — **✅ 2026-11-09**:两笔请假 API 实测(通过写回+意见+聚合判断、超限 over_ratio=true、execution 全 RESOLVED);workflow 共 5 个版本(请假流因节点锁死做过 1 次 revision 改回组织员);备份 nocobase_20261109_stage4_workflow.sql;踩坑与 forms 结构见 docs/features/s4-workflow.md

## 阶段5:AI Portal 写课表/排座 React 页面 🔄(代码完成,待浏览器走查)

> 前置:2026-11-09 为启用 AI Portal 升级至 NocoBase 2.4.0-alpha.17(两次升级前均 pg_dump 备份,数据无损,决策 D36);Portal main 源码 `demo/main/`,部署于 http://127.0.0.1:13000/x/main/
>
> - [x] 周视图课表组件(格子 + 拖拽,响应式) — **✅ 2026-11-09**:`/schedule/week`,7×5 表格+冲突高亮+冲突提示卡;拖拽调课补齐(拖课程卡到其他格子=update+写 change_log「周课表拖拽调课」,与排课画布逻辑一致)
> - [x] 排课画布 + 调课(拖拽专题进格子、调课记录历史) — **✅ 2026-11-09**:`/schedule/board`,拖专题=create;拖课调课=update+nb_dx_change_log;拖拽落点错位已修(D49:旧构建钟面当 UTC 存,存量数据已重写+反算改显式东八区)
> - [x] 座位表组件(教室布局 + 拖拽排座 + 按学号/年龄自动排座) — **✅ 2026-11-09**:`/schedule/seats`,6×8 初始化、拖拽换座/清座;自动排座按钮不生效已修(filter 误用 klass→class_id + 只排未分配学员避免一人两座)
> - [x] 冲突检测(同教室/同教师同时段)、智能排课简化版 — **✅ 2026-11-09**:detectConflicts(周课表+画布均有高亮+提示卡)、smartSchedule 贪心版一键填空位
> - [ ] (后置)三维排课视图
> - 验证:拖拽排课无冲突,排座自动分配 — **🔄 代码层全满足**(typecheck/7 单测/build/deploy 过),**浏览器端待 Violet 走查**(须强刷)

## 阶段6:移动端配学员核心页 ✅

- [x] 扫码报名 / 请假申请 / 材料提交 / 学员录 / 作业 — **✅ 2026-11-09**:mobile Portal(/v/mobile,portalUid `__default_mobile__`)6 页全建:扫码报名 396774382895104 / 请假申请 396774621970432(表单+我的请假记录) / 材料提交 396774414352384 / 学员录 396774630359040(只读) / 我的作业 396774636650496(作业列表+提交表单) / 课程表 396774655524864(jsBlock 入口卡);r_student 补 12 条 route 授权 + nb_dx_material create;蓝本 .artifacts/nocobase-ui-builder/stage6-mobile/;逻辑档案 docs/features/s6-mobile.md;备份 nocobase_20261109_stage6_mobile.sql。踩坑:关联目标 >10 字段 fieldGroups 须挂目标表且全覆盖;蓝本不支持 js action clickSettings(改 jsBlock)
- [x] 课表页挂 Link(指向 AI Portal 课表,组件响应式) — **✅ 2026-11-09**:「课程表」页 jsBlock 渲染入口卡,点击 window.open 打开 /x/main/schedule/week(不复制数据,单一数据源)
- [x] 班次报名二维码(走查反馈补做,决策 D46) — **✅ 2026-11-09**:AI Portal `/x/main/qr` 生成页(qrcode npm 包本地生成,origin 自适应,可下载)+ admin 班次管理页「报名二维码」行操作(JSRecordActionModel uid s5w1ecobnf2)+ 移动报名页 fieldValue 规则 autoKlassFromUrl(URL ?class=<班次id> 自动选班次);typecheck/build/deploy 全过,/qr 与 /mobile 报名页均 200;备份 nocobase_20261109_qr_signup.sql;详见 docs/features/s6-mobile.md 补充节
- [x] 二维码交互改版:弹窗直出+建班即得码(决策 D50) — **⏳ 2026-11-09 代码完成待 Violet 部署自测**:①班次管理行操作改原生 popup(删除 s5w1ecobnf2 window.open 跳转版,新建 PopupCollectionActionModel d84vmbh85ma + 弹窗 JSBlock d6jsr0yfxhv,点击当前页弹 dialog 直接展示二维码 iframe);②/qr 页支持 ?class=<id> 直查班次(保留 ?token 兼容),二维码只依赖班次 id → 新建班次立即可弹码;③二维码内容路径修正 /mobile/... → /v/mobile/3cfhfajaa4x(缺 /v 前缀应用内 404,Violet 实测发现);main 侧 class-qr.tsx 改动需 nb portal deploy main 生效,弹窗行操作已即时生效;配置产物 .artifacts/qr-dialog/
- [x] 走查修复:报名待审无数据 + 操作栏列序(决策 D51/D52) — **✅ 2026-11-09 已自测**:①移动端 4 个 createForm(报名/请假/材料/作业)补 status 默认值规则(此前漏配,UI 提交落库空 status,待审 tab 按 pending 过滤查不到;API 测试数据带 status 掩盖了 bug),存量 2 条已修;②45 处表格块操作栏 moveNode 移至末列(admin+mobile 实测表头 ✓);纯服务端配置,前端刷新即生效;备份 nocobase_20261109_fix_status_actions.sql
- [x] AI Portal 走查 bug 修复(决策 D47/D48) — **✅ 2026-11-09**:①api.ts 双 unwrap bug(listResource 等三 helper 取 `.data` 永远 undefined → 页面下拉/课表拿空数组,API 200 有数据),统一修复覆盖 /qr + 排课三页;②5 角色授 main Portal 访问权(rolesMultiPortals,__default_portal__),修学员 403 死链;无头浏览器回归:/qr 4 班次+二维码生成 ✓、学员直达周课表+本班 scope 自动选中 ✓;main 已重新 deploy;验证方式升级:本机 Playwright 无头浏览器,走查先自测
- 验证:手机浏览器全流程可操作 — **🔄 API 层通过**:student_test 实测 leave create(进审批流)/material/submission/registration/assignment(本班 scope count=1)全 200;/v/mobile HTTP 200;**浏览器端手机走查待 Violet**。遗留:公开扫码报名(未登录)需 public forms,后置

## 阶段7:造演示数据 + 按角色演示脚本走查 🔄

- [x] 造演示数据(班次/学员/专题/课表/教材)
- 验证:41 张业务表全覆盖灌入(4 班次/21 学员/8 师资/12 专题/29 课节含冲突演示对/48 座位/教材链路/请假 6/评估 30/投票问卷/报名 6/缴费 4/作业);学员账号实测 scope 过滤全部生效(**D26 已关闭**);脚本 gen_demo_data.py 幂等保护;备份 nocobase_20261109_stage7_demo_data.sql;逻辑档案 docs/features/s7-demo-data.md
- [ ] 演示脚本走查:组织员建班 → 学员扫码报名 → 审核通过 → 学员请假(1/7 提醒)→ 排课拖拽 → 学员手机看课表 → 评估打分 → 统计出图(待 Violet 浏览器端走查,数据已就绪)
