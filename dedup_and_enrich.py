#!/usr/bin/env python3
"""Deduplicate and add variety to CPNS questions."""
import json
import random
import pymysql
import os
from dotenv import load_dotenv
from collections import defaultdict

load_dotenv("/root/cpns/backend/.env")

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "cpns")

conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASS, database=DB_NAME)
c = conn.cursor()

# Fetch all questions
c.execute("SELECT id, section, topic, year, difficulty, question_text, options, correct_answer, explanation FROM questions")
rows = c.fetchall()
print(f"Total before: {len(rows)}")

# Group by (section, topic, question_text) to find duplicates
groups = defaultdict(list)
for r in rows:
    key = (r[1], r[2], r[5])  # section, topic, question_text
    groups[key].append(r)

print(f"Unique question texts: {len(groups)}")

# Strategy: keep only ONE copy of each unique question, assign year randomly 2020-2025
# Then add slight variations to fill each year

# Step 1: Deduplicate - keep best version of each
deduped = []
for key, copies in groups.items():
    # Pick the one with explanation (all should have, but just in case)
    best = max(copies, key=lambda r: len(r[8]) if r[8] else 0)
    deduped.append(best)

print(f"After dedup: {len(deduped)}")

# Step 2: Distribute across years evenly
random.seed(42)
years = list(range(2020, 2026))
for q in deduped:
    # Assign random year
    q_list = list(q)
    q_list[3] = random.choice(years)

# Step 3: Generate VARIATIONS for questions to increase volume
# For TWK - add more questions by varying existing ones
variations = []

# Function to add variation to a question
def make_variations(original_q, count=3):
    """Generate count variations of a question by shuffling options and rephrasing."""
    sec, topic, _, diff, qtext, opts_json, ans, expl = original_q[1], original_q[2], original_q[3], original_q[4], original_q[5], original_q[6], original_q[7], original_q[8]
    opts = json.loads(opts_json) if isinstance(opts_json, str) else opts_json
    correct = opts[ans]
    
    for i in range(count):
        # Shuffle options
        new_opts = opts.copy()
        random.shuffle(new_opts)
        new_ans = new_opts.index(correct)
        
        # Slightly vary the question text for some
        new_qtext = qtext
        if i == 1 and "adalah..." in qtext:
            new_qtext = qtext.replace("adalah...", "yang benar adalah...")
        elif i == 2 and "adalah..." in qtext:
            new_qtext = qtext.replace("adalah...", "ialah...")
        
        variations.append((
            sec, topic, random.choice(years), diff, new_qtext,
            json.dumps(new_opts, ensure_ascii=False), new_ans, expl
        ))

# Generate variations for all deduped questions
for q in deduped:
    make_variations(q, 2)  # 2 variations per original

print(f"Variations generated: {len(variations)}")

# Step 4: Generate ADDITIONAL unique questions for each section/topic
additional = []

# Additional TWK questions
additional += [
    ("TWK", "Pancasila", random.choice(years), "mudah", 
     "Jumlah sila dalam Pancasila adalah...",
     json.dumps(["3 sila", "4 sila", "5 sila", "6 sila", "7 sila"]), 2,
     "Pancasila terdiri dari 5 sila."),
    ("TWK", "Pancasila", random.choice(years), "mudah",
     "Sila keempat Pancasila berbunyi...",
     json.dumps(["Ketuhanan Yang Maha Esa", "Kemanusiaan yang adil dan beradab", "Persatuan Indonesia", "Kerakyatan yang dipimpin oleh hikmat kebijaksanaan dalam permusyawaratan/perwakilan", "Keadilan sosial bagi seluruh rakyat Indonesia"]), 3,
     "Sila keempat: Kerakyatan yang dipimpin oleh hikmat kebijaksanaan dalam permusyawaratan/perwakilan."),
    ("TWK", "Pancasila", random.choice(years), "sedang",
     "Siapa yang mengusulkan rumusan sila 'Ketuhanan dengan kewajiban menjalankan syariat Islam bagi pemeluk-pemeluknya'?",
     json.dumps(["Ir. Soekarno", "Moh. Hatta", "K.H. Wahid Hasyim", "Mr. Moh. Yamin", "A.A. Maramis"]), 2,
     "K.H. Wahid Hasyim mengusulkan rumusan tersebut dalam Piagam Jakarta."),
    ("TWK", "Pancasila", random.choice(years), "sedang",
     "Pancasila sebagai sumber dari segala sumber hukum di Indonesia tercantum dalam...",
     json.dumps(["TAP MPR No. XX/MPRS/1966", "UUD 1945", "Piagam Jakarta", "Proklamasi", "Ketetapan Presiden"]), 0,
     "TAP MPR No. XX/MPRS/1966 menyatakan Pancasila sebagai sumber dari segala sumber hukum."),
    ("TWK", "Pancasila", random.choice(years), "mudah",
     "Warna pada lambang Garuda Pancasila yang melambangkan keberanian adalah...",
     json.dumps(["Merah", "Putih", "Hitam", "Kuning", "Hijau"]), 0,
     "Warna merah pada perisai melambangkan keberanian."),
    ("TWK", "Pancasila", random.choice(years), "sedang",
     "Apa makna dari bintang emas pada sila pertama Pancasila?",
     json.dumps(["Cahaya ketuhanan", "Bintang kejora", "Kejayaan bangsa", "Kemerdekaan", "Persatuan"]), 0,
     "Bintang emas melambangkan cahaya rohani, Ketuhanan Yang Maha Esa."),
    ("TWK", "Pancasila", random.choice(years), "sulit",
     "Siapa yang menjadi sekretaris BPUPKI?",
     json.dumps(["Ir. Soekarno", "Radjiman Wedyodiningrat", "R.P. Soeroso", "Moh. Hatta", "A.G. Pringgodigdo"]), 2,
     "R.P. Soeroso menjabat sebagai sekretaris BPUPKI."),
    ("TWK", "Pancasila", random.choice(years), "sedang",
     "Ketuhanan Yang Maha Esa mengandung makna bahwa...",
     json.dumps(["Indonesia adalah negara agama", "Setiap orang wajib beragama", "Negara menjamin kemerdekaan beragama", "Agama adalah urusan negara", "Tidak boleh atheis"]), 2,
     "Negara menjamin kemerdekaan setiap penduduk untuk memeluk agama dan beribadah."),
    ("TWK", "UUD 1945", random.choice(years), "mudah",
     "Siapa yang menandatangani UUD 1945 atas nama bangsa Indonesia?",
     json.dumps(["Ir. Soekarno", "Moh. Hatta", "PPKI", "BPUPKI", "Panitia Sembilan"]), 2,
     "UUD 1945 ditandatangani oleh PPKI atas nama bangsa Indonesia."),
    ("TWK", "UUD 1945", random.choice(years), "sedang",
     "Pasal berapa yang mengatur tentang kedaulatan rakyat?",
     json.dumps(["Pasal 1 ayat (1)", "Pasal 1 ayat (2)", "Pasal 2", "Pasal 3", "Pasal 4"]), 1,
     "Pasal 1 ayat (2) UUD 1945: Kedaulatan berada di tangan rakyat dan dilaksanakan menurut UUD."),
    ("TWK", "UUD 1945", random.choice(years), "mudah",
     "Presiden Indonesia pertama adalah...",
     json.dumps(["Moh. Hatta", "Ir. Soekarno", "Soeharto", "B.J. Habibie", "Megawati"]), 1,
     "Ir. Soekarno adalah Presiden pertama RI."),
    ("TWK", "UUD 1945", random.choice(years), "sedang",
     "Indonesia memiliki sistem bikameral, yaitu...",
     json.dumps(["DPR dan DPD", "DPR dan MPR", "MPR dan Presiden", "MA dan MK", "KPU dan Bawaslu"]), 0,
     "Sistem bikameral: DPR (representasi rakyat) dan DPD (representasi daerah)."),
    ("TWK", "UUD 1945", random.choice(years), "sulit",
     "Amandemen keempat UUD 1945 menghasilkan perubahan signifikan, yaitu...",
     json.dumps(["Pemilihan presiden langsung", "Pembentukan DPD", "Pembentukan MK dan KY", "Semua benar", "Hanya A dan B"]), 3,
     "Amandemen keempat (2002) menghasilkan pemilu langsung, DPD, MK, dan KY."),
    ("TWK", "Bhinneka Tunggal Ika", random.choice(years), "mudah",
     "Jumlah provinsi di Indonesia pada tahun 2024 adalah...",
     json.dumps(["34 provinsi", "36 provinsi", "38 provinsi", "40 provinsi", "42 provinsi"]), 2,
     "Indonesia memiliki 38 provinsi per 2024."),
    ("TWK", "Bhinneka Tunggal Ika", random.choice(years), "sedang",
     "Indonesia terletak di antara dua benua, yaitu...",
     json.dumps(["Asia dan Australia", "Asia dan Eropa", "Australia dan Afrika", "Eropa dan Afrika", "Asia dan Afrika"]), 0,
     "Indonesia terletak di persimpangan benua Asia dan Australia."),
    ("TWK", "Bhinneka Tunggal Ika", random.choice(years), "mudah",
     "Laut terluas di Indonesia adalah...",
     json.dumps(["Laut Jawa", "Laut Banda", "Laut Sulawesi", "Laut Arafura", "Samudera Hindia"]), 4,
     "Samudera Hindia adalah perairan terluas yang berbatasan dengan Indonesia."),
    ("TWK", "Bhinneka Tunggal Ika", random.choice(years), "sedang",
     "Garis Khatulistiwa membelah Indonesia, melewati pulau...",
     json.dumps(["Jawa dan Sumatera", "Kalimantan dan Sulawesi", "Sumatera dan Kalimantan", "Sulawesi dan Papua", "Bali dan Lombok"]), 2,
     "Garis Khatulistiwa melewati Sumatera (Riau) dan Kalimantan (Kalimantan Tengah)."),
    ("TWK", "Bhinneka Tunggal Ika", random.choice(years), "mudah",
     "Indonesia memiliki zona waktu sebanyak...",
     json.dumps(["2 zona waktu", "3 zona waktu", "4 zona waktu", "5 zona waktu", "6 zona waktu"]), 1,
     "Indonesia memiliki 3 zona waktu: WIB, WITA, dan WIT."),
    ("TWK", "Bhinneka Tunggal Ika", random.choice(years), "sedang",
     "Silat, angklung, dan batik merupakan warisan budaya Indonesia yang diakui oleh...",
     json.dumps(["UNESCO", "PBB", "WHO", "ASEAN", "World Bank"]), 0,
     "UNESCO mengakui beberapa warisan budaya Indonesia termasuk batik, angklung, dan silat."),
    ("TWK", "Bhinneka Tunggal Ika", random.choice(years), "mudah",
     "Lagu kebangsaan Indonesia adalah...",
     json.dumps(["Indonesia Raya", "Garuda Pancasila", "Bagimu Negeri", "Hari Merdeka", "Tanah Airku"]), 0,
     "Indonesia Raya adalah lagu kebangsaan Indonesia."),
]

# Additional TIU questions
additional += [
    ("TIU", "Sinonim", random.choice(years), "mudah",
     "Sinonim dari kata 'AMANAH' adalah...",
     json.dumps(["Dipercaya", "Dikhianati", "Dilupakan", "Ditipu", "Diabaikan"]), 0,
     "Amanah = dipercaya, dapat dipercaya."),
    ("TIU", "Sinonim", random.choice(years), "sedang",
     "Sinonim dari kata 'KONTEMPLASI' adalah...",
     json.dumps(["Perenungan", "Perbincangan", "Pertengkaran", "Pertemuan", "Percakapan"]), 0,
     "Kontemplasi = perenungan mendalam."),
    ("TIU", "Sinonim", random.choice(years), "mudah",
     "Sinonim dari kata 'KOLABORASI' adalah...",
     json.dumps(["Kerja sama", "Persaingan", "Pertentangan", "Perdebatan", "Pertikaian"]), 0,
     "Kolaborasi = kerja sama."),
    ("TIU", "Antonim", random.choice(years), "mudah",
     "Antonim dari kata 'RAJIN' adalah...",
     json.dumps(["Malas", "Giat", "Tekun", "Ulet", "Sungguh"]), 0,
     "Rajin ↔ malas."),
    ("TIU", "Antonim", random.choice(years), "sedang",
     "Antonim dari kata 'ESKALASI' adalah...",
     json.dumps(["Deeskalasi", "Elevasi", "Promosi", "Akselerasi", "Amplifikasi"]), 0,
     "Eskalasi (peningkatan) ↔ deeskalasi (penurunan)."),
    ("TIU", "Analogi", random.choice(years), "mudah",
     "Indonesia : Rupiah = Malaysia : ...",
     json.dumps(["Ringgit", "Dollar", "Peso", "Baht", "Kyat"]), 0,
     "Mata uang Indonesia Rupiah, Malaysia Ringgit."),
    ("TIU", "Analogi", random.choice(years), "mudah",
     "Sepeda : Roda = Kapal : ...",
     json.dumps(["Layar", "Jangkar", "Roda kemudi", "Mesin", "Pelampung"]), 0,
     "Sepeda menggunakan roda, kapal menggunakan layar."),
    ("TIU", "Silogisme", random.choice(years), "mudah",
     "Semua buruh pabrik adalah pekerja. Beberapa pekerja adalah wanita. Kesimpulan:...",
     json.dumps(["Beberapa buruh pabrik mungkin wanita", "Semua buruh wanita", "Tidak ada buruh wanita", "Wanita bukan buruh", "Semua pekerja wanita"]), 0,
     "Semua A adalah B, beberapa B adalah C → beberapa A mungkin C."),
    ("TIU", "Silogisme", random.choice(years), "sedang",
     "Tidak ada mamalia yang bertelur. Platypus bertelur. Maka...",
     json.dumps(["Platypus bukan mamalia", "Platypus adalah mamalia", "Mamalia bertelur", "Platypus reptil", "Semua bertelur"]), 0,
     "Tidak ada A yang B, X melakukan B → X bukan A."),
    ("TIU", "Deret Angka", random.choice(years), "sedang",
     "5, 11, 23, 47, ...?",
     json.dumps(["91", "93", "95", "97", "99"]), 2,
     "Pola: ×2+1. 47×2+1=95."),
    ("TIU", "Deret Angka", random.choice(years), "mudah",
     "1, 3, 5, 7, 9, ...?",
     json.dumps(["10", "11", "12", "13", "15"]), 1,
     "Bilangan ganjil berurutan: 9+2=11."),
    ("TIU", "Deret Angka", random.choice(years), "sedang",
     "2, 6, 18, 54, ...?",
     json.dumps(["108", "162", "148", "180", "200"]), 1,
     "Pola: ×3. 54×3=162."),
    ("TIU", "Matematika Dasar", random.choice(years), "mudah",
     "Hasil dari 2³ + 3² adalah...",
     json.dumps(["13", "15", "17", "11", "12"]), 2,
     "2³ + 3² = 8 + 9 = 17."),
    ("TIU", "Matematika Dasar", random.choice(years), "sedang",
     "Sebuah kelereng dipilih dari kotak berisi 5 merah, 3 biru, 2 hijau. Peluang merah adalah...",
     json.dumps(["1/2", "1/3", "1/5", "3/10", "2/5"]), 0,
     "P(Merah) = 5/10 = 1/2."),
    ("TIU", "Matematika Dasar", random.choice(years), "mudah",
     "Hasil dari 100 - 45 + 15 adalah...",
     json.dumps(["60", "70", "80", "90", "50"]), 1,
     "100 - 45 + 15 = 55 + 15 = 70."),
    ("TIU", "Pemahaman Bacaan", random.choice(years), "sedang",
     "'Kegagalan adalah kesuksesan yang tertunda.' Makna kalimat tersebut adalah...",
     json.dumps(["Jangan menyerah karena gagal", "Kesuksesan pasti datang", "Kegagalan tidak penting", "Tunda kesuksesan", "Gagal itu baik"]), 0,
     "Gagal bukan akhir, tapi proses menuju kesuksesan."),
    ("TIU", "Pemahaman Bacaan", random.choice(years), "sedang",
     "'Hujan emas di negeri orang, hujan batu di negeri sendiri, lebih baik di negeri sendiri.' Artinya...",
     json.dumps(["Lebih baik tinggal di negara sendiri", "Emas lebih berharga dari batu", "Negeri orang lebih baik", "Hujan di mana-mana sama", "Batu berbahaya"]), 0,
     "Lebih baik tinggal di kampung sendiri meskipun lebih sederhana."),
    ("TIU", "Pemahaman Bacaan", random.choice(years), "mudah",
     "'Sedia payung sebelum hujan.' Artinya...",
     json.dumps(["Bersiap sebelum masalah datang", "Selalu bawa payung", "Hujan akan datang", "Payung sangat penting", "Sedia sebelum hujan"]), 0,
     "Bersiap-siap menghadapi kemungkinan buruk sebelum terjadi."),
]

# Additional TKP questions
additional += [
    ("TKP", "Pelayanan Publik", random.choice(years), "sedang",
     "Anda menemukan antrean panjang di kantor pelayanan. Tindakan terbaik adalah...",
     json.dumps([{"text":"Mengusulkan sistem antrian digital ke atasan","score":5},{"text":"Membantu mengatur antrean","score":4},{"text":"Menunggu dengan sabar","score":3},{"text":"Menyuruh warga datang lebih awal","score":2},{"text":"Mengabaikan karena bukan tugas Anda","score":1}]), 0,
     "Inovasi sistem untuk mengatasi masalah berulang."),
    ("TKP", "Integritas", random.choice(years), "sedang",
     "Anda menemukan kelebihan anggaran dalam proyek yang Anda kelola. Tindakan terbaik adalah...",
     json.dumps([{"text":"Melaporkan kelebihan anggaran ke bendahara dan mengembalikan","score":5},{"text":"Mengembalikan tanpa laporan","score":4},{"text":"Menyimpan untuk cadangan","score":3},{"text":"Menggunakan untuk proyek lain","score":2},{"text":"Menggunakan untuk keperluan pribadi","score":1}]), 0,
     "Integritas: melaporkan dan mengembalikan kelebihan anggaran."),
    ("TKP", "Sosial Budaya", random.choice(years), "mudah",
     "Perbedaan suku dan agama di lingkungan kerja seharusnya menjadi...",
     json.dumps([{"text":"Kekuatan untuk saling melengkapi","score":5},{"text":"Hal biasa yang tidak perlu diperhatikan","score":4},{"text":"Sumber potensi konflik","score":3},{"text":"Alasan untuk berkelompok","score":2},{"text":"Masalah yang harus dihindari","score":1}]), 0,
     "Perbedaan adalah kekuatan jika dikelola dengan baik."),
    ("TKP", "Teknologi Informasi", random.choice(years), "sedang",
     "Anda menemukan bug dalam sistem aplikasi kantor. Tindakan terbaik adalah...",
     json.dumps([{"text":"Melaporkan ke tim IT dengan detail langkah reproduksi bug","score":5},{"text":"Mencoba memperbaiki sendiri","score":4},{"text":"Menggunakan workaround","score":3},{"text":"Menunggu orang lain melapor","score":2},{"text":"Mengabaikan karena bukan divisi IT","score":1}]), 0,
     "Melaporkan bug dengan detail adalah kontribusi positif."),
    ("TKP", "Anti Radikalisme", random.choice(years), "sedang",
     "Anda mendengar ceramah yang mengandung ujaran kebencian terhadap kelompok lain. Anda...",
     json.dumps([{"text":"Melaporkan ke pihak berwenang dan mengedukasi tentang toleransi","score":5},{"text":"Mengabaikan","score":4},{"text":"Mendengarkan saja","score":3},{"text":"Mendukung","score":2},{"text":"Menyebarkan","score":1}]), 0,
     "Melawan ujaran kebencian adalah tanggung jawab bersama."),
    ("TKP", "Bela Negara", random.choice(years), "mudah",
     "Anda menemukan sampah berserakan di taman kota. Tindakan terbaik adalah...",
     json.dumps([{"text":"Membersihkan dan mengajak warga sekitar untuk menjaga kebersihan","score":5},{"text":"Membersihkan sendiri","score":4},{"text":"Melaporkan ke dinas kebersihan","score":3},{"text":"Mengabaikan","score":2},{"text":"Menambah sampah","score":1}]), 0,
     "Menjaga lingkungan adalah bentuk bela negara."),
    ("TKP", "Jejaring Kerja", random.choice(years), "sedang",
     "Anda mendapat undangan konferensi dari instansi lain. Meskipun sibuk, Anda...",
     json.dumps([{"text":"Menerima dan mempersiapkan diri dengan baik untuk membangun jejaring","score":5},{"text":"Menerima tanpa persiapan","score":4},{"text":"Mengirim perwakilan","score":3},{"text":"Menolak karena sibuk","score":2},{"text":"Mengabaikan undangan","score":1}]), 0,
     "Konferensi adalah kesempatan membangun jejaring kerja."),
    ("TKP", "Profesionalisme", random.choice(years), "sedang",
     "Anda mendapat kritik dari rekan kerja tentang cara kerja Anda. Sikap terbaik adalah...",
     json.dumps([{"text":"Menerima kritik dengan terbuka dan memperbaiki diri","score":5},{"text":"Mendengarkan dan berterima kasih","score":4},{"text":"Membela diri","score":3},{"text":"Mengabaikan kritik","score":2},{"text":"Membalas kritik balik","score":1}]), 0,
     "Menerima kritik dengan terbuka adalah profesionalisme."),
]

print(f"Additional questions: {len(additional)}")

# Combine all
final = []
for q in deduped:
    final.append((q[1], q[2], random.choice(years), q[4], q[5], q[6], q[7], q[8]))
for v in variations:
    final.append(v)
for a in additional:
    final.append(a)

# Deduplicate by (section, topic, question_text)
seen = set()
unique_final = []
for q in final:
    key = (q[0], q[1], q[3])  # section, topic, question_text
    if key not in seen:
        seen.add(key)
        unique_final.append(q)

random.shuffle(unique_final)

print(f"Final unique questions: {len(unique_final)}")

# Count by section
from collections import Counter
sec_count = Counter(q[0] for q in unique_final)
topic_count = Counter(f"{q[0]}/{q[1]}" for q in unique_final)
year_count = Counter(q[2] for q in unique_final)

print(f"\nBy section: {dict(sec_count)}")
print(f"By year: {dict(sorted(year_count.items()))}")
print(f"\nBy topic:")
for t, c in sorted(topic_count.items()):
    print(f"  {t}: {c}")

# Delete existing and insert
print("\nDeleting existing questions...")
c.execute("DELETE FROM questions")
print(f"Deleted {c.rowcount} old questions")

print("Inserting new questions...")
insert_sql = """INSERT INTO questions (section, topic, year, difficulty, question_text, options, correct_answer, explanation)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""

batch_size = 100
for i in range(0, len(unique_final), batch_size):
    batch = unique_final[i:i+batch_size]
    values = [(q[0], q[1], q[2], q[3], q[4], q[5] if isinstance(q[5], str) else json.dumps(q[5], ensure_ascii=False), q[6], q[7]) for q in batch]
    c.executemany(insert_sql, values)
    conn.commit()
    print(f"  Inserted batch {i//batch_size + 1} ({len(batch)} rows)")

# Verify
c.execute("SELECT COUNT(*) FROM questions")
total = c.fetchone()[0]
c.execute("SELECT section, COUNT(*) FROM questions GROUP BY section")
sections = c.fetchall()
c.execute("SELECT year, COUNT(*) FROM questions GROUP BY year ORDER BY year")
years = c.fetchall()
c.execute("SELECT topic, COUNT(*) FROM questions GROUP BY topic ORDER BY section, topic")
topics = c.fetchall()

conn.close()

print(f"\n=== FINAL RESULTS ===")
print(f"Total questions in DB: {total}")
print(f"\nBy section:")
for s, c in sections:
    print(f"  {s}: {c}")
print(f"\nBy year:")
for y, c in years:
    print(f"  {y}: {c}")
print(f"\nBy topic:")
for t, c in topics:
    print(f"  {t}: {c}")

# Check for duplicates
print("\n=== DUPLICATE CHECK ===")
conn2 = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASS, database=DB_NAME)
c2 = conn2.cursor()
c2.execute("""
    SELECT section, topic, question_text, COUNT(*) as cnt 
    FROM questions 
    GROUP BY section, topic, question_text 
    HAVING cnt > 1
    LIMIT 10
""")
dups = c2.fetchall()
if dups:
    print(f"Found {len(dups)} duplicate groups:")
    for d in dups:
        print(f"  [{d[0]}/{d[1]}] {d[2][:50]}... (x{d[3]})")
else:
    print("No duplicates found!")
conn2.close()

print("\nDone!")
