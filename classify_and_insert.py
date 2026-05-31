#!/usr/bin/env python3
"""Classify UNK questions by keyword matching, then insert all new questions to DB."""
import json
import re
import mysql.connector

DB_CONFIG = {"host": "localhost", "user": "root", "database": "cpns"}
INPUT = "/root/cpns/new_extracted.json"

# Keywords for classification
TWK_KEYWORDS = [
    'pancasila', 'uud', 'uud 1945', 'mpr', 'dpr', 'dprd', 'presiden',
    'proklamasi', 'sejarah', 'pemerintahan', 'negara', 'demokrasi', 'ham',
    'bhineka', 'nkri', 'bpupki', 'ppki', 'soekarno', 'hatta',
    'undang-undang', 'tap mpr', 'pasal', 'konstitusi', 'hukum dasar',
    'ideologi', 'sila', 'dasar negara', 'pembukaan', 'batang tubuh',
    'gotong royong', 'musyawarah', 'keadilan', 'persatuan',
    'perwakilan', 'perundangan', 'ketatanegaraan', 'hankam',
    'pertahanan', 'keamanan', 'militer', 'tni', 'polri',
    'pilkada', 'pemilu', 'partai', 'lembaga negara',
    'ir. soekarno', 'moh. hatta', 'deklarasi', 'sumpah pemuda',
]

TIU_KEYWORDS = [
    'deret', 'analogi', 'sinonim', 'antonim', 'silogisme',
    'matematika', 'logika', 'analisis', 'cerita', 'bacaan',
    'tabel', 'grafik', 'barisan', 'hitungan', 'jumlah',
    'selisih', 'kali', 'bagi', 'pembulatan',
    'pemahaman', 'kesimpulan', 'asumsi', 'argumen',
    'sebanding', 'berlawanan', 'persamaan', 'perbedaan',
    'getir', 'marah', 'kata', 'hubungan kata',
    'jika ... maka', 'semua', 'beberapa', 'tidak semua',
    'pola gambar', 'deret angka', 'aritmatika',
]

TKP_KEYWORDS = [
    'pelayanan', 'integritas', 'profesional', 'konflik',
    'keputusan', 'situasi', 'rekan', 'atasan', 'inisiatif',
    'kerja sama', 'tim', 'disiplin', 'tanggung jawab',
    'motivasi', 'kepemimpinan', 'komunikasi', 'etika',
    'organisasi', 'bawahan', 'pengawasan', 'koordinasi',
    'pelayanan publik', 'kepentingan umum', 'netralitas',
    'anti radikalisme', 'bela negara', 'jejaring kerja',
    'sosial budaya', 'teknologi informasi',
    'anda seorang', 'ketika anda', 'jika anda',
    'sebagai seorang', 'dalam situasi',
]


def classify_question(text):
    """Classify question by keywords."""
    text_lower = text.lower()
    
    twk_score = sum(1 for kw in TWK_KEYWORDS if kw in text_lower)
    tiu_score = sum(1 for kw in TIU_KEYWORDS if kw in text_lower)
    tkp_score = sum(1 for kw in TKP_KEYWORDS if kw in text_lower)
    
    # TKP questions often start with "Anda" or describe situations
    if re.search(r'^(?:anda|ketika|sebagai\s+seorang|dalam\s+situasi)', text_lower):
        tkp_score += 2
    
    scores = {'TWK': twk_score, 'TIU': tiu_score, 'TKP': tkp_score}
    best = max(scores, key=scores.get)
    
    if scores[best] > 0:
        return best
    return 'TWK'  # Default to TWK for CPNS content


def main():
    with open(INPUT) as f:
        questions = json.load(f)
    
    print(f"📊 Loaded {len(questions)} questions")
    
    # Classify UNK questions
    classified = {'TWK': 0, 'TIU': 0, 'TKP': 0}
    for q in questions:
        if not q.get('section'):
            section = classify_question(q['question_text'])
            q['section'] = section
            classified[section] += 1
    
    print(f"🏷️  Classified UNK questions: {classified}")
    
    # Final section breakdown
    sections = {}
    for q in questions:
        s = q.get('section', 'UNK')
        sections[s] = sections.get(s, 0) + 1
    print(f"📊 Final breakdown: {sections}")
    
    # Insert to DB
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Get existing for final dedup
        cursor.execute("SELECT question_text FROM questions")
        existing = set()
        for row in cursor.fetchall():
            norm = re.sub(r'\s+', ' ', row[0].strip().lower())[:100]
            existing.add(norm)
        
        insert_sql = """
            INSERT INTO questions (section, topic, year, difficulty, question_text, options, correct_answer, explanation)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        inserted = 0
        skipped = 0
        for q in questions:
            norm = re.sub(r'\s+', ' ', q['question_text'].strip().lower())[:100]
            if norm in existing:
                skipped += 1
                continue
            
            options_json = json.dumps(q['options'], ensure_ascii=False)
            section = q.get('section', 'TWK')
            topic = section  # Default topic = section
            source = q.get('source_file', '')
            
            # Convert letter answer to 0-indexed int (a=0, b=1, c=2, d=3, e=4)
            correct = q.get('correct_answer')
            if correct and isinstance(correct, str):
                correct = ord(correct.lower()) - ord('a')
            elif correct is None:
                correct = 0  # Default
            
            cursor.execute(insert_sql, (
                section,
                topic,
                None,  # year
                None,  # difficulty
                q['question_text'],
                options_json,
                correct,
                None,  # explanation
            ))
            inserted += 1
            existing.add(norm)
        
        conn.commit()
        
        # Verify total
        cursor.execute("SELECT COUNT(*) FROM questions")
        total = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        print(f"\n✅ Inserted: {inserted}")
        print(f"⏭️  Skipped (dupes): {skipped}")
        print(f"📊 Total in DB: {total}")
        
    except Exception as e:
        print(f"❌ DB Error: {e}")


if __name__ == "__main__":
    main()
