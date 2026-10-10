# Shadowrocket 分流模块

Google、YouTube、X／Twitter、GitHub、ChatGPT、Gemini、Codex 等已收录服务及相关域名走代理；其余保留上游直连规则，并补充大陆 GeoIP 直连。未命中流量沿用原配置。

## 导入链接

```text
https://raw.githubusercontent.com/hmxxgit/shadowrocket_direct_module/main/sr_routing.module
```

## 使用

1. **配置 → 模块 → ＋**，粘贴新链接并下载。
2. 启用 **大陆直连与海外服务代理**，移到模块列表最上方，停用旧版模块。
3. **全局路由 → 配置**，选择代理节点并重新连接。

模块不提供节点。更新时重新下载模块。

规则来源：[GMOogway](https://github.com/GMOogway/shadowrocket-rules)、[v2fly](https://github.com/v2fly/domain-list-community)。来源及许可见 [NOTICE.md](NOTICE.md)。
