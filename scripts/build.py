#!/usr/bin/env python3
"""Build the static module from reviewed, pinned snapshots."""
import json
from domestic import domestic_direct_rules
from policy import ROOT, MODULE, module_rules, priority_direct_rules


def build():
    metadata = json.loads((ROOT / "upstream/source.json").read_text())
    proxy, direct, removed = module_rules()
    domestic, stats = domestic_direct_rules()
    priority = priority_direct_rules()
    priority_set = set(priority)
    direct = [rule for rule in direct if rule not in priority_set]
    header = (
        "#!name=大陆直连与海外服务代理\n"
        "#!desc=分流模块：字节跳动全系服务及微信输入法优先直连；Google/YouTube/X/GitHub/ChatGPT/Gemini/Codex 等服务优先代理，微信/QQ 等国内应用直连，其余保留上游直连并补充大陆 GeoIP；无脚本/解密。\n"
        "#!url=https://raw.githubusercontent.com/hmxxgit/shadowrocket_direct_module/main/sr_routing.module\n"
        "#!homepage=https://github.com/hmxxgit/shadowrocket_direct_module\n"
        "# Derived from GMOogway/shadowrocket-rules; GPL-3.0 (see LICENSE-GPL-3.0).\n"
        f"# Upstream commit: {metadata['commit']}\n"
        f"# Upstream SHA-256: {metadata['sha256']}\n"
        "# Overseas service domains: pinned v2fly/domain-list-community (MIT); see upstream/proxy-services/.\n"
        "# Enable and move this module to the top of the Shadowrocket module list.\n"
        "[Rule]\n"
        "# ByteDance and WeType services use DIRECT before all other routing rules.\n"
    )
    text = (header + "\n".join(priority) +
            "\n\n# Overseas AI, social and developer services use PROXY.\n" + "\n".join(proxy) +
            "\n\n# Reviewed upstream direct rules, excluding overseas-service conflicts.\n" +
            "\n".join(direct) +
            "\n\n# Additional domestic application domains from pinned v2fly lists.\n" + "\n".join(domestic) +
            "\n\n# Mainland China IP fallback, using Shadowrocket's GeoIP database.\nGEOIP,CN,DIRECT\n")
    print("Domestic import:", stats)
    MODULE.write_text(text, encoding="utf-8")
    print(f"Built: {len(priority)} priority ByteDance/IME DIRECT rules; {len(proxy)} overseas-service PROXY rules; removed {len(removed)} conflicting DIRECT rules.")


if __name__ == "__main__":
    build()
