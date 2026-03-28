# ByteC
ByteC

## Lark CLI 安装

### 前置要求

- Node.js（`npm` / `npx`）
- Go `v1.23`+、Python 3（仅从源码构建时需要）

### 方式一：npm 安装（推荐）

```bash
npm install -g @larksuite/cli
npx skills add larksuite/cli -y -g
```

### 方式二：从源码构建

```bash
git clone https://github.com/larksuite/cli.git
cd cli
make install
npx skills add larksuite/cli -y -g
```

### 安装后配置

```bash
# 1. 初始化配置（交互式，仅需一次）
lark-cli config init

# 2. 登录认证（自动选择常用权限）
lark-cli auth login --recommend

# 3. 验证安装
lark-cli calendar +agenda
```

> **注意**：安装 CLI Skill（`npx skills add larksuite/cli -y -g`）是获得完整功能所必需的步骤。
