# SETUP.md — 环境搭建 / 跨电脑重建手册

> 适用场景：新电脑上重建本项目环境。完成后回到 `STATE.md` 续做。
> 路径约定：本机当前为 Windows `E:\贵州顺拓\demo`，WSL `/mnt/e/贵州顺拓/demo`（换电脑后路径可能再变，以 CLAUDE.md 实际位置为准）。

## 1. 基础依赖

```bash
# Node.js 22（nb CLI 强制要求 22+，v20 会直接拒绝运行）
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
nvm install 22
nvm alias default 22   # 必做：否则新会话回落 v20，nb 报版本错误

# 验证（新开终端）
node -v   # 预期 v22.x
```

## 2. Docker（只跑 PostgreSQL，应用不进容器）

**Windows 已装 Docker Desktop 的电脑**：
1. Docker Desktop → Settings → Resources → **WSL Integration**
2. 勾选「Enable integration with my default WSL distro」及本发行版 → Apply & Restart
3. 新开 WSL 终端验证：`docker ps` 无报错即成

**全新电脑（未装 Docker Desktop）**：安装 Docker Desktop for Windows 后重复上述步骤。

## 3. 安装 nb CLI 并初始化 NocoBase

```bash
# nb 要求 Node 22+（v20 会直接拒绝运行）
npm install -g @nocobase/cli   # 2.2.x stable
npm install -g skills          # 预装，避免 nb 启动时 npx 临时下载超时
nb --version

# 浏览器可视化向导（需人工点选）：
nb init --ui --locale zh-CN --ui-port 13100
#   向导中按需选择，本项目实际采用（2026-11-08）：
#   1) 安装模式：新安装（install-new）
#   2) 获取方式：Docker（镜像 registry.cn-shanghai.aliyuncs.com/nocobase/nocobase:latest-full）
#   3) 数据库：内置（nb 自动起 nb-dx-demo-postgres 容器，nocobase/nocobase/nocobase）
#   4) 认证：OAuth 设备登录（CLI 提示浏览器打开 /idpOAuth/device?user_code=XXX 批准）
# 完成后应用跑在 http://localhost:13000，`nb env list` 可见 dx-demo 环境
```

> 备选方案（原计划）：npm 源本地跑应用 + 自建 PG 容器。若需此模式：
> 先 `docker run -d --name dx-demo-pg -e POSTGRES_PASSWORD=<密码> -e POSTGRES_DB=dx_demo -p 5432:5432 -v dx-demo-pgdata:/var/lib/postgresql/data postgres:16`，再在向导中选 npm 源 + 自定义数据库。

## 4. 验证安装 + Skills

```bash
nb env list                    # 预期：dx-demo 行存在且带 * （当前）
nb env info dx-demo            # App / DB 均 running
curl -o /dev/null -w "%{http_code}\n" http://127.0.0.1:13000/   # 预期 200
ls ~/.claude/skills/ | grep nocobase   # 预期：一批 nocobase-* skill 目录（nb init 自动同步）
```

> 若 skills 为空：`nb skills update --yes` 重装。验证方式：Claude Code 会话中让 agent 执行一次 `nb env list`。

## 5. 恢复备份（换电脑续做时执行，全新搭建跳过）

```bash
# 找 backups/ 里最新的 dump；内置库容器端口不映射宿主机，走 docker exec
nb app stop dx-demo
# 清空全新 init 产生的默认 schema（避免与备份冲突）
docker exec nb-dx-demo-postgres psql -U nocobase -d nocobase -c 'DROP SCHEMA public CASCADE; CREATE SCHEMA public;'
docker exec -i nb-dx-demo-postgres psql -U nocobase -d nocobase < backups/<最新文件>.sql 2>&1 | grep -i error || echo "恢复完成（无 error 即成功，no privileges 告警可忽略）"
nb app start dx-demo
curl -o /dev/null -w "%{http_code}\n" http://127.0.0.1:13000/   # 预期 200
```

> 恢复后所有 collections / 界面配置 / 数据即回备份时点，无需重配。OAuth 会话过期则 `nb env auth dx-demo` 重新授权。

## 6. dsl-reconciler（YAML 建模工具链，阶段1+ 需要）

```bash
# 1) 装 Node 依赖（js-yaml / axios / tsx）
cd ~/.claude/skills/nocobase-dsl-reconciler/src && npm install

# 2) workspace symlink（真实产物在 demo 文件夹的 models/ 内）
mkdir -p ~/.agents/skills/nocobase-dsl-reconciler/workspaces
ln -sfn "$(wslpath -a 'E:\贵州顺拓\demo\models' 2>/dev/null || echo <WSL下demo路径>/models)" \
        ~/.agents/skills/nocobase-dsl-reconciler/workspaces/dx-demo
# 本机示例：ln -sfn /mnt/e/贵州顺拓/demo/models ~/.agents/skills/nocobase-dsl-reconciler/workspaces/dx-demo

# 3) 推送（models/collections/*.yaml → 应用）
export NB_TOKEN=$(python3 -c "import json;print(json.load(open('$HOME/.nocobase/config.json'))['envs']['dx-demo']['auth']['accessToken'])")
export NB_URL=http://127.0.0.1:13000
cd ~/.claude/skills/nocobase-dsl-reconciler/src
npx tsx cli/cli.ts push dx-demo --force --copy   # 幂等：已建的表做 diff upsert
```

> token 过期先跑 `nb env auth dx-demo` 刷新；注意 ~/.claude/skills 实际指向 ~/.agents/skills（symlink）。

## 7. 备份纪律（每阶段结束必做）

```bash
# 在 demo 文件夹根目录（backups/ 的上级）内执行：
docker exec nb-dx-demo-postgres pg_dump -U nocobase nocobase > "backups/nocobase_$(date +%Y%m%d).sql"
```

- 备份文件随 demo 文件夹一起拷贝迁移
- 阶段3（PC 管理端）每个模块完成后再额外 dump 一次

## 8. 服务器部署（内网试用，2026-11-09）

部署目标：内网物理机 `10.10.40.44`（Ubuntu 24.04，4C/8G，用户 ops），compose 方式双容器，**不装 nb CLI**。

### 8.1 迁移物构成（打包脚本产物见 `.artifacts/server-deploy/`）

| 内容 | 说明 |
|---|---|
| `nocobase_YYYYMMDD_server_deploy.sql` | 部署时点 fresh pg_dump |
| `docker-compose.yml` | postgres:16 + nocobase:2.4.0-alpha.17-full 双服务 |
| `storage/apps/` | aes_key.dat + idp_oauth_jwks.json（root 权限，须 `docker cp` 从容器内取出） |
| `storage/portals/` | Portal main 部署产物（含 dist） |
| `storage/uploads/` | 上传文件（logo 等） |

**要点**：纯 pg_dump 不够，`storage/portals` 与 `uploads` 必须随迁（两者都不在数据库里）；`APP_KEY` 必须原样保留在 compose 中（否则历史 token/会话失效）。

### 8.2 部署步骤（已在 10.10.40.44 完成，重做时照抄）

```bash
# 本机：打迁移包并传输
tar czf dx-demo-deploy.tar.gz -C .artifacts/server-deploy pkg
scp dx-demo-deploy.tar.gz ops@10.10.40.44:/home/ops/
ssh ops@10.10.40.44 'mkdir -p /home/ops/dx-demo && tar xzf /home/ops/dx-demo-deploy.tar.gz -C /home/ops/dx-demo'

# 服务器：起 PG → 恢复 → 起应用（顺序不能反）
cd /home/ops/dx-demo/pkg
docker compose pull
docker compose up -d postgres && sleep 8
docker exec -i nb-dx-demo-postgres psql -U nocobase -d nocobase < nocobase_20261109_server_deploy.sql
docker compose up -d   # app 约 30s 内就绪
curl -o /dev/null -w "%{http_code}\n" http://127.0.0.1:13000/   # 预期 200
```

### 8.3 服务器侧信息

- 部署目录 `/home/ops/dx-demo/pkg`（storage bind mount 同目录下）
- 访问地址：`http://10.10.40.44:13000/`（管理端）、`http://10.10.40.44:13000/x/main/`（Portal）
- 服务器上与 nb 托管模式的差异：`DB_HOST=postgres`（compose 服务名，非容器名）；restart 策略 `unless-stopped`（nb 本机托管是无策略）；compose 自带 pg healthcheck
- 账号密码与本机完全一致（同一份库）：管理员 = Violet 保管那套；测试账号 = D27 四个 `*_test`
- 服务器另有他人在跑的业务容器（semantic-dev，端口 5173/8080/28080），互不相干，勿动
- 备份命令（服务器侧）：`docker exec nb-dx-demo-postgres pg_dump -U nocobase nocobase > dx-demo-backup.sql`

## 9. 常见问题

| 症状 | 处理 |
|---|---|
| `docker: command not found`（WSL 内） | Docker Desktop WSL 集成未启用 → 第 2 步 |
| docker pull 报 `docker.mirrors.ustc.edu.cn: no such host` | 该镜像源已停服；Settings → Docker Engine 将 registry-mirrors 换为 `["https://docker.1ms.run", "https://docker.m.daocloud.io"]` |
| `nb` 报 `Node.js 22 or later is required` | `nvm install 22 && nvm alias default 22`，然后在 Node 22 下重装 `npm i -g @nocobase/cli` |
| nb 任何命令都报 `skills list timed out after 15000ms` | 全局预装 skills 包：`npm i -g skills`（根因：npx 临时下载慢于 15s 超时） |
| push 报 `Cannot find package 'js-yaml'` | dsl-reconciler 依赖未装 → 第 6 节第 1 步 `npm install` |
| push 报 `routes.yaml not found .../workspaces/dx-demo` | workspace symlink 未建 → 第 6 节第 2 步 |
| Claude Code 会话里 nb 报 Node 20 | 该 shell 继承旧 PATH → `source ~/.nvm/nvm.sh && nvm use 22`（每会话首次用 nb 前执行；已 `alias default 22` 的则重开终端） |
| `nb init` 连不上数据库 | 确认容器状态、密码正确、端口未被占用 |
| NocoBase 页面打不开 | `nb app start dx-demo` 重启；或 `docker ps` 确认 nb-dx-demo-app / nb-dx-demo-postgres 在跑 |
