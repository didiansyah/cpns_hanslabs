import re
import sys
sys.path.insert(0, "/root/cpns/backend")
from db import SessionLocal
from models import Question

PREFIXES = [
    "Selesaikan soal hitung berikut dan pilih jawaban yang paling tepat: ",
    "Pilih jawaban yang paling tepat untuk pertanyaan berikut: ",
]

TWK_RULES = [
    ("Pancasila", ["pancasila", "sila", "garuda", "bpupki", "ppki", "piagam jakarta", "dasar negara"]),
    ("UUD 1945", ["uud", "pasal", "amandemen", "mpr", "dpr", "dpd", "mk", "mahkamah", "konstitusi", "pembukaan"]),
    ("Sejarah Indonesia", ["proklamasi", "sumpah pemuda", "budi utomo", "diponegoro", "cut nyak", "soekarno", "hatta", "kemerdekaan", "penjajahan"]),
    ("Bhinneka Tunggal Ika", ["bhinneka", "keragaman", "toleransi", "plural", "suku", "budaya", "agama"]),
    ("Bela Negara", ["bela negara", "warga negara", "pertahanan", "hankam", "ancaman", "kedaulatan"]),
    ("Anti Radikalisme", ["radikal", "teror", "ekstrem", "intoleran"]),
]

TKP_RULES = [
    ("Pelayanan Publik", ["pelanggan", "masyarakat", "layanan", "pelayanan", "keluhan", "publik", "antrian"]),
    ("Jejaring Kerja", ["tim", "rekan", "atasan", "rapat", "kolabor", "koordinasi", "konflik"]),
    ("Integritas", ["jujur", "gratifikasi", "suap", "aturan", "rahasia", "data", "laporan", "kesalahan"]),
    ("Teknologi Informasi", ["aplikasi", "sistem", "digital", "komputer", "teknologi", "online"]),
]


def strip_bad_prefix(text: str) -> str:
    out = text or ""
    changed = True
    while changed:
        changed = False
        for prefix in PREFIXES:
            if out.startswith(prefix):
                out = out[len(prefix):]
                changed = True
    return out


def classify(text: str, rules, default: str) -> str:
    lower = text.lower()
    for topic, keys in rules:
        if any(key in lower for key in keys):
            return topic
    return default


def main():
    db = SessionLocal()
    changed = 0
    for q in db.query(Question).all():
        original = (q.topic, q.question_text)
        clean = strip_bad_prefix(q.question_text or "")
        if q.section == "TWK":
            q.topic = classify(clean, TWK_RULES, "Hankam" if "negara" in clean.lower() else (q.topic if q.topic not in ("Matematika Dasar", "Analogi", "Deret Angka") else "Pancasila"))
            if len(clean) < 56:
                q.question_text = f"Dalam konteks materi {q.topic}, jawaban yang paling tepat untuk pertanyaan berikut adalah: {clean}"
            else:
                q.question_text = clean
        elif q.section == "TKP":
            q.topic = classify(clean, TKP_RULES, q.topic if q.topic not in ("Matematika Dasar", "Analogi", "Deret Angka") else "Profesionalisme")
            if len(clean) < 56:
                q.question_text = f"Pada situasi kerja berikut, pilih respons yang paling tepat dan profesional: {clean}"
            else:
                q.question_text = clean
        if (q.topic, q.question_text) != original:
            changed += 1
    db.commit()
    db.close()
    print(f"restored_non_tiu_topics={changed}")

if __name__ == "__main__":
    main()
