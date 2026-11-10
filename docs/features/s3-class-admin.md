# s3-班务管理 — 班务管理六页逻辑说明（阶段3-4）

> 完成日期：2026-11-09。对应蓝本：`.artifacts/nocobase-ui-builder/stage3-class-admin/`（生成脚本 `gen_class_admin.py`）。
> 数据模型：`models/collections/nb_dx_leave|go_out|dropout|attendance|eval_record|vote|vote_record.yaml`（阶段1 已建）。

## 业务范围

班务管理共 6 个页面，挂「班务管理」菜单组（routeId `396730107232256`）：

| 页面 | 集合 | routeId | 用途 |
|---|---|---|---|
| 请假管理 | nb_dx_leave | 396730107232257 | 请假申请列表（类型/起止时间/天数/审批状态/超1/7提醒标记） |
| 外出报备 | nb_dx_go_out | 396730495205376 | 外出报备记录（报备类型/事由地点/起止时间/状态） |
| 退学管理 | nb_dx_dropout | 396730507788288 | 退学申请（原因/附件/审批状态/审批意见） |
| 考勤统计 | nb_dx_attendance | 396730658783232 | 考勤状态分布饼图 + 明细表（打卡时间/位置/方式） |
| 党性考核 | nb_dx_eval_record | 396731189362688 | 党性自评/复评记录（dataScope 过滤 kind=party_self/party_review） |
| 优秀学员 | nb_dx_vote | 396730780418048 | 评选投票（打分/单选/多选），关联投票明细 vote_record |

## 业务规则

1. **党性考核复用评估模型**：不单独建党性表。党性考核 = `eval_record.kind ∈ {party_self, party_review}`（学员先自评、评议小组复评），评估项五维度（党性意识/学习态度/廉洁自律/遵章守纪/突出表现）存 `items_json` 简化存储，方案定义在 `eval_scheme.kind=party`。页面用块级 `settings.dataScope` 过滤，把专题评估/综合评估记录排除在外。
2. **优秀学员复用投票模型**：不单独建评选表。`vote.kind ∈ {single, multi, score}` 覆盖"投票/打分"两种评选方式，明细在 `vote_record`（voter/score_value/option_selected）。评选结果公示（阶段7 造数据时体现）。
3. **考勤状态五态**：normal/late/absent/leave/goout——请假与外出报备会反映到考勤状态，demo 阶段为手工维护，阶段4 workflow 审批通过后由人工联动（不自动写考勤）。
4. **请假 1/7 提醒**：`over_ratio` 布尔字段为标记位，阶段4 请假审批流（聚合已批时长判断 ≤ 总学时 1/7）实现自动置位；PC 页面本期只做展示。
5. **审批状态机均为纯展示**：leave/dropout 的 status 由人工流转，阶段4 才接 workflow。

## 权限设计（按 D23 矩阵实测 collection ACL 授 route）

| 角色 | route 条数 | 授予页面 | 说明 |
|---|---|---|---|
| r_leader | 13 | 全 6 页 | 全表 view+export |
| r_organizer | 11 | 请假/外出/退学/考勤/党性考核 | 事务 4 表 CRUD + eval 2 表 view；**无 vote_record 权限故不授优秀学员页** |
| r_academic | 9 | 请假/外出/退学/考勤 | 事务 4 表 view；eval/vote 4 表无权限 |
| r_teacher | 7 | 考勤统计/党性考核/优秀学员 | attendance/eval_2表/vote_2表 CRUD；请假/外出/退学无权限 |
| r_student | 13 | 全 6 页 | leave/go_out/dropout/eval_record create+view、attendance/vote view、vote_record create+view |

注：organizer 若后续需要优秀学员评选结果，须先给 r_organizer 补 `nb_dx_vote_record` 的 view 权限（D23 矩阵变更，需 Violet 确认），再补 route 授权。

## 蓝本阶段踩坑（新增两条，接续 s3-textbook 四条）

1. **块级 `defaultFilter` 强制 `{logic, items}` 结构且至少 3 个 filterable 字段**：`{"$and":[...]}` 包装直接被拒（defaultFilter-logic-required/items-required），单字段条件被拒（defaultFilter-minimum-fields，"must include at least 3 filterable fields"）。**单字段过滤改用 `settings.dataScope.filter`**（`{"logic":"$and","items":[{"path":"kind","operator":"$in","value":[...]}]}`），一次通过且读回确认保留。dataScope 不受 3 字段物化校验约束。
2. **chart 块必须显式 `assets.charts.<key>`**：块里写 `"chart": "attByStatus"` 而 assets 未定义 → `chart-block-asset-reference-missing`。补 `assets.charts.attByStatus.query`（measure `count id` alias + dimension status）+ `visual`（pie，mappings category/value）即过。count 聚合写法 `{"field":"id","aggregation":"count","alias":"..."}` 有效。
3. 复用既有经验：关联目标 >10 字段给 fieldGroups（student/class/topic 已验证方案 + 新构造 course_schedule 分组）；表格关联列用点路径（`klass.name`/`creator.nickname`，users 必须 `.nickname`）。

## 列单元格渲染规则（D70 补充）

- 表格列的单元格渲染由 **TableColumnModel 下的 field 子模型**（subKey=field，如 `9f4vkck3k1e`）决定，不是列模型本身：select 类字段默认 `DisplayEnumFieldModel`（显示枚举 label），input/number 等默认 `DisplayTextFieldModel`（显示原始值）。boolean 字段想显示"是/否"，把 field 子模型换成 `DisplayEnumFieldModel` 并在 `props.options` 显式映射，**不动集合定义**（boolean 字段还要参与工作流判断）。
- **value 必须混配字符串与布尔两种**：`[{"value":"true","label":"是"},{"value":true,"label":"是"},{"value":"false","label":"否"},{"value":false,"label":"否"}]`——boolean 字段值经 API 序列化到前端是字符串 `"true"`，纯布尔映射匹配不上会 fallback 显示原值；两种 value 同一值只会命中一项，不重复渲染。
- NULL 值显示空白（isEmptyEnumValue 短路），属预期。
- 坑：`docker exec psql -c` 直写中文 JSON 会编码乱码——中文改动后必须验 UTF-8 字节（是=e698af/否=e590a6），或改用 Unicode 转义/文件管道。
