# s3-eval-survey — 教学评估 + 投票问卷 + 统计图表（阶段3-6）

> 2026-11-09 完成。菜单组「教学评估」routeId=`396739781394432`，6 页 + 6 tab 共 13 条 route。
> 蓝本：`.artifacts/nocobase-ui-builder/stage3-eval-survey/`（含生成脚本 gen_eval_survey.py，6 页由脚本一次生成，蓝本改字段后重跑脚本即可再生成）。

## 业务逻辑

### 评估体系（eval_scheme + eval_record）

- **方案先行**：`nb_dx_eval_scheme` 定义评估方案（方案类型 topic/comprehensive/party + 评估方式 score/grade/mixed + 评估项目 items_text 每行一项 + 分值区间）。party 类型方案在班务模块「党性考核」页消费（见 s3-class-admin.md），本模块管理端只负责方案本身的维护。
- **记录四类**：`nb_dx_eval_record.kind` = topic（专题评估）/ comprehensive（综合评估）/ party_self（党性自评）/ party_review（党性复评）。本模块拆两页分别过滤 topic、comprehensive；party 两类留在班务模块页。同一张表多视角过滤，不建重复表。
- **逐项得分简化存储**：评估项目明细存 `items_json` 文本（如"党性意识:18;学习态度:19"），不建逐项明细表。理由：demo 粒度下逐项表的录入成本远高于统计价值；后期若需逐项统计再升级为 JSON 字段或子表。
- **专题评估关联链**：record → schedule（课次）+ topic（专题）+ scheme，用于回答"哪个专题讲得好"；综合评估只挂 klass + scheme。
- **学员打分入口**：r_student 对 eval_record 有 create+view（S1 本人 scope，只看自己的记录），真正的填报动作走移动端（阶段6），本阶段管理页只覆盖教务/教师视角的记录维护与查看。

### 投票（vote + vote_record）

- `nb_dx_vote`（标题/问题/选项 options_text 每行一个/方式 single·multi·score/范围 class·all/状态/截止时间）+ `nb_dx_vote_record`（所选选项、多选分号分隔、打分记 score_value、投票时间）。
- 班务模块「优秀学员」页（s3-class-admin.md）已覆盖学员投票场景；本模块「投票管理」页是发起方/管理视角（查看进行中的投票与状态）。
- **投票管理页刻意只放 vote 主表，不放 vote_record 明细块**：organizer 对 vote_record 无 collection 权限，若同页挂明细 tab 会授不了 route（授了也整块报错）。vote_record 的查看与统计收敛到「统计图表」页（仅 leader/teacher）。

### 不记名问卷（survey + survey_answer）

- `nb_dx_survey`（名称/班次/方式/每设备每日限填 limit_per_day/状态/截止时间）+ `nb_dx_survey_answer`（答卷摘要/明细 answers_json/设备标识 device_tag/提交时间）。
- **不记名通过"无学员字段 + 设备标识"实现**：答卷表不带 student 关联，限次靠 device_tag（设备指纹/随机码）。ACL 层面学员对答卷表用内置 own scope（阶段2 D25），保证只能改自己的答卷但看不到他人答卷与学员身份的关联。
- 页面双 tab：问卷列表（survey）+ 答卷明细（survey_answer）。organizer 对 survey_answer 无权限，故本页不授 organizer（survey 单表他可看，但拆页反而稀释，demo 取整页不授）。

### 统计图表页（4 chart）

| 图表 | 集合 | 聚合 | 维度 | 形态 |
|---|---|---|---|---|
| 评估类型平均分 | eval_record | avg(score) | kind | bar |
| 评估记录分布 | eval_record | count | kind | pie |
| 投票选项分布 | vote_record | count(option_selected) | option_selected | bar |
| 各问卷答卷数 | survey_answer | count | survey.name | bar |

- 只授 leader/teacher：统计是管理视角；organizer/student 缺 survey_answer 或 vote_record 的 view，且不需要看全量统计。
- **avg 聚合可用**：`{"field":"score","aggregation":"avg","alias":"avgScore"}` 与 count 同构，apply 一次通过（此前只验证过 count，本模块补齐 avg）。

## 配置决策

### route 权限矩阵（按实测 collection ACL 授）

| 页面 | leader | organizer | teacher | student | academic |
|---|---|---|---|---|---|
| 评估方案 | ✅ | ✅ | ✅ | —（无 eval_scheme 权限） | —（6 表全无） |
| 专题评估 | ✅ | ✅ | ✅ | ✅（S1 只看本人） | — |
| 综合评估 | ✅ | ✅ | ✅ | ✅（S1 只看本人） | — |
| 投票管理 | ✅ | ✅ | ✅ | ✅ | — |
| 不记名问卷（双tab） | ✅ | —（无答卷权限） | ✅ | ✅（own） | — |
| 统计图表 | ✅ | — | ✅ | — | — |

计数：leader/teacher 各 14 条（组+6页+7tab）、organizer 9 条、student 10 条、academic 0 条。academic 在阶段2 就未授这 6 张表（评估/问卷/投票是教师工作面，教务不参与），菜单同步不授。

### 落库位置与验证方式（与前面模块不同的坑）

- **chart 块配置存在 `flowModels` 表的 `options.stepParams.chartSettings`**（use=ChartBlockModel），不在 `uiSchemas`——用 `uiSchemas` 或页面 schema 读回验证 chart 会扑空，验证 SQL：
  `select count(*) from "flowModels" where options::text like '%<chartAlias>%';`
- dataScope 过滤（专题/综合评估页的 kind 条件）同样在 flowModels options 里，两个页各 1 条命中即验证通过。

### 蓝本踩坑（延续与新增）

1. **survey_answer 描述字段触发 Description Review**（同教材模块 stock 字段）：`answers_json`/`device_tag` 的 description 是"简化存储"语义说明，声明 `formBehaviorDescriptionReview.fields.<字段> = {decision:"unsupported", reasonCode:"ambiguous-description"}` 后通过。
2. 自建菜单组写法：`navigation.group = {title, icon}`（不带 routeId），组随首个页面自动创建。
3. 复用方案：关联目标集合的 defaults fieldGroups（student/class/topic/course_schedule 15 字段级）预防性全给；users 显示列用 `.nickname`；bar 图 mappings 用 x/y、pie 用 category/value。

## route id 速查

| 项 | id |
|---|---|
| 组「教学评估」 | 396739781394432 |
| 评估方案 | 396739781394433（tab ...434） |
| 专题评估 | 396739798171648（tab ...649） |
| 综合评估 | 396739804463104（tab ...105） |
| 投票管理 | 396739812851712（tab ...713） |
| 不记名问卷 | 396739944972288（tab 问卷列表 ...289 / 答卷明细 396739963846656） |
| 统计图表 | 396739821240320（tab ...321） |

## 补充（2026-11-10，D62）：三页新增弹窗拆模板副本 + kind 默认值

**问题**：Violet 线上「专题评估新增提交了但没数据」。取证：党性考核/专题评估/综合评估三页「新增」弹窗此前**共用模板** tfqylic8j8y（新增党性考核记录，usageCount=3），kind/班级/课程字段无默认值且非必填——只填学员提交时记录落库 kind 为空，被各页 kind 过滤（topic/comprehensive/party_*）吞掉（status=200 但列表不可见，日志取证）。

**规则**：①同表多视角（kind 区分）的新增弹窗**必须每页独立模板副本**（`convert-template-to-copy`），不允许跨 kind 页共用一个新增表单；②副本各自配 `set-field-value-rules` kind 静态默认值（runjs 形态 `return 'topic';`），学员选择器 `editItemSettings.required={required:true}`（configure 不支持 settings，SQL 直改，D60 同款）。

**坑**：弹窗挂模板时 props/props 均看不到 kind 字段绑定，取证要走 `flow-surfaces get --uid <按钮uid>` 看 `popup.template.uid` → `get-template` 看 targetUid 再展开表单树；`flowModelTreePath` 对 popup 子树不展开（ancestor 查无 descendant），须按模板链路查。
