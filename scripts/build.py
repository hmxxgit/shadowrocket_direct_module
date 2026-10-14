#!/usr/bin/env python3
"""Offline deterministic build. Upstream changes never update release implicitly."""
import hashlib
import json
from collections import Counter
from policy import ROOT, MODULE, generate


def render(rules):
    return (
        '#!name=大陆直连与海外服务代理\n'
        '#!desc=国内已确认业务 DIRECT；海外已确认业务 PROXY；未匹配流量沿用原配置。无节点、脚本、重写或 HTTPS 解密。\n'
        '#!url=https://raw.githubusercontent.com/hmxxgit/shadowrocket_direct_module/main/sr_routing.module\n'
        '#!homepage=https://github.com/hmxxgit/shadowrocket_direct_module\n'
        '# Derived from pinned GMOogway, v2fly and Johnshall snapshots; see NOTICE.md.\n'
        '# Product policy: rules/services.json; license GPL-3.0.\n'
        '# PROXY exceptions precede DIRECT; GEOIP,CN is the last fallback; no FINAL.\n'
        '[Rule]\n' + '\n'.join(rule.line() for rule in rules) + '\n')


def build():
    rules, report = generate()
    text = render(rules)
    MODULE.write_text(text)
    report.update({'baseline':json.loads((ROOT / 'rules/baseline.json').read_text()),
                   'rules':len(rules),'bytes':len(text.encode()),
                   'domains':len({r.value for r in rules if r.kind in {'DOMAIN','DOMAIN-SUFFIX'}}),
                   'counts':dict(Counter(r.policy for r in rules)),
                   'sha256':hashlib.sha256(text.encode()).hexdigest()})
    path = ROOT / 'reports/build.json'
    path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(f'Built {len(rules):,} rules / {report["bytes"]:,} bytes; {report["counts"]}')
    print('Optimization:',report['optimization'],'; unresolved conflicts:',report['unresolved_conflicts'])


if __name__ == '__main__':
    build()
