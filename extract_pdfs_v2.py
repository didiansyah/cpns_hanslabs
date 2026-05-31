#!/usr/bin/env python3
"""Extract CPNS questions from PDF bank soal files - improved parser."""
import fitz
import re
import json
import os

PDF_DIR = "/root/cpns/bank-soal"
OUTPUT = "/root/cpns/extracted_questions.json"

PDFS = [
    ("TWK+PEMBAHASAN.pdf", "TWK"),
    ("TWK+TIU+TKP + PEMBAHASAN.pdf", None),
    ("TWK+TIU+TKP+ PEMBAHASAN.pdf", None),
    ("SOAL TO 1 + KUNCI JAWABAN/SOAL TKD-TWK.pdf", "TWK"),
    ("SOAL TO 1 + KUNCI JAWABAN/SOAL TKD-TIU.pdf", "TIU"),
    ("SOAL TO 1 + KUNCI JAWABAN/SOAL TKD-TKP.pdf", "TKP"),
    ("CPNS/HOTS SKD CPNS 01 Soal dan Pembahasan.pdf", None),
    ("CPNS/HOTS SKD CPNS 02 Soal dan Pembahasan.pdf", None),
    ("CPNS/TKP CPNS.pdf", "TKP"),
    ("CPNS/KISI-KISI TKD CPNS 2021.pdf", None),
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

def parse_questions_v2(text, default_section=None):
    """Parse questions handling multi-line options."""
    questions = []
    
    # Detect section from headers
    def detect_section(text_block):
        t = text_block.lower()
        if 'twk' in t or 'wawasan kebangsaan' in t or 'ideologi' in t:
            return "TWK"
        elif 'tiu' in t or 'intelegensi umum' in t or 'verbal' in t or 'numerik' in t:
            return "TIU"
        elif 'tkp' in t or 'karakteristik pribadi' in t:
            return "TKP"
        return None
    
    # Clean text: normalize whitespace
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    # Split into blocks by double newline or question number pattern
    # First, find all question boundaries
    q_pattern = re.compile(r'(?:^|\n)\s*(\d+)\.\s+', re.MULTILINE)
    
    # Find all question starts
    q_starts = []
    for m in q_pattern.finditer(text):
        q_starts.append((m.start(), m.group(1)))
    
    current_section = default_section
    
    for idx, (start, qnum) in enumerate(q_starts):
        # Get text until next question
        end = q_starts[idx+1][0] if idx+1 < len(q_starts) else len(text)
        block = text[start:end].strip()
        
        # Check for section header in block
        sec = detect_section(block)
        if sec:
            current_section = sec
        
        # Parse the block
        # Remove the question number prefix
        block = re.sub(r'^\s*\d+\.\s*', '', block)
        
        # Find options: a. b. c. d. e. (with possible newlines)
        opt_pattern = re.compile(r'\n\s*([a-e])[.):\s]+', re.IGNORECASE)
        opt_matches = list(opt_pattern.finditer(block))
        
        if len(opt_matches) < 3:
            continue
        
        # Question text is before first option
        q_text = block[:opt_matches[0].start()].strip()
        # Clean up question text
        q_text = re.sub(r'\s+', ' ', q_text).strip()
        
        if len(q_text) < 10:
            continue
        
        # Extract options
        options = []
        for i, m in enumerate(opt_matches):
            opt_start = m.end()
            opt_end = opt_matches[i+1].start() if i+1 < len(opt_matches) else len(block)
            opt_text = block[opt_start:opt_end].strip()
            opt_text = re.sub(r'\s+', ' ', opt_text).strip()
            if opt_text:
                options.append(opt_text)
        
        if len(options) < 4:
            continue
        
        # Limit to 5 options
        options = options[:5]
        
        questions.append({
            "section": current_section or "TWK",
            "question_text": q_text,
            "options": options,
            "correct_answer": 0,  # Will be set later from answer key
            "source": "pdf"
        })
    
    return questions

all_questions = []

for pdf_file, default_sec in PDFS:
    pdf_path = os.path.join(PDF_DIR, pdf_file)
    if not os.path.exists(pdf_path):
        print(f"SKIP: {pdf_file}")
        continue
    
    print(f"\n{'='*60}")
    print(f"Extracting: {pdf_file}")
    text = extract_text(pdf_path)
    print(f"  Text: {len(text)} chars")
    
    if len(text) < 100:
        continue
    
    questions = parse_questions_v2(text, default_sec)
    print(f"  Parsed: {len(questions)} questions")
    
    for q in questions:
        q["source_file"] = pdf_file
    
    all_questions.extend(questions)

print(f"\n{'='*60}")
print(f"TOTAL: {len(all_questions)}")

# Count by section
from collections import Counter
sec_count = Counter(q["section"] for q in all_questions)
print(f"By section: {dict(sec_count)}")

# Show quality samples
print(f"\nQuality samples:")
for sec in ["TWK", "TIU", "TKP"]:
    qs = [q for q in all_questions if q["section"] == sec]
    if qs:
        q = qs[0]
        print(f"\n[{sec}] {q['question_text'][:100]}")
        for i, opt in enumerate(q['options'][:5]):
            print(f"  {chr(65+i)}. {opt[:80]}")

# Save
with open(OUTPUT, 'w', encoding='utf-8') as f:
    json.dump(all_questions, f, ensure_ascii=False, indent=2)

print(f"\nSaved {len(all_questions)} questions to {OUTPUT}")
