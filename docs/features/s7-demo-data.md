# s7 演示数据 — 业务逻辑与数据约定

> 生成脚本：`.artifacts/stage7-demo-data/gen_demo_data.py`（主体）+ `gen_demo_data_part2.py`（断点续跑段）。
> 脚本幂等保护：teacher/seat/textbook 任一非空即退出，防止重复灌入。

## 数据规模总览（41 张业务表全覆盖）

| 模块 | 内容 |
|---|---|
| 班次 4 | 班1「第1期中青班」**当前班**（ZQ2601，21 天 240 学时，2026-01-05~02-06，组织员=用户3，第一报告厅）；班2「乡村振兴专题培训班」**可报名**（ZT2602，5 天，12-01 开班，扫码报名演示用）；班3「第2期中青班」计划班次；班4「2025年秋季进修班」历史班次 |
| 学员 21 | 班1 16 人（学号 ZQ2601-01~16，含班长/副班长/学习/生活/党小组长职务，分组 1-4）；班2 2 人（待报到）；班4 3 人（2 结业 1 退学）。**学员1 张明远绑定 student_test 账号（user 6）** |
| 师资 8 | 校内 6 + 外请 2 + 领导干部上讲台 1（陈立·省委组织部副部长） |
| 专题 12 | theory/spirit/ability/field 四类，必修/选修兼有，3 个 excellent/approved 状态点缀；全部挂专题评估方案 |
| 课表 29 | 班1 第 1-2 周（专题课/活动/选修/视频课混合）+ 班2 1 节；含**1 对刻意冲突**（第1周周三第1节「依法行政」与「压力管理」同占第一报告厅）供冲突高亮演示；1 条 changed 状态 + change_log 调课记录 |
| 座位 48 | 班1 6×8 全量，学员 1-16 按学号坐第 1-2 排 |
| 教材链路 | 教材 6 本 + 采购 3（received/ordered/draft）+ 领用 2 + 退库 1 + 荐书 3 + 库存流水 4 |
| 班务 | 请假 6（含 over_ratio 已触发 1 条、pending 2、withdrawn 1）+ 外出 2 + 退学 1（配套班4 退学学员）+ 考勤 32（两节课×16 人，混 late/absent/leave/goout）+ 打卡 3 + 承诺书 1 + 材料表 2 |
| 评估问卷 | 方案 3（score/grade/mixed）+ 专题评估 10 + 综合评估 8 + 党性自评 8 + 党性考评 4 + 投票 1（12 票分布 5 候选人）+ 问卷 1（匿名答卷 8，device_tag ANON-xxx） |
| 报名缴费 | 报名 6（pending 4 供报名流审批演示 / approved 2 已建学员）；缴费 4（approved 2 / pending 2） |
| 作业 | 作业 1（党性分析材料）+ 提交 3（2 submitted / 1 reviewed 92 分） |
| 门户 | 公告 4（campus top/teaching/student/guide）+ 新闻 3 + 评论 2 |

## 关键约定

1. **课表时间双轨**：`day_of_week` 权威（D38），`start_time/end_time` 按 2026-01-04（周一）起占位 + 五节次（08:30/10:30/14:00/16:00/19:00 起）。周课表/排课画布按此展示。
2. **请假超限演示闭环**：班1 total_days=21 → 阈值 3 天。leave#4（2.6 天 approved）over_ratio=true 已触发提醒；另造 pending 2 天一条供浏览器走审批流。
3. **workflow 联动**：请假 pending 2 条挂在组织员（用户3）待办；报名 pending 4 条挂教务（用户4）；学员1 绑定 student_test 可全流程演示「学员提交→审批→通知」。
4. **D26 数据级验证已补**（2026-11-09，学员 student_test 登录实测）：学员表只见本人（S1b）、请假/考勤只见本人记录（S1）、座位/班次只见本班（S2）、新闻全员可见——scope 过滤全部生效，决策关闭。

## 踩坑记录（重灌/维护必读）

1. **REST 认证头**：2.4 alpha 的 REST API 用 `Authorization: Bearer <token>` + `X-Authenticator: basic`，仅 `X-Token` 会 401（CLI 内部走 Bearer）。token 过期先 `nb env auth dx-demo`。
2. **create body 平铺**（D37 同款）：m2o 用 FK 列（`class_id`/`topic_id`/`teacher_id`），不包 `values`。
3. **附件字段别塞文本**：`declaration` 的 health_code/trip_code/test_report 是 attachment 接口，传文本会 500（bigint cast 失败），文字内容并入 `content`。
4. **destroy 带 filter 必须放 query**（`?filter=<urlencoded json>`），放 body 报 "filter or filterByTk is required"。
5. **id 序列不连续**：删除后新建的记录 id 跳号（如师资实际 10-17），脚本里写死 id 会悬空——本轮已踩（课表/选课 topic_id 引用字面量 1-12，后按 topic_name 回填修复）。**重灌或新增数据一律先查回真实 id**。
6. **阶段3 遗留 test 脏数据**（师资/活动/基地/拟开发专题/案例/校外宣讲/退学各 1 条 "test"）已在本轮清理；如恢复旧备份需重查。
