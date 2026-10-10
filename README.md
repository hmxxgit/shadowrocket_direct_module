# Shadowrocket 大陆直连与海外服务代理

已收录的 Google、YouTube、X／Twitter、GitHub、ChatGPT、Gemini、Codex 等服务及相关 API、CDN、下载域名优先走 `PROXY`；其余保留上游直连规则，并补充 `GEOIP,CN,DIRECT`。未命中流量由原配置处理。

## 导入链接

新版：

```text
https://raw.githubusercontent.com/hmxxgit/shadowrocket_direct_module/main/sr_routing.module
```

[旧链接继续可用](https://raw.githubusercontent.com/hmxxgit/shadowrocket_direct_module/main/sr_direct_list.module)，保留改名前的版本，不随新版更新。

## 使用

1. **配置 → 模块 → ＋**，粘贴新版链接并下载。
2. 启用 **大陆直连与海外服务代理**，移到模块列表最上方。
3. 停用旧版模块，避免重复分流。
4. **全局路由 → 配置**，选择代理节点并重新连接。

模块不提供节点。代理出口由当前配置的 `PROXY` 策略及所选节点决定。直连列表仍包含部分 Apple 等海外服务；并非所有海外域名都自动代理。

## 更新与校验

更新后在 Shadowrocket 中重新下载新版模块。规则为固定快照，不自动追随上游。

```sh
python3 scripts/build.py
python3 scripts/validate.py
```

构建只更新新版文件，旧入口保持原样。已通过静态路由校验，未进行客户端播放测速。

## 来源与许可

直连规则来自 [GMOogway/shadowrocket-rules](https://github.com/GMOogway/shadowrocket-rules)，代理域名来自 [v2fly/domain-list-community](https://github.com/v2fly/domain-list-community)。来源、固定版本与许可见 [NOTICE.md](NOTICE.md)；原始快照保存在 `upstream/`。
