"""Reuse pinned domestic lists without broadening exact-host entries."""
import hashlib
import json
from policy import ROOT, module_rules, priority_direct_rules


def suffixes(domain):
    labels = domain.split('.')
    return ['.'.join(labels[i:]) for i in range(len(labels))]


def domestic_direct_rules():
    directory = ROOT / 'upstream/domestic'
    metadata = json.loads((directory / 'source.json').read_text())
    for name, info in metadata['files'].items():
        if hashlib.sha256((directory / name).read_bytes()).hexdigest() != info['sha256']:
            raise ValueError(f'Domestic snapshot SHA-256 mismatch: {name}')
    candidates, visited = set(), set()

    def expand(name, selectors=()):
        key = (name, selectors)
        if key in visited:
            return
        visited.add(key)
        for raw in (directory / name).read_text().splitlines():
            fields = raw.split('#', 1)[0].split()
            if not fields:
                continue
            token, attributes = fields[0], {v[1:] for v in fields[1:]}
            if token.startswith('include:'):
                expand(token.split(':', 1)[1], tuple(sorted(set(selectors) | attributes)))
                continue
            if '!cn' in attributes or any(
                (s.startswith('-') and s[1:] in attributes) or
                (not s.startswith('-') and s not in attributes) for s in selectors
            ):
                continue
            if token.startswith('full:'):
                candidates.add(('DOMAIN', token.split(':', 1)[1].lower()))
            elif token.startswith('domain:') or ':' not in token:
                candidates.add(('DOMAIN-SUFFIX', token.removeprefix('domain:').lower()))
            else:
                raise ValueError(f'Unsupported domestic rule: {name}: {token}')

    for name in metadata['roots']:
        expand(name)
    proxy, direct, _ = module_rules()
    existing = [line.split(',') for line in priority_direct_rules() + direct]
    covered = {value.lower() for kind, value, _ in existing if kind == 'DOMAIN-SUFFIX'}
    exact = {value.lower() for kind, value, _ in existing if kind == 'DOMAIN'}
    protected = {line.split(',')[1] for line in proxy}
    eligible, added = [], []
    stats = dict(candidates=len(candidates), covered=0, redundant=0, proxy_conflicts=0)
    for kind, domain in sorted(candidates):
        ancestors = suffixes(domain)
        if any(d in protected for d in ancestors) or (kind == 'DOMAIN-SUFFIX' and any(
                p.endswith('.' + domain) for p in protected)):
            stats['proxy_conflicts'] += 1
        elif any(d in covered for d in ancestors) or (kind == 'DOMAIN' and domain in exact):
            stats['covered'] += 1
        else:
            eligible.append((kind, domain))
    imported_suffixes = {value for kind, value in eligible if kind == 'DOMAIN-SUFFIX'}
    for kind, domain in eligible:
        ancestors = suffixes(domain)
        if any(d in imported_suffixes for d in (ancestors if kind == 'DOMAIN' else ancestors[1:])):
            stats['redundant'] += 1
        else:
            added.append(f'{kind},{domain},DIRECT')
    stats['added'] = len(added)
    return added, stats
