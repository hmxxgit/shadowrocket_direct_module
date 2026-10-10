# Shadowrocket 中国大陆直连模块（Google 强制代理）

为当前配置补充大陆直连规则，并强制已收录的 Google／YouTube 服务使用 `PROXY`。Google 代理规则排在模块最前面，不再让 Google 下载、视频 CDN、字体、API 或大陆可访问的 Google 服务命中原上游的直连规则。

发布模块共 **112,460 条规则**：844 条 Google `PROXY` 规则、111,615 条保留的上游 `DIRECT` 规则，以及 1 条 `GEOIP,CN,DIRECT`。从原始上游移除了 120 条 Google 相关直连规则，包括 `googlevideo.com` 和 Google Play 的 `xn--ngstr-lra8j.com` 下载直连正则；其余上游规则保持原顺序。

Google 域名来自固定版本的 v2fly/domain-list-community，递归展开 Google、Gemini 及其包含的 YouTube、Android、Google Play、Firebase、Google FCM、Google Trust Services、Blogspot 等列表。包含 `@cn` 和 `@ads` 条目，Google 中国域名、广告、统计、证书服务也走代理。`full:` 域名转换为对应域名及其子域的代理规则；去除已被父域覆盖的重复条目，并补充 Google DNS、reCAPTCHA 和部分大陆服务根域。两条 Google 下载正则由整个域名的代理规则覆盖。

这是固定版本的域名规则覆盖，不会自动识别 Google 将来新增的域名、未收录的第三方服务或无域名信息的连接。这里的“中国大陆直连”是使用场景名称，不是严格的服务器地理白名单；保留的上游仍包含 Apple、部分海外服务、广告和统计域名。

## 导入链接

```text
https://raw.githubusercontent.com/hmxxgit/shadowrocket_direct_module/main/sr_direct_list.module
```

[打开 / 下载模块](https://raw.githubusercontent.com/hmxxgit/shadowrocket_direct_module/main/sr_direct_list.module)

完整静态文件，导入时无需再下载第三方规则集。

## 在 Shadowrocket 中使用

1. 打开 **配置 → 模块 → 右上角 `+`**，粘贴模块链接并下载。已安装旧版本时，更新原模块即可。
2. 启用 **中国大陆直连（Google 强制代理）**。
3. 在模块页面右上角 `···` 中调整顺序，将本模块移到**模块列表最上方**。
4. 首页 **全局路由** 使用 **配置**，选择所需代理节点，重新连接使配置生效。

模块不提供节点，不是节点订阅或完整 `.conf`。Google 使用内置 `PROXY` 策略；其出口由当前配置的 `PROXY` 策略及所选节点决定。本模块的 Google 规则优先于原配置里的 YouTube 等分组规则，未命中本模块的流量继续由原配置决定。

模块规则优先于配置文件规则；多个模块中，上面的模块优先。Google 代理规则在本模块最前面，保留的 `.cn` 通用直连规则在其后，Google 的中国域名也优先代理。禁用或删除模块可撤销它的路由影响。

新增的 `GEOIP,CN,DIRECT` 放在所有域名规则后，没有添加 `no-resolve`，由 Shadowrocket 的 GeoIP 数据库匹配大陆 IP；显式域名规则优先于 GeoIP 推断。

优先级依据：[GMOogway 上游说明](https://github.com/GMOogway/shadowrocket-rules#使用方法)、[Shadowrocket 社区手册](https://github.com/LOWERTOP/Shadowrocket/wiki#规则优先级)。

## 校验范围

| 检查项 | 结果 |
| --- | --- |
| 功能节 | 仅 `[Rule]` |
| Google 规则 | 844 条 `DOMAIN-SUFFIX,…,PROXY`，置于直连规则之前 |
| 上游处理 | 精确移除 120 条 Google 冲突规则，其余逐条、原顺序保留 |
| GeoIP 补充 | 仅 `GEOIP,CN,DIRECT` |
| 脚本、MITM、证书、解密、重写、DNS 修改 | 无 |
| 远程规则集引用、代理节点、上传日志功能 | 无 |

保留的 6 条 `URL-REGEX` 仅用于直连路由匹配，不执行脚本或请求重写。由于保留其他上游广告／统计域名，模块可能优先匹配原配置的广告拦截或其他自定义策略。

校验器检查两份来源的固定哈希、唯一 `[Rule]` 节、允许的规则类型和策略、重复规则、完整输出顺序及上游过滤结果；另检查 34 个代表性 Google／YouTube 地址的代理路由，以及大陆通用直连规则。包含曾被直连正则匹配的视频／下载地址、Google 中国域名、字体、API、Gmail、Drive、证书、Firebase、统计和广告服务。

这些是文件级静态校验，未对本次版本进行 Shadowrocket 客户端播放测速。安装后可在连接记录中核对 `googlevideo.com`、`youtube.com` 等是否命中 `PROXY`，大陆网站是否继续命中 `DIRECT`。

## 来源、更新与复现

- 直连规则：[GMOogway/shadowrocket-rules](https://github.com/GMOogway/shadowrocket-rules)，固定提交 `12fb8a1e037502a536f86ec9faf1cdbb2c576a48`。未修改的原始快照与哈希存于 `upstream/`。
- Google 域名：[v2fly/domain-list-community](https://github.com/v2fly/domain-list-community)，固定提交 `c6adacf29cc4fb05e04651fcf03e00989ef9f797`。全部依赖列表、许可及每文件哈希存于 `upstream/google/`。
- 快照及修改日期：2026-10-10（Asia/Shanghai）。

本模块不会自动追随上游。更新时需审查新快照，重新构建、校验并发布；Shadowrocket 内更新模块才能获取新规则。导入链接保持不变，可将 `main` 替换为提交 SHA 固定版本。

使用 Python 3 标准库离线复现：

```sh
python3 scripts/build.py
python3 scripts/validate.py
```

构建脚本先生成 Google 代理规则，再过滤直连快照中的冲突规则，最后添加大陆 GeoIP。重新构建不会恢复本次移除的 Google 直连规则。

## 许可

直连快照及派生模块采用 GPL-3.0，见 `LICENSE-GPL-3.0`。Google 域名快照采用 MIT，见 `upstream/google/LICENSE`。自编脚本及文档采用仓库原有 MIT 许可，见 `LICENSE`。来源和修改说明见 `NOTICE.md`。
