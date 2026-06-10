#!/usr/bin/env python3
import json, pickle, re, time, mimetypes
from pathlib import Path
from urllib.parse import urlparse
from bs4 import BeautifulSoup

BASE='https://cat.bkn.go.id/simulasi/'
SESSION='/tmp/bkn_session.pkl'
OUTDIR=Path('/root/cpns/scraped/bkn_cat')
RAW=OUTDIR/'raw_ajax'
IMGDIR=OUTDIR/'images'
IMGDIR.mkdir(parents=True, exist_ok=True)
s=pickle.load(open(SESSION,'rb'))

def clean(x): return re.sub(r'\s+', ' ', x or '').strip()

def download(url, prefix):
    name=Path(urlparse(url).path).name or f'{prefix}.jpg'
    path=IMGDIR/f'{prefix}_{name}'
    if not path.exists():
        r=s.get(url,timeout=30); r.raise_for_status(); path.write_bytes(r.content)
    return str(path)

def parse_question(html, nomor):
    soup=BeautifulSoup(html,'html.parser')
    h4_el=soup.find('h4'); badge_el=soup.select_one('.badge'); q_el=soup.select_one('.soal-text')
    h4=clean(h4_el.get_text(' ') if h4_el else '')
    badge=clean(badge_el.get_text(' ') if badge_el else '')
    q=clean(q_el.get_text(' ') if q_el else '')
    stem_images=[]
    soal_content=soup.select_one('.soal-content')
    if soal_content:
        for idx,img in enumerate(soal_content.find_all('img'),1):
            src=img.get('src')
            if src: stem_images.append({'url':src,'alt':img.get('alt') or '', 'local_path': download(src, f'q{nomor:03d}_stem{idx}')})
    options=[]
    for div in soup.select('.pilihan-jawaban'):
        inp=div.select_one('input')
        letter=clean(div.select_one('.pilihan-huruf').get_text(' ') if div.select_one('.pilihan-huruf') else '')
        text=clean(div.select_one('.pilihan-text').get_text(' ') if div.select_one('.pilihan-text') else '')
        value=inp.get('value') if inp else letter.lower()
        imgs=[]
        for idx,img in enumerate(div.find_all('img'),1):
            src=img.get('src')
            if src: imgs.append({'url':src,'alt':img.get('alt') or '', 'local_path': download(src, f'q{nomor:03d}_opt{letter or idx}')})
        options.append({'letter':letter,'value':value,'text':text,'images':imgs})
    m=re.search(r'Soal\s+(\d+)\s+dari\s+(\d+)', h4, re.I)
    return {
        'nomor': int(m.group(1)) if m else nomor,
        'total': int(m.group(2)) if m else None,
        'section_label': badge,
        'question_text': q,
        'stem_images': stem_images,
        'options': options,
        'source': 'cat.bkn.go.id/simulasi',
        'source_session': 'Simulasi CAT SKD CPNS',
        'correct_answer': None,
        'explanation': None,
    }
questions=[]; errors=[]
for p in sorted(RAW.glob('*.json')):
    nomor=int(p.stem)
    try:
        data=json.loads(p.read_text(encoding='utf-8'))
        if data.get('status')!='success':
            errors.append({'nomor':nomor,'status':data.get('status'),'data':data}); continue
        q=parse_question(data.get('soal_html',''), nomor)
        questions.append(q)
    except Exception as e:
        errors.append({'nomor':nomor,'error':repr(e)})

out={'scraped_at':time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),'source_url':BASE,'exam':'Simulasi CAT SKD CPNS','sesi_id':54298,'count':len(questions),'questions':questions,'errors':errors}
(OUTDIR/'bkn_skd_questions_raw.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
section_map={'Tes Wawasan Kebangsaan (TWK)':'TWK','Tes Intelegensi Umum (TIU)':'TIU','Tes Karakteristik Pribadi (TKP)':'TKP'}
staged=[]
for q in questions:
    opts=[]
    for o in q['options']:
        text=o['text']
        if o['images']:
            text=(text+' ' if text else '')+' '.join('[image:'+img['local_path']+']' for img in o['images'])
        opts.append(text)
    stem=q['question_text']
    if q['stem_images']:
        stem=(stem+'\n' if stem else '')+'\n'.join('[image:'+img['local_path']+']' for img in q['stem_images'])
    staged.append({'section':section_map.get(q['section_label'],q['section_label']),'topic':'BKN SKD Scrape - staged','year':2026,'difficulty':'medium','question_text':stem,'options':opts,'correct_answer':None,'explanation':'','source':'cat.bkn.go.id/simulasi','source_nomor':q['nomor'],'raw_images':{'stem':q['stem_images'],'options':[o['images'] for o in q['options']]}})
(OUTDIR/'bkn_skd_questions_staging_no_answers.json').write_text(json.dumps(staged,ensure_ascii=False,indent=2),encoding='utf-8')
from collections import Counter
val={'count':len(staged),'sections':dict(Counter(x['section'] for x in staged)),'bad_option_count':[x['source_nomor'] for x in staged if len(x['options'])!=5],'empty_question':[x['source_nomor'] for x in staged if not x['question_text']],'duplicate_stems':[k for k,v in Counter(x['question_text'] for x in staged).items() if v>1],'missing_answers':sum(1 for x in staged if x['correct_answer'] is None),'image_questions':[x['source_nomor'] for x in staged if x['raw_images']['stem'] or any(x['raw_images']['options'])],'downloaded_images':len(list(IMGDIR.glob('*'))),'errors':errors}
(OUTDIR/'validation_report.json').write_text(json.dumps(val,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(val,ensure_ascii=False,indent=2))
