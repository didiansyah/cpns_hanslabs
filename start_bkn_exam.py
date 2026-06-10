#!/usr/bin/env python3
import json, pickle, re, time
from pathlib import Path
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
BASE='https://cat.bkn.go.id/simulasi/'
SESSION='/tmp/bkn_session.pkl'
OUTDIR=Path('/root/cpns/scraped/bkn_cat'); OUTDIR.mkdir(parents=True, exist_ok=True)
s=pickle.load(open(SESSION,'rb'))

def req(method,path,**kw):
    url=path if str(path).startswith('http') else urljoin(BASE,path)
    r=s.request(method,url,timeout=30,allow_redirects=True,**kw)
    print(method,url,'->',r.status_code,r.url,'hist',[(h.status_code,h.headers.get('location')) for h in r.history])
    r.raise_for_status(); return r

def clean(x): return re.sub(r'\s+',' ',x or '').strip()
def dump(name,r):
    (OUTDIR/f'{name}.html').write_text(r.text,encoding='utf-8')
    print(name, clean(BeautifulSoup(r.text,'html.parser').get_text(' '))[:2000])

def discover_exam_page(html):
    soup=BeautifulSoup(html,'html.parser')
    forms=[]
    for f in soup.find_all('form'):
        forms.append({'action':f.get('action'),'method':f.get('method'),'inputs':[(i.get('name'),i.get('value'),i.get('type')) for i in f.find_all('input')]})
    scripts=[sc.get('src') or sc.string[:200] if sc.string else '' for sc in soup.find_all('script')]
    links=[(a.get('href'),clean(a.get_text(' '))) for a in soup.find_all('a')]
    return {'title': soup.title.string if soup.title else '', 'forms':forms, 'links':links, 'scripts':scripts}

exam_id='d44fae1b-68b6-4456-9efe-6e279e687964'
# start exam once
info=req('GET',f'ujian_peserta/info/{exam_id}')
dump('info_before_start',info)
start=req('POST',f'ujian_peserta/mulai/{exam_id}', data={'ci_csrf_token':''})
dump('after_start',start)
meta=discover_exam_page(start.text)
(OUTDIR/'after_start_meta.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(meta,ensure_ascii=False,indent=2)[:5000])
# try likely pages/endpoints
candidates=[]
for href,txt in meta['links']:
    if href and ('ujian' in href or 'soal' in href or 'peserta' in href): candidates.append(href)
for p in ['ujian_peserta/kerjakan','ujian_peserta/soal','ujian_peserta/ujian','ujian_peserta/get_soal','ujian_peserta/detail','ujian_peserta']:
    candidates.append(p)
seen=set()
for c in candidates:
    if c in seen: continue
    seen.add(c)
    try:
        rr=req('GET',c)
        safe=re.sub(r'[^A-Za-z0-9_.-]+','_',c.split('/simulasi/')[-1] if '/simulasi/' in c else c).strip('_')[:80]
        dump('candidate_'+safe,rr)
    except Exception as e:
        print('ERR',c,e)
pickle.dump(s, open(SESSION,'wb'))
print('done')
