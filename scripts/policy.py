"""Typed, fail-closed conversion of pinned snapshots and reviewed product policy.

Only services.json authorizes routing. Corporate ownership, IP geography and CDN
location are not evidence of product region. Unsupported regexes are reported.
"""
import csv
import hashlib
import io
import json
import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / 'sr_routing.module'
DOMAIN = re.compile(r'(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)(?:\.[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)*\Z')


@dataclass(frozen=True, order=True)
class Rule:
    kind: str
    value: str
    policy: str

    def line(self):
        output = io.StringIO()
        csv.writer(output, lineterminator='').writerow((self.kind, self.value, self.policy))
        return output.getvalue()


def suffixes(domain):
    labels = domain.split('.')
    return ['.'.join(labels[i:]) for i in range(len(labels))]


def covers(parent, child):
    if parent.kind == 'DOMAIN-SUFFIX' and child.kind in {'DOMAIN', 'DOMAIN-SUFFIX'}:
        return parent.value in suffixes(child.value)
    return parent.kind == child.kind and parent.value == child.value


def verify_snapshots(root=ROOT):
    """Verify every vendored file, including licenses and unused review evidence."""
    for path in sorted((root / 'upstream').rglob('source.json')):
        metadata = json.loads(path.read_text())
        if not re.fullmatch(r'[0-9a-f]{40}', metadata['commit']):
            raise ValueError(f'Invalid pinned commit: {path}')
        if metadata.get('license_sha256'):
            license_path = root / metadata['license_path']
            if not license_path.is_relative_to(root) or '..' in license_path.parts:
                raise ValueError('Unsafe license path')
            if hashlib.sha256(license_path.read_bytes()).hexdigest() != metadata['license_sha256']:
                raise ValueError('License SHA-256 mismatch')
        files = metadata.get('files', { 'sr_direct_list.module': metadata })
        for name, info in files.items():
            file = path.parent / name
            if not file.is_relative_to(path.parent) or '/' in name or name in {'.', '..'}:
                raise ValueError(f'Unsafe snapshot name: {name}')
            if hashlib.sha256(file.read_bytes()).hexdigest() != info['sha256']:
                raise ValueError(f'Snapshot SHA-256 mismatch: {file}')
            if metadata['commit'] not in info['url']:
                raise ValueError(f'Unpinned snapshot URL: {info["url"]}')


def snapshot_domains(directory, roots=None, policy='PROXY', exclude_attributes=(), events=None):
    """Return typed rules; full hosts never become suffixes; regexes never broaden.

    Include selectors (@cn, @-!cn) constrain entries recursively. Attribute tags
    do not change the domain type. A cycle or unlocked dependency fails the build.
    Domain regex syntax is not equivalent to Shadowrocket URL-REGEX, so skip and
    report it, even when a separately reviewed suffix already covers its hosts.
    """
    metadata = json.loads((directory / 'source.json').read_text())
    result, visited, active = set(), set(), set()
    events = events if events is not None else []

    def expand(name, selectors=()):
        if name not in metadata['files']:
            raise ValueError(f'Unlocked include: {directory.name}/{name}')
        key = (name, selectors)
        if name in active:
            raise ValueError(f'Include cycle: {name}')
        if key in visited:
            return
        visited.add(key)
        active.add(name)
        for number, raw in enumerate((directory / name).read_text().splitlines(), 1):
            fields = raw.split('#', 1)[0].split()
            if not fields:
                continue
            token = fields[0]
            if any(not attr.startswith('@') for attr in fields[1:]):
                raise ValueError(f'Invalid attributes: {name}:{number}')
            attrs = {attr[1:] for attr in fields[1:]}
            if token.startswith('include:'):
                expand(token[8:], tuple(sorted(set(selectors) | attrs)))
                continue
            filtered = bool(attrs.intersection(exclude_attributes)) or any(
                (s.startswith('-') and s[1:] in attrs) or
                (not s.startswith('-') and s not in attrs) for s in selectors)
            status = 'attribute-filtered' if filtered else 'candidate'
            rule = None
            if not filtered:
                if token.startswith('regexp:'):
                    status = 'unconverted-domain-regexp'
                elif token.startswith('full:'):
                    rule = Rule('DOMAIN', token[5:].lower(), policy)
                elif token.startswith('domain:') or ':' not in token:
                    rule = Rule('DOMAIN-SUFFIX', token.removeprefix('domain:').lower(), policy)
                else:
                    raise ValueError(f'Unknown rule type: {name}:{number}: {token}')
                if rule:
                    if not DOMAIN.fullmatch(rule.value):
                        raise ValueError(f'Invalid domain: {rule.value}')
                    result.add(rule)
            events.append({'source':f'{directory.name}/{name}:{number}', 'token':token,
                           'attributes':sorted(attrs), 'policy':policy, 'status':status})
        active.remove(name)

    for name in metadata['roots'] if roots is None else roots:
        expand(name)
    return sorted(result)


def reviewed_imports(directory_name=None):
    config = json.loads((ROOT / 'rules/services.json').read_text())
    events, rules = [], []
    for entry in config['imports']:
        if directory_name and entry['directory'] != directory_name:
            continue
        directory = ROOT / 'upstream' / entry['directory']
        roots = None if entry['roots'] == 'metadata' else entry['roots']
        rules += snapshot_domains(directory, roots, entry['policy'],
                                  entry.get('exclude_attributes', ()), events)
    excluded = set(config['excluded_rules'])
    shared = set(config['shared_suffixes'])
    accepted = []
    for rule in rules:
        if (rule.value in shared) or f'{rule.kind},{rule.value}' in excluded:
            events.append({'source':'review-filter', 'token':rule.line(),
                           'status':'shared-or-unconfirmed-infrastructure'})
        else:
            accepted.append(rule)
    return accepted, events


def manual_rules():
    config = json.loads((ROOT / 'rules/services.json').read_text())
    rules = []
    for group in config['groups']:
        if group['policy'] not in {'DIRECT', 'PROXY'} or not group['sources']:
            raise ValueError(f'Invalid reviewed group: {group}')
        for key, kind in [('suffix','DOMAIN-SUFFIX'), ('exact','DOMAIN')]:
            for value in group[key]:
                if not DOMAIN.fullmatch(value) or '.' not in value:
                    raise ValueError(f'Invalid reviewed domain: {value}')
                rules.append(Rule(kind, value, group['policy']))
    return rules


def parse_legacy_rule(line):
    fields = [field.strip() for field in next(csv.reader([line], strict=True))]
    if len(fields) != 3:
        raise ValueError(f'Unsupported legacy options: {line}')
    kind, value, policy = fields
    if kind == 'IP-CIDR' and ':' in value:
        kind = 'IP-CIDR6'
    return Rule(kind.upper(), value.lower(), policy.upper())


def legacy_rules():
    """Legacy snapshots remain evidence, never blanket policy authorization."""
    source = ROOT / 'upstream/sr_direct_list.module'
    rules = [Rule(*next(csv.reader([line], strict=True))) for line in
             source.read_text().split('[Rule]\n', 1)[1].splitlines()
             if line and not line.startswith('#')]
    metadata = json.loads((ROOT / 'upstream/johnshall/source.json').read_text())
    for name in metadata['roots']:
        section = None
        for raw in (ROOT / 'upstream/johnshall' / name).read_text().splitlines():
            line = raw.split('#', 1)[0].strip()
            if line.startswith('['):
                section = line
            elif line and section == '[Rule]':
                fields = [field.strip() for field in next(csv.reader([line], strict=True))]
                if len(fields) >= 3 and fields[2].upper() == 'DIRECT':
                    rules.append(parse_legacy_rule(line))
    return rules


def optimize(rules):
    """Remove only same-policy redundancy; cross-policy exceptions are preserved."""
    unique = set(rules)
    suffix = {policy:{r.value for r in unique if r.kind == 'DOMAIN-SUFFIX' and r.policy == policy}
              for policy in ('DIRECT','PROXY')}
    result = []
    for rule in sorted(unique):
        ancestors = suffixes(rule.value) if rule.kind == 'DOMAIN' else suffixes(rule.value)[1:]
        if rule.kind in {'DOMAIN','DOMAIN-SUFFIX'} and any(d in suffix[rule.policy] for d in ancestors):
            continue
        result.append(rule)
    return result, {'duplicates':len(rules)-len(unique), 'same_policy_covered':len(unique)-len(result)}


def conflict_pairs(rules):
    domains = [r for r in rules if r.kind in {'DOMAIN','DOMAIN-SUFFIX'}]
    suffix = {(r.policy,r.value):r for r in domains if r.kind=='DOMAIN-SUFFIX'}
    exact = {(r.policy,r.value):r for r in domains if r.kind=='DOMAIN'}
    pairs = set()
    for rule in domains:
        opposite = 'DIRECT' if rule.policy=='PROXY' else 'PROXY'
        parents = [suffix[(opposite,d)] for d in suffixes(rule.value) if (opposite,d) in suffix]
        if rule.kind=='DOMAIN' and (opposite,rule.value) in exact:
            parents.append(exact[(opposite,rule.value)])
        for parent in parents:
            proxy,direct = (rule,parent) if rule.policy=='PROXY' else (parent,rule)
            pairs.add((proxy.line().rsplit(',',1)[0],direct.line().rsplit(',',1)[0]))
    return [{'proxy':p,'direct':d} for p,d in sorted(pairs)]


def generate():
    verify_snapshots()
    rules, events = reviewed_imports()
    rules += manual_rules()
    config = json.loads((ROOT / 'rules/services.json').read_text())
    # Legacy entries require a reviewed same-policy domain covering their scope.
    # Regex and unknown overseas/company/shared roots are not authorized.
    legacy = legacy_rules()
    legacy_stats = {'reviewed_covered':0,'unknown_or_mixed':0,'url_regex_omitted':0,'private_ip':0,'geoip':0}
    authorized_suffix = {r.value for r in rules if r.policy=='DIRECT' and r.kind=='DOMAIN-SUFFIX'}
    authorized_exact = {r.value for r in rules if r.policy=='DIRECT' and r.kind=='DOMAIN'}
    for rule in legacy:
        if rule.kind in {'DOMAIN','DOMAIN-SUFFIX'}:
            if (any(d in authorized_suffix for d in suffixes(rule.value)) or
                    (rule.kind=='DOMAIN' and rule.value in authorized_exact)):
                rules.append(rule); legacy_stats['reviewed_covered'] += 1
            else:
                legacy_stats['unknown_or_mixed'] += 1
        elif rule.kind in {'IP-CIDR','IP-CIDR6'}:
            import ipaddress
            network = ipaddress.ip_network(rule.value, strict=True)
            if not (network.is_private or network.is_link_local or network.is_loopback):
                raise ValueError(f'Unreviewed public IP: {rule}')
            rules.append(rule); legacy_stats['private_ip'] += 1
        elif rule.kind == 'GEOIP' and rule.value == 'cn':
            legacy_stats['geoip'] += 1
        elif rule.kind == 'URL-REGEX':
            legacy_stats['url_regex_omitted'] += 1
        else:
            raise ValueError(f'Unknown legacy rule: {rule}')
    optimized, stats = optimize(rules)
    conflicts = conflict_pairs(optimized)
    intentional = [{'proxy':e['proxy'], 'direct':e['direct']} for e in config['intentional_overlaps']]
    if any(pair not in intentional for pair in conflicts):
        raise ValueError(f'Unreviewed DIRECT/PROXY overlap: {conflicts}')
    if any(pair not in conflicts for pair in intentional):
        raise ValueError('Stale intentional overlap')
    # PROXY domain exceptions precede domestic parents; IP fallback is always last.
    optimized.sort(key=lambda r:(0 if r.policy == 'PROXY' else 1, r.kind, r.value))
    optimized.append(Rule('GEOIP','CN','DIRECT'))
    return optimized, {'optimization':stats, 'legacy':legacy_stats, 'overlaps':conflicts,
                       'unresolved_conflicts':0, 'conversion_events':events}
