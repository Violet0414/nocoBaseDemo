# s3-教材管理 — 教材管理全套逻辑说明（阶段3-2）

> 完成日期：2026-11-09。对应蓝本：`.artifacts/nocobase-ui-builder/stage3-textbook/`。
> 数据模型：`models/collections/nb_dx_textbook|purchase|requisition|textbook_return|recommendation.yaml`（阶段1 已建）。

## 业务范围

教材管理共 6 个页面，挂「教材管理」菜单组（routeId `396714401660928`）：

| 页面 | 集合 | 用途 |
|---|---|---|
| 教材信息 | nb_dx_textbook | 教材主档（名称/分类/出版社/定价/ISBN），`stock` 字段为当前库存 |
| 教材采购 | nb_dx_purchase | 采购流水（数量/单价/金额/供应商/状态：草稿→已下单→已入库） |
| 教材领用 | nb_dx_requisition | 班级领用流水（批次/数量/状态：已提交→已领用→已取消） |
| 教材退库 | nb_dx_textbook_return | 退库流水（关联领用单） |
| 学员荐书 | nb_dx_recommendation | 学员推荐书目（书名/作者/理由/推荐人/班级） |
| 库存报表 | nb_dx_textbook（chart+table） | 各分类库存占比饼图 + 库存明细表 |

## 业务规则

1. **库存 `stock` 的维护口径**：库存由采购/领用/退库三类流水推算维护，不在表单里直接随意填。demo 阶段为简化，未做 workflow 联动（不自动加减库存），库存数字由教务人员在「教材信息」里手工维护——阶段7 造演示数据时按流水口径填入合理数字即可。表单生成时该字段的元数据描述（"由采购/领用/退库流水维护"）按 `unsupported / ambiguous-description` 审核通过，不转成 UI 行为。
2. **荐书与教材主档解耦**：学员荐书（recommendation）是独立集合，审核采纳后由教务人员手工在教材信息里建档，demo 不做自动转化。
3. **退库必须挂领用单**：textbook_return 有 requisition m2o 字段（关联领用单），数据完整性靠表单必填约束（demo 未做 workflow 强校验）。
4. **状态机均为纯展示**：purchase.status / requisition.status 是 select 字段人工流转，阶段4 的 4 条审批流不涉及教材模块。

## 权限设计（对应 decisions D23 矩阵）

| 角色 | collection ACL | 菜单 route 授权 |
|---|---|---|
| r_leader | 5 表 view+export | 全 13 条（组+6页×2） |
| r_academic | 5 表 create/view/update/destroy/export | 全 13 条 |
| r_student | textbook view；recommendation create+view；其余 3 表无 | 5 条（组+教材信息+学员荐书） |
| r_organizer / r_teacher | 无任何教材表权限 | 不授 |

学员不授「库存报表」路由：报表属管理视角，虽然学员对 textbook 有 view 权限，菜单上不给入口。

## 蓝本阶段踩坑（后续建页直接复用经验）

1. **关联目标集合 >10 字段必须给 fieldGroups**：表格显示 `klass.name` / `student.name` 这类虚线路径时，后端会为生成的 view 弹窗自动建关联弹窗，目标集合（nb_dx_class/nb_dx_student，各 15 字段）超过 10 字段阈值就要求显式 `defaults.collections.<目标>.fieldGroups`（含 popups 三件套）。分组方案已存蓝本，后续教务/班务模块建页直接复用。
2. **字段名 `date` 在生成的 details 弹窗中不计入有效字段**：nb_dx_textbook_return 标量字段仅 textbook_name/quantity/date，生成 view 弹窗的 details 镜像只认出 2 个有效字段（<3 触发 `data-block-visible-fields-minimum`），解法是给 view 记录动作显式 inline popup + details 块 + fieldGroups（关联字段须对象形式 `{"field":"textbook","titleField":"name"}`）。标量字段 ≥4 的集合不会踩到。
3. **`stock` 带描述字段必须过 formBehaviorDescriptionReview**：合法出口是 `{"decision":"unsupported","reasonCode":"ambiguous-description"}`（自定义 reasonCode 会被拒）。
4. **多块页 layout**：所有非 filter 块各占一行会被拒（`block-layout-single-column`），把多个块放进同一 `rows` 数组即可（各 span 24 视觉上仍换行）。
