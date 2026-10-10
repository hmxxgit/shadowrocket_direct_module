#!/usr/bin/env python3
"""Build the static module from the reviewed, pinned upstream snapshot."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def build():
    source = ROOT / "upstream/sr_direct_list.module"
    metadata = json.loads((ROOT / "upstream/source.json").read_text())
    assert hashlib.sha256(source.read_bytes()).hexdigest() == metadata["sha256"]
    text = source.read_text(encoding="utf-8")
    assert text.count("[Rule]") == 1
    # Keep every upstream rule, in its original order, without remote dependencies.
    rules = text.split("[Rule]\n", 1)[1].rstrip("\n")
    header = (
        "#!name=中国大陆直连（完整上游版）\n"
        "#!desc=完整继承 GMOogway 直连规则并补充大陆 GeoIP；含上游海外服务域名；仅 DIRECT，无脚本/解密。\n"
        "#!homepage=https://github.com/hmxxgit/shadowrocket_direct_module\n"
        "# Derived from GMOogway/shadowrocket-rules; GPL-3.0 (see LICENSE-GPL-3.0).\n"
        f"# Upstream commit: {metadata['commit']}\n"
        f"# Upstream SHA-256: {metadata['sha256']}\n"
        "# Enable and move this module to the top of the Shadowrocket module list.\n"
        "[Rule]\n"
    )
    extra = "\n\n# Mainland China IP fallback, using Shadowrocket's GeoIP database.\nGEOIP,CN,DIRECT\n"
    (ROOT / "sr_direct_list.module").write_text(header + rules + extra, encoding="utf-8")


if __name__ == "__main__":
    build()
