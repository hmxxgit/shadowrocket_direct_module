# Shadowrocket 分流模块

**已确认的中国大陆业务 DIRECT，已确认的海外业务 PROXY，未匹配流量沿用原配置。** 按产品和实际域名区分国内版、国际版，不按公司总部或 CDN 所在地分类。模块适合在更换 iPhone 后恢复基本一致的域名分流策略，独立于机场、订阅和节点。

## 安装与更新

正式模块地址和文件名保持不变：

```text
https://raw.githubusercontent.com/hmxxgit/shadowrocket_direct_module/main/sr_routing.module
```

1. 在新 iPhone 安装 Shadowrocket。
2. 导入自己的代理节点或机场订阅，选择可用节点。
3. 在 **配置 → 模块 → ＋** 导入上面的地址。
4. 启用「大陆直连与海外服务代理」，停用旧版重复模块，将本模块移到模块列表最上方。
5. 选择 **规则／配置** 路由模式（以当前 Shadowrocket 界面名称为准），重新连接，并用连接日志核对实际命中规则。

更新时重新下载模块。本模块不添加节点、不修改订阅，不含 FINAL、HTTPS 解密、脚本、重写、广告拦截或全局路由设置。未命中本模块的流量由现有配置继续处理。节点仍需要自行选择；分流不保证流媒体地区解锁。

其他模块、原配置规则、域名映射、DNS 与 GeoIP 数据库会影响实际结果。模块置顶是安装建议，不能代替实机检查合并顺序；其他模块的相同域名规则、FINAL 或策略覆盖需要用户自行停用或调整。

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

这是已审阅静态覆盖范围，不是这些 APP 所有网络端点的完整保证。业务清单、精确主机、共享平台排除项及有意的交叉规则全部维护在 [rules/services.json](rules/services.json)，其他文件不重复维护发布分类。测试样例独立维护，避免仅验证生成器自己的输出。

## 共享域名和暂不分类的场景

2026-10-14 检查公开官网 HTML 后确认：豆包与 Dola 同时引用 `lf-flow-web-cdn.doubao.com`，飞书与 Lark 同时引用 `p1-hera.feishucdn.com`，Coze 国内外同时引用 `lf-c-flwb.bytetos.com`。这些主机交回原配置。因此豆包采用精确根域及已确认国内入口规则，不能再使用整个 `doubao.com` 后缀 DIRECT。JD 与 Joybuy 共享的 `sgm-static.jd.com`、`storage.360buyimg.com` 也不强制分类。

官网引用证据及获取结果保存在 [rules/domain_evidence.json](rules/domain_evidence.json)。证据证明页面引用了资源，不能证明 iOS APP 的所有登录、视频、WebSocket 或更新流量；也不会把第三方外链自动加入规则。

Auth0、Statsig、Azure、AWS、CloudFront、Akamai、腾讯/阿里/百度云，以及 Vercel/Netlify/Cloudflare 多租户托管父域不会因为某个已收录 APP 使用它们而整体代理。上游 `full:` 明确指向的服务专用云/CDN主机仍用 `DOMAIN` 精确规则；无法确认专属用途的通用主机排除。

DeepSeek 没有在本次审查证据中确认可独立区分的国际域名，`deepseek.com` 不强制代理。Apple Music 的中国区与国际区共享服务域名，不能仅靠域名判定地区，因此 `music.apple.com` 等交回原配置。TikTok Music 的旧服务/关闭后的残留端点不靠名称猜测新增规则；确认过的 TikTok 产品域名仍代理，其他新发现域名需审阅。

共享业务端点无法通过当前域名规则完整区分，这也是一致性保证的边界。对交回原配置的主机，若目的 IP 被 GeoIP 判为 CN，末尾的 `GEOIP,CN,DIRECT` 仍会命中；否则继续原配置。GEOIP 不是域名归属判断。

## 构建、转换与审核

Python 3.12+，无第三方运行依赖。构建和验证使用本地锁定快照，不联网、不自动升级上游：

```sh
python3 scripts/build.py
python3 scripts/validate.py
python3 scripts/audit.py
```

`audit.py` 需要 Git 中保留基线提交 `0e966387b804cebc797cc030bc0d275814cc7a1a`，浅克隆需补全历史；前两条命令不依赖历史。

- `full:` → `DOMAIN`；普通域名与 `domain:` → `DOMAIN-SUFFIX`；include 递归展开并应用正/负属性选择器。
- include 循环、未锁定依赖、未知类型、损坏哈希都会使构建失败。
- 域名正则与 URL 正则语义不同；本次不做有损转换。转换报告逐条记录遗漏的正则；不会从正则推导整个共享域名的后缀规则。
- ChatGPT 动态 Azure WebSocket 正则、Netflix AWS 动态 API 正则暂不发布，依赖原配置处理；Google Play 正则中的已确认产品域名由独立服务后缀覆盖。
- 旧 GMOogway 的 8 条 URL-REGEX 不发布，其中 Google 视频直连规则会违反本项目海外服务代理原则；其他表达式也不能作为未确认业务的分类依据。模块没有 URL-REGEX，因此不依赖 TLS URL 可见性或解密。
- 三个现有上游及许可证完整保留。GMOogway 和 Johnshall 的域名只有被本项目明确审阅的产品范围覆盖才采用；局域网、回环和私有 IPv4/IPv6 条目保留。企业混合列表中的未标注条目也不自动认为属于国内业务。
- 去除完全重复及同策略父域已经覆盖的规则；跨策略范围必须显式登记并测试。海外域名规则在国内规则前，GeoIP 最后；无 FINAL。

[reports/build.json](reports/build.json) 包含转换细节、去重统计和模块 SHA-256；[reports/audit.json](reports/audit.json) 记录发布差异与全源审计摘要；[reports/source-audit.tsv.gz](reports/source-audit.tsv.gz) 是完整压缩逐条审计清单。保留快照和审计证据不代表继续认可旧分类。

2026-10-14 本轮结果：114,057 → **2,760 条**，3,843,865 → **96,649 字节**；其中 PROXY 2,346 条，DIRECT 414 条（含 7 条局域网/私有地址与 1 条 GeoIP）。新增 569 个域名，141 个已有域名的类型或策略改变，111,774 个旧域名因范围冗余或归属未经确认而不再发布。数量下降的主体是停止强制分类未知业务，不是单纯去重；上游原始规则没有删除。

基线存在 16 组域名范围交叉；当前仅有 1 组已声明的 WeTV/QQ 精确例外，未解决冲突为 0。生成候选中去除 305 个完全重复条目和 372 个同策略覆盖条目。

## 自动化维护与验证边界

GitHub Actions 每次 main 推送或 PR 执行离线构建、全部验证、审计及发布可复现检查。每周一北京时间 10:17 和手工触发的上游检查会验证远端固定提交的 SHA-256、比较最新提交对应文件、上传差异报告并提示人工审核；只有读取权限，不修改或推送正式模块。Actions 本身固定提交，不依赖浮动标签。GitHub 的计划任务可能延迟。

上游变化需维护者审查域名归属、属性变化、共享父域和新增依赖，更新 source.json、快照及唯一产品清单，重新构建/验证/审计，再发布。不能仅更新哈希后让新规则自动进入正式版。手动刷新公开网页证据：`python3 scripts/collect_evidence.py`，它只更新证据文件，不改变分类。

当前 **688 个首条命中静态模拟用例通过**，另有精确域名、include/属性、正则遗漏、循环/未锁定引用、SHA-256 损坏、优化顺序等回归测试。测试包含主域、典型子域、API/CDN、共享基础设施反向用例、私有 IPv4/IPv6，以及目的 IP 被判 CN 时明确海外规则仍优先代理。

**实机待验证：** iOS Shadowrocket 多模块合并顺序、DNS/CNAME/IPv6、QUIC、登录/验证码/支付、TikTok/Lite/Shop 视频与上传、CapCut 资源下载、Lark 通话、AI 语音/WebSocket、后台更新以及流媒体地区解锁。没有在真实 iPhone 上测试，不将静态模拟表述为实机验证。

来源与许可见 [NOTICE.md](NOTICE.md)。
