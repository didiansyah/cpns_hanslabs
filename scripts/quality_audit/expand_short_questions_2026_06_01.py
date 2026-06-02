import re
import sys
sys.path.insert(0, "/root/cpns/backend")
from db import SessionLocal
from models import Question

WORD_PROMPT_RE = re.compile(r"^(Sinonim|Antonim) dari kata '([^']+)' adalah\.\.\.$", re.I)
ANALOGY_MARKERS = (" : ", "= ...", "=....", "= …", "...")
MATH_RE = re.compile(r"(\d|\bx\b|persen|pangkat|rata-rata|hasil kali|kg|ons|kwintal|gram|\+|\-|=)", re.I)
SEQUENCE_RE = re.compile(r"^[-\d,\s]+\??$|^[-\d,\s]+,$")


def normalized_topic(text: str, topic: str) -> str:
    if SEQUENCE_RE.match(text.strip()) or text.strip().endswith("...?" ):
        return "Deret Angka"
    if MATH_RE.search(text) and not " : " in text:
        return "Matematika Dasar"
    if " : " in text or "= ..." in text or "=...." in text or text.strip().startswith("..."):
        return "Analogi"
    return topic


def expand_question(q: Question) -> str:
    text = (q.question_text or "").strip()
    topic = q.topic or ""
    match = WORD_PROMPT_RE.match(text)
    if match:
        kind, word = match.groups()
        if kind.lower() == "sinonim":
            return f"Dalam tes verbal, pilih kata yang memiliki makna paling sama dengan kata '{word}'."
        return f"Dalam tes verbal, pilih kata yang memiliki makna paling berlawanan dengan kata '{word}'."
    if topic == "Analogi" or " : " in text or text.startswith("..."):
        return f"Tentukan pasangan kata yang memiliki hubungan analogi paling tepat untuk melengkapi bentuk berikut: {text}"
    if topic == "Deret Angka" or SEQUENCE_RE.match(text):
        return f"Tentukan angka berikutnya dari pola deret berikut: {text}"
    if topic == "Matematika Dasar" or MATH_RE.search(text):
        return f"Selesaikan soal hitung berikut dan pilih jawaban yang paling tepat: {text}"
    if topic == "Silogisme":
        return f"Berdasarkan premis berikut, tentukan kesimpulan yang paling logis: {text}"
    if topic == "Pemahaman Bacaan" or text.startswith("'"):
        return f"Baca pernyataan berikut, lalu pilih makna atau kesimpulan yang paling tepat: {text}"
    if q.section == "TWK":
        return f"Dalam konteks materi {topic}, jawaban yang paling tepat untuk pertanyaan berikut adalah: {text}"
    if q.section == "TKP":
        return f"Pada situasi kerja berikut, pilih respons yang paling tepat dan profesional: {text}"
    return f"Pilih jawaban yang paling tepat untuk pertanyaan berikut: {text}"


def main():
    db = SessionLocal()
    changed = 0
    topic_changed = 0
    for q in db.query(Question).all():
        original_text = q.question_text
        original_topic = q.topic
        q.topic = normalized_topic(q.question_text or "", q.topic or "")
        if q.topic != original_topic:
            topic_changed += 1
        if len((q.question_text or "").strip()) < 56:
            q.question_text = expand_question(q)
        if q.question_text != original_text or q.topic != original_topic:
            changed += 1
    db.commit()
    db.close()
    print(f"updated_questions={changed} topic_changed={topic_changed}")

if __name__ == "__main__":
    main()
