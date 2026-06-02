#!/usr/bin/env python3
"""Build clean CPNS question generation corpus from /root/cpns/bank-soal PDFs.

Outputs:
- question_training_corpus.jsonl: deduped high-quality examples for generator/RAG
- question_training_corpus_summary.json: counts and source stats
- generator_style_guide.md: compact rules distilled from examples

This intentionally does NOT insert into production DB. Use the corpus to guide generation/import after review.
"""
import json, re, hashlib
from pathlib import Path
from collections import Counter, defaultdict

import fitz

ROOT = Path('/root/cpns')
PDF_DIR = ROOT / 'bank-soal'
OUT_JSONL = ROOT / 'question_training_corpus.jsonl'
OUT_SUMMARY = ROOT / 'question_training_corpus_summary.json'
OUT_GUIDE = ROOT / 'generator_style_guide.md'

SKIP_PARTS = {'BAHASA INGGRIS', 'PSIKOTES', 'TES BERGAMBAR', 'CORE VALUE', 'KISI-KISI SOAL BUMN 2022'}
CPNS_HINTS = ('CPNS','SKD','TWK','TIU','TKP','TES WAWASAN','INTELEGENSI','KARAKTERISTIK','SOAL LATIHAN','DRILLING','DIKTAT')
BAD_RE = re.compile(r'(HANYA\s+SOAL\s+LATIHAN|KUNCI\s+JAWABAN|BAGIAN\s+PERTAMA|BAGIAN\s+KEDUA|QUESTION\s+NO|QUESTIONS\s+NO|PETUNJUK|PEMBAHASAN\s+SOAL|SOAL-SOAL|MEDIAEDUKASI|CENDEKIA|DOWNLOAD|WWW\.|HTTP)', re.I)
CONTAM_RE = re.compile(r'(KUNCI\s+JAWABAN|HANYA\s+SOAL\s+LATIHAN|BAGIAN\s+(PERTAMA|KEDUA)|Question\s+no|Questions\s+no|PART\s+TWO|Yang\s+tercetak|SOAL-SOAL|PEMBAHASAN:|\bJawab(?:an)?\s*:)', re.I)

TWK_TOPICS = {
    'Pancasila':['pancasila','sila ','garuda','ideologi','dasar negara','piagam jakarta','bpupki','ppki'],
    'UUD 1945':['uud','pasal','mpr','dpr','dpd','mk','ma','presiden','konstitusi','amandemen','undang-undang','interpelasi','otonomi'],
    'Bhinneka Tunggal Ika':['bhinneka','bhineka','tunggal ika','suku','budaya','toleransi','keragaman','persatuan','gotong royong'],
    'Sejarah Indonesia':['proklamasi','soekarno','hatta','kerajaan','voc','penjajahan','sumpah pemuda','reformasi','bpupki','ppki','agresi'],
    'Hankam':['tni','polri','pertahanan','keamanan','hankam','militer','bela negara','ancaman','wajib militer'],
}
TIU_TOPICS = {
    'Sinonim':['sinonim','persamaan kata','searti','makna kata',' = ____'],
    'Antonim':['antonim','lawan kata','berlawanan','> <'],
    'Analogi':['analogi','padanan kata','hubungan kata',':'],
    'Silogisme':['semua ','sebagian','beberapa','tidak ada','kesimpulan','simpulan','premis'],
    'Deret Angka':['deret','barisan','angka berikut','pola bilangan'],
    'Matematika Dasar':['berapa','hitung','hasil dari','persen','luas','volume','perbandingan','rata-rata','aljabar','umur','jarak','kecepatan','kg','liter','rupiah'],
    'Pemahaman Bacaan':['bacaan','paragraf','wacana','ide pokok','kalimat inti','gagasan utama'],
}
TKP_TOPICS = {
    'Pelayanan Publik':['pelayanan','masyarakat','warga','loket','publik','keluhan','instansi'],
    'Integritas':['suap','gratifikasi','jujur','korupsi','manipulasi','presensi','curang','integritas'],
    'Profesionalisme':['deadline','tugas','atasan','laporan','kinerja','profesional','pekerjaan','kantor'],
    'Bela Negara':['bendera','negara','bangsa','upacara','nasionalisme','pancasila'],
    'Jejaring Kerja':['tim','rekan','kolaborasi','koordinasi','kerja sama','rapat'],
    'Sosial Budaya':['tetangga','lingkungan','budaya','gotong royong','perbedaan','sosial'],
    'Teknologi Informasi':['teknologi','aplikasi','digital','komputer','internet','media sosial'],
    'Anti Radikalisme':['radikal','teror','intoleran','ekstrem','kebencian'],
}

def clean(s):
    s = str(s or '').replace('\u00a0',' ')
    s = re.sub(r'[\r\t]+',' ',s)
    s = re.sub(r'\s+',' ',s).strip()
    s = re.sub(r'^(?:SOAL\s+)?(?:NO\.?\s*)?\d+\s*[.)]\s*','',s, flags=re.I)
    return s.strip(' -–—')

def normalize_key(s):
    return re.sub(r'\W+','', clean(s).lower())[:220]

def extract_text(pdf):
    try:
        doc = fitz.open(pdf)
        pages=[]
        for p in doc:
            pages.append(p.get_text('text'))
        doc.close()
        return '\n'.join(pages)
    except Exception as e:
        return ''

def section_from_source(path):
    u = str(path).upper()
    if 'TKP' in u or 'KARAKTERISTIK' in u: return 'TKP'
    if 'TIU' in u or 'VERBAL' in u or 'ARITMATIKA' in u or 'DERET' in u: return 'TIU'
    if 'TWK' in u or 'WAWASAN' in u: return 'TWK'
    return None

def classify_section_topic(qtext, options, default_section=None):
    t = (qtext + ' ' + ' '.join(options)).lower()
    scores = {'TWK':0,'TIU':0,'TKP':0}
    for kws in TWK_TOPICS.values(): scores['TWK'] += sum(1 for k in kws if k in t)
    for kws in TIU_TOPICS.values(): scores['TIU'] += sum(1 for k in kws if k in t)
    for kws in TKP_TOPICS.values(): scores['TKP'] += sum(1 for k in kws if k in t)
    if re.match(r'^(anda|saya|ketika|sebagai seorang|pada saat)', qtext.lower()): scores['TKP'] += 3
    if re.match(r'^\s*[\d,.;/¼½¾\s]+(\.\.\.|…|\?)', qtext): scores['TIU'] += 3
    section = max(scores, key=scores.get) if max(scores.values()) > 0 else (default_section or 'TWK')
    if default_section and scores[section] <= 1:
        section = default_section
    maps = {'TWK':TWK_TOPICS,'TIU':TIU_TOPICS,'TKP':TKP_TOPICS}[section]
    best_topic, best_score = None, -1
    for topic,kws in maps.items():
        sc = sum(1 for k in kws if k in t)
        if sc > best_score:
            best_topic, best_score = topic, sc
    defaults = {'TWK':'UUD 1945','TIU':'Matematika Dasar','TKP':'Profesionalisme'}
    return section, best_topic if best_score > 0 else defaults[section]

def parse_answer_keys(text):
    keys = {}
    # Common compact key lines: "1. A 2. C ..." or table-like text after KUNCI
    tail_chunks = re.split(r'(?:KUNCI\s+JAWABAN|ANSWER\s+KEY|PEMBAHASAN)', text, flags=re.I)
    key_text = '\n'.join(tail_chunks[1:]) if len(tail_chunks) > 1 else text[-12000:]
    for n, letter in re.findall(r'\b(?:No\.?\s*)?(\d{1,3})\s*[.)\-: ]\s*\(?([A-Ea-e])\)?\b', key_text):
        i = int(n)
        if 1 <= i <= 200:
            keys[i] = ord(letter.lower()) - 97
    return keys

def parse_blocks(text, source_path):
    text = text.replace('\r','\n')
    # normalize OCR weird option bullets into A. style without flattening all newlines
    q_re = re.compile(r'(?m)^[ \t]*(\d{1,3})\s*[.)]\s+(.+)')
    starts = list(q_re.finditer(text))
    keys = parse_answer_keys(text)
    default_section = section_from_source(source_path)
    out=[]
    for idx,m in enumerate(starts):
        qnum = int(m.group(1))
        start = m.start(); end = starts[idx+1].start() if idx+1 < len(starts) else len(text)
        block = text[start:end].strip()
        # Stop parsing if this is clearly key/explanation section
        if re.search(r'^(?:KUNCI|PEMBAHASAN)\b', block, re.I):
            continue
        # Options can appear as new lines or inline. Add sentinels before A-E markers.
        b = re.sub(r'\n+', '\n', block)
        # avoid splitting abbreviations by requiring option marker followed by non-lowercase-ish phrase
        opt_re = re.compile(r'(?im)(?:^|\n|\s)([A-E])\s*[.)]\s+')
        opts = list(opt_re.finditer(b))
        if len(opts) < 4:
            continue
        qtext = b[m.end()-start:opts[0].start()].strip()
        qtext = clean(qtext)
        options=[]
        for oi,om in enumerate(opts[:5]):
            os = om.end(); oe = opts[oi+1].start() if oi+1 < min(len(opts),5) else len(b)
            options.append(clean(b[os:oe]))
        options = [o for o in options if o]
        if len(options) != 5:
            continue
        if not quality_ok(qtext, options):
            continue
        section, topic = classify_section_topic(qtext, options, default_section)
        ans = keys.get(qnum)
        explanation = f"Pola soal diambil dari bank soal CPNS: {source_path.name}. Gunakan pembahasan konseptual saat generate varian baru."
        out.append({
            'section': section, 'topic': topic, 'year': 2024, 'difficulty': infer_difficulty(qtext, options),
            'question_text': qtext, 'options': options, 'correct_answer': ans,
            'explanation': explanation, 'source_file': str(source_path.relative_to(PDF_DIR)), 'source_question_no': qnum,
            'training_use': 'style_and_pattern_reference'
        })
    return out

def infer_difficulty(q, opts):
    l = len(q) + sum(len(o) for o in opts)//5
    if l > 360: return 'sulit'
    if l > 180: return 'sedang'
    return 'mudah'

def quality_ok(qtext, options):
    if len(qtext) < 18 or len(qtext) > 900: return False
    qt = qtext.lstrip()
    if qt.startswith((':', ';', ',', '.', '….')): return False
    if re.search(r'\([A-E]\)|Untuk\s+soal\s+nomor|Respon\s+saya\s*:', qtext, re.I): return False
    # PyMuPDF sometimes clips the first capital from line-wrapped questions; those are bad training data.
    first = qt[:1]
    if first and first.isalpha() and first.islower(): return False
    if BAD_RE.search(qtext): return False
    if any(CONTAM_RE.search(o) for o in options): return False
    if any(len(o) < 1 or len(o) > 260 for o in options): return False
    if any(o.strip() in {'-', '_', '—'} for o in options): return False
    norm_opts=[normalize_key(o) for o in options]
    if len(set(norm_opts)) != 5: return False
    # reject pure English imported BUMN/TOEFL material
    en_hits = len(re.findall(r'\b(the|what|which|should|author|paragraph|meeting|better|could|from|your)\b', qtext.lower()))
    if en_hits >= 3: return False
    return True

def main():
    pdfs=[]
    for pdf in PDF_DIR.rglob('*.pdf'):
        parts_upper={p.upper() for p in pdf.relative_to(PDF_DIR).parts[:-1]}
        if parts_upper & SKIP_PARTS: continue
        u=str(pdf.relative_to(PDF_DIR)).upper()
        if not any(h in u for h in CPNS_HINTS): continue
        pdfs.append(pdf)
    rows=[]; source_stats={}
    for pdf in sorted(pdfs):
        text=extract_text(pdf)
        qs=parse_blocks(text, pdf) if len(text)>100 else []
        source_stats[str(pdf.relative_to(PDF_DIR))]={'chars':len(text),'parsed':len(qs)}
        rows.extend(qs)
    seen=set(); unique=[]
    for r in rows:
        key=normalize_key(r['question_text'])
        if key in seen: continue
        seen.add(key); unique.append(r)
    # Keep all unique clean examples from the new PDF folder as training/reference data.
    # Even if a question already exists in production DB, it is still useful as a style exemplar.
    novel = unique
    with open(OUT_JSONL,'w',encoding='utf-8') as f:
        for r in novel:
            f.write(json.dumps(r, ensure_ascii=False)+'\n')
    counts=Counter((r['section'], r['topic']) for r in novel)
    summary={
        'pdfs_considered': len(pdfs), 'raw_candidates': len(rows), 'unique_candidates': len(unique),
        'novel_training_examples': len(novel), 'by_section': Counter(r['section'] for r in novel),
        'by_topic': {f'{s}/{t}':c for (s,t),c in sorted(counts.items())}, 'source_stats': source_stats,
        'outputs': {'jsonl': str(OUT_JSONL), 'style_guide': str(OUT_GUIDE)}
    }
    with open(OUT_SUMMARY,'w',encoding='utf-8') as f: json.dump(summary,f,ensure_ascii=False,indent=2,default=dict)
    guide = build_guide(novel, counts)
    OUT_GUIDE.write_text(guide, encoding='utf-8')
    print(json.dumps({k:summary[k] for k in ['pdfs_considered','raw_candidates','unique_candidates','novel_training_examples','by_section']}, ensure_ascii=False, indent=2, default=dict))
    print('wrote', OUT_JSONL, OUT_SUMMARY, OUT_GUIDE)

def sample(rows, section, topic, n=2):
    out=[]
    for r in rows:
        if r['section']==section and r['topic']==topic:
            out.append(r)
        if len(out)>=n: break
    return out

def build_guide(rows, counts):
    lines=[]
    lines.append('# CPNS Question Generator Style Guide\n')
    lines.append('Generated from `/root/cpns/bank-soal` clean PDF corpus. Use this as retrieval/context before generating new soal.\n')
    lines.append('## Global rules\n')
    lines += [
        '- Output 5 options exactly (A-E), unique and non-empty.',
        '- `correct_answer` is 0-indexed: A=0, B=1, C=2, D=3, E=4.',
        '- Always include a specific explanation; never use placeholder-only pembahasan.',
        '- Avoid PDF artifacts: `KUNCI JAWABAN`, `INI HANYA SOAL LATIHAN`, page headers, source watermarks.',
        '- Keep question self-contained; do not depend on previous/next page context.',
        '- TWK should test civic knowledge; TIU should test reasoning/verbal/numeric; TKP should be situational judgement.',
    ]
    lines.append('\n## Corpus distribution\n')
    for (sec,topic),cnt in sorted(counts.items()):
        lines.append(f'- {sec}/{topic}: {cnt} examples')
    lines.append('\n## Good example patterns\n')
    for sec in ['TWK','TIU','TKP']:
        topics=sorted({topic for (s, topic), _cnt in counts.items() if s == sec})[:4]
        for topic in topics:
            exs=sample(rows, sec, topic, 1)
            if not exs: continue
            e=exs[0]
            lines.append(f'\n### {sec} / {topic}\n')
            lines.append(f'Question: {e["question_text"]}')
            for i,o in enumerate(e['options']): lines.append(f'{chr(65+i)}. {o}')
            lines.append(f'Difficulty: {e["difficulty"]}')
    return '\n'.join(lines)+'\n'

if __name__ == '__main__':
    main()
