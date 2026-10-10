"""Import explicit DIRECT rules from pinned Johnshall white-list configs."""
import csv
import hashlib
import ipaddress
import json
from domestic import domestic_direct_rules, suffixes
from policy import ROOT, module_rules, priority_direct_rules


def johnshall_direct_rules():
    directory = ROOT / 'upstream/johnshall'
    metadata = json.loads((directory / 'source.json').read_text())
    for name, info in metadata['files'].items():
        if hashlib.sha256((directory / name).read_bytes()).hexdigest() != info['sha256']:
            raise ValueError(f'Johnshall snapshot SHA-256 mismatch: {name}')
    candidates = set()
    for name in metadata['roots']:
        section = None
        for raw in (directory / name).read_text().splitlines():
            line = raw.split('#', 1)[0].strip()
            if line.startswith('['):
                section = line
            if not line or section != '[Rule]' or line.startswith('['):
                continue
            fields = [value.strip() for value in next(csv.reader([line], strict=True))]
            if len(fields) < 3 or fields[2].upper() != 'DIRECT':
                continue
            kind, value, _ = fields[:3]
            if len(fields) != 3:
                raise ValueError(f'Unsupported DIRECT options: {line}')
            if kind in {'DOMAIN', 'DOMAIN-SUFFIX'}:
                value = value.lower()
            elif kind == 'IP-CIDR':
                network = ipaddress.ip_network(value, strict=True)
                if not (network.is_private or network.is_loopback or network.is_link_local):
                    raise ValueError(f'Unreviewed public DIRECT IP range: {line}')
                kind = 'IP-CIDR6' if network.version == 6 else 'IP-CIDR'
                value = str(network)
            elif kind != 'GEOIP' or value != 'CN':
                raise ValueError(f'Unsupported DIRECT rule: {line}')
            candidates.add((kind, value))
    proxy, direct, _ = module_rules()
    domestic, _ = domestic_direct_rules()
    existing = [line.split(',') for line in priority_direct_rules() + direct + domestic + ['GEOIP,CN,DIRECT']]
    covered = {value.lower() for kind, value, _ in existing if kind == 'DOMAIN-SUFFIX'}
    exact = {(kind, value.lower()) for kind, value, _ in existing}
    protected = {line.split(',')[1] for line in proxy}
    eligible, added, conflicts = [], [], []
    stats = dict(candidates=len(candidates), covered=0, redundant=0, proxy_conflicts=0)
    for kind, value in sorted(candidates):
        if kind in {'DOMAIN', 'DOMAIN-SUFFIX'} and (
            any(d in protected for d in suffixes(value)) or
            (kind == 'DOMAIN-SUFFIX' and any(p.endswith('.' + value) for p in protected))
        ):
            conflicts.append(f'{kind},{value},DIRECT')
            stats['proxy_conflicts'] += 1
        elif (kind, value.lower()) in exact or (kind in {'DOMAIN', 'DOMAIN-SUFFIX'} and
                                              any(d in covered for d in suffixes(value))):
            stats['covered'] += 1
        else:
            eligible.append((kind, value))
    imported_suffixes = {value for kind, value in eligible if kind == 'DOMAIN-SUFFIX'}
    for kind, value in eligible:
        if kind in {'DOMAIN', 'DOMAIN-SUFFIX'} and any(
            d in imported_suffixes for d in (suffixes(value) if kind == 'DOMAIN' else suffixes(value)[1:])
        ):
            stats['redundant'] += 1
        else:
            added.append(f'{kind},{value},DIRECT')
    stats['added'] = len(added)
    return added, stats, conflicts
