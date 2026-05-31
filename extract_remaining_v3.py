#!/usr/bin/env python3
"""Extract CPNS questions v4 - improved section detection with position-based mapping."""
import fitz
import re
import json
import os
import mysql.connector

PDF_DIR = "/root/cpns/bank-soal"
OUTPUT = "/root/cpns/new_extracted.json"
DB_CONFIG = {"host": "localhost", "user": "root", "database": "cpns"}

PDFS = [
    ("1.  SOAL LATIHAN TWK-TIU-TKP.pdf", None),
    ("2. SOAL LATIHAN TWK-TIU-TKP.pdf", None),
    ("3. SOAL LATIHAN TWK-TIU-TKP.pdf", None),
    ("4. SOAL LATIHAN TWK-TIU-TKP.pdf", None),
    ("5. SOAL LATIHAN TWK-TIU-TKP.pdf", None),
    ("6. SOAL LATIHAN TWK-TIU-TKP.pdf", None),
    ("7. SOAL LATIHAN TWK-TIU-TKP.pdf", None),
    ("8. SOAL LATIHAN TWK-TIU-TKP.pdf", None),
    ("A. SOAL LATIHAN HOST.pdf", None),
    ("B.SOAL LATIHAN HOST.pdf", None),
    ("MATERI TWK.pdf", "TWK"),
    ("SOAL KILAS BALIK CPNS 2015.pdf", None),
    ("SOAL LATIAN TIU VERBAL.pdf", "TIU"),
    ("SUPER DIKTAT CPNS.pdf", None),
    ("TKP CPNS.pdf", "TKP"),
]


def extract_text(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        print(f"  Error: {e}")
        return ""


def detect_section_boundaries(text):
    """Find section boundaries in text. Returns list of (position, section)."""
    boundaries = []
    
    patterns = [
        # Explicit with NOMOR range
        (r'(?:WAWASAN\s+KEBANGSAAN|TWK).*?NOMOR\s+(\d+)\s*(?:s\.d\.|sampai|-)\s*(\d+)', 'TWK', True),
        (r'(?:INTELEGENSI\s*UMUM|TIU).*?NOMOR\s+(\d+)\s*(?:s\.d\.|sampai|-)\s*(\d+)', 'TIU', True),
        (r'(?:KARAKTERISTIK\s*PRIBADI|TKP).*?NOMOR\s+(\d+)\s*(?:s\.d\.|sampai|-)\s*(\d+)', 'TKP', True),
        # Short headers - position based
        (r'(?:TES\s+)?WAWASAN(?:\s+KEBANGSAAN)?', 'TWK', False),
        (r'(?:TES\s+)?INTELEGENSI(?:\s+UMUM)?', 'TIU', False),
        (r'(?:TES\s+)?KARAKTERISTIK(?:\s+PRIBADI)?', 'TKP', False),
        (r'(?:TES\s+)?KARAKTERSITIK(?:\s+KEPRIBADIAN)?', 'TKP', False),
        (r'PEMBAHASAN\s+SOAL\s+TES\s+TWK', 'TWK', False),
        (r'PEMBAHASAN\s+SOAL\s+TES\s+TIU', 'TIU', False),
        (r'PEMBAHASAN\s+SOAL\s+TES\s+TKP', 'TKP', False),
        (r'TES\s+TKP', 'TKP', False),
    ]
    
    for pattern, section, has_range in patterns:
        for m in re.finditer(pattern, text, re.IGNORECASE):
            if has_range:
                start_num = int(m.group(1))
                end_num = int(m.group(2))
                boundaries.append((m.start(), section, start_num, end_num))
            else:
                boundaries.append((m.start(), section, None, None))
    
    boundaries.sort(key=lambda x: x[0])
    return boundaries


def parse_questions(text, default_section=None, source_file=""):
    """Parse questions with improved section detection."""
    questions = []
    lines = text.split('\n')
    
    # Find section boundaries
    boundaries = detect_section_boundaries(text)
    
    # Build number-based section map from range-based boundaries
    num_section_map = {}
    for _, section, start_num, end_num in boundaries:
        if start_num and end_num:
            for n in range(start_num, end_num + 1):
                num_section_map[n] = section
    
    # Build position-based section map
    pos_sections = []
    for pos, section, _, _ in boundaries:
        pos_sections.append((pos, section))
    
    def get_section_for_pos(text_pos, q_num):
        # First try number-based
        if q_num in num_section_map:
            return num_section_map[q_num]
        # Then try position-based
        current = default_section
        for pos, section in pos_sections:
            if text_pos >= pos:
                current = section
            else:
                break
        return current or default_section
    
    # Parse answer keys
    answer_keys = {}
    answer_patterns = [
        re.compile(r'^\s*(\d+)\s*[\.\):]\s*\(?([a-eA-E])\)?'),
        re.compile(r'^\s*(\d+)\s+\(?([a-eA-E])\)?\s*$'),
        re.compile(r'^\s*No\.?\s*(\d+)\s*[:=]\s*([a-eA-E])', re.IGNORECASE),
    ]
    
    # Find answer key section
    answer_start = None
    for i, line in enumerate(lines):
        ls = line.strip()
        if re.search(r'(?:KUNCI|JAWABAN|PEMBAHASAN)\s*(?:JAWABAN)?', ls, re.IGNORECASE) and len(ls) < 50:
            answer_start = i
            break
    
    if answer_start:
        for line in lines[answer_start:]:
            ls = line.strip()
            for pat in answer_patterns:
                m = pat.match(ls)
                if m:
                    answer_keys[int(m.group(1))] = m.group(2).lower()
                    break
    
    # Also try inline answer format: "1. A" or "1 A"
    if not answer_keys:
        for line in lines:
            ls = line.strip()
            m = re.match(r'^(\d+)\s+([a-eA-E])\s*$', ls)
            if m:
                answer_keys[int(m.group(1))] = m.group(2).lower()
    
    # Parse questions
    q_pattern = re.compile(r'^\s*(\d+)\s*[\.\)]\s*(.+)')
    opt_pattern = re.compile(r'^\s*([a-eA-E])\s*[\.\)]\s*(.+)')
    inline_opt_pattern = re.compile(r'([a-eA-E])\.\s+([A-Z\u00C0-\u024F][^.]*?)(?=\s+[b-eB-E]\.\s|$)')
    
    current_q = None
    current_opts = []
    current_num = 0
    current_q_pos = 0
    
    for i, line in enumerate(lines):
        ls = line.strip()
        if not ls:
            continue
        
        # Skip headers/metadata
        if len(ls) < 3:
            continue
        if re.match(r'^(?:BAGIAN|SOAL\s+(?:DAN|LATIHAN)|INI\s+HANYA|PEMBAHASAN(?:\s+SOAL)?|Poin\s+No|NOMOR\s+\d)', ls, re.IGNORECASE):
            continue
        
        # New question
        q_match = q_pattern.match(ls)
        if q_match:
            num = int(q_match.group(1))
            # Save previous question
            if current_q and len(current_opts) >= 3:
                sec = get_section_for_pos(current_q_pos, current_num)
                questions.append({
                    "section": sec,
                    "question_text": current_q.strip(),
                    "options": current_opts[:],
                    "correct_answer": answer_keys.get(current_num),
                    "source_file": source_file,
                })
            current_num = num
            current_q = q_match.group(2)
            current_opts = []
            # Find position in original text
            q_text = q_match.group(0)
            current_q_pos = text.find(q_text, max(0, current_q_pos - 100))
            if current_q_pos == -1:
                current_q_pos = 0
            continue
        
        # Option on its own line
        o_match = opt_pattern.match(ls)
        if o_match and current_q:
            current_opts.append(o_match.group(2).strip())
            continue
        
        # Inline options
        if current_q and re.search(r'[a-eA-E]\.\s+\w', ls):
            inline = inline_opt_pattern.findall(ls)
            if len(inline) >= 2:
                for letter, text_opt in inline:
                    current_opts.append(text_opt.strip())
                continue
        
        # Continuation of question text
        if current_q and not current_opts:
            if len(ls) > 3 and not re.match(r'^\d+[\.\)]', ls):
                current_q += " " + ls
    
    # Last question
    if current_q and len(current_opts) >= 3:
        sec = get_section_for_pos(current_q_pos, current_num)
        questions.append({
            "section": sec,
            "question_text": current_q.strip(),
            "options": current_opts[:],
            "correct_answer": answer_keys.get(current_num),
            "source_file": source_file,
        })
    
    return questions


def get_existing_questions():
    """Get existing question texts for dedup."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT question_text FROM questions")
        existing = set()
        for row in cursor.fetchall():
            text = re.sub(r'\s+', ' ', row[0].strip().lower())[:100]
            existing.add(text)
        cursor.close()
        conn.close()
        return existing
    except Exception as e:
        print(f"⚠️  DB dedup check failed: {e}")
        return set()


def normalize_for_dedup(text):
    text = re.sub(r'\s+', ' ', text.strip().lower())
    text = re.sub(r'[^\w\s]', '', text)
    return text[:100]


def main():
    all_questions = []
    stats = {}
    
    for pdf_name, default_section in PDFS:
        pdf_path = os.path.join(PDF_DIR, pdf_name)
        if not os.path.exists(pdf_path):
            print(f"⚠️  Not found: {pdf_name}")
            continue
        
        print(f"📄 {pdf_name}")
        text = extract_text(pdf_path)
        if not text.strip():
            print(f"   ❌ No text extracted")
            continue
        
        questions = parse_questions(text, default_section, pdf_name)
        print(f"   ✅ {len(questions)} questions")
        
        if questions:
            sections = {}
            for q in questions:
                s = q.get("section") or "UNK"
                sections[s] = sections.get(s, 0) + 1
            print(f"   📊 {sections}")
        
        all_questions.extend(questions)
        stats[pdf_name] = len(questions)
    
    # Dedup
    print(f"\n🔍 Dedup against existing DB...")
    existing = get_existing_questions()
    
    new_questions = []
    dupes = 0
    for q in all_questions:
        norm = normalize_for_dedup(q["question_text"])
        if norm in existing:
            dupes += 1
        else:
            new_questions.append(q)
            existing.add(norm)
    
    print(f"   Extracted: {len(all_questions)} | Dupes: {dupes} | New: {len(new_questions)}")
    
    # Section breakdown
    section_counts = {}
    for q in new_questions:
        s = q.get("section") or "UNK"
        section_counts[s] = section_counts.get(s, 0) + 1
    print(f"\n📊 New by section:")
    for s, c in sorted(section_counts.items()):
        print(f"   {s}: {c}")
    
    with open(OUTPUT, 'w') as f:
        json.dump(new_questions, f, ensure_ascii=False, indent=2)
    print(f"\n💾 Saved to {OUTPUT}")
    
    return new_questions


if __name__ == "__main__":
    main()
