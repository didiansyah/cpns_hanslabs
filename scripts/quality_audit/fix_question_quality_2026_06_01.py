import os
import sys

sys.path.insert(0, "/root/cpns/backend")
from db import SessionLocal
from models import Question

TYPO_REPLACEMENTS = {
    "Kedaan": "Keadaan",
    "kedaan": "keadaan",
    " bias berlaku": " bisa berlaku",
    " bias ": " bisa ",
    "kapanpun": "kapan pun",
    "didalam": "di dalam",
}

# Question-specific surgical fixes from audit.
OPTION_FIXES = {
    1853: [
        "Ketetapan",
        "Kebimbangan",
        "Keputusan",
        "Penyelesaian",
        "Tekad",
    ],
    2482: [
        "Bantahan atau keberatan yang diajukan terdakwa/penasihat hukum terhadap dakwaan jaksa",
        "Putusan akhir hakim atas perkara pidana",
        "Tuntutan pidana yang dibacakan jaksa penuntut umum",
        "Keterangan saksi dalam persidangan perkara pidana",
        "Upaya hukum setelah putusan berkekuatan hukum tetap",
    ],
}

# Duplicate TKP items with same stem; keep the lower ID, improve wording, retire duplicate by making it distinct but valid.
TKP_FIXES = {
    2350: "Di tengah proyek besar yang membutuhkan tanggung jawab tinggi, saya mengalami kegagalan besar. Sikap saya sebaiknya adalah ...",
    3085: "Saat tugas tim mengalami kegagalan besar dan berdampak pada target kerja, respons terbaik saya adalah ...",
}


def clean_text(text: str) -> str:
    value = text or ""
    for old, new in TYPO_REPLACEMENTS.items():
        value = value.replace(old, new)
    value = value.replace("yang mana artinya adalah", "istilah tersebut berarti")
    return value


def main():
    db = SessionLocal()
    changed = 0
    for q in db.query(Question).all():
        original_text = q.question_text
        original_options = q.options
        original_explanation = q.explanation

        q.question_text = clean_text(q.question_text)
        q.explanation = clean_text(q.explanation)

        if isinstance(q.options, list):
            cleaned_options = []
            for opt in q.options:
                if isinstance(opt, dict):
                    opt = {**opt, "text": clean_text(str(opt.get("text", "")))}
                elif isinstance(opt, str):
                    opt = clean_text(opt)
                cleaned_options.append(opt)
            q.options = cleaned_options

        if q.id in OPTION_FIXES:
            q.options = OPTION_FIXES[q.id]
            if q.correct_answer is None or q.correct_answer > 4:
                q.correct_answer = 0

        if q.id in TKP_FIXES:
            q.question_text = TKP_FIXES[q.id]
            if isinstance(q.options, list):
                seen = set()
                fixed = []
                for idx, opt in enumerate(q.options):
                    if isinstance(opt, dict):
                        text = clean_text(str(opt.get("text", ""))).strip()
                        if text.lower() in seen:
                            text = f"{text} dengan menyusun langkah perbaikan yang terukur"
                        seen.add(text.lower())
                        fixed.append({**opt, "text": text})
                    else:
                        text = clean_text(str(opt)).strip()
                        if text.lower() in seen:
                            text = f"{text} dengan langkah perbaikan terukur"
                        seen.add(text.lower())
                        fixed.append(text)
                q.options = fixed

        if q.question_text != original_text or q.options != original_options or q.explanation != original_explanation:
            changed += 1
    db.commit()
    print(f"updated_questions={changed}")
    db.close()


if __name__ == "__main__":
    main()
