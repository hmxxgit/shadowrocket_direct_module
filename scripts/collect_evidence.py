#!/usr/bin/env python3
"""Manually invoked evidence refresh; never modifies routing classifications."""
import concurrent.futures
import hashlib
import json
import re
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo
from urllib.parse import urlsplit
from policy import ROOT

URLS = ['https://www.capcut.com/','https://www.larksuite.com/','https://www.coze.com/',
        'https://www.trae.ai/','https://www.dola.com/','https://www.temu.com/',
        'https://www.joybuy.com/','https://www.coze.cn/','https://www.doubao.com/',
        'https://www.feishu.cn/','https://shurufa.doubao.com/']


def collect(url):
    try:
        request = urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
        with urllib.request.urlopen(request,timeout=25) as response:
            body = response.read()
            final = response.url
        hosts = sorted({urlsplit(u).hostname for u in re.findall(r'https?://[^\s<>"\x27\\]+',body.decode(errors='replace')) if urlsplit(u).hostname})
        return {'url':url,'final_url':final,'sha256':hashlib.sha256(body).hexdigest(),
                'referenced_hosts':hosts,'evidence':'public HTML references; not iOS traffic capture'}
    except Exception as error:
        return {'url':url,'error':str(error)}


if __name__ == '__main__':
    with concurrent.futures.ThreadPoolExecutor(6) as executor:
        evidence = list(executor.map(collect,URLS))
    output = {'reviewed_date':datetime.now(ZoneInfo('Asia/Shanghai')).date().isoformat(), 'pages':evidence}
    (ROOT/'rules/domain_evidence.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
    print(f'{len(evidence)} official pages checked; classifications unchanged')
