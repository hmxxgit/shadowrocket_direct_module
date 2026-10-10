# Shadowrocket 中国大陆直连模块

通过一个 HTTPS 链接导入 Shadowrocket，为正在使用的配置补充优先匹配的直连规则。

按项目需求，本模块**完整继承 GMOogway 的直连模块**，保留全部 111,735 条上游规则，再增加 1 条 `GEOIP,CN,DIRECT`，共 **111,736 条规则**。所有规则策略均为 `DIRECT`。

这里的“中国大陆直连”是使用场景名称，**不是严格的服务器地理白名单**：上游包含 Apple、部分海外下载服务、广告和统计域名，完整继承版本也保留了这些条目。这些域名命中时同样直连。域名、CDN 地址和 IP 归属可能变化。

## 导入链接

复制以下链接：

```text
https://raw.githubusercontent.com/hmxxgit/shadowrocket_direct_module/main/sr_direct_list.module
```

[打开 / 下载模块](https://raw.githubusercontent.com/hmxxgit/shadowrocket_direct_module/main/sr_direct_list.module)

使用 HTTPS 防止下载内容在传输中被篡改。模块是一个完整的静态文本文件，导入时无需另外下载第三方规则集。访问 GitHub Raw 如有困难，可使用现有可用网络或代理下载。

## 在 Shadowrocket 中使用

1. 打开 **配置 → 模块 → 右上角 `+`**，粘贴上面的模块链接并下载。
2. 启用 **中国大陆直连（完整上游版）**。
3. 在模块页面右上角 `···` 中调整顺序，将本模块移到**模块列表最上方**。
4. 使用你原来的配置，将首页 **全局路由** 设置为 **配置**；重新连接使配置生效。

不要把它当作节点订阅或完整 `.conf` 配置导入。它不提供代理节点，也不设置未命中流量的最终策略；未命中规则的流量继续由原配置决定。

### “规则全部追加在配置文件前面”的实现

Shadowrocket 的模块规则优先于配置文件规则；多个模块中，排在上面的模块优先。启用并置顶本模块，就能让这些域名直连规则在原配置规则之前参与匹配。**这是模块合并后的生效优先级，不会把 11 万条文本实际写进或覆盖原 `.conf` 文件。** 无需给 `[Rule]` 添加 `%APPEND%`。

新增的 `GEOIP,CN,DIRECT` 写在模块域名规则后，利用 Shadowrocket 的 GeoIP 数据库匹配中国大陆 IP，也用于补充未知域名解析后的大陆地址；没有加 `no-resolve`。实际覆盖 IPv4/IPv6 的程度取决于当前数据库。Shadowrocket 自动编译时会把显式规则放在 GeoIP 等推断规则前，因此 GeoIP 补充项不能保证覆盖原配置中的显式域名代理规则。

优先级依据：[上游项目使用说明](https://github.com/GMOogway/shadowrocket-rules#使用方法)、[Shadowrocket 社区手册：规则优先级](https://github.com/LOWERTOP/Shadowrocket/wiki#规则优先级)、[模块](https://github.com/LOWERTOP/Shadowrocket/wiki#模块)。

## 安全审计与使用边界

本次静态审计和校验结果：

| 检查项 | 结果 |
| --- | --- |
| 功能节 | 只有 `[Rule]` |
| 规则策略 | 全部 `DIRECT` |
| 上游规则完整性 | 111,735 条逐条、原顺序保留，无删改、无重复 |
| 新增规则 | 仅 `GEOIP,CN,DIRECT` |
| 脚本、定时任务、远程脚本 | 无 |
| MITM、证书、HTTPS 解密 | 无 |
| Hosts、DNS 配置修改、URL/请求/响应重写 | 无 |
| 第三方规则集引用、代理服务器、上传日志功能 | 无 |

上游的 8 条 `URL-REGEX` 属于路由匹配规则，策略为 `DIRECT`，不是 URL 重写，也不会执行代码。其余为 111,174 条 `DOMAIN-SUFFIX` 和 553 条 `DOMAIN`。

**可确认本次发布文件仅改变路由匹配，没有内置执行代码、解密、篡改请求或收集上传信息的功能。** 这不等于保证所有目标网站安全，也不等于所有域名都在大陆。直连使用当前网络出口，命中流量不会经过代理；HTTPS 网站仍使用自身的 HTTPS 加密。

由于保留上游广告/统计域名且模块置顶，部分原有广告拦截、自定义代理或拒绝规则可能被本模块的直连规则优先匹配。若需要某些例外规则优先，把它们放进另一个模块并置于本模块之上；这会改变对应例外的优先级。禁用或删除本模块即可撤销它对路由的影响。

规则文件约 3.6 MiB，较旧系统或同时加载多个大模块时可能遇到内存限制。安装后请检查实际日志，而不是仅凭模块显示“启用”判断效果。

## 验证是否生效

1. 连接后访问 `www.qq.com`、`www.taobao.com` 等上游覆盖域名，在 **数据 → 代理** 的连接记录中查看命中规则和 `DIRECT` 策略；需要时开启日志记录。
2. 测试一个你确认位于大陆、且未被显式域名规则匹配的 IP，检查是否命中 `GEOIP,CN,DIRECT`。
3. 测试原配置中需要代理的服务，确认未命中本模块时仍按原配置路由；如果命中上游保留的海外服务规则，则会直连，需按上节添加例外。

本仓库已做文件级静态校验和完整性校验；未在真实 iPhone/Shadowrocket 客户端上完成运行测试。客户端版本、其他模块、DNS 和 GeoIP 数据库会影响实际匹配结果。

## 来源、更新与复现

- 参考来源：[GMOogway/shadowrocket-rules](https://github.com/GMOogway/shadowrocket-rules)。
- 固定上游提交：`12fb8a1e037502a536f86ec9faf1cdbb2c576a48`。
- 快照日期：2026-10-10（Asia/Shanghai）。原始快照及 SHA-256 存于 [`upstream/`](upstream/)。
- 本模块**不会自动追随上游变化**；远程链接会获取本仓库 `main` 分支的最新发布内容。需要更新时先审查新快照、记录来源，再构建、验证并发布。Shadowrocket 内需重新下载/更新模块才能取得仓库的新版本。
- 需要固定本次版本时，将链接中的 `main` 替换为本仓库对应的完整提交 SHA。

本地使用 Python 3 标准库即可复现，无需安装依赖，无需联网：

```sh
python3 scripts/build.py
python3 scripts/validate.py
```

校验器检查来源哈希、唯一 `[Rule]` 节、允许的规则类型、全 `DIRECT`、重复规则及上游规则逐条一致性，并输出发布文件 SHA-256。规则更新后应重新核查语义；静态语法检查无法替代客户端实测。

## 许可

上游快照及派生模块采用 **GPL-3.0**，见 [`LICENSE-GPL-3.0`](LICENSE-GPL-3.0)。自编脚本和文档采用仓库原有 MIT 许可，见 [`LICENSE`](LICENSE)。来源和修改说明见 [`NOTICE.md`](NOTICE.md)。
