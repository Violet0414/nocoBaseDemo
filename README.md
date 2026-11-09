# 党校智慧管理平台 Demo

依据 `dx.xlsx` 功能清单（综合门户 / 智慧教务 / 学员服务 / 移动应用 四大块）搭建的 NocoBase 演示项目，全程由 AI Agent（Claude Code）驱动搭建，人做决策和验收。

## 文件夹导览

| 文件/目录 | 用途 |
|---|---|
| `STATE.md` | **当前进度快照（续做入口）** |
| `PLAN.md` | 实施计划（选型/阶段/风险） |
| `TASKS.md` | 任务清单（逐阶段 checkbox） |
| `dx.xlsx` | 功能清单原件（177 行） |
| `docs/SETUP.md` | 环境搭建 / 跨电脑重建手册 |
| `docs/decisions.md` | 关键决策记录 |
| `models/` | 阶段1 数据模型 YAML |
| `workflows/` | 阶段4 审批流编排记录 |
| `ai-portal/` | 阶段5 AI Portal React 源码 |
| `backups/` | pg_dump 数据库备份 |
| `snapshots/` | 版本快照导出 / 验收记录 |

## 跨电脑续做（三步走）

1. **拷贝**：整个 demo 文件夹拷到新电脑（U盘/网盘均可，无 git 依赖）
2. **重建环境**：按 `docs/SETUP.md` 安装 Node → nb CLI → 启用 Docker WSL 集成 → 起 PG 容器 → 恢复 `backups/` 最新 dump（或全新初始化）
3. **续做**：Claude Code 打开本文件夹，agent 读 `CLAUDE.md` → `STATE.md` 即可从未完成任务继续

## 优先级

管理端优先：阶段0（接入）→ 1（建模）→ 2（ACL）→ 3（PC 管理端）→ 4（审批流）；阶段5（AI Portal）/ 6（移动端）/ 7（收尾）后置。
