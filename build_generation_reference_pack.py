#!/usr/bin/env python3
"""Build a clean generation reference pack from production DB + PDF training corpus summary."""
import json, re, random
from collections import defaultdict
from pathlib import Path
import pymysql

ROOT=Path('/root/cpns')
OUT=ROOT/'generation_reference_pack.jsonl'
GUIDE=ROOT/'generator_style_guide.md'
SUMMARY=ROOT/'question_training_corpus_summary.json'

TOPIC_KW = {
 'TIU': {
  'Sinonim':['sinonim','persamaan kata','searti'], 'Antonim':['antonim','lawan kata','berlawanan'],
  'Analogi':['analogi',':'], 'Silogisme':['semua ','sebagian','beberapa','kesimpulan','simpulan'],
  'Deret Angka':['deret','barisan','pola','angka berikut'],
  'Matematika Dasar':['berapa','hitung','hasil dari','persen','luas','volume','perbandingan','rata-rata','nilai dari','umur','jarak','kecepatan'],
  'Pemahaman Bacaan':['bacaan','paragraf','wacana','ide pokok','kalimat inti','kesimpulan yang tepat']},
 'TWK': {
  'Pancasila':['pancasila','sila','ideologi','dasar negara'], 'UUD 1945':['uud','pasal','mpr','dpr','konstitusi','undang-undang','interpelasi'],
  'Bhinneka Tunggal Ika':['bhinneka','bhineka','tunggal ika','toleransi','suku','budaya','persatuan'],
  'Sejarah Indonesia':['proklamasi','soekarno','hatta','kerajaan','voc','penjajahan','sumpah pemuda','bpupki','ppki'],
  'Hankam':['tni','polri','pertahanan','keamanan','hankam','militer','bela negara','nkri']},
 'TKP': {
  'Pelayanan Publik':['pelayanan','masyarakat','warga','publik','keluhan'], 'Integritas':['jujur','suap','gratifikasi','korupsi','curang','integritas'],
  'Profesionalisme':['tugas','atasan','laporan','kinerja','profesional','deadline','pekerjaan'], 'Bela Negara':['negara','bangsa','nasionalisme','pancasila'],
  'Jejaring Kerja':['tim','rekan','koordinasi','kerja sama','rapat'], 'Sosial Budaya':['lingkungan','budaya','tetangga','gotong royong'],
  'Teknologi Informasi':['teknologi','aplikasi','digital','komputer','internet'], 'Anti Radikalisme':['radikal','teror','intoleran','ekstrem']}
}

def ok(q):
    text=q['question_text'] or ''
    opts=q['options'] if isinstance(q['options'], list) else json.loads(q['options'])
    if len(text)<25 or len(text)>650: return False
    if len(opts)!=5: return False
    if any(not str(o).strip() or str(o).strip()=='-' for o in opts): return False
    if len(set(str(o).strip().lower() for o in opts))!=5: return False
    blob=(text+' '+' '.join(map(str,opts))).upper()
    if any(bad in blob for bad in ['KUNCI JAWABAN','INI HANYA','PETUNJUK','BAGIAN PERTAMA']): return False
    t=(text+' '+' '.join(map(str,opts))).lower()
    kws=TOPIC_KW.get(q.get('section'),{}).get(q.get('topic'),[])
    if kws and not any(k in t for k in kws): return False
    return True

conn=pymysql.connect(host='localhost',user='root',database='cpns',charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
with conn.cursor() as cur:
    cur.execute('SELECT id,section,topic,year,difficulty,question_text,options,correct_answer,explanation FROM questions ORDER BY id')
    rows=cur.fetchall()
conn.close()
rows=[r for r in rows if ok(r)]
by=defaultdict(list)
for r in rows: by[(r['section'],r['topic'])].append(r)
# deterministic balanced sample: max 20/topic
pack=[]
for key in sorted(by):
    sample=by[key][:20]
    pack.extend(sample)
with open(OUT,'w',encoding='utf-8') as f:
    for r in pack:
        opts=r['options'] if isinstance(r['options'], list) else json.loads(r['options'])
        f.write(json.dumps({**r,'options':opts,'source':'production_db_clean'}, ensure_ascii=False)+'\n')
# PDF summary counts
pdf_summary={}
if SUMMARY.exists():
    pdf_summary=json.loads(SUMMARY.read_text(encoding='utf-8'))
lines=['# CPNS Question Generator Style Guide','',
'Use this guide + `/root/cpns/generation_reference_pack.jsonl` before generating soal baru.', '',
'## Hard rules',
'- Generate exactly 5 unique non-empty options (A-E).',
'- `correct_answer` must be 0-indexed: A=0, B=1, C=2, D=3, E=4.',
'- Always write a specific explanation with the reasoning/legal basis/pattern; never placeholder.',
'- Do not copy PDF artifacts: page numbers, `KUNCI JAWABAN`, `INI HANYA SOAL LATIHAN`, source headers.',
'- Keep every question self-contained and classifiable into one CPNS section/topic.',
'- TKP answers should be scored by best ASN behavior: integrity, service orientation, professionalism, collaboration.',
'',
'## Clean reference distribution from DB']
for key in sorted(by): lines.append(f'- {key[0]}/{key[1]}: {len(by[key])} clean examples ({min(20,len(by[key]))} in reference pack)')
if pdf_summary:
    lines += ['', '## New PDF folder extraction summary',
              f'- PDFs considered: {pdf_summary.get("pdfs_considered")}',
              f'- Clean extracted examples kept: {pdf_summary.get("unique_candidates")}',
              '- Raw PDF corpus file: `/root/cpns/question_training_corpus.jsonl`',
              '- Note: PDF extraction is supplemental only; production DB examples are the primary generation style reference.']
lines += ['', '## Few-shot examples by section/topic']
for key in sorted(by):
    r=by[key][0]; opts=r['options'] if isinstance(r['options'], list) else json.loads(r['options'])
    lines += ['', f'### {key[0]} / {key[1]}', '', f'Question: {r["question_text"]}']
    for i,o in enumerate(opts): lines.append(f'{chr(65+i)}. {o}')
    lines.append(f'Correct: {chr(65+int(r["correct_answer"]))}')
    lines.append(f'Explanation: {r["explanation"]}')
GUIDE.write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'clean_db_examples':len(rows),'reference_pack':len(pack),'topics':len(by),'out':str(OUT),'guide':str(GUIDE)},ensure_ascii=False,indent=2))
