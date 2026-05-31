#!/usr/bin/env python3
"""Extract remaining CPNS PDFs."""
import fitz, re, json, os, random
from collections import Counter

PDF_DIR = "/root/cpns/bank-soal"

# Remaining CPNS-relevant PDFs
REMAINING = [
    "1.  SOAL LATIHAN TWK-TIU-TKP.pdf",
    "2. SOAL LATIHAN TWK-TIU-TKP.pdf",
    "3. SOAL LATIHAN TWK-TIU-TKP.pdf",
    "4. SOAL LATIHAN TWK-TIU-TKP.pdf",
    "5. SOAL LATIHAN TWK-TIU-TKP.pdf",
    "6. SOAL LATIHAN TWK-TIU-TKP.pdf",
    "7. SOAL LATIHAN TWK-TIU-TKP.pdf",
    "8. SOAL LATIHAN TWK-TIU-TKP.pdf",
    "A. SOAL LATIHAN HOST.pdf",
    "B.SOAL LATIHAN HOST.pdf",
    "SOAL KILAS BALIK CPNS 2015.pdf",
    "SOAL LATIAN TIU VERBAL.pdf",
    "MATERI TWK.pdf",
    "TKP CPNS.pdf",
    "Buku Latihan Soal BUMN dan CPNS.pdf",
    "SUKSES MENAKLUKAN BUMN&CPNS.pdf",
    "SOAL 2019-2020 CPNS-BUMN BY CENDEKIAPEDIA+PEMBAHASAN.pdf",
    "DRILLING SOAL-SOAL CPNS.pdf",
    "CPNS/SUPER DIKTAT CPNS.pdf",
]

def extract_text(path):
    try:
        doc = fitz.open(path)
        text = ""
        for p in doc:
            text += p.get_text()
        doc.close()
        return text
    except: return ""

def parse(text, default_sec=None):
    qs = []
    def detect(t):
        tl = t.lower()
        if any(k in tl for k in ['twk', 'wawasan kebangsaan', 'ideologi', 'pancasila', 'uud 1945']):
            return 'TWK'
        if any(k in tl for k in ['tiu', 'intelegensi', 'verbal', 'numerik', 'sinonim', 'antonim', 'analogi']):
            return 'TIU'
        if any(k in tl for k in ['tkp', 'karakteristik', 'pelayanan', 'profesional']):
            return 'TKP'
        return None
    
    q_pat = re.compile(r'(?:^|\n)\s*(\d+)\.\s+', re.MULTILINE)
    starts = [(m.start(), m.group(1)) for m in q_pat.finditer(text)]
    sec = default_sec
    
    for idx, (start, num) in enumerate(starts):
        end = starts[idx+1][0] if idx+1 < len(starts) else len(text)
        block = text[start:end].strip()
        s = detect(block)
        if s: sec = s
        
        block = re.sub(r'^\s*\d+\.\s*', '', block)
        opt_pat = re.compile(r'\n\s*([a-e])[.):\s]+', re.IGNORECASE)
        opts = list(opt_pat.finditer(block))
        if len(opts) < 3: continue
        
        q_text = block[:opts[0].start()].strip()
        q_text = re.sub(r'\s+', ' ', q_text).strip()
        if len(q_text) < 10: continue
        
        options = []
        for i, m in enumerate(opts):
            s2 = m.end()
            e2 = opts[i+1].start() if i+1 < len(opts) else len(block)
            ot = block[s2:e2].strip()
            ot = re.sub(r'\s+', ' ', ot).strip()
            if ot: options.append(ot)
        
        if len(options) < 4: continue
        options = options[:5]
        while len(options) < 5: options.append("-")
        
        qs.append({"section": sec or "TWK", "question_text": q_text, "options": options})
    return qs

all_q = []
for pdf in REMAINING:
    path = os.path.join(PDF_DIR, pdf)
    if not os.path.exists(path):
        continue
    print(f"Extracting: {pdf}")
    text = extract_text(path)
    if len(text) < 100:
        print(f"  SKIP (too short)")
        continue
    qs = parse(text)
    print(f"  Parsed: {len(qs)}")
    for q in qs:
        q["source_file"] = pdf
    all_q.extend(qs)

print(f"\nTotal extracted: {len(all_q)}")

# Clean
def clean(q):
    t = re.sub(r'MEDIAEDUKASI\.MY\.ID|MEDIAEDUKASI|INI HANYA SOAL LATIHAN|Poin \d+|\(C\)', '', q["question_text"])
    t = re.sub(r'\s+', ' ', t).strip()
    if len(t) < 15: return None
    opts = []
    for o in q["options"]:
        o = re.sub(r'MEDIAEDUKASI\.MY\.ID|\s+', ' ', o).strip()
        if len(o) > 1 and len(o) < 500: opts.append(o)
    if len(opts) < 4: return None
    while len(opts) < 5: opts.append("-")
    return {"section": q["section"], "question_text": t, "options": opts[:5]}

cleaned = [c for q in all_q if (c := clean(q))]
print(f"After cleaning: {len(cleaned)}")

# Dedup
seen = set()
unique = []
for q in cleaned:
    key = re.sub(r'\s+', '', q["question_text"].lower())[:100]
    if key not in seen:
        seen.add(key)
        unique.append(q)

print(f"After dedup: {len(unique)}")
sec_count = Counter(q["section"] for q in unique)
print(f"By section: {dict(sec_count)}")

# Insert to DB
import pymysql
from dotenv import load_dotenv
load_dotenv("/root/cpns/backend/.env")

conn = pymysql.connect(host="localhost", user="root", password=os.getenv("DB_PASSWORD",""), database="cpns")
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM questions")
existing = cur.fetchone()[0]

years = [2020,2021,2022,2023,2024,2025]
diffs = ["mudah","sedang","sulit"]
topics = {"TWK":["Pancasila","UUD 1945","Bhinneka Tunggal Ika","Sejarah Indonesia","Hankam"],
          "TIU":["Sinonim","Antonim","Analogi","Silogisme","Deret Angka","Matematika Dasar","Pemahaman Bacaan"],
          "TKP":["Pelayanan Publik","Profesionalisme","Integritas","Sosial Budaya","Teknologi Informasi","Anti Radikalisme","Bela Negara","Jejaring Kerja"]}

insert_sql = "INSERT INTO questions (section, topic, year, difficulty, question_text, options, correct_answer, explanation) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
inserted = 0
for i in range(0, len(unique), 100):
    batch = unique[i:i+100]
    vals = [(q["section"], random.choice(topics.get(q["section"],["Umum"])), random.choice(years), random.choice(diffs),
             q["question_text"], json.dumps(q["options"], ensure_ascii=False), 0,
             f"Soal dari bank soal CPNS ({q.get('source_file','PDF')})") for q in batch]
    cur.executemany(insert_sql, vals)
    conn.commit()
    inserted += len(batch)

cur.execute("SELECT COUNT(*) FROM questions")
total = cur.fetchone()[0]
cur.execute("SELECT section, COUNT(*) FROM questions GROUP BY section ORDER BY section")
secs = cur.fetchall()
conn.close()

print(f"\n=== FINAL ===")
print(f"Was: {existing}, Added: {inserted}, Total: {total}")
for s, c in secs:
    print(f"  {s}: {c}")
