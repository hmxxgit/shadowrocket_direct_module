# Shadowrocket 大陆直连与海外服务代理分流模块

这是一个同时包含 `DIRECT` 和 `PROXY` 策略的 Shadowrocket 分流模块：已收录的海外 AI、社交、开发服务优先代理，其余保留经冲突过滤的上游直连规则，并补充大陆 GeoIP 直连。代理规则排在模块最前面，包含 Google／YouTube、X／Twitter、GitHub、ChatGPT／Codex、Gemini 及其 API、静态资源、下载、登录和遥测域名。

发布模块共 **113,405 条规则**：1,794 条海外服务 `PROXY` 规则、111,610 条保留的上游 `DIRECT` 规则，以及 1 条 `GEOIP,CN,DIRECT`。从原始上游移除了 125 条海外服务相关直连规则，包括 `googlevideo.com` 和 Google Play 的 `xn--ngstr-lra8j.com` 下载直连正则；其余上游规则保持原顺序。

代理域名来自固定版本的 v2fly/domain-list-community，展开 Google／Gemini、海外 AI、海外社交媒体类别和常用开发／通讯服务列表。覆盖 YouTube、X／Twitter、GitHub／Copilot、GitLab、ChatGPT／Codex／Sora、Claude、Cursor、Windsurf、Perplexity、Hugging Face、OpenRouter、Discord、Telegram、Reddit、Instagram、Facebook、LinkedIn、Docker、npm、PyPI、Homebrew、Rust、JetBrains、Anaconda、Stack Exchange 等，包含各列表收录的 CDN、API、下载、静态资源及遥测域名。包含 `@cn` 和 `@ads` 条目，Google 中国域名、广告、统计、证书服务也走代理。`full:` 域名转换为对应域名及其子域的代理规则；去除已被父域覆盖的重复条目，并补充 Google DNS、reCAPTCHA、部分大陆服务根域及 OpenAI 相关的认证／实验服务。Google 下载正则由整个域名覆盖；ChatGPT 动态 WebSocket 域名由 `webpubsub.azure.com` 代理规则覆盖，该共享后缀下的其他服务也走代理。

这是固定版本的域名规则覆盖，不会自动识别服务将来新增的域名、未收录的第三方服务或无域名信息的连接。其中的大陆直连规则并非严格的服务器地理白名单；保留的上游仍包含 Apple、部分海外服务、广告和统计域名。

## 新的导入链接

```text
https://raw.githubusercontent.com/hmxxgit/shadowrocket_direct_module/main/sr_routing.module
```

[打开 / 下载模块](https://raw.githubusercontent.com/hmxxgit/shadowrocket_direct_module/main/sr_routing.module)

发布文件已由 `sr_direct_list.module` 更名为 **`sr_routing.module`**。保留 `.module` 扩展名，仍从 Shadowrocket 的模块入口导入。完整静态文件，导入时无需再下载第三方规则集。

## 在 Shadowrocket 中使用

1. 打开 **配置 → 模块 → 右上角 `+`**，粘贴上面的新链接并下载。
2. 启用 **大陆直连与海外服务代理**。
3. 在模块页面右上角 `···` 中调整顺序，将本模块移到**模块列表最上方**。
4. 如果已安装旧版直连模块，停用或删除旧模块，只启用新版，避免两个版本重复参与分流。
5. 首页 **全局路由** 使用 **配置**，选择所需代理节点，重新连接使配置生效。

模块不提供节点，不是节点订阅或完整 `.conf`。这些服务使用内置 `PROXY` 策略；其出口由当前配置的 `PROXY` 策略及所选节点决定。本模块的海外服务规则优先于原配置里的 YouTube 等分组规则，未命中本模块的流量继续由原配置决定。

模块规则优先于配置文件规则；多个模块中，上面的模块优先。海外服务代理规则在本模块最前面，保留的 `.cn` 通用直连规则在其后，Google 的中国域名也优先代理。禁用或删除模块可撤销它的路由影响。

新增的 `GEOIP,CN,DIRECT` 放在所有域名规则后，没有添加 `no-resolve`，由 Shadowrocket 的 GeoIP 数据库匹配大陆 IP；显式域名规则优先于 GeoIP 推断。

优先级依据：[GMOogway 上游说明](https://github.com/GMOogway/shadowrocket-rules#使用方法)、[Shadowrocket 社区手册](https://github.com/LOWERTOP/Shadowrocket/wiki#规则优先级)。

## 校验范围

| 检查项 | 结果 |
| --- | --- |
| 功能节 | 仅 `[Rule]` |
| 海外服务规则 | 1,794 条 `DOMAIN-SUFFIX,…,PROXY`，置于直连规则之前 |
| 上游处理 | 精确移除 125 条海外服务冲突规则，其余逐条、原顺序保留 |
| GeoIP 补充 | 仅 `GEOIP,CN,DIRECT` |
| 脚本、MITM、证书、解密、重写、DNS 修改 | 无 |
| 远程规则集引用、代理节点、上传日志功能 | 无 |

保留的 6 条 `URL-REGEX` 仅用于直连路由匹配，不执行脚本或请求重写。由于保留其他上游广告／统计域名，模块可能优先匹配原配置的广告拦截或其他自定义策略。

校验器检查两份来源的固定哈希、唯一 `[Rule]` 节、允许的规则类型和策略、重复规则、完整输出顺序及上游过滤结果；另检查 80 个代表性服务地址的代理路由，以及大陆通用直连规则。包含曾被直连正则匹配的视频／下载地址、Google 中国域名、字体、API、Gmail、Drive、证书、Firebase、统计和广告服务，以及 X／Twitter、GitHub 下载、ChatGPT／Codex、Claude、Cursor、Copilot、Hugging Face 等。

这些是文件级静态校验，未对本次版本进行 Shadowrocket 客户端播放测速。安装后可在连接记录中核对 `googlevideo.com`、`youtube.com` 等是否命中 `PROXY`，大陆网站是否继续命中 `DIRECT`。

## 来源、更新与复现

- 直连规则：[GMOogway/shadowrocket-rules](https://github.com/GMOogway/shadowrocket-rules)，固定提交 `12fb8a1e037502a536f86ec9faf1cdbb2c576a48`。未修改的原始快照与哈希存于 `upstream/`。
- 海外服务域名：[v2fly/domain-list-community](https://github.com/v2fly/domain-list-community)，固定提交 `c6adacf29cc4fb05e04651fcf03e00989ef9f797`。全部依赖列表、许可及每文件哈希存于 `upstream/proxy-services/`。
- 快照及修改日期：2026-10-10（Asia/Shanghai）。

本模块不会自动追随上游。更新时需审查新快照，重新构建、校验并发布；Shadowrocket 内更新模块才能获取新规则。当前发布入口为 `sr_routing.module`；旧文件名已停止发布，请使用上面的新链接。可将 `main` 替换为提交 SHA 固定版本。

使用 Python 3 标准库离线复现：

```sh
python3 scripts/build.py
python3 scripts/validate.py
```

构建脚本生成 `sr_routing.module`：先生成海外服务代理规则，再过滤直连快照中的冲突规则，最后添加大陆 GeoIP。重新构建不会恢复本次移除的海外服务直连规则。

## 许可

直连快照及派生模块采用 GPL-3.0，见 `LICENSE-GPL-3.0`。海外服务域名快照采用 MIT，见 `upstream/proxy-services/LICENSE`。自编脚本及文档采用仓库原有 MIT 许可，见 `LICENSE`。来源和修改说明见 `NOTICE.md`。
