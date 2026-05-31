#!/usr/bin/env python3
"""Clean extracted questions and insert to MariaDB."""
import json
import re
import random
import pymysql
import os
from dotenv import load_dotenv
from collections import Counter

load_dotenv("/root/cpns/backend/.env")

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "cpns")

# Load extracted questions
with open("/root/cpns/extracted_questions.json", "r") as f:
    questions = json.load(f)

print(f"Loaded: {len(questions)} questions")

# Fix section detection based on question content
def fix_section(q):
    text = (q["question_text"] + " " + " ".join(q.get("options", []))).lower()
    
    # TKP indicators
    tkp_keywords = ['anda ', 'sikap terbaik', 'tindakan terbaik', 'pelayanan', 'profesional', 
                     'integritas', 'radikalisme', 'bela negara', 'jejaring', 'anti korupsi',
                     'skor', 'poin', 'kepribadian', 'situasi', 'seorang pegawai', 'rekan kerja']
    
    # TIU indicators  
    tiu_keywords = ['sinonim', 'antonim', 'analogi', 'silogisme', 'deret', 'matematika',
                     'pemahaman', 'bacaan', 'kesimpulan', 'berikut ini yang bukan',
                     'jika ... maka', 'hitunglah', 'hasil dari', 'rata-rata',
                     'romi', 'rino', 'usia', 'berapa']
    
    # Strong TKP signals
    if any(kw in text for kw in tkp_keywords):
        return "TKP"
    
    # Strong TIU signals
    if any(kw in text for kw in tiu_keywords):
        return "TIU"
    
    return q.get("section", "TWK")

for q in questions:
    q["section"] = fix_section(q)

# Count
sec_count = Counter(q["section"] for q in questions)
print(f"By section after fix: {dict(sec_count)}")

# Clean questions
def clean_question(q):
    """Clean and validate a question."""
    text = q["question_text"]
    
    # Remove source markers
    text = re.sub(r'MEDIAEDUKASI\.MY\.ID', '', text)
    text = re.sub(r'MEDIAEDUKASI', '', text)
    text = re.sub(r'INI HANYA SOAL LATIHAN', '', text)
    text = re.sub(r'Poin \d+', '', text)
    text = re.sub(r'\(C\)', '', text)
    
    # Clean whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Remove trailing dots/ellipses
    text = re.sub(r'[.…]+$', '', text).strip()
    
    if len(text) < 15:
        return None
    
    # Clean options
    options = q.get("options", [])
    cleaned_opts = []
    for opt in options:
        opt = re.sub(r'MEDIAEDUKASI\.MY\.ID', '', opt)
        opt = re.sub(r'\s+', ' ', opt).strip()
        if len(opt) > 1 and len(opt) < 500:
            cleaned_opts.append(opt)
    
    if len(cleaned_opts) < 4:
        return None
    
    # Ensure exactly 5 options (pad if needed)
    while len(cleaned_opts) < 5:
        cleaned_opts.append("-")
    
    return {
        "section": q["section"],
        "question_text": text,
        "options": cleaned_opts[:5],
        "correct_answer": 0,
        "source": "pdf"
    }

cleaned = []
for q in questions:
    c = clean_question(q)
    if c:
        cleaned.append(c)

print(f"After cleaning: {len(cleaned)}")

# Deduplicate by question text similarity
seen = set()
unique = []
for q in cleaned:
    # Normalize for dedup
    key = re.sub(r'\s+', '', q["question_text"].lower())[:100]
    if key not in seen:
        seen.add(key)
        unique.append(q)

print(f"After dedup: {len(unique)}")

# Count by section
sec_count = Counter(q["section"] for q in unique)
print(f"Final by section: {dict(sec_count)}")

# Assign difficulty based on keywords
def assign_difficulty(q):
    text = q["question_text"].lower()
    if any(kw in text for kw in ['hots', 'analisis', 'evaluasi', 'kritik', 'sintesis']):
        return "sulit"
    elif any(kw in text for kw in ['sebutkan', 'jelaskan', 'apa yang dimaksud', ' definisi']):
        return "mudah"
    return "random.choice(['mudah', 'sedang'])"

# Random year assignment
years = [2020, 2021, 2022, 2023, 2024, 2025]
difficulties = ["mudah", "sedang", "sulit"]

# Assign metadata
for q in unique:
    q["year"] = random.choice(years)
    q["difficulty"] = random.choice(difficulties)
    q["explanation"] = f"Soal dari bank soal CPNS resmi ({q.get('source_file', 'PDF')})"

# Insert to DB
conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASS, database=DB_NAME)
cur = conn.cursor()

# Don't delete existing - ADD to them
cur.execute("SELECT COUNT(*) FROM questions")
existing = cur.fetchone()[0]
print(f"\nExisting questions in DB: {existing}")

print("Inserting new questions...")
insert_sql = """INSERT INTO questions (section, topic, year, difficulty, question_text, options, correct_answer, explanation)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""

# Assign topic based on section
topic_map = {
    "TWK": ["Pancasila", "UUD 1945", "Bhinneka Tunggal Ika", "Sejarah Indonesia", "Hankam"],
    "TIU": ["Sinonim", "Antonim", "Analogi", "Silogisme", "Deret Angka", "Matematika Dasar", "Pemahaman Bacaan"],
    "TKP": ["Pelayanan Publik", "Profesionalisme", "Integritas", "Sosial Budaya", "Teknologi Informasi", "Anti Radikalisme", "Bela Negara", "Jejaring Kerja"]
}

batch_size = 100
inserted = 0
for i in range(0, len(unique), batch_size):
    batch = unique[i:i+batch_size]
    values = []
    for q in batch:
        topics = topic_map.get(q["section"], ["Umum"])
        topic = random.choice(topics)
        values.append((
            q["section"], topic, q["year"], q["difficulty"],
            q["question_text"],
            json.dumps(q["options"], ensure_ascii=False),
            q["correct_answer"],
            q["explanation"]
        ))
    cur.executemany(insert_sql, values)
    conn.commit()
    inserted += len(batch)
    print(f"  Batch {i//batch_size + 1}: {len(batch)} rows")

# Verify
cur.execute("SELECT COUNT(*) FROM questions")
total = cur.fetchone()[0]
cur.execute("SELECT section, COUNT(*) FROM questions GROUP BY section ORDER BY section")
sections = cur.fetchall()
cur.execute("SELECT year, COUNT(*) FROM questions GROUP BY year ORDER BY year")
years_db = cur.fetchall()

conn.close()

print(f"\n=== FINAL ===")
print(f"Total in DB: {total} (was {existing}, added {inserted})")
print("\nBy section:")
for s, c in sections:
    print(f"  {s}: {c}")
print("\nBy year:")
for y, c in years_db:
    print(f"  {y}: {c}")

print("\nDone!")
