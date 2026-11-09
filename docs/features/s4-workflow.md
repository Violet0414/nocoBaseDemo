# s4 — 工作流审批 4 条流 + 审批待办页（阶段4）

> 完成日期：2026-11-09 ｜ 蓝本/脚本：`.artifacts/nocobase-workflow/s4-workflows/`（含 `gen_workflows.py`、`s4-todo-page.json`）｜ 备份：`nocobase_20261109_stage4_workflow.sql`

## 一、为什么用 Manual 节点 DIY（决策 D2 落地）

正规"审批节点"（`@nocobase/plugin-workflow-approval`）是 $8000 商业插件，本环境未安装。免费版 workflow core + `workflow-manual` 插件已启用，用 **collection 触发器 + manual 节点 + condition/update 节点** 组装出等效审批流。

## 二、4 条流的统一架构

所有流都是同一个骨架：

```
collection 触发器（add 时 status=pending 才触发）
  → manual 审批节点（update 表单写回申请记录）
  → [通过分支的后续自动化]
```

| 流 | 触发表 | 审批人（测试账号） | 通过分支动作 |
|---|---|---|---|
| 请假审批流 | nb_dx_leave | r_organizer（测试组织员 id 3） | 聚合累计已批请假天数 → 与 class.total_days/7 比较 → 超限写 over_ratio=true |
| 退学审批流 | nb_dx_dropout | r_leader（测试校领导 id 2） | 学员学籍状态改为 dropout（"账号禁用"简化为状态流转） |
| 报名审核流 | nb_dx_registration | r_academic（测试教务 id 4） | 无（结果由 manual 表单写回） |
| 缴费审核流 | nb_dx_payment | r_academic（测试教务 id 4） | 无（同上） |

**关键规则：**
1. **审批结果的写法**：manual 节点的 form 类型用 `update`，`filter` 用 `{{$context.data.id}}` 定位触发记录；两个 action 按钮（通过/驳回）各自带 `values: {"status": "approved"/"rejected"}` 预设值——**审批人只点按钮，status 由按钮自动写入申请记录**，表单里只需填审批意见。两个 action 的 job status 都用 `1`（RESOLVED），保证执行引擎不会因"驳回"中断流程（驳回分支不需要停，只需记录状态）。
2. **1/7 聚合提醒（D21）**：聚合节点 sum(duration_days)，过滤 `student.id = 触发记录学员 AND status=approved`（manual 表单已先写回 status=approved，所以聚合天然含本次）；calculation 节点算 `total_days/7`；condition 比较，true 分支 update over_ratio=true。学员可感知"该学员累计请假已超总学习天数 1/7"。
3. **触发器 appends**：请假流预载 `["student","klass"]`（聚合过滤和 total_days 都要用）；退学流预载 `["student"]`。

## 三、审批入口（待办两页）

- **审批待办**（flowPage，routeId 396747054514176，综合门户组下）：4 个 tab（请假/退学/报名/缴费待审），每个 tab 是对应表的表格，`settings.dataScope.filter` 固定过滤 `status=pending`。**只给 view 动作**——审批动作不在记录页做。
- **工作台待办**（legacy page，routeId 396748572852224，综合门户组下）：传统 1.x 式页面挂 manual 插件的 **WorkflowTodo** 块（待办任务列表 + 弹窗表单提交）。**这是审批人实际执行审批操作的入口**。
- 两页均授权 r_leader / r_organizer / r_academic（teacher 对 4 表无 view 权限不授）。

### 为什么待办块要单独用 legacy page

flowPage 的蓝本（flow-surfaces apply-blueprint）只支持 table/chart/jsBlock/markdown 四种块，挂不了 WorkflowTodo 这种插件自定义组件；flowPage 的 schema 也不走 uiSchemas 树（内容在 flowModels 表）。所以审批操作入口用传统 page（desktopRoutes type=page + uiSchemas insert + WorkflowTodo 块 schema），2.x 引擎对 legacy page 有兼容渲染。**查看入口（审批待办）用 flowPage 保持全站风格统一，操作入口（工作台待办）用 legacy page 容纳插件块。**

## 四、验证结果（2026-11-09 实测）

1. **请假全流程**：admin 创建请假（0.5 天）→ 组织员审批通过 → 记录 status=approved + 意见写回 → 聚合 0.5 < 21/7=3，未超限（update 分支正确未执行）。
2. **超限提醒**：第二笔请假 2.6 天审批通过 → 累计 3.1 > 3 → **over_ratio=true** ✓。
3. **退学流程**：admin 审批通过 → dropout.status=approved + 学员 nb_dx_student.status=dropout ✓（实测后学员状态已改回 active，测试数据保留）。

## 五、踩坑（新）

1. **manual 节点 forms 结构（手写）**：`forms.<formKey> = {type:"update", title, collection, dataSource, filter, schema(Formily UI schema，字段节点用 x-component:"CollectionField" + x-collection-field), actions:[{key,title,status,values}]}`。fields 的 uiSchema 可从 fields 表 options->uiSchema 取。
2. **job status 常量**：PENDING=0, RESOLVED=1, REJECTED=-5。manual action 的 status 用 1 而不是 -5，理由见"关键规则 1"。
3. **manual task submit 400 陷阱**：execution 刚创建几秒内通过 API 提交审批会 400（Bad Request，服务端 validateTask 抛出），**重启应用后可提交**。正常业务节奏（提交与审批间隔数分钟）未复现，疑为 2.2.41 的 execution 队列/内存状态 bug。演示走查时若遇 400，重启 `nb-dx-demo-app` 即可。
4. **已执行的 workflow 节点锁死**：workflow 有 execution 后（versionStats.executed>0），节点 config 不可再 update（报 "Nodes in executed workflow could not be reconfigured"），必须 `workflows revision`（带 `--filter '{"key":"<key>"}'` 同 key 新版本）→ 改新版本节点 → 启用新版本。
5. **审批人测试**：manual task 提交校验 `assignees.includes(currentUser.id)`，X-Role 覆盖无效。测试时把 assignees 临时换成 admin(1)，测完 revision 改回真实审批人。

## 补充（2026-11-09 晚，D54）：报名审核流 v2 — 审核通过自动建档+开账号

**为什么**：原报名流审核只改 status，学员档案/登录账号全靠手工或脚本造，演示时「报名→审核→学员登录看课表」闭环断在账号环节。

**节点链**（报名审核流 v2，key `re5oyih3tpo`）：

```
manual 报名审核（教务，assignee academic）
 └ condition「审核是否通过」 (equal manual.review.status == approved)
    └ branch true(1): query「按手机号查已有学员档案」(nb_dx_student, phone = trigger.phone, multiple=false)
        └ condition「是否无学员档案」(equal query结果 == null)
            ├ branch true(1): create「开通学员账号」(users: username=手机号, nickname=姓名,
            │                 password=dx123456, roles=["r_student"])
            │                 → create「创建学员档案」(student: 挂 class_id + user_id, active/yes)
            │                 → update「回写报名关联」(registration.student_id/user_id)
            └ branch false(0): update「关联已有档案」(registration.student_id = query.id)
```

**账号口径**：用户名 = 报名手机号，初始密码统一 `dx123456`（演示口径，与测试账号一致）。

**实测**（公开报名 API → academic 审批 → 无头链路）：新手机号 true 分支——users 建 + r_student 绑 + student 挂班绑 user_id + registration 回写 ✓；同手机号二次报名 false 分支——只回写关联不重复开号 ✓；新账号 auth:signIn 登录成功，S1b（只见本人）/S2（只见本班）scope 自动生效 ✓。

**踩坑**（详见 decisions D54a）：f-string 转义多 `$` 导致变量失效；branchIndex 只标分支首节点（true=1/false=0）且分支节点 downstreamId 必须为空，否则重复执行；SQL 直改节点配置后必须 `workflows sync`；query/create 结果是 record 本体引用 `.id`；无 `empty` calculator 用 `equal`+null。
