import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from dotenv import load_dotenv
load_dotenv()
from db import SessionLocal
from models import Question

db = SessionLocal()

questions = [
    # TWK - Pancasila
    {"section": "TWK", "topic": "Pancasila", "year": 2024, "difficulty": "easy", "question_text": "Sila pertama Pancasila berbunyi...", "options": ["Ketuhanan Yang Maha Esa", "Kemanusiaan yang adil dan beradab", "Persatuan Indonesia", "Kerakyatan yang dipimpin oleh hikmat kebijaksanaan dalam permusyawaratan/perwakilan", "Keadilan sosial bagi seluruh rakyat Indonesia"], "correct_answer": 0, "explanation": "Sila pertama: Ketuhanan Yang Maha Esa."},
    {"section": "TWK", "topic": "Pancasila", "year": 2024, "difficulty": "medium", "question_text": "Sila keempat Pancasila berbunyi...", "options": ["Ketuhanan Yang Maha Esa", "Kemanusiaan yang adil dan beradab", "Persatuan Indonesia", "Kerakyatan yang dipimpin oleh hikmat kebijaksanaan dalam permusyawaratan/perwakilan", "Keadilan sosial bagi seluruh rakyat Indonesia"], "correct_answer": 3, "explanation": "Sila keempat: Kerakyatan yang dipimpin oleh hikmat kebijaksanaan dalam permusyawaratan/perwakilan."},
    {"section": "TWK", "topic": "Pancasila", "year": 2025, "difficulty": "hard", "question_text": "Seorang PNS menolak upacara bendera dengan alasan keyakinannya. Sikap yang tepat adalah...", "options": ["Membiarkan karena itu hak pribadi", "Melaporkan langsung ke atasan", "Memahami keyakinannya tapi menjelaskan kewajiban sebagai PNS", "Memaksa untuk ikut upacara", "Mengabaikan dan melanjutkan upacara"], "correct_answer": 2, "explanation": "Sikap tepat: memahami keyakinan tapi menjelaskan kewajiban sebagai PNS sesuai nilai Pancasila."},
    # TWK - UUD 1945
    {"section": "TWK", "topic": "UUD 1945", "year": 2023, "difficulty": "medium", "question_text": "Amandemen UUD 1945 yang mengatur tentang pemilihan presiden secara langsung adalah amandemen ke...", "options": ["Amandemen I", "Amandemen II", "Amandemen III", "Amandemen IV", "Belum diamandemen"], "correct_answer": 3, "explanation": "Amandemen IV mengatur pemilihan presiden dan wakil presiden secara langsung oleh rakyat."},
    {"section": "TWK", "topic": "UUD 1945", "year": 2024, "difficulty": "easy", "question_text": "Pasal 1 ayat 1 UUD 1945 berbunyi...", "options": ["Indonesia adalah negara kesatuan", "Kedaulatan berada di tangan rakyat", "Negara Indonesia adalah negara kesatuan yang berbentuk republik", "Presiden adalah kepala negara", "Majelis Permusyawaratan Rakyat terdiri atas anggota DPR dan DPD"], "correct_answer": 2, "explanation": "Pasal 1 ayat 1: Negara Indonesia adalah negara kesatuan yang berbentuk republik."},
    # TWK - NKRI
    {"section": "TWK", "topic": "NKRI", "year": 2024, "difficulty": "easy", "question_text": "Lambang negara Indonesia adalah...", "options": ["Garuda Pancasila", "Bhinneka Tunggal Ika", "Merah Putih", "Burung Elang", "Nusantara"], "correct_answer": 0, "explanation": "Lambang negara Indonesia adalah Garuda Pancasila dengan semboyan Bhinneka Tunggal Ika."},
    # TIU - Sinonim
    {"section": "TIU", "topic": "Sinonim", "year": 2024, "difficulty": "easy", "question_text": "ABSTRAK memiliki persamaan makna dengan...", "options": ["Konkret", "Nyata", "Teoritis", "Praktis", "Fisik"], "correct_answer": 2, "explanation": "Abstrak = teoritis (tidak berwujud). Lawan: konkret/nyata."},
    {"section": "TIU", "topic": "Antonim", "year": 2024, "difficulty": "easy", "question_text": "Lawan kata dari EKSPANSI adalah...", "options": ["Kontraksi", "Ekstensi", "Inflasi", "Deflasi", "Reduksi"], "correct_answer": 0, "explanation": "Ekspansi (perluasan) berlawanan dengan kontraksi (penyusutan)."},
    # TIU - Analogi
    {"section": "TIU", "topic": "Analogi", "year": 2024, "difficulty": "easy", "question_text": "TANGAN : SARUNG TANGAN = KAKI : ...", "options": ["Kaos kaki", "Sepatu", "Sandal", "Celana", "Topi"], "correct_answer": 1, "explanation": "Sarung tangan untuk melindungi tangan = sepatu untuk melindungi kaki."},
    # TIU - Deret Angka
    {"section": "TIU", "topic": "Deret Angka", "year": 2024, "difficulty": "medium", "question_text": "2, 6, 18, 54, ... Angka berikutnya adalah...", "options": ["108", "162", "216", "180", "144"], "correct_answer": 1, "explanation": "Pola: ×3. 54 × 3 = 162."},
    {"section": "TIU", "topic": "Deret Angka", "year": 2025, "difficulty": "hard", "question_text": "1, 1, 2, 3, 5, 8, ... Angka berikutnya adalah...", "options": ["10", "11", "12", "13", "15"], "correct_answer": 3, "explanation": "Deret Fibonacci: 5 + 8 = 13."},
    # TIU - Soal Cerita
    {"section": "TIU", "topic": "Soal Cerita", "year": 2024, "difficulty": "medium", "question_text": "Jika A berusia 2× B, dan jumlah usia mereka 60 tahun. Usia A adalah...", "options": ["20", "30", "40", "50", "60"], "correct_answer": 2, "explanation": "2B + B = 60 → 3B = 60 → B = 20 → A = 2×20 = 40."},
    # TIU - Silogisme
    {"section": "TIU", "topic": "Silogisme", "year": 2024, "difficulty": "medium", "question_text": "Semua mahasiswa rajin. Budi adalah mahasiswa. Kesimpulan yang tepat adalah...", "options": ["Budi tidak rajin", "Budi rajin", "Semua yang rajin adalah mahasiswa", "Budi bukan mahasiswa", "Tidak dapat disimpulkan"], "correct_answer": 1, "explanation": "Premis mayor: Semua mahasiswa rajin. Premis minor: Budi mahasiswa. Kesimpulan: Budi rajin."},
    # TKP - Pelayanan Publik
    {"section": "TKP", "topic": "Pelayanan Publik", "year": 2024, "difficulty": "medium", "question_text": "Anda petugas pelayanan. Warga datang dengan berkas TIDAK LENGKAP, sudah bolak-balik, dan marah. Apa yang Anda lakukan?", "options": [{"text": "Tolak berkas, suruh lengkapi", "score": 1}, {"text": "Terima & proses walau tidak lengkap", "score": 2}, {"text": "Jelaskan kekurangan & minta lengkapi", "score": 3}, {"text": "Jelaskan sabar + berikan daftar lengkap", "score": 4}, {"text": "Jelaskan sabar + daftar + tawarkan bantuan supaya tidak bolak-balik", "score": 5}], "correct_answer": None, "explanation": "Skor 5: Inisiatif + empati + solusi preventif."},
    # TKP - Anti-Radikalisme
    {"section": "TKP", "topic": "Anti-Radikalisme", "year": 2025, "difficulty": "hard", "question_text": "Tetangga Anda sering ikut kelompok yang sebar kebencian di medsos. Apa tindakan Anda?", "options": [{"text": "Biarkan, urusan pribadi", "score": 1}, {"text": "Langsung lapor polisi", "score": 2}, {"text": "Tegur langsung", "score": 3}, {"text": "Lapor ke RT/RW", "score": 4}, {"text": "Pendekatan persuasif + lapor ke RT/RW/BNPT untuk preventif", "score": 5}], "correct_answer": None, "explanation": "Skor 5: Bijak + tegas + preventif."},
    # TKP - Profesionalisme
    {"section": "TKP", "topic": "Profesionalisme", "year": 2024, "difficulty": "medium", "question_text": "Anda diminta atasan selesaikan laporan 2 hari. Rekan minta bantuan untuk pekerjaan mendesak. Apa yang Anda lakukan?", "options": [{"text": "Tolak bantu rekan, fokus kerjaan sendiri", "score": 1}, {"text": "Bantu rekan duluan karena kasihan", "score": 2}, {"text": "Bantu rekan setelah kerjaan selesai", "score": 3}, {"text": "Atur waktu agar keduanya selesai", "score": 4}, {"text": "Atur prioritas + selesaikan laporan duluan + arahkan rekan untuk selesaikan sendiri", "score": 5}], "correct_answer": None, "explanation": "Skor 5: Proaktif + solutif + mandiri."},
    # More TWK
    {"section": "TWK", "topic": "Bhinneka Tunggal Ika", "year": 2024, "difficulty": "easy", "question_text": "Semboyan Negara Indonesia adalah...", "options": ["Bhinneka Tunggal Ika", "Pancasila", "NKRI Harga Mati", "Merdeka atau Mati", "Tunggal Ika"], "correct_answer": 0, "explanation": "Bhinneka Tunggal Ika berarti berbeda-beda tetapi tetap satu."},
    {"section": "TWK", "topic": "Sejarah", "year": 2023, "difficulty": "medium", "question_text": "BPUPKI dibentuk pada tanggal...", "options": ["1 Maret 1945", "29 April 1945", "7 Agustus 1945", "17 Agustus 1945", "18 Agustus 1945"], "correct_answer": 1, "explanation": "BPUPKI (Badan Penyelidik Usaha Persiapan Kemerdekaan Indonesia) dibentuk 29 April 1945."},
    # More TIU
    {"section": "TIU", "topic": "Aritmatika", "year": 2024, "difficulty": "easy", "question_text": "Berapa hasil dari 15% dari 200?", "options": ["20", "25", "30", "35", "40"], "correct_answer": 2, "explanation": "15% × 200 = 30."},
    {"section": "TIU", "topic": "Perbandingan", "year": 2025, "difficulty": "medium", "question_text": "Jika 5 orang menyelesaikan pekerjaan dalam 10 hari, berapa hari jika dikerjakan oleh 10 orang?", "options": ["2", "3", "4", "5", "6"], "correct_answer": 3, "explanation": "5 × 10 = 10 × x → x = 5 hari."},
]

for q in questions:
    db.add(Question(**q))

db.commit()
print(f"Seeded {len(questions)} questions!")
db.close()
