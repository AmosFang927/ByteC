# Playwright Browser Skill for OpenClaw - Mac/Linux 版本
版本: 2.1.0

## 快速安装

### 方法一：自动部署（推荐）

1. 解压此文件到任意目录
2. 在此目录打开终端
3. 添加执行权限并运行部署脚本：

```bash
chmod +x auto-deploy.sh
./auto-deploy.sh
```

或使用英文版本：

```bash
chmod +x auto-deploy-en.sh
./auto-deploy-en.sh
```

### 方法二：手动部署

1. 复制整个文件夹到：
   ```
   ~/.openclaw/skills/playwright-browser-skill/
   ```

2. 编辑配置文件：
   ```
   ~/.openclaw/settings/mcp.json
   ```

3. 添加以下配置：
   ```json
   {
     "mcpServers": {
       "playwright-browser": {
         "command": "node",
         "args": ["/Users/你的用户名/.openclaw/skills/playwright-browser-skill/dist/mcp-server.js"],
         "disabled": false
       }
     }
   }
   ```

4. 重启 OpenClaw

## 使用说明

部署完成后，在 OpenClaw 对话中输入：

```
请使用 Playwright Browser Skill 技能来访问互联网和控制浏览器
```

然后就可以使用浏览器相关功能了！

## 包含内容

- ✅ 编译后的代码 (dist/)
- ✅ 完整依赖包 (node_modules/)
- ✅ 技能文档 (skill-package/)
- ✅ 自动部署脚本
- ✅ 完整文档

## 系统要求

- macOS 10.15 或更高版本
- Linux（Ubuntu 20.04+, Debian 11+, Fedora 35+）
- Node.js 18 或更高版本

## 支持

- 📧 Email: 91fapiao@gmail.com
- 🐛 Issues: https://github.com/91fapiao-cn/playwright-browser-skill/issues
- 📚 文档: 查看 README.md

---
**Made with ❤️ for OpenClaw Community**
