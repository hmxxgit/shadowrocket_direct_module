# 分流范围与例外

[返回首页与安装入口](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/README.md) · [查看正式模块](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/sr_routing.module) · [业务分类清单](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/rules/services.json) · [域名证据](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/rules/domain_evidence.json)

## 国内与国际产品


| 产品/业务 | 策略与范围 |
| --- | --- |
| 抖音、头条、西瓜、剪映、番茄小说、懂车帝 | 国内产品专用域名 DIRECT |
| 豆包、豆包输入法 | `doubao.com`、`www.doubao.com` 精确直连；已确认的 API、输入法入口和语音主机直连；不覆盖整个共享父域 |
| 飞书、巨量引擎、火山引擎国内入口 | 已收录国内产品域名 DIRECT |
| TikTok / Lite / Shop | `tiktok.com`、`tiktokv.com`、`tiktokcdn.com` 及锁定 TikTok 产品列表中的 API、视频、资源和 Shop 专用域名 PROXY |
| CapCut 国际版 | `capcut.com`、`capcutcdn-us.com` PROXY |
| Lark 国际版 | `larksuite.com`、`larksuitecdn.com`、`larksuiteimg.com`、`larksuitepkg.com` PROXY；不整包导入混合的 `lark-global` 列表 |
| Coze、TRAE、Dola 国际版 | `coze.com`、`trae.ai`、`traecdn.us`、`dola.com` 和已收录国际专用基础设施 PROXY；`coze.cn`、`trae.cn` 国内入口 DIRECT |
| 微信、QQ、微信输入法 | 已确认国内域名 DIRECT；`wetv.qq.com` 精确 PROXY 优先于 `qq.com` 后缀 DIRECT |
| 淘宝、天猫、支付宝、京东、拼多多 | 已确认国内域名 DIRECT；JD 混合公司列表不整包导入 |
| AliExpress、Alibaba 国际 B2B、Lazada、Alipay+ / HK、Joybuy | 国际产品域名 PROXY；不把阿里海外业务视为国内业务 |
| 百度、B 站、网易、国内社交/音乐/地图/银行/12306 | 已确认国内服务 DIRECT；B 站国际 `bilibili.tv` / `biliintl.com`、网易 `easebar.com`、Webnovel PROXY |
| 小米、华为 | 国内商城/明确国内入口 DIRECT；小米已标明海外的精确主机、Petal、`dbankcloud.ru` PROXY；全球账号、设备同步和共享父域交回原配置 |
| Google / YouTube / Gmail / Drive / Play / Maps / Photos / Translate / Cloud | 锁定 Google 产品规则 PROXY；即使某服务通过大陆 CDN 提供，也不会只凭 CDN 位置改为 DIRECT |
| 海外 AI、社交、开发、购物与流媒体 | 复用锁定的 v2fly 服务列表与已审阅补充；包括 OpenAI/ChatGPT/Codex、Claude、Gemini、Perplexity、Grok、Hugging Face、OpenRouter、Cursor、Windsurf、GitHub、GitLab、Docker、npm、PyPI、X、Meta、Telegram、Discord、WhatsApp、Signal、Netflix、Disney+、Prime Video、Max、Spotify、Amazon、eBay、Temu |

这是已审阅静态覆盖范围，不是这些 APP 所有网络端点的完整保证。业务清单、精确主机、共享平台排除项及有意的交叉规则全部维护在 [rules/services.json](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/rules/services.json)，其他文件不重复维护发布分类。测试样例独立维护，避免仅验证生成器自己的输出。

## 共享域名和暂不分类的场景

2026-10-14 检查公开官网 HTML 后确认：豆包与 Dola 同时引用 `lf-flow-web-cdn.doubao.com`，飞书与 Lark 同时引用 `p1-hera.feishucdn.com`，Coze 国内外同时引用 `lf-c-flwb.bytetos.com`。这些主机交回原配置。因此豆包采用精确根域及已确认国内入口规则，不能再使用整个 `doubao.com` 后缀 DIRECT。JD 与 Joybuy 共享的 `sgm-static.jd.com`、`storage.360buyimg.com` 也不强制分类。

官网引用证据及获取结果保存在 [rules/domain_evidence.json](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/rules/domain_evidence.json)。证据证明页面引用了资源，不能证明 iOS APP 的所有登录、视频、WebSocket 或更新流量；也不会把第三方外链自动加入规则。

Auth0、Statsig、Azure、AWS、CloudFront、Akamai、腾讯/阿里/百度云，以及 Vercel/Netlify/Cloudflare 多租户托管父域不会因为某个已收录 APP 使用它们而整体代理。上游 `full:` 明确指向的服务专用云/CDN主机仍用 `DOMAIN` 精确规则；无法确认专属用途的通用主机排除。

DeepSeek 没有在本次审查证据中确认可独立区分的国际域名，`deepseek.com` 不强制代理。Apple Music 的中国区与国际区共享服务域名，不能仅靠域名判定地区，因此 `music.apple.com` 等交回原配置。TikTok Music 的旧服务/关闭后的残留端点不靠名称猜测新增规则；确认过的 TikTok 产品域名仍代理，其他新发现域名需审阅。

共享业务端点无法通过当前域名规则完整区分，这也是一致性保证的边界。对交回原配置的主机，若目的 IP 被 GeoIP 判为 CN，末尾的 `GEOIP,CN,DIRECT` 仍会命中；否则继续原配置。GEOIP 不是域名归属判断。

