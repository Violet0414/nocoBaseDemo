# CLAUDE.md — 党校智慧管理平台 Demo

## 项目是什么

党校智慧管理平台 demo（依据 `dx.xlsx` 功能清单，177 行四大块：综合门户 / 智慧教务 / 学员服务 / 移动应用），基于 NocoBase v2 stable + AI Agent（Claude Code）驱动搭建。完整计划见 `PLAN.md`，任务清单见 `TASKS.md`。

## 每次会话必做（新会话 / 换电脑续做）

1. **先读 `STATE.md`** — 当前进度快照，明确"做到哪、下一步做什么"
2. 对照 `TASKS.md` 的 checkbox 找到第一个未完成任务，继续执行
3. 读 `docs/decisions.md` 避免重复讨论已定决策

## 工作纪律（每完成任务后）

- 更新 `STATE.md`（当前阶段、已完成、下一步、本机环境差异记录）
- 勾选 `TASKS.md` 对应 checkbox 并填验证结果
- **每完成一个功能点/阶段，把该功能的业务逻辑与配置决策写入 `docs/features/`**（命名 `s<阶段>-<模块>.md`，登记到 `docs/features/README.md` 索引；写"为什么/规则是什么"，不写操作流水账）——便于后期迭代修改
- **每阶段结束必须跑 pg_dump 备份到 `backups/`**（命令见 `docs/SETUP.md`）
- 关键决策随时补录 `docs/decisions.md`

## 优先级（Violet 2026-11-08 确认）

管理端优先：阶段0→1→2→3→4 先行；阶段5（AI Portal）/6（移动端）/7（收尾）后置。

## 环境约定

- 本项目工作目录 = 本文件夹（Windows 路径 `E:\贵州顺拓\demo`，WSL 路径 `/mnt/e/贵州顺拓/demo`）
- 版本管理：**git + GitHub 远端**（2026-11-09 Violet 启用，origin = https://github.com/Violet0414/nocoBaseDemo.git ）。`.gitignore` 排除：`backups/`（数据库 dump 留本地，走 U盘/网盘拷贝）、`.claude/`（含 API token，严禁入库）、`main/node_modules`、`main/dist`。所有产物必须落在本文件夹内，不要写到 `~` 或其他位置
- Docker 只跑 PostgreSQL，NocoBase 应用本地跑（nb CLI 管理）
- 环境重建步骤见 `docs/SETUP.md`

## 协作偏好

- 请称呼用户为 **Violet**，自称 **芒果怪**
- 每次回复结尾加上 **Ciallo～(∠・ω< )⌒☆!**
- 全程用中文交流
