#!/usr/bin/env python3
import json, pickle, re, time
from pathlib import Path
from bs4 import BeautifulSoup

BASE='https://cat.bkn.go.id/simulasi/'
SESSION='/tmp/bkn_session.pkl'
OUTDIR=Path('/root/cpns/scraped/bkn_cat')
RAW=OUTDIR/'raw_ajax'
RAW.mkdir(parents=True, exist_ok=True)
s=pickle.load(open(SESSION,'rb'))

def clean(x):
    return re.sub(r'\s+', ' ', x or '').strip()

def parse_question(html, nomor):
    soup=BeautifulSoup(html,'html.parser')
    h4=clean(soup.find('h4').get_text(' ') if soup.find('h4') else '')
    badge=clean(soup.select_one('.badge').get_text(' ') if soup.select_one('.badge') else '')
    q=clean(soup.select_one('.soal-text').get_text(' ') if soup.select_one('.soal-text') else '')
    options=[]
    for div in soup.select('.pilihan-jawaban'):
        letter=clean(div.select_one('.pilihan-huruf').get_text(' ') if div.select_one('.pilihan-huruf') else '')
        text=clean(div.select_one('.pilihan-text').get_text(' ') if div.select_one('.pilihan-text') else '')
        value=div.select_one('input').get('value') if div.select_one('input') else letter.lower()
        options.append({'letter':letter,'value':value,'text':text})
    m=re.search(r'Soal\s+(\d+)\s+dari\s+(\d+)', h4, re.I)
    return {
        'nomor': int(m.group(1)) if m else nomor,
        'total': int(m.group(2)) if m else None,
        'section_label': badge,
        'question_text': q,
        'options': options,
        'source': 'cat.bkn.go.id/simulasi',
        'source_session': 'Simulasi CAT SKD CPNS',
        'correct_answer': None,
        'explanation': None,
    }

questions=[]
errors=[]
sesi_id=54298
for nomor in range(1,111):
    try:
        r=s.post(BASE+'ujian_peserta/get_soal_ajax',data={'sesi_id':sesi_id,'nomor_soal':nomor},headers={'Content-Type':'application/x-www-form-urlencoded'},timeout=30)
        print(nomor, r.status_code, r.text[:80].replace('\n',' '))
        r.raise_for_status()
        data=r.json()
        (RAW/f'{nomor:03d}.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
        if data.get('status')!='success':
            errors.append({'nomor':nomor,'status':data.get('status'),'data':data})
            continue
        q=parse_question(data.get('soal_html',''), nomor)
        q['jawaban_count']=data.get('jawaban_count')
        q['sisa_waktu']=data.get('sisa_waktu')
        questions.append(q)
        time.sleep(0.12)
    except Exception as e:
        print('ERR',nomor,e)
        errors.append({'nomor':nomor,'error':repr(e)})

out={
    'scraped_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
    'source_url': BASE,
    'exam': 'Simulasi CAT SKD CPNS',
    'sesi_id': sesi_id,
    'count': len(questions),
    'questions': questions,
    'errors': errors,
}
(OUTDIR/'bkn_skd_questions_raw.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
# cleaner CPNS app staging format, no import yet
section_map={'Tes Wawasan Kebangsaan (TWK)':'TWK','Tes Intelegensi Umum (TIU)':'TIU','Tes Karakteristik Pribadi (TKP)':'TKP'}
staged=[]
for q in questions:
    opts=[o['text'] for o in q['options']]
    staged.append({
        'section': section_map.get(q['section_label'], q['section_label']),
        'topic': 'BKN SKD Scrape - staged',
        'year': 2026,
        'difficulty': 'medium',
        'question_text': q['question_text'],
        'options': opts,
        'correct_answer': None,
        'explanation': '',
        'source': q['source'],
        'source_nomor': q['nomor'],
    })
(OUTDIR/'bkn_skd_questions_staging_no_answers.json').write_text(json.dumps(staged,ensure_ascii=False,indent=2),encoding='utf-8')
# validation
from collections import Counter
val={
    'count': len(staged),
    'sections': Counter(x['section'] for x in staged),
    'bad_option_count': [x['source_nomor'] for x in staged if len(x['options'])!=5],
    'empty_question': [x['source_nomor'] for x in staged if not x['question_text']],
    'duplicate_stems': [k for k,v in Counter(x['question_text'] for x in staged).items() if v>1],
    'missing_answers': len([x for x in staged if x['correct_answer'] is None]),
    'errors': errors,
}
# Counter not JSON serializable directly
val['sections']=dict(val['sections'])
(OUTDIR/'validation_report.json').write_text(json.dumps(val,ensure_ascii=False,indent=2),encoding='utf-8')
pickle.dump(s, open(SESSION,'wb'))
print('WROTE', OUTDIR/'bkn_skd_questions_raw.json')
print('WROTE', OUTDIR/'bkn_skd_questions_staging_no_answers.json')
print('VALIDATION', json.dumps(val,ensure_ascii=False,indent=2))
