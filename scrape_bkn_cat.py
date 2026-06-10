#!/usr/bin/env python3
import json, os, pickle, re, sys, time
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE='https://cat.bkn.go.id/simulasi/'
SESSION='/tmp/bkn_session.pkl'
OUTDIR=Path('/root/cpns/scraped/bkn_cat')
OUTDIR.mkdir(parents=True, exist_ok=True)

s=pickle.load(open(SESSION,'rb'))

def get(path):
    url=urljoin(BASE,path)
    r=s.get(url,timeout=30)
    print('GET', r.status_code, r.url)
    r.raise_for_status()
    return r

def post(path, data):
    url=urljoin(BASE,path)
    r=s.post(url,data=data,allow_redirects=True,timeout=30)
    print('POST', r.status_code, r.url, [(h.status_code,h.headers.get('location')) for h in r.history])
    r.raise_for_status()
    return r

def clean(x):
    return re.sub(r'\s+', ' ', x or '').strip()

def links(html):
    soup=BeautifulSoup(html,'html.parser')
    return [(a.get('href'), clean(a.get_text(' '))) for a in soup.find_all('a')]

def parse_tables(html):
    soup=BeautifulSoup(html,'html.parser')
    tables=[]
    for table in soup.find_all('table'):
        headers=[clean(th.get_text(' ')) for th in table.find_all('th')]
        rows=[]
        for tr in table.find_all('tr'):
            cells=[clean(td.get_text(' ')) for td in tr.find_all('td')]
            if cells:
                row={headers[i] if i < len(headers) else f'col{i}': cells[i] for i in range(len(cells))}
                row['_links']=[(a.get('href'), clean(a.get_text(' '))) for a in tr.find_all('a')]
                rows.append(row)
        tables.append({'headers':headers,'rows':rows})
    return tables

home=get('ujian_peserta')
(OUTDIR/'ujian_peserta.html').write_text(home.text,encoding='utf-8')
print('title', BeautifulSoup(home.text,'html.parser').title.string if BeautifulSoup(home.text,'html.parser').title else '')
print(json.dumps(parse_tables(home.text), ensure_ascii=False, indent=2)[:5000])
exam_links=[]
for href, txt in links(home.text):
    if href and '/ujian_peserta/info/' in href:
        exam_links.append((href,txt))
print('exam_links', exam_links)

all_pages={}
for href,txt in exam_links:
    uuid=href.rstrip('/').split('/')[-1]
    r=get(href)
    (OUTDIR/f'info_{uuid}.html').write_text(r.text,encoding='utf-8')
    soup=BeautifulSoup(r.text,'html.parser')
    all_pages[f'info_{uuid}']={'url':r.url,'title':soup.title.string if soup.title else '', 'text': clean(soup.get_text(' '))[:3000], 'links': links(r.text), 'tables': parse_tables(r.text)}
    print('\nINFO',uuid)
    print(all_pages[f'info_{uuid}']['text'][:1500])
    print('links', all_pages[f'info_{uuid}']['links'])

(OUTDIR/'discovery.json').write_text(json.dumps(all_pages,ensure_ascii=False,indent=2),encoding='utf-8')
pickle.dump(s, open(SESSION,'wb'))
print('wrote', OUTDIR)
