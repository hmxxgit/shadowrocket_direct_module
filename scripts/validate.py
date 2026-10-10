#!/usr/bin/env python3
"""Check the published module's routing-only scope and snapshot integrity."""
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

from policy import MODULE, module_rules, priority_direct_rules

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


def verify_ime_routing(rules):
    # Independent representative endpoints from the official apps and websites.
    hosts = [
        "shurufa.doubao.com", "api-normal.doubao.com", "ime.doubao.com",
        "static.doubaocdn.com", "wx.qpic.cn",
        "frontier-audio-ime-quic.doubao.com", "frontier-audio-ime-ws.doubao.com",
        "frontier-ime.doubao.com", "ime.oceancloudapi.com", "ime-gw.oceancloudapi.com",
        "speech.bytedance.com", "imagex.bytedanceapi.com", "effect.snssdk.com",
        "is.snssdk.com", "crash.snssdk.com", "pc-mon.zijieapi.com",
        "tnc0-bjlgy.zijieapi.com", "log-klink.zijieapi.com", "rtlog.zijieapi.com",
        "p0-ime-clip-private.byteimg.com", "p0-ime-clip2-private.byteimg.com",
        "lf-speechfe-cdn.bytespeech.com", "lf3-static.bytednsdoc.com",
        "z.weixin.qq.com", "wetype.weixin.qq.com", "download.z.weixin.qq.com",
        "wxkb.weixin.qq.com", "wetype.wxqcloud.qq.com",
        "wxkeyboardcms-1258476243.file.myqcloud.com",
        "download.weread.qq.com", "cdn.weread.qq.com", "oss.weread.qq.com",
    ]
    parsed = [next(csv.reader([line], strict=True)) for line in rules]
    for host in hosts:
        matches = [(kind, value, policy) for kind, value, policy in parsed
                   if (kind == "DOMAIN" and host == value) or
                   (kind == "DOMAIN-SUFFIX" and (host == value or host.endswith("." + value)))]
        require(matches and matches[0][2] == "DIRECT", f"IME does not route DIRECT: {host}")
        require(not any(policy == "PROXY" for _, _, policy in matches),
                f"Conflicting IME proxy rule remains: {host}")
    print(f"PASS: {len(hosts)} IME API/voice/sync/download/monitoring routing cases.")


def verify_bytedance_routing(rules):
    # Check every collected direct domain and descendants against all proxy suffixes.
    direct_domains = {line.split(",")[1] for line in priority_direct_rules()}
    proxy_suffixes = {value for kind, value, policy in
                      (next(csv.reader([line], strict=True)) for line in rules)
                      if kind == "DOMAIN-SUFFIX" and policy == "PROXY"}
    for domain in direct_domains:
        labels = domain.split(".")
        require(not any(".".join(labels[i:]) in proxy_suffixes for i in range(len(labels))),
                f"Priority direct domain still matches a proxy suffix: {domain}")
        require(not any(proxy.endswith("." + domain) for proxy in proxy_suffixes),
                f"Child domain still configured as proxy: {domain}")
    samples = [
        "www.douyin.com", "www.doubao.com", "api.doubao.com", "api.douyin.com",
        "www.iesdouyin.com", "p3.douyinpic.com", "v3.douyinvod.com",
        "www.toutiao.com", "www.ixigua.com", "www.jianying.com", "www.jimeng.com",
        "www.feishu.cn", "www.larksuite.com", "www.volcengine.com", "ark.volces.com",
        "speech.bytedance.com", "imagex.bytedanceapi.com", "log.zijieapi.com",
        "api.snssdk.com", "p3.pstatp.com", "lf.bytefcdn.com", "s.byteoversea.com",
        "www.fanqienovel.com", "www.juejin.cn", "www.dongchedi.com",
        "www.coze.com", "www.trae.ai", "www.dola.com", "www.marscode.com",
        "www.tiktok.com", "api.tiktokv.com", "www.capcut.com",
        "bytedance.map.fastly.net", "tiktokcdn.com.akamaized.net",
    ]
    parsed = [next(csv.reader([line], strict=True)) for line in rules]
    for host in samples:
        policy = next((policy for kind, value, policy in parsed
                       if (kind == "DOMAIN" and host == value) or
                       (kind == "DOMAIN-SUFFIX" and (host == value or host.endswith("." + value)))), None)
        require(policy == "DIRECT", f"ByteDance service does not route DIRECT: {host}")
    print(f"PASS: {len(samples)} ByteDance service cases; all {len(direct_domains)} priority direct suffixes conflict-free.")


def validate():
    source = ROOT / "upstream/sr_direct_list.module"
    metadata = json.loads((ROOT / "upstream/source.json").read_text())
    require(hashlib.sha256(source.read_bytes()).hexdigest() == metadata["sha256"], "Upstream SHA-256 mismatch")
    allowed = {"DOMAIN", "DOMAIN-SUFFIX", "URL-REGEX"}
    upstream = read_rules(source, allowed)
    require(len(upstream) == metadata["rule_count"], "Upstream count mismatch")
    result = read_rules(MODULE, allowed | {"GEOIP"}, ("DIRECT", "PROXY"))
    proxy, direct, removed = module_rules()
    priority = priority_direct_rules()
    priority_set = set(priority)
    direct = [rule for rule in direct if rule not in priority_set]
    require(result == priority + proxy + direct + ["GEOIP,CN,DIRECT"], "Incorrect Service priority or unexpected rules")
    require(len(direct) + len(removed) + len(priority_set.intersection(upstream)) == len(upstream), "Upstream partition mismatch")
    verify_service_routing(result)
    verify_ime_routing(result)
    verify_bytedance_routing(result)
    require((ROOT / "LICENSE-GPL-3.0").is_file(), "Missing upstream license")
    require((ROOT / "NOTICE.md").is_file(), "Missing attribution")
    counts = Counter(line.split(",", 1)[0] for line in result)
    print(f"PASS: {len(result):,} rules; {len(proxy)} Overseas-service PROXY rules; {len(removed)} DIRECT conflicts removed; only [Rule].")
    print(dict(counts))
    print("Module SHA-256:", hashlib.sha256(MODULE.read_bytes()).hexdigest())


if __name__ == "__main__":
    validate()
