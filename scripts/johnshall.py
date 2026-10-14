"""Pinned Johnshall evidence; only reviewed domains and local IPs are published."""
import json
from policy import ROOT, legacy_rules


def johnshall_direct_rules():
    count = json.loads((ROOT/'upstream/source.json').read_text())['rule_count']
    return legacy_rules()[count:]
