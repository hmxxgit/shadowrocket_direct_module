# 来源与许可

`upstream/sr_direct_list.module` 完整来自 [GMOogway/shadowrocket-rules](https://github.com/GMOogway/shadowrocket-rules)，作者/发布者 GMOogway；保留了原始元数据与全部规则。

- 固定提交：`12fb8a1e037502a536f86ec9faf1cdbb2c576a48`
- 原始文件：[sr_direct_list.module](https://github.com/GMOogway/shadowrocket-rules/blob/12fb8a1e037502a536f86ec9faf1cdbb2c576a48/sr_direct_list.module)
- 获取及修改日期：2026-10-10（Asia/Shanghai）
- 上游许可：GNU General Public License v3.0，原文保存在 `LICENSE-GPL-3.0`。

本项目将派生模块发布为 `sr_routing.module`（大陆直连与海外服务代理分流模块），对原模块更改名称、说明、主页和来源注释；移除 125 条海外服务相关直连规则，在最前面增加 1,794 条海外服务 `PROXY` 规则，并在其余上游直连规则之后增加 `GEOIP,CN,DIRECT`。这个派生模块以及上游快照按 GPL-3.0 分发；完整可编辑规则、补充规则和构建方式均在本仓库公开。

仓库原有 `LICENSE`（MIT，Copyright (c) 2026 答案在书里）保留，适用于本项目自行编写的构建/校验脚本和文档；不替代上述上游及派生模块的 GPL-3.0 许可。

## 海外服务域名来源

海外服务代理域名列表来自 [v2fly/domain-list-community](https://github.com/v2fly/domain-list-community)，固定提交 `c6adacf29cc4fb05e04651fcf03e00989ef9f797`，许可为 MIT（Copyright (c) 2018-2019 V2Ray），全文保留于 `upstream/proxy-services/LICENSE`。

原始 Google／Gemini、海外 AI、海外社交媒体及开发／通讯服务列表和所有递归依赖未经修改地保存在 `upstream/proxy-services/`，来源链接及 SHA-256 见该目录的 `source.json`。构建时展开依赖，保留全部属性条目，转换为域名后缀代理规则、去除冗余子域，并补充少量服务根域和 OpenAI 相关认证、实验服务域名。Google Play 的两个正则由整个下载域名覆盖；ChatGPT 的动态 WebSocket 正则由共享后缀 `webpubsub.azure.com` 的代理规则覆盖。发布模块仍按 GPL-3.0 分发。

## 输入法直连规则

2026-10-11 新增豆包输入法和微信输入法的 20 条优先直连规则，覆盖已确认的 API、语音、同步、下载、资源和监控服务。域名来源为官方站点、官方应用中的域名常量；完整条目与来源记录见 `rules/ime_direct.json`。共享 CDN／监控域名采用后缀直连，同一后缀下的其他服务也会直连。构建时将这些规则放在海外代理规则之前，并去除与上游完全重复的直连条目。
