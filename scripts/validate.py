#!/usr/bin/env python3
"""Check the published module's routing-only scope and snapshot integrity."""
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

from policy import MODULE, module_rules

ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_rules(path, allowed, policies=("DIRECT",)):
    rules = []
    sections = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line or line.startswith("#"):
            continue
        if line.startswith("["):
            sections.append(line)
            require(line == "[Rule]", f"{path.name}:{number}: unexpected section")
            continue
        require(sections == ["[Rule]"], f"{path.name}:{number}: rule outside [Rule]")
        fields = next(csv.reader([line], strict=True))
        require(len(fields) == 3, f"{path.name}:{number}: invalid field count")
        kind, value, policy = fields
        require(kind in allowed and policy in policies, f"{path.name}:{number}: unsafe rule type/policy")
        require(policy != "PROXY" or kind == "DOMAIN-SUFFIX", f"{path.name}:{number}: unexpected proxy rule")
        require(value and not any(ord(c) < 32 for c in value), f"{path.name}:{number}: invalid value")
        if kind in {"DOMAIN", "DOMAIN-SUFFIX"}:
            require(re.fullmatch(r"[A-Za-z0-9_.-]+", value) is not None, f"{path.name}:{number}: invalid domain")
            require("*" not in value and "/" not in value, f"{path.name}:{number}: broad domain")
        elif kind == "URL-REGEX":
            require(value.startswith("^https?"), f"{path.name}:{number}: unexpected regex")
            re.compile(value)
        else:
            require(value == "CN", f"{path.name}:{number}: non-mainland GeoIP")
        rules.append(line)
    require(sections == ["[Rule]"], "Expected exactly one [Rule] section")
    require(len(rules) == len(set(rules)), f"{path.name}: duplicate rules")
    return rules


def verify_service_routing(rules):
    """Check named services, CDN/API hosts and former direct video regexes independently."""
    samples = [
        "www.google.com", "www.google.com.hk", "www.google.cn", "gemini.google.com",
        "www.youtube.com", "youtubei.googleapis.com", "i.ytimg.com", "lh3.ggpht.com",
        "r1---sn-ni5abcde.googlevideo.com", "r1.sn-2x3abcde.googlevideo.com",
        "r1---sn-j5oabcde.xn--ngstr-lra8j.com", "redirector.c.play.google.com",
        "dl.google.com", "fonts.gstatic.com", "update.googleapis.com", "mail.google.com",
        "accounts.google.com", "drive.google.com", "lh3.googleusercontent.com",
        "www.google.co.jp", "mtalk.google.com", "dns.google", "ocsp.pki.goog",
        "www.recaptcha.net", "www.recaptcha-cn.net", "www.gstatic-cn.com",
        "www.googleapis-cn.com", "beacons.gvt2.com", "googleadservices.com",
        "www.googletagmanager-cn.com", "google-analytics.com", "doubleclick.net",
        "firebase-settings.crashlytics.com", "example.blogspot.com",
        "x.com", "api.x.com", "api.twitter.com", "pbs.twimg.com", "t.co",
        "github.com", "api.github.com", "raw.githubusercontent.com",
        "objects.githubusercontent.com", "githubassets.com", "ghcr.io",
        "github-cloud.s3.amazonaws.com", "copilot-proxy.githubusercontent.com",
        "chatgpt.com", "chat.com", "api.openai.com", "codex.openai.com",
        "ab.chatgpt.com", "cdn.oaistatic.com", "files.oaiusercontent.com",
        "oaistatsig.com", "openaimerge.com", "sora.com",
        "chatgpt-async-webps-prod-example-123.webpubsub.azure.com",
        "openaiapi-site.azureedge.net", "auth.openai.com", "auth0.com",
        "claude.ai", "api.anthropic.com", "cursor.com", "windsurf.com",
        "api.perplexity.ai", "huggingface.co", "cdn-lfs.hf.co", "openrouter.ai",
        "gitlab.com", "registry.npmjs.org", "pypi.org", "files.pythonhosted.org",
        "registry-1.docker.io", "discord.com", "telegram.org", "reddit.com",
        "instagram.com", "facebook.com", "linkedin.com",
    ]
    parsed = [next(csv.reader([line], strict=True)) for line in rules]
    for host in samples:
        matches = []
        for kind, value, policy in parsed:
            match = ((kind == "DOMAIN" and host == value) or
                     (kind == "DOMAIN-SUFFIX" and (host == value or host.endswith("." + value))) or
                     (kind == "URL-REGEX" and re.search(value, "https://" + host + "/videoplayback")))
            if match:
                matches.append((kind, value, policy))
        require(matches and matches[0][2] == "PROXY", f"Overseas service does not route to PROXY: {host}")
        require(not any(policy == "DIRECT" and (kind, value) != ("DOMAIN-SUFFIX", "cn")
                        for kind, value, policy in matches),
                f"Conflicting Overseas-service DIRECT rule remains: {host}")
    # Important mainland services retain their original direct domain routing.
    for host in ["qq.com", "taobao.com", "baidu.com", "cn"]:
        require(any(kind == "DOMAIN-SUFFIX" and value == host and policy == "DIRECT"
                    for kind, value, policy in parsed), f"Mainland direct rule missing: {host}")
    print(f"PASS: {len(samples)} Overseas service/video routing cases and mainland direct rules.")


def validate():
    source = ROOT / "upstream/sr_direct_list.module"
    metadata = json.loads((ROOT / "upstream/source.json").read_text())
    require(hashlib.sha256(source.read_bytes()).hexdigest() == metadata["sha256"], "Upstream SHA-256 mismatch")
    allowed = {"DOMAIN", "DOMAIN-SUFFIX", "URL-REGEX"}
    upstream = read_rules(source, allowed)
    require(len(upstream) == metadata["rule_count"], "Upstream count mismatch")
    result = read_rules(MODULE, allowed | {"GEOIP"}, ("DIRECT", "PROXY"))
    proxy, direct, removed = module_rules()
    require(result == proxy + direct + ["GEOIP,CN,DIRECT"], "Incorrect Service priority or unexpected rules")
    require(len(direct) + len(removed) == len(upstream), "Upstream partition mismatch")
    verify_service_routing(result)
    require((ROOT / "LICENSE-GPL-3.0").is_file(), "Missing upstream license")
    require((ROOT / "NOTICE.md").is_file(), "Missing attribution")
    counts = Counter(line.split(",", 1)[0] for line in result)
    print(f"PASS: {len(result):,} rules; {len(proxy)} Overseas-service PROXY rules; {len(removed)} DIRECT conflicts removed; only [Rule].")
    print(dict(counts))
    print("Module SHA-256:", hashlib.sha256(MODULE.read_bytes()).hexdigest())


if __name__ == "__main__":
    validate()
