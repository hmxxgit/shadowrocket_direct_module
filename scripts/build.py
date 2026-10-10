#!/usr/bin/env python3
"""Build the static module from reviewed, pinned snapshots."""
import json
from policy import ROOT, module_rules


def build():
    metadata = json.loads((ROOT / "upstream/source.json").read_text())
    proxy, direct, removed = module_rules()
    header = (
        "#!name=中国大陆直连（海外服务强制代理）\n"
        "#!desc=Google/YouTube/X/GitHub/ChatGPT/Codex 等海外服务优先 PROXY；移除相关上游直连规则，保留其余直连规则并补充大陆 GeoIP；无脚本/解密。\n"
        "#!homepage=https://github.com/hmxxgit/shadowrocket_direct_module\n"
        "# Derived from GMOogway/shadowrocket-rules; GPL-3.0 (see LICENSE-GPL-3.0).\n"
        f"# Upstream commit: {metadata['commit']}\n"
        f"# Upstream SHA-256: {metadata['sha256']}\n"
        "# Overseas service domains: pinned v2fly/domain-list-community (MIT); see upstream/proxy-services/.\n"
        "# Enable and move this module to the top of the Shadowrocket module list.\n"
        "[Rule]\n"
        "# Overseas AI, social and developer services use PROXY, including related CDN/API domains.\n"
    )
    text = (header + "\n".join(proxy) +
            "\n\n# Reviewed upstream direct rules, excluding overseas-service conflicts.\n" +
            "\n".join(direct) +
            "\n\n# Mainland China IP fallback, using Shadowrocket's GeoIP database.\nGEOIP,CN,DIRECT\n")
    (ROOT / "sr_direct_list.module").write_text(text, encoding="utf-8")
    print(f"Built: {len(proxy)} overseas-service PROXY rules; removed {len(removed)} conflicting DIRECT rules.")


if __name__ == "__main__":
    build()
