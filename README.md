# Shadowrocket 分流模块

**已确认的中国大陆业务走直连，已确认的海外业务走代理，其他流量沿用原配置。** 本模块只负责分流，不提供代理节点或机场订阅。

[下载正式模块](https://raw.githubusercontent.com/hmxxgit/shadowrocket_direct_module/main/sr_routing.module) · [查看模块内容](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/sr_routing.module) · [分流范围与例外](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/docs/routing-guide.md) · [文件直达](#文件直达) · [反馈问题](https://github.com/hmxxgit/shadowrocket_direct_module/issues)

## 安装：只需这一个模块

**[sr_routing.module — 下载 / 长按复制链接](https://raw.githubusercontent.com/hmxxgit/shadowrocket_direct_module/main/sr_routing.module)**

需要粘贴地址时，复制下面整行：

```text
https://raw.githubusercontent.com/hmxxgit/shadowrocket_direct_module/main/sr_routing.module
```

1. 在 iPhone 的 Shadowrocket 中导入自己的节点或订阅，选择可用节点。
2. 打开 **配置 → 模块 → ＋**，粘贴上面的链接并下载。
3. 启用 **大陆直连与海外服务代理**，停用重复的旧模块，并将本模块置顶。
4. 选择 **规则／配置** 路由模式（名称以当前界面为准），重新连接。
5. 查看连接日志，确认常用服务命中预期的 `DIRECT` 或 `PROXY`。

**换手机时：** 安装 Shadowrocket → 恢复自己的节点 / 订阅 → 按上述链接导入模块。模块地址保持不变。

## 常用操作

| 想做什么 | 直接操作 / 入口 |
| --- | --- |
| 更新模块 | 在 Shadowrocket 中重新下载同一模块地址，再重新连接；[获取最新版](https://raw.githubusercontent.com/hmxxgit/shadowrocket_direct_module/main/sr_routing.module) |
| 查看具体规则 | [正式模块全文](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/sr_routing.module)；搜索需要检查的域名 |
| 了解哪些服务直连或代理 | [产品与业务范围](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/docs/routing-guide.md#国内与国际产品) |
| 排查共享域名、未分类服务 | [共享域名与例外说明](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/docs/routing-guide.md#共享域名和暂不分类的场景) |
| 确认发布检查情况 | [自动验证记录](https://github.com/hmxxgit/shadowrocket_direct_module/actions/workflows/validate.yml) · [构建报告](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/reports/build.json) |
| 恢复原配置的分流行为 | 停用本模块，重新连接 |
| 报告分流问题 | [提交反馈](https://github.com/hmxxgit/shadowrocket_direct_module/issues/new)，附服务名称、域名、预期策略和实际命中规则；隐去节点凭据和个人信息 |

## 使用前知道这三点

- **不是全量国内 / 海外规则。** 已审阅的国内产品使用 `DIRECT`，海外产品使用 `PROXY`；共享云服务和无法确认的域名通常交回原配置。末尾保留 `GEOIP,CN,DIRECT`，无 `FINAL`。
- **规则会受现有配置影响。** 其他模块、规则顺序、DNS 与 GeoIP 都可能改变最终命中；置顶后仍应检查连接日志。模块不添加节点、HTTPS 解密、脚本、重写或广告拦截，也不保证流媒体地区解锁。
- **静态验证不等于 iPhone 实测。** 多模块合并、DNS / IPv6、登录支付、视频上传、语音通话等仍需实机检查；[查看验证边界](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/docs/maintenance.md#自动化维护与验证边界)。

## 文件直达

| 文件 | 什么时候看 |
| --- | --- |
| [正式分流模块](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/sr_routing.module) · [直接下载](https://raw.githubusercontent.com/hmxxgit/shadowrocket_direct_module/main/sr_routing.module) | 安装、更新、查找最终发布规则 |
| [分流范围与例外](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/docs/routing-guide.md) | 查产品覆盖、共享域名和未分类场景 |
| [业务分类清单](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/rules/services.json) | 查具体域名、策略、来源和排除项 |
| [官网域名证据](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/rules/domain_evidence.json) · [输入法证据](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/rules/ime_direct.json) | 核对域名分类依据 |
| [构建报告](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/reports/build.json) · [审计报告](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/reports/audit.json) · [逐条审计清单](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/reports/source-audit.tsv.gz) | 查转换遗漏、规则统计、哈希和发布差异 |
| [构建与维护指南](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/docs/maintenance.md) | 运行验证、查看脚本 / 工作流 / 上游来源入口 |
| [来源与许可](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/NOTICE.md) · [模块 GPL-3.0](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/LICENSE-GPL-3.0) · [脚本与文档 MIT](https://github.com/hmxxgit/shadowrocket_direct_module/blob/main/LICENSE) | 查使用和分发条款 |

维护者入口：[发布验证](https://github.com/hmxxgit/shadowrocket_direct_module/actions/workflows/validate.yml) · [上游检查](https://github.com/hmxxgit/shadowrocket_direct_module/actions/workflows/upstream-review.yml) · [更新记录](https://github.com/hmxxgit/shadowrocket_direct_module/commits/main/)。上游检查只生成报告，正式规则经人工审核后发布。
