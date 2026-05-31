#!/usr/bin/env python3
"""Extract CPNS questions from PDF bank soal files."""
import fitz
import re
import json
import os

PDF_DIR = "/root/cpns/bank-soal"
OUTPUT = "/root/cpns/extracted_questions.json"

# PDFs to extract (CPNS-specific)
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
    ("MATERI SOAL LENGKAP SKD 2020 BY CENDEKIA.pdf", None),
    ("SOAL 2019-2020 CPNS-BUMN BY CENDEKIAPEDIA+PEMBAHASAN.pdf", None),
    ("DRILLING SOAL-SOAL CPNS.pdf", None),
]

def extract_text(pdf_path):
    """Extract text from PDF."""
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

def parse_questions(text, default_section=None):
    """Parse questions from extracted text."""
    questions = []
    
    # Pattern: number. question text \n a. option \n b. option ... \n answer/key
    # Various formats found in PDFs
    
    # Split by question numbers
    # Match patterns like "1. " or "1)" or "Soal 1"
    lines = text.split('\n')
    
    current_q = None
    current_opts = []
    current_section = default_section
    in_options = False
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        
        # Detect section headers
        line_lower = line.lower()
        if any(kw in line_lower for kw in ['tes wawasan kebangsaan', 'twk']):
            current_section = "TWK"
            continue
        elif any(kw in line_lower for kw in ['tes intelegensi umum', 'tiu']):
            current_section = "TIU"
            continue
        elif any(kw in line_lower for kw in ['tes karakteristik pribadi', 'tkp']):
            current_section = "TKP"
            continue
        
        # Detect new question (number followed by period)
        q_match = re.match(r'^(\d+)\.\s*(.+)', line)
        if q_match and len(line) > 10:
            # Save previous question
            if current_q and current_opts:
                questions.append({
                    "section": current_section or "TWK",
                    "question_text": current_q,
                    "options": current_opts,
                    "source": "pdf"
                })
            
            current_q = q_match.group(2).strip()
            current_opts = []
            in_options = True
            continue
        
        # Detect options (a. b. c. d. e.)
        opt_match = re.match(r'^([a-e])[.):\s]+(.+)', line, re.IGNORECASE)
        if opt_match and in_options:
            current_opts.append(opt_match.group(2).strip())
            continue
        
        # Continue question text if no option marker
        if current_q and not opt_match and in_options and len(line) > 3:
            # Could be continuation of question or option
            if current_opts:
                # Append to last option
                current_opts[-1] += " " + line
            else:
                current_q += " " + line
    
    # Save last question
    if current_q and current_opts:
        questions.append({
            "section": current_section or "TWK",
            "question_text": current_q,
            "options": current_opts,
            "source": "pdf"
        })
    
    return questions

all_questions = []

for pdf_file, default_sec in PDFS:
    pdf_path = os.path.join(PDF_DIR, pdf_file)
    if not os.path.exists(pdf_path):
        print(f"SKIP: {pdf_file} not found")
        continue
    
    print(f"\n{'='*60}")
    print(f"Extracting: {pdf_file}")
    text = extract_text(pdf_path)
    print(f"  Text length: {len(text)} chars")
    
    if len(text) < 100:
        print(f"  SKIP: too short")
        continue
    
    questions = parse_questions(text, default_sec)
    print(f"  Questions parsed: {len(questions)}")
    
    for q in questions:
        q["source_file"] = pdf_file
    
    all_questions.extend(questions)

print(f"\n{'='*60}")
print(f"TOTAL QUESTIONS EXTRACTED: {len(all_questions)}")

# Show sample
print(f"\nSample questions:")
for q in all_questions[:5]:
    print(f"  [{q['section']}] {q['question_text'][:80]}...")
    print(f"    Options: {q['options'][:3]}...")

# Save to JSON
with open(OUTPUT, 'w', encoding='utf-8') as f:
    json.dump(all_questions, f, ensure_ascii=False, indent=2)

print(f"\nSaved to {OUTPUT}")
