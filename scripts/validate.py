#!/usr/bin/env python3
"""Static first-match simulator and independent policy/conversion regressions.

Real Shadowrocket module merge order, DNS, GeoIP contents, QUIC and URL-REGEX on
TLS are device-dependent. Passing this suite is not an iOS runtime verification.
"""
import csv
import hashlib
import ipaddress
import json
import re
import tempfile
from collections import Counter
from pathlib import Path
from build import render
from policy import ROOT, MODULE, Rule, DOMAIN, conflict_pairs, generate, snapshot_domains, optimize, verify_snapshots, parse_legacy_rule, legacy_rules


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_rules(path):
    result, sections = [], []
    for number, line in enumerate(path.read_text().splitlines(), 1):
        if not line or line.startswith('#'):
            continue
        if line.startswith('['):
            sections.append(line)
            require(sections == ['[Rule]'], f'Unexpected section: {number}')
            continue
        require(sections == ['[Rule]'], f'Rule outside section: {number}')
        fields = next(csv.reader([line], strict=True))
        require(len(fields) == 3, f'Invalid field count: {number}')
        rule = Rule(*fields)
        require(rule.policy in {'DIRECT','PROXY'}, f'Unsafe policy: {rule}')
        require(rule.kind in {'DOMAIN','DOMAIN-SUFFIX','IP-CIDR','IP-CIDR6','GEOIP'}, f'Unsafe rule: {rule}')
        if rule.kind.startswith('DOMAIN'):
            require(DOMAIN.fullmatch(rule.value), f'Invalid domain: {rule}')
        elif rule.kind.startswith('IP-CIDR'):
            net = ipaddress.ip_network(rule.value, strict=True)
            require(net.version == (6 if rule.kind == 'IP-CIDR6' else 4), f'IP kind: {rule}')
            require(rule.policy == 'DIRECT' and (net.is_private or net.is_link_local or net.is_loopback), f'Public IP rule: {rule}')
        else:
            require(rule.value == 'CN' and rule.policy == 'DIRECT', f'Invalid GEOIP: {rule}')
        result.append(rule)
    require(sections == ['[Rule]'], 'Missing [Rule]')
    require(len(result) == len(set(result)), 'Duplicate rules')
    require(result[-1] == Rule('GEOIP','CN','DIRECT'), 'GEOIP must be the last rule')
    return result


def route(rules, host='', address=None, geoip_cn=False, url=None):
    """First matching rule wins; unknown is delegated to the existing config.

    geoip_cn is a mocked classification of the destination address, not a guess
    from domain suffix. It intentionally remains independent of the hostname.
    """
    host = host.lower().rstrip('.')
    ip = ipaddress.ip_address(address) if address else None
    for rule in rules:
        kind, value, policy = rule.kind, rule.value, rule.policy
        match = ((kind == 'DOMAIN' and host == value) or
                 (kind == 'DOMAIN-SUFFIX' and (host == value or host.endswith('.'+value))) or
                 (kind == 'URL-REGEX' and url is not None and re.search(value,url)) or
                 (kind == 'GEOIP' and value == 'CN' and geoip_cn))
        if kind in {'IP-CIDR','IP-CIDR6'} and ip:
            net = ipaddress.ip_network(value)
            match = ip.version == net.version and ip in net
        if match:
            return policy
    return 'ORIGINAL'


def conversion_tests():
    require(parse_legacy_rule('DOMAIN-SUFFIX, qq.com, Direct') == Rule('DOMAIN-SUFFIX','qq.com','DIRECT'), 'Legacy policy case/whitespace')
    require(len(legacy_rules()) > 112000, 'Legacy DIRECT import unexpectedly truncated')
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp)
        (path/'root').write_text('full:exact.example @cn\nsuffix.example @cn\nregexp:^api[0-9]+\\.shared\\.example$\ninclude:child @-!cn\n')
        (path/'child').write_text('cn.example @cn\nglobal.example @!cn\ninclude:leaf\n')
        (path/'leaf').write_text('domain:nested.example\nfull:api.shared.example\n')
        metadata = {'roots':['root'],'files':{n:{} for n in ['root','child','leaf']}}
        (path/'source.json').write_text(json.dumps(metadata))
        events = []
        rules = snapshot_domains(path, events=events)
        require(Rule('DOMAIN','exact.example','PROXY') in rules, 'full: broadened')
        require(Rule('DOMAIN-SUFFIX','suffix.example','PROXY') in rules, 'Suffix lost')
        require(route(rules,'child.exact.example') == 'ORIGINAL','Exact child misrouted')
        require(route(rules,'a.suffix.example') == 'PROXY','Suffix child lost')
        require(route(rules,'global.example') == 'ORIGINAL','Negative include selector ignored')
        require(route(rules,'nested.example') == 'PROXY','Nested include lost')
        require(route(rules,'api.shared.example') == 'PROXY','Exact shared host lost')
        require(route(rules,'api7.shared.example') == 'ORIGINAL','Regex broadened')
        require(any(e['status']=='unconverted-domain-regexp' for e in events),'Regex omission unreported')
        positive = snapshot_domains(path, roots=['child'], exclude_attributes=['!cn'])
        require(route(positive,'global.example') == 'ORIGINAL','Excluded attribute ignored')
        (path/'leaf').write_text('include:root\n')
        try:
            snapshot_domains(path)
        except ValueError as error:
            require('cycle' in str(error), 'Unexpected cycle error')
        else:
            raise ValueError('Include cycle accepted')
        (path/'leaf').write_text('include:unlocked\n')
        try:
            snapshot_domains(path)
        except ValueError as error:
            require('Unlocked' in str(error), 'Unexpected missing dependency error')
        else:
            raise ValueError('Unlocked include accepted')
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        directory = root/'upstream/test'
        directory.mkdir(parents=True)
        (directory/'locked').write_text('original')
        commit = 'a'*40
        (directory/'source.json').write_text(json.dumps({'commit':commit,'files':{'locked':{
            'url':'https://example.test/'+commit+'/locked',
            'sha256':hashlib.sha256(b'original').hexdigest()}}}))
        verify_snapshots(root)
        (directory/'locked').write_text('tampered')
        try:
            verify_snapshots(root)
        except ValueError as error:
            require('SHA-256' in str(error),'Unexpected integrity error')
        else:
            raise ValueError('Tampered snapshot accepted')
    # Optimization must retain a more specific opposite-policy exception.
    fixture = [Rule('DOMAIN-SUFFIX','example','DIRECT'),Rule('DOMAIN-SUFFIX','sub.example','DIRECT'),
               Rule('DOMAIN','api.sub.example','PROXY'),Rule('DOMAIN','a.example','DIRECT')]
    compact, _ = optimize(fixture)
    for host in ['example','sub.example','a.example','api.sub.example','other.example']:
        ordered = sorted(fixture,key=lambda r:r.policy!='PROXY')
        ordered_compact = sorted(compact,key=lambda r:r.policy!='PROXY')
        require(route(ordered,host)==route(ordered_compact,host), 'Optimization changed policy')
    # URL rules in old input have first-match semantics too; no TLS support claim.
    regex = Rule('URL-REGEX',r'^https?://api\.example/','PROXY')
    require(route([regex,Rule('DOMAIN-SUFFIX','example','DIRECT')], 'api.example',url='https://api.example/x')=='PROXY','URL ordering')
    print('PASS: exact/suffix/regex/attributes/include/cycle and optimizer regressions')


def validate():
    rules = read_rules(MODULE)
    generated, report = generate()
    require(rules == generated and MODULE.read_text() == render(generated), 'Release differs from reproducible build')
    published_report = json.loads((ROOT/'reports/build.json').read_text())
    require(published_report['sha256'] == hashlib.sha256(MODULE.read_bytes()).hexdigest(),'Stale build report')
    require(published_report['conversion_events'] == report['conversion_events'],'Stale conversion report')
    conversion_tests()
    cases = json.loads((ROOT/'rules/routing_cases.json').read_text())
    count = 0
    for expected, hosts in cases.items():
        for host in hosts:
            require(route(rules,host) == expected,f'{host}: expected {expected}, got {route(rules,host)}')
            count += 1
            if expected == 'PROXY':
                require(route(rules,host,address='1.2.3.4',geoip_cn=True) == 'PROXY',f'GEOIP overrides PROXY: {host}')
                count += 1
            if expected == 'ORIGINAL':
                require(route(rules,host,geoip_cn=True)=='DIRECT',f'CN fallback missing: {host}')
                count += 1
    # Every explicitly asserted service root also gets a representative child test.
    for expected in ('DIRECT','PROXY'):
        for host in cases[expected]:
            if Rule('DOMAIN-SUFFIX',host,expected) in rules:
                require(route(rules,'test.'+host)==expected,f'Suffix order: {host}')
                count += 1
    for address in ['10.1.2.3','127.0.0.1','172.20.0.1','192.168.1.1','::1','fd00::1','fe80::1']:
        require(route(rules,address=address)=='DIRECT',f'Local address: {address}')
        count += 1
    require(route(rules,address='8.8.8.8')=='ORIGINAL','Public IP force-routed')
    overlaps = conflict_pairs(rules)
    require(overlaps==report['overlaps'] and report['unresolved_conflicts']==0,'Unexpected overlaps')
    for name in ['LICENSE-GPL-3.0','NOTICE.md','upstream/proxy-services/LICENSE','upstream/domestic/LICENSE','upstream/bytedance/LICENSE']:
        require((ROOT/name).is_file(),f'Missing license/attribution: {name}')
    print(f'PASS: {count} first-match routing cases; {len(overlaps)} reviewed overlap; 0 unresolved conflicts')
    print(f'PASS: {len(rules):,} rules, {MODULE.stat().st_size:,} bytes; pinned SHA-256 verified; deterministic release')
    print('STATIC SIMULATION PASSED; real iOS Shadowrocket verification pending')


if __name__ == '__main__':
    validate()
