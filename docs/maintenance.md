# 构建与维护

[返回首页与安装入口](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/README.md) · [分流范围与例外](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/docs/routing-guide.md) · [运行记录](https://github.com/hmxxgit/shadowrocket_direct_module/actions) · [来源与许可](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/NOTICE.md)

## 维护文件直达

| 文件 | 用途 |
| --- | --- |
| [构建脚本](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/scripts/build.py) · [验证脚本](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/scripts/validate.py) · [审计脚本](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/scripts/audit.py) | 离线生成、验证与审计 |
| [上游检查脚本](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/scripts/check_upstream.py) · [网页证据采集](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/scripts/collect_evidence.py) | 检查上游变化、刷新证据 |
| [业务分类](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/rules/services.json) · [测试用例](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/rules/routing_cases.json) · [审计基线](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/rules/baseline.json) | 审阅分类、独立测试与差异比较 |
| [发布验证工作流](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/.github/workflows/validate.yml) · [上游检查工作流](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/.github/workflows/upstream-review.yml) | 查看自动化维护配置 |
| [构建报告](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/reports/build.json) · [审计报告](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/reports/audit.json) · [完整逐条清单](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/reports/source-audit.tsv.gz) | 查看统计、SHA-256、差异与逐条记录 |
| [GMOogway 来源](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/upstream/source.json) · [Johnshall 来源](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/upstream/johnshall/source.json) | 固定版本与文件哈希 |
| [海外服务来源](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/upstream/proxy-services/source.json) · [字节产品来源](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/upstream/bytedance/source.json) · [国内服务来源](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/upstream/domestic/source.json) | v2fly 锁定快照与依赖 |

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

[reports/build.json](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/reports/build.json) 包含转换细节、去重统计和模块 SHA-256；[reports/audit.json](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/reports/audit.json) 记录发布差异与全源审计摘要；[reports/source-audit.tsv.gz](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/reports/source-audit.tsv.gz) 是完整压缩逐条审计清单。保留快照和审计证据不代表继续认可旧分类。

2026-10-14 本轮结果：114,057 → **2,760 条**，3,843,865 → **96,649 字节**；其中 PROXY 2,346 条，DIRECT 414 条（含 7 条局域网/私有地址与 1 条 GeoIP）。新增 569 个域名，141 个已有域名的类型或策略改变，111,774 个旧域名因范围冗余或归属未经确认而不再发布。数量下降的主体是停止强制分类未知业务，不是单纯去重；上游原始规则没有删除。

基线存在 16 组域名范围交叉；当前仅有 1 组已声明的 WeTV/QQ 精确例外，未解决冲突为 0。生成候选中去除 305 个完全重复条目和 372 个同策略覆盖条目。

## 自动化维护与验证边界

GitHub Actions 每次 main 推送或 PR 执行离线构建、全部验证、审计及发布可复现检查。每周一北京时间 10:17 和手工触发的上游检查会验证远端固定提交的 SHA-256、比较最新提交对应文件、上传差异报告并提示人工审核；只有读取权限，不修改或推送正式模块。Actions 本身固定提交，不依赖浮动标签。GitHub 的计划任务可能延迟。

上游变化需维护者审查域名归属、属性变化、共享父域和新增依赖，更新 source.json、快照及唯一产品清单，重新构建/验证/审计，再发布。不能仅更新哈希后让新规则自动进入正式版。手动刷新公开网页证据：`python3 scripts/collect_evidence.py`，它只更新证据文件，不改变分类。

当前 **688 个首条命中静态模拟用例通过**，另有精确域名、include/属性、正则遗漏、循环/未锁定引用、SHA-256 损坏、优化顺序等回归测试。测试包含主域、典型子域、API/CDN、共享基础设施反向用例、私有 IPv4/IPv6，以及目的 IP 被判 CN 时明确海外规则仍优先代理。

**实机待验证：** iOS Shadowrocket 多模块合并顺序、DNS/CNAME/IPv6、QUIC、登录/验证码/支付、TikTok/Lite/Shop 视频与上传、CapCut 资源下载、Lark 通话、AI 语音/WebSocket、后台更新以及流媒体地区解锁。没有在真实 iPhone 上测试，不将静态模拟表述为实机验证。

来源与许可见 [NOTICE.md](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/NOTICE.md)。
