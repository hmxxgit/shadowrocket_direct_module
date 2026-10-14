#!/usr/bin/env python3
"""Read-only upstream watch: verify pinned bytes and report candidate differences.

No checkout writes, auto-accept, commits or release updates. Network errors fail.
"""
import concurrent.futures
import difflib
import hashlib
import json
import os
import urllib.request
from pathlib import Path
from policy import ROOT, verify_snapshots


def request(url, api=False):
    headers = {'User-Agent':'shadowrocket-routing-review'}
    if api and os.environ.get('GH_TOKEN'):
        headers['Authorization'] = 'Bearer '+os.environ['GH_TOKEN']
    with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=30) as response:
        return response.read()


def meaningful_lines(content):
    return {line.split('#',1)[0].strip() for line in content.decode().splitlines()
            if line.split('#',1)[0].strip()}


def check(output):
    verify_snapshots()
    repositories, jobs = {}, []
    for path in sorted((ROOT/'upstream').rglob('source.json')):
        m = json.loads(path.read_text())
        repo = m['repository'].removeprefix('https://github.com/')
        if repo not in repositories:
            info = json.loads(request(f'https://api.github.com/repos/{repo}',True))
            latest = json.loads(request(f'https://api.github.com/repos/{repo}/commits/{info["default_branch"]}',True))['sha']
            repositories[repo] = latest
        if m.get('license_sha256'):
            jobs.append((m['license_path'],{'url':m['license_url'],'sha256':m['license_sha256']},
                         m['commit'],repositories[repo]))
        files = m.get('files',{'sr_direct_list.module':m})
        for name, info in files.items():
            jobs.append((str(path.parent.relative_to(ROOT)/name),info,m['commit'],repositories[repo]))

    def inspect(job):
        name,info,pinned,latest = job
        original = request(info['url'])
        if hashlib.sha256(original).hexdigest()!=info['sha256']:
            raise ValueError(f'Remote pinned SHA-256 mismatch: {name}')
        candidate = request(info['url'].replace('/'+pinned+'/', '/'+latest+'/'))
        actual = hashlib.sha256(candidate).hexdigest()
        diff = list(difflib.unified_diff(original.decode().splitlines(),candidate.decode().splitlines(),fromfile=pinned,tofile=latest,lineterm='')) if actual!=info['sha256'] else []
        added = sorted(meaningful_lines(candidate)-meaningful_lines(original))
        removed = sorted(meaningful_lines(original)-meaningful_lines(candidate))
        return {'file':name,'pinned_commit':pinned,'candidate_commit':latest,
                'pinned_sha256_verified':True,'candidate_sha256':actual,
                'changed':bool(diff),'content_changed':bool(added or removed),
                'added_entries':added,'removed_entries':removed,'diff':diff}

    with concurrent.futures.ThreadPoolExecutor(8) as executor:
        changes = list(executor.map(inspect,jobs))
    result = {'review_required':any(c['changed'] for c in changes),'repositories':repositories,'files':changes,
              'instruction':'Human review required for all routing changes; release was not modified.'}
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    if result['review_required']:
        print('::warning::Upstream changes require human routing review; release unchanged')
    print(f'Pinned integrity verified for {len(changes)} files; {sum(c["changed"] for c in changes)} candidate changes require review')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    check(parser.parse_args().output)
