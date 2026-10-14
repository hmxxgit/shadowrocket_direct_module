#!/usr/bin/env python3
"""Reproducible full-source audit and release delta (requires baseline Git history)."""
import csv
import gzip
import io
import json
import subprocess
from collections import Counter
from policy import ROOT, Rule, conflict_pairs, optimize, generate, legacy_rules, snapshot_domains


def audit():
    rules, _ = generate()
    output = io.StringIO()
    writer = csv.writer(output,delimiter='\t',lineterminator='\n')
    writer.writerow(['source','kind','value','original_policy','decision'])
    counts = Counter()
    domains = [r for r in rules if r.kind.startswith('DOMAIN')]
    suffix_policies = {}
    exact_policies = {}
    for rule in domains:
        target = suffix_policies if rule.kind == 'DOMAIN-SUFFIX' else exact_policies
        target.setdefault(rule.value,set()).add(rule.policy)

    def decision(rule):
        if not rule.kind.startswith('DOMAIN'):
            return 'retained-local-ip' if rule in rules else 'omitted-regex-or-fallback'
        from policy import suffixes
        policies = set().union(*(suffix_policies.get(d,set()) for d in suffixes(rule.value)))
        if rule.kind == 'DOMAIN':
            policies |= exact_policies.get(rule.value,set())
        if len(policies)>1:
            return 'reviewed-first-match-exception'
        if policies:
            return next(iter(policies))
        return 'unconfirmed-original-config'

    def record(source, rule):
        status = decision(rule)
        counts[f'{source}:{status}'] += 1
        writer.writerow([source,rule.kind,rule.value,rule.policy,status])

    gmo_count = json.loads((ROOT/'upstream/source.json').read_text())['rule_count']
    for index,rule in enumerate(legacy_rules()):
        record('GMOogway' if index<gmo_count else 'Johnshall',rule)
    for path in sorted((ROOT/'upstream').glob('*/source.json')):
        if path.parent.name == 'johnshall':
            continue
        events = []
        for rule in snapshot_domains(path.parent,events=events,policy='DIRECT' if path.parent.name in {'domestic','bytedance'} else 'PROXY'):
            record(path.parent.name,rule)
        for event in events:
            if event['status']=='unconverted-domain-regexp':
                writer.writerow([event['source'],'regexp',event['token'],'','unconverted-original-config'])
    compressed = io.BytesIO()
    with gzip.GzipFile(filename='',fileobj=compressed,mode='wb',compresslevel=9,mtime=0) as archive:
        archive.write(output.getvalue().encode())
    (ROOT/'reports/source-audit.tsv.gz').write_bytes(compressed.getvalue())
    baseline = json.loads((ROOT/'rules/baseline.json').read_text())
    old = subprocess.check_output(['git','show',f'{baseline["commit"]}:sr_routing.module'],cwd=ROOT,text=True)
    previous = [Rule(*next(csv.reader([line],strict=True))) for line in old.splitlines() if line and not line.startswith(('#','['))]
    old_by_domain = {}
    for rule in previous:
        if rule.kind.startswith('DOMAIN'):
            old_by_domain.setdefault(rule.value,set()).add((rule.kind,rule.policy))
    old_domains = {r.value for r in previous if r.kind.startswith('DOMAIN')}
    new_domains = {r.value for r in rules if r.kind.startswith('DOMAIN')}
    # Summarize domain-level changes without confusing them with rule counts.
    changed = sorted({r.value for r in rules if r.kind.startswith('DOMAIN') and
                      any(kind!=r.kind or policy!=r.policy for kind,policy in old_by_domain.get(r.value,()))})
    delta = {'baseline':baseline,'source_decisions':dict(sorted(counts.items())),
             'added_domains':sorted(new_domains-old_domains),'added_domain_count':len(new_domains-old_domains),
             'removed_domain_count':len(old_domains-new_domains),'changed_domains':changed,
             'changed_domain_count':len(changed),'new_rules':len(rules), 'baseline_optimization':optimize(previous)[1],
             'baseline_domain_overlap_count':len(conflict_pairs(previous))}
    (ROOT/'reports/audit.json').write_text(json.dumps(delta,ensure_ascii=False,indent=2)+'\n')
    print(f'Audit: +{delta["added_domain_count"]} domains; {delta["changed_domain_count"]} kind/policy changes; {delta["removed_domain_count"]} uncertain/redundant domains omitted')


if __name__ == '__main__':
    audit()
