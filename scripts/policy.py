"""Pinned Google domain coverage and direct-rule conflict filtering."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOOGLE = ROOT / "upstream/google"
# Google-owned recursive DNS endpoints also need proxy routing.
EXTRA_DOMAINS = {"dns.google", "recaptcha.net", "recaptcha-cn.net", "googleflights.net",
                 "googleapis-cn.com", "googleapps-cn.com", "gstatic-cn.com"}


def google_domains():
    metadata = json.loads((GOOGLE / "source.json").read_text())
    for name, info in metadata["files"].items():
        actual = hashlib.sha256((GOOGLE / name).read_bytes()).hexdigest()
        if actual != info["sha256"]:
            raise ValueError(f"Google snapshot SHA-256 mismatch: {name}")
    domains = set(EXTRA_DOMAINS)
    visited = set()

    def expand(name):
        if name in visited:
            return
        visited.add(name)
        for raw in (GOOGLE / name).read_text().splitlines():
            line = raw.split("#", 1)[0].strip()
            if not line:
                continue
            token = line.split()[0]  # Include all attributes, including @cn and @ads.
            if token.startswith("include:"):
                expand(token.split(":", 1)[1])
            elif token.startswith("regexp:"):
                # Both pinned regexes are already covered by whole-domain suffix rules.
                if not any(d in token.replace("\\", "") for d in
                           ("googlevideo.com", "xn--ngstr-lra8j.com")):
                    raise ValueError(f"Unreviewed Google regex: {token}")
            elif token.startswith("full:"):
                domains.add(token.split(":", 1)[1].lower())
            elif ":" in token:
                raise ValueError(f"Unreviewed Google rule: {token}")
            else:
                domains.add(token.lower())

    for name in metadata["roots"]:
        expand(name)
    # Remove redundant child domains; a suffix rule covers the parent and descendants.
    return sorted(d for d in domains if not any(
        ".".join(d.split(".")[i:]) in domains for i in range(1, len(d.split(".")))))


def conflicts_with_google(line, domains):
    kind, value, _ = next(csv.reader([line], strict=True))
    if kind in {"DOMAIN", "DOMAIN-SUFFIX"}:
        value = value.lower()
        labels = value.split(".")
        if any(".".join(labels[i:]) in domains for i in range(len(labels))):
            return True
        return False  # Keep broad mainland suffixes such as .cn; Google rules precede them.
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
    domains = set(google_domains())
    upstream = source_rules()
    removed, direct = [], []
    for line in upstream:
        (removed if conflicts_with_google(line, domains) else direct).append(line)
    proxy = [f"DOMAIN-SUFFIX,{domain},PROXY" for domain in sorted(domains)]
    return proxy, direct, removed
