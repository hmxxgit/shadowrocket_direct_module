# 来源与许可

本项目的自行编写脚本和文档沿用仓库 [LICENSE](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/LICENSE)：MIT，Copyright (c) 2026 答案在书里。上游快照各自保留原许可证；派生发布模块 [sr_routing.module](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/sr_routing.module) 按 GPL-3.0 分发，完整可编辑来源和构建脚本公开在本仓库。

## GMOogway

[upstream/sr_direct_list.module](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/upstream/sr_direct_list.module) 原样保留 [GMOogway/shadowrocket-rules](https://github.com/GMOogway/shadowrocket-rules) 作者/发布者 GMOogway 的完整模块与元数据。

- 固定提交：`12fb8a1e037502a536f86ec9faf1cdbb2c576a48`。
- 原始文件：[sr_direct_list.module](https://github.com/GMOogway/shadowrocket-rules/blob/12fb8a1e037502a536f86ec9faf1cdbb2c576a48/sr_direct_list.module)。
- 获取日期：2026-10-10（Asia/Shanghai）。
- GPL-3.0 原文：[LICENSE-GPL-3.0](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/LICENSE-GPL-3.0)；原始来源与 SHA-256：[upstream/source.json](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/upstream/source.json)。

2026-10-14 修改派生模块的名称、说明、规则分类和排序。停止整包继承未确认业务的直连策略，只在已审阅国内产品域名范围内复用直连条目；旧 URL-REGEX 不发布。原始快照不变，逐条处理情况保存在 [reports/source-audit.tsv.gz](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/reports/source-audit.tsv.gz)。

## v2fly/domain-list-community

服务列表、属性条目和递归依赖来自 [v2fly/domain-list-community](https://github.com/v2fly/domain-list-community)，固定提交 `c6adacf29cc4fb05e04651fcf03e00989ef9f797`。MIT，Copyright (c) 2018-2019 V2Ray；许可证分别完整保留在 [upstream/proxy-services/LICENSE](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/upstream/proxy-services/LICENSE)、[upstream/bytedance/LICENSE](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/upstream/bytedance/LICENSE)、[upstream/domestic/LICENSE](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/upstream/domestic/LICENSE)。各目录 `source.json` 保留文件原始链接、根列表与 SHA-256。

原有 Google/AI/社交/开发、字节跳动与国内公司列表及全部依赖均保留。2026-10-14 在相同固定提交补充 Netflix、Disney（含递归依赖）、HBO/Max、Spotify、Prime Video、Signal、WhatsApp、Vercel、Netlify、Cloudflare 原始列表及依赖；新增快照未经修改。

派生转换保留精确主机、后缀和 include/属性的语义，不把域名正则扩大为共享父域；无法无损转换的规则记录在构建报告中。停止把整套字节跳动（包括 TikTok、CapCut、Lark、Coze、TRAE、Dola）直连，改用产品地域分类。对共享域名和混合公司列表采取显式筛选。唯一发布分类清单为 [rules/services.json](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/rules/services.json)；报告中的数字由构建/审计脚本生成，不作为人工维护的分类来源。

## Johnshall

[upstream/johnshall/](https://github.com/hmxxgit/shadowrocket_direct_module/tree/main/upstream/johnshall) 原样保留 [Johnshall/Shadowrocket-ADBlock-Rules-Forever](https://github.com/Johnshall/Shadowrocket-ADBlock-Rules-Forever) 的 [sr_top500_whitelist.conf](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/upstream/johnshall/sr_top500_whitelist.conf)、[sr_cnip.conf](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/upstream/johnshall/sr_cnip.conf) 和许可声明。作者署名 Moshel、Johnshall，项目源自 h2y/Shadowrocket-ADBlock-Rules。

- 固定提交：`d245e4dc6ca3628988f4f1430ecd1f034789344d`。
- 获取日期：2026-10-11（Asia/Shanghai）。
- 原始链接、作者、SHA-256 与许可网址：[upstream/johnshall/source.json](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/upstream/johnshall/source.json)。
- 原始快照按 [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) 发布，许可声明见 [Johnshall LICENSE](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/upstream/johnshall/LICENSE)。

2026-10-14 改为只复用已审阅国内产品范围内的明确 DIRECT 条目和私有/回环/局域网地址；IPv6 的原 IP-CIDR 写法规范为 IP-CIDR6。不沿用其中对未确认海外、Apple CDN 或共享云服务的白名单分类，不导入 DNS、General、回国、广告、解密或 FINAL 设置。对 BY-SA 4.0 材料的改编贡献按 GPL-3.0 发布，见 [Creative Commons 兼容许可说明](https://creativecommons.org/compatible-licenses/) 中 GPLv3 的单向兼容规定。

## 人工补充与网页证据

豆包输入法、微信输入法的原始来源说明保留在 [rules/ime_direct.json](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/rules/ime_direct.json)，其中观察到的域名仅作证据，不授权整体父域直连。人工业务清单与来源见 [rules/services.json](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/rules/services.json)。

2026-10-14 增加 CapCut、Lark、Coze 国内外、TRAE、Dola、豆包、飞书、输入法、Temu、Joybuy 官方公开页面的域名引用证据：[rules/domain_evidence.json](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/rules/domain_evidence.json)。仅保存来源网址、内容 SHA-256、域名等事实信息，不分发页面正文、应用安装器、个人数据或用户网络日志。共享主机发现用于收紧发布规则，官网的第三方外链不自动成为分类规则。网页观察不等于 iOS APP 全部请求已验证。
