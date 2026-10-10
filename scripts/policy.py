"""Pinned service domain coverage with priority direct exceptions."""
import csv
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "sr_routing.module"
SERVICES = ROOT / "upstream/proxy-services"
# Supplemental service roots and shared login/experimentation/WebSocket infrastructure.
EXTRA_DOMAINS = {"dns.google", "recaptcha.net", "recaptcha-cn.net", "googleflights.net",
                 "googleapis-cn.com", "googleapps-cn.com", "gstatic-cn.com",
                 "auth0.com", "openaimerge.com", "oaistatsig.com", "featuregates.org",
                 "statsigapi.net", "statsig.com", "webpubsub.azure.com"}


def ime_direct_rules():
    data = json.loads((ROOT / "rules/ime_direct.json").read_text())
    domains = data["domains"]
    if len(domains) != len(set(domains)):
        raise ValueError("Duplicate IME direct domains")
    for domain in domains:
        if not re.fullmatch(r"[a-z0-9-]+(?:\.[a-z0-9-]+)+", domain):
            raise ValueError(f"Invalid IME direct domain: {domain}")
    return [f"DOMAIN-SUFFIX,{domain},DIRECT" for domain in domains]


def snapshot_domains(directory, extra=()):
    metadata = json.loads((directory / "source.json").read_text())
    for name, info in metadata["files"].items():
        actual = hashlib.sha256((directory / name).read_bytes()).hexdigest()
        if actual != info["sha256"]:
            raise ValueError(f"Service snapshot SHA-256 mismatch: {name}")
    domains = set(extra)
    visited = set()

    def expand(name):
        if name in visited:
            return
        visited.add(name)
        for raw in (directory / name).read_text().splitlines():
            line = raw.split("#", 1)[0].strip()
            if not line:
                continue
            token = line.split()[0]  # Include all attributes, including @cn and @ads.
            if token.startswith("include:"):
                expand(token.split(":", 1)[1])
            elif token.startswith("regexp:"):
                # Reviewed dynamic hosts are covered by whole-domain suffix rules.
                if not any(d in token.replace("\\", "") for d in
                           ("googlevideo.com", "xn--ngstr-lra8j.com", "webpubsub.azure.com")):
                    raise ValueError(f"Unreviewed service regex: {token}")
            elif token.startswith("full:"):
                domains.add(token.split(":", 1)[1].lower())
            elif ":" in token:
                raise ValueError(f"Unreviewed service rule: {token}")
            else:
                domains.add(token.lower())

    for name in metadata["roots"]:
        expand(name)
    # Remove redundant child domains; a suffix rule covers the parent and descendants.
    return sorted(d for d in domains if not any(
        ".".join(d.split(".")[i:]) in domains for i in range(1, len(d.split(".")))))


def priority_direct_rules():
    domains = {line.split(",")[1] for line in ime_direct_rules()}
    domains.update(snapshot_domains(ROOT / "upstream/bytedance"))
    domains = sorted(d for d in domains if not any(
        ".".join(d.split(".")[i:]) in domains for i in range(1, len(d.split(".")))))
    return [f"DOMAIN-SUFFIX,{domain},DIRECT" for domain in domains]


def proxy_domains():
    direct = {line.split(",")[1] for line in priority_direct_rules()}
    return [domain for domain in snapshot_domains(SERVICES, EXTRA_DOMAINS)
            if not any(".".join(domain.split(".")[i:]) in direct
                       for i in range(len(domain.split("."))))]


def conflicts_with_proxy(line, domains):
    kind, value, _ = next(csv.reader([line], strict=True))
    if kind in {"DOMAIN", "DOMAIN-SUFFIX"}:
        value = value.lower()
        labels = value.split(".")
        if any(".".join(labels[i:]) in domains for i in range(len(labels))):
            return True
        return False  # Keep broad mainland suffixes such as .cn; service rules precede them.
    if kind == "URL-REGEX":
        literal = value.replace("\\.", ".")
        return any(d in literal for d in ("googlevideo.com", "xn--ngstr-lra8j.com"))
    return False


def source_rules():
    source = ROOT / "upstream/sr_direct_list.module"
    metadata = json.loads((ROOT / "upstream/source.json").read_text())
    if hashlib.sha256(source.read_bytes()).hexdigest() != metadata["sha256"]:
        raise ValueError("Upstream SHA-256 mismatch")
    return [line for line in source.read_text().split("[Rule]\n", 1)[1].splitlines()
            if line and not line.startswith("#")]


def module_rules():
    domains = set(proxy_domains())
    upstream = source_rules()
    removed, direct = [], []
    for line in upstream:
        (removed if conflicts_with_proxy(line, domains) else direct).append(line)
    proxy = [f"DOMAIN-SUFFIX,{domain},PROXY" for domain in sorted(domains)]
    return proxy, direct, removed
