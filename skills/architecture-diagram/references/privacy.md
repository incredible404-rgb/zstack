# 隐私打码

对外分享架构图时默认往严里打：漏一项隐私有泄露风险，多打一项随时可以按需放开。

| 类别 | 图里怎么写 |
|---|---|
| 组织名、内部项目代号、业务编号 | `业务目录`、`核心服务`，不出现内部原词 |
| 本机用户名、个人主目录绝对路径、盘符 | 不写路径前缀，只写仓库内相对路径 |
| 私有仓库名与账号、机器人账号、个人邮箱 | `私有仓库`、`通知机器人` 黑条（`chip=`） |
| 私有 Webhook、内网管理地址、心跳入口 | `内网入口` 黑条 |
| 设备名、主机名、局域网/Tailscale/公网 IP、端口、密钥指纹 | 不画 |
| 密钥、令牌、账户余额与配额明细 | 绝不出现 |

公开开源工具名（Git、Claude Code、Codex、Playwright、Tailscale 等）与通用文件名不算隐私。

## 自动扫描

```python
from svgkit import privacy_scan, default_private_terms
terms = default_private_terms() + [r"internal-corp", r"secret-project-name"]
assert privacy_scan(open(out, encoding="utf-8").read(), terms) == []
```

项目专有敏感词从项目本地配置读取并在内存里拼接，**不要把敏感原值硬编码进图生成脚本**。`@` 会命中 CSS 的 `@media`，默认的邮箱正则已自动排除 CSS 规则关键字。
