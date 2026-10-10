#!/usr/bin/env python3
"""Check the published module's routing-only scope and snapshot integrity."""
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_rules(path, allowed):
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
        require(kind in allowed and policy == "DIRECT", f"{path.name}:{number}: unsafe rule type/policy")
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


def validate():
    source = ROOT / "upstream/sr_direct_list.module"
    metadata = json.loads((ROOT / "upstream/source.json").read_text())
    require(hashlib.sha256(source.read_bytes()).hexdigest() == metadata["sha256"], "Upstream SHA-256 mismatch")
    allowed = {"DOMAIN", "DOMAIN-SUFFIX", "URL-REGEX"}
    upstream = read_rules(source, allowed)
    require(len(upstream) == metadata["rule_count"], "Upstream count mismatch")
    result = read_rules(ROOT / "sr_direct_list.module", allowed | {"GEOIP"})
    require(result == upstream + ["GEOIP,CN,DIRECT"], "Upstream changed or unexpected supplemental rules")
    require((ROOT / "LICENSE-GPL-3.0").is_file(), "Missing upstream license")
    require((ROOT / "NOTICE.md").is_file(), "Missing attribution")
    counts = Counter(line.split(",", 1)[0] for line in result)
    print(f"PASS: {len(result):,} rules; all DIRECT; only [Rule]; upstream preserved exactly.")
    print(dict(counts))
    print("Module SHA-256:", hashlib.sha256((ROOT / "sr_direct_list.module").read_bytes()).hexdigest())


if __name__ == "__main__":
    validate()
