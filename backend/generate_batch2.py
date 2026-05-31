#!/usr/bin/env python3
"""Generate MORE CPNS questions — Batch 2."""
import json
import pymysql

DB_CONFIG = {"host": "localhost", "user": "root", "database": "cpns", "charset": "utf8mb4"}

# ============================================================
# TWK — Hankam
# ============================================================
TWK_HANKAM = [
    {"question_text": "TNI terdiri dari tiga angkatan, yaitu...", "options": ["TNI AD, TNI AL, TNI AU", "Polri, TNI, Brimob", "Kostrad, Kopassus, Marinir", "AD, AL, Polisi Militer", "AD, AL, AU, Polri"], "correct_answer": 0, "explanation": "TNI terdiri dari TNI AD (Angkatan Darat), TNI AL (Angkatan Laut), dan TNI AU (Angkatan Udara) sesuai UU No. 34/2004."},
    {"question_text": "Panglima TNI diangkat dan diberhentikan oleh...", "options": ["Menteri Pertahanan", "Presiden", "DPR", "Mahkamah Agung", "MPR"], "correct_answer": 1, "explanation": "Panglima TNI diangkat dan diberhentikan oleh Presiden dengan persetujuan DPR sesuai UUD 1945 Pasal 13."},
    {"question_text": "Sistem pertahanan dan keamanan negara Indonesia menggunakan sistem...", "options": ["Total", "Semi militer", "Rakyat Semesta", "Militer profesional", "Komponen cadangan"], "correct_answer": 2, "explanation": "Indonesia menggunakan Sistem Pertahanan dan Keamanan Rakyat Semesta (Sishankamrata) sesuai UUD 1945."},
    {"question_text": "Hankamrata adalah singkatan dari...", "options": ["Pertahanan Keamanan Nasional", "Pertahanan Keamanan Rakyat Semesta", "Hankam dan Rakyat Terpadu", "Pertahanan Wilayah Rakyat", "Hankam Negara Rakyat"], "correct_answer": 1, "explanation": "Hankamrata = Pertahanan dan Keamanan Rakyat Semesta, konsep pertahanan Indonesia."},
    {"question_text": "Kopassus adalah satuan khusus milik...", "options": ["TNI AL", "TNI AU", "TNI AD", "Polri", "BAIS"], "correct_answer": 2, "explanation": "Kopassus (Komando Pasukan Khusus) adalah satuan elite TNI AD."},
    {"question_text": "Tugas utama TNI AL adalah...", "options": ["Menjaga udara", "Menjaga laut dan pantai", "Menjaga darat", "Menjaga perbatasan", "Intelijen strategis"], "correct_answer": 1, "explanation": "TNI AL bertugas menegakkan hukum dan menjaga keamanan di wilayah laut dan pantai Indonesia."},
    {"question_text": "Indonesia termasuk dalam organisasi pertahanan...", "options": ["NATO", "SEATO", "Tidak tergantung aliansi militer manapun", "Pakta Warsawa", "ANZUS"], "correct_answer": 2, "explanation": "Indonesia menganut politik luar negeri bebas aktif dan tidak tergabung dalam aliansi militer manapun."},
    {"question_text": "Bais adalah singkatan dari...", "options": ["Badan Akseptasi Intelijen Strategis", "Badan Intelijen Strategis", "Badan Analisis Informasi Strategis", "Badan Akuisisi Intelijen Nasional", "Badan Asistensi Intelijen Negara"], "correct_answer": 1, "explanation": "BAIS = Badan Intelijen Strategis, merupakan badan intelijen militer TNI."},
    {"question_text": "Konsep pertahanan rakyat semesta melibatkan...", "options": ["Hanya TNI", "TNI dan Polri", "Seluruh rakyat dan sumber daya nasional", "Hanya komponen militer", "Hanya relawan"], "correct_answer": 2, "explanation": "Pertahanan rakyat semesta melibatkan seluruh rakyat dan sumber daya nasional sebagai kekuatan pertahanan."},
    {"question_text": "UU No. 34 Tahun 2004 mengatur tentang...", "options": ["Polri", "TNI", "Pertahanan Negara", "Keamanan Nasional", "Intelijen Negara"], "correct_answer": 1, "explanation": "UU No. 34 Tahun 2004 adalah tentang Tentara Nasional Indonesia."},
]

# ============================================================
# TWK — Sejarah Indonesia
# ============================================================
TWK_SEJARAH = [
    {"question_text": "Kerajaan Hindu tertua di Indonesia adalah...", "options": ["Majapahit", "Sriwijaya", "Kutai", "Tarumanegara", "Singasari"], "correct_answer": 2, "explanation": "Kerajaan Kutai (abad ke-4) adalah kerajaan Hindu tertua di Indonesia, terletak di Kalimantan Timur."},
    {"question_text": "Proklamasi kemerdekaan Indonesia dibacakan pada tanggal...", "options": ["17 Agustus 1945", "1 Juni 1945", "28 Oktober 1928", "10 November 1945", "21 April 1945"], "correct_answer": 0, "explanation": "Proklamasi kemerdekaan RI dibacakan pada 17 Agustus 1945 oleh Ir. Soekarno dan Drs. Moh. Hatta."},
    {"question_text": "BPUPKI dibentuk pada tanggal...", "options": ["29 April 1945", "1 Maret 1945", "7 Agustus 1945", "17 Agustus 1945", "28 Oktober 1928"], "correct_answer": 0, "explanation": "BPUPKI (Badan Penyelidik Usaha Persiapan Kemerdekaan Indonesia) dibentuk pada 29 April 1945."},
    {"question_text": "Sumpah Pemuda dicetuskan pada tahun...", "options": ["1908", "1928", "1945", "1942", "1955"], "correct_answer": 1, "explanation": "Sumpah Pemuda dicetuskan pada Kongres Pemuda II, 28 Oktober 1928."},
    {"question_text": "VOC didirikan di Indonesia pada tahun...", "options": ["1602", "1619", "1596", "1800", "1799"], "correct_answer": 0, "explanation": "VOC (Vereenigde Oostindische Compagnie) didirikan pada tahun 1602 dan mulai beroperasi di Indonesia."},
    {"question_text": "Pahlawan nasional yang dijuluki 'Bapak Pendidikan Nasional' adalah...", "options": ["Soekarno", "Mohammad Hatta", "Ki Hadjar Dewantara", "Diponegoro", "Ahmad Yani"], "correct_answer": 2, "explanation": "Ki Hadjar Dewantara (Raden Mas Soewardi Soerjaningrat) dijuluki Bapak Pendidikan Nasional."},
    {"question_text": "Perjanjian Renville ditandatangani pada tahun...", "options": ["1946", "1947", "1948", "1949", "1950"], "correct_answer": 2, "explanation": "Perjanjian Renville ditandatangani pada 17 Januari 1948 di atas USS Renville."},
    {"question_text": "Pemberontakan DI/TII dipimpin oleh...", "options": ["Ahmad Husein", "Kartosuwiryo", "Daud Beureueh", "Amir Fatah", "Muso"], "correct_answer": 1, "explanation": "DI/TII (Darul Islam/Tentara Islam Indonesia) dipimpin oleh S.M. Kartosuwiryo."},
    {"question_text": "Gerakan Non-Blok (Non-Aligned Movement) dicetuskan pada tahun...", "options": ["1945", "1955", "1961", "1965", "1970"], "correct_answer": 2, "explanation": "Gerakan Non-Blok dicetuskan pada Konferensi Beograd 1961 oleh Soekarno, Nehru, Nasser, Tito, dan Nkrumah."},
    {"question_text": "Konferensi Asia-Afrika berlangsung di...", "options": ["Jakarta", "Bandung", "Yogyakarta", "Surabaya", "Bali"], "correct_answer": 1, "explanation": "Konferensi Asia-Afrika (KAA) berlangsung di Bandung pada 18-24 April 1955."},
]

# ============================================================
# TWK — Pancasila
# ============================================================
TWK_PANCASILA = [
    {"question_text": "Silka pertama Pancasila berbunyi...", "options": ["Kemanusiaan yang adil dan beradab", "Ketuhanan Yang Maha Esa", "Persatuan Indonesia", "Kerakyatan yang dipimpin oleh hikmat kebijaksanaan", "Keadilan sosial bagi seluruh rakyat Indonesia"], "correct_answer": 1, "explanation": "Silka pertama Pancasila adalah Ketuhanan Yang Maha Esa."},
    {"question_text": "Pancasila sebagai dasar negara Indonesia pertama kali dicetuskan oleh...", "options": ["Mohammad Hatta", "Soekarno", "Soepomo", "Moh. Yamin", "Rajiman Wediodiningrat"], "correct_answer": 1, "explanation": "Pancasila pertama kali dicetuskan oleh Ir. Soekarno dalam pidatonya pada 1 Juni 1945 di depan BPUPKI."},
    {"question_text": "Lambang sila ketiga Pancasila adalah...", "options": ["Bintang", "Pohon beringin", "Kepala banteng", "Padi dan kapas", "Rantai"], "correct_answer": 2, "explanation": "Lambang sila ketiga (Persatuan Indonesia) adalah pohon beringin."},
    {"question_text": "Maklumat Pemerintah tanggal 3 November 1945 berisi tentang...", "options": ["Pembubaran BPUPKI", "Pembentukan KNIP", "Pengesahan UUD 1945", "Dekrit Presiden", "Pembentukan partai politik"], "correct_answer": 1, "explanation": "Maklumat Pemerintah 3 November 1945 berisi pembentukan KNIP (Komite Nasional Indonesia Pusat) sebagai pengganti MPR sementara."},
    {"question_text": "Pancasila disahkan sebagai dasar negara pada tanggal...", "options": ["1 Juni 1945", "18 Agustus 1945", "17 Agustus 1945", "28 Oktober 1928", "5 Juli 1959"], "correct_answer": 1, "explanation": "Pancasila disahkan sebagai dasar negara pada 18 Agustus 1945 bersamaan dengan pengesahan UUD 1945 oleh PPKI."},
    {"question_text": "Sila keempat Pancasila dilambangkan dengan...", "options": ["Bintang", "Pohon beringin", "Kepala banteng", "Padi dan kapas", "Rantai"], "correct_answer": 2, "explanation": "Sila keempat (Kerakyatan yang dipimpin oleh hikmat kebijaksanaan) dilambangkan dengan kepala banteng."},
    {"question_text": "Pancasila sebagai sumber dari segala sumber hukum tertuang dalam...", "options": ["Pembukaan UUD 1945", "Batang Tubuh UUD 1945", "TAP MPR", "UU No. 12/2011", "Dekrit Presiden"], "correct_answer": 0, "explanation": "Pancasila sebagai sumber dari segala sumber hukum tertuang dalam Pembukaan UUD 1945."},
    {"question_text": "Nilai-nilai Pancasila tercermin dalam sikap...", "options": ["Individualistis", "Gotong royong", "Materialistis", "Hedonistis", "Egoistis"], "correct_answer": 1, "explanation": "Gotong royong mencerminkan nilai-nilai Pancasila, terutama sila ketiga dan kelima."},
    {"question_text": "Pancasila digali oleh...", "options": ["Presiden", "BPUPKI", "MPR", "DPR", "Mahkamah Konstitusi"], "correct_answer": 1, "explanation": "Pancasila digali/dirumuskan oleh BPUPKI (Badan Penyelidik Usaha Persiapan Kemerdekaan Indonesia)."},
    {"question_text": "Sila kelima Pancasila berbunyi...", "options": ["Ketuhanan Yang Maha Esa", "Kemanusiaan yang adil dan beradab", "Persatuan Indonesia", "Kerakyatan yang dipimpin oleh hikmat kebijaksanaan", "Keadilan sosial bagi seluruh rakyat Indonesia"], "correct_answer": 4, "explanation": "Sila kelima Pancasila adalah Keadilan sosial bagi seluruh rakyat Indonesia."},
]

# ============================================================
# TIU — Analogi
# ============================================================
TIU_ANALOGI = [
    {"question_text": "Dokter : Rumah Sakit = Hakim : ...", "options": ["Penjara", "Pengadilan", "Kantor polisi", "Kantor gubernur", "Sekolah"], "correct_answer": 1, "explanation": "Dokter bekerja di Rumah Sakit, Hakim bekerja di Pengadilan."},
    {"question_text": "Buku : Perpustakaan = Lukisan : ...", "options": ["Kanvas", "Museum", "Kuas", "Warna", "Studio"], "correct_answer": 1, "explanation": "Buku disimpan di Perpustakaan, Lukisan dipajang di Museum."},
    {"question_text": "Kapal : Laut = Pesawat : ...", "options": ["Bandara", "Udara", "Hanggar", "Pilot", "Sayap"], "correct_answer": 1, "explanation": "Kapal berlayar di Laut, Pesawat terbang di Udara."},
    {"question_text": "Siswa : Ujian = Tersangka : ...", "options": ["Penjara", "Pengacara", "Sidang", "Polisi", "Vonis"], "correct_answer": 2, "explanation": "Siswa menghadapi Ujian, Tersangka menghadapi Sidang."},
    {"question_text": "Pena : Menulis = Gunting : ...", "options": ["Kertas", "Memotong", "Tukang cukur", "Benang", "Jarum"], "correct_answer": 1, "explanation": "Pena digunakan untuk Menulis, Gunting digunakan untuk Memotong."},
    {"question_text": "Atlet : Medali = Pelajar : ...", "options": ["Buku", "Rapor", "Sekolah", "Guru", "Pena"], "correct_answer": 1, "explanation": "Atlet mendapat Medali, Pelajar mendapat Rapor."},
    {"question_text": "Koki : Dapur = Dokter : ...", "options": ["Obat", "Rumah Sakit", "Pasien", "Resep", "Operasi"], "correct_answer": 1, "explanation": "Koki bekerja di Dapur, Dokter bekerja di Rumah Sakit."},
    {"question_text": "Hak : Kewajiban = Utang : ...", "options": ["Piutang", "Bank", "Uang", "Bunga", "Kredit"], "correct_answer": 0, "explanation": "Hak berpasangan dengan Kewajiban, Utang berpasangan dengan Piutang."},
    {"question_text": "Panas : Dingin = Tinggi : ...", "options": ["Pendek", "Rendah", "Dalam", "Jauh", "Lebar"], "correct_answer": 1, "explanation": "Panas berlawanan dengan Dingin, Tinggi berlawanan dengan Rendah."},
    {"question_text": "Bulan : Tahun = Menit : ...", "options": ["Detik", "Jam", "Waktu", "Jam dinding", "Kalender"], "correct_answer": 1, "explanation": "12 Bulan = 1 Tahun, 60 Menit = 1 Jam."},
]

# ============================================================
# TIU — Silogisme
# ============================================================
TIU_SILOGISME = [
    {"question_text": "Semua mahasiswa wajib kuliah. Budi adalah mahasiswa. Maka...", "options": ["Budi tidak wajib kuliah", "Budi wajib kuliah", "Budi mungkin kuliah", "Budi sudah lulus", "Budi tidak kuliah"], "correct_answer": 1, "explanation": "Premis mayor: Semua mahasiswa wajib kuliah. Premis minor: Budi mahasiswa. Kesimpulan: Budi wajib kuliah."},
    {"question_text": "Semua hewan bernapas. Kucing adalah hewan. Maka...", "options": ["Kucing tidak bernapas", "Kucing bernapas", "Kucing adalah karnivora", "Semua kucing hidup", "Tidak ada kesimpulan"], "correct_answer": 1, "explanation": "Dari dua premis, kesimpulan logis: Kucing bernapas."},
    {"question_text": "Beberapa pegawai adalah sarjana. Semua sarjana berpendidikan tinggi. Maka...", "options": ["Semua pegawai berpendidikan tinggi", "Beberapa pegawai berpendidikan tinggi", "Tidak ada pegawai berpendidikan tinggi", "Semua sarjana adalah pegawai", "Beberapa sarjana bukan pegawai"], "correct_answer": 1, "explanation": "Karena beberapa pegawai adalah sarjana, dan semua sarjana berpendidikan tinggi, maka beberapa pegawai berpendidikan tinggi."},
    {"question_text": "Tidak ada kucing yang bisa terbang. Semua kucing adalah mamalia. Maka...", "options": ["Semua mamalia bisa terbang", "Tidak ada mamalia yang bisa terbang", "Beberapa mamalia tidak bisa terbang", "Semua kucing bisa terbang", "Tidak ada kesimpulan"], "correct_answer": 2, "explanation": "Karena kucing adalah mamalia dan tidak bisa terbang, maka beberapa mamalia tidak bisa terbang."},
    {"question_text": "Semua buah mengandung vitamin. Pepaya adalah buah. Maka...", "options": ["Pepaya tidak mengandung vitamin", "Pepaya mengandung vitamin", "Semua buah adalah pepaya", "Vitamin hanya ada di buah", "Pepaya adalah sayuran"], "correct_answer": 1, "explanation": "Premis: Semua buah mengandung vitamin. Pepaya adalah buah. Kesimpulan: Pepaya mengandung vitamin."},
    {"question_text": "Beberapa guru mengajar bahasa Inggris. Semua guru berpendidikan S1. Maka...", "options": ["Semua yang berpendidikan S1 adalah guru", "Beberapa yang mengajar bahasa Inggris berpendidikan S1", "Tidak ada guru yang berpendidikan S1", "Semua guru mengajar bahasa Inggris", "Beberapa guru tidak berpendidikan S1"], "correct_answer": 1, "explanation": "Karena beberapa guru mengajar bahasa Inggris dan semua guru S1, maka beberapa yang mengajar bahasa Inggris berpendidikan S1."},
    {"question_text": "Semua pohon berdaun. Apel adalah pohon. Maka...", "options": ["Apel tidak berdaun", "Apel berdaun", "Semua yang berdaun adalah pohon", "Apel adalah buah", "Tidak ada kesimpulan"], "correct_answer": 1, "explanation": "Premis: Semua pohon berdaun. Apel adalah pohon. Kesimpulan: Apel berdaun."},
    {"question_text": "Beberapa mobil berwarna merah. Semua mobil beroda empat. Maka...", "options": ["Semua yang beroda empat adalah mobil", "Beberapa yang berwarna merah beroda empat", "Tidak ada mobil berwarna merah", "Semua mobil berwarna merah", "Beberapa mobil tidak beroda empat"], "correct_answer": 1, "explanation": "Karena beberapa mobil berwarna merah dan semua mobil beroda empat, maka beberapa yang berwarna merah beroda empat."},
    {"question_text": "Semua ikan hidup di air. Ikan paus hidup di air. Maka...", "options": ["Ikan paus adalah ikan", "Ikan paus bukan ikan", "Semua yang hidup di air adalah ikan", "Ikan paus tidak hidup di air", "Tidak ada kesimpulan pasti"], "correct_answer": 4, "explanation": "Tidak ada kesimpulan pasti karena ikan paus hidup di air bukan berarti ikan paus adalah ikan (itu mamalia)."},
    {"question_text": "Tidak ada burung yang berenang. Beberapa hewan bisa terbang. Maka...", "options": ["Semua hewan bisa terbang", "Beberapa hewan yang terbang bukan burung", "Tidak ada hewan yang bisa terbang", "Semua burung bisa terbang", "Beberapa burung berenang"], "correct_answer": 1, "explanation": "Karena tidak ada burung yang berenang dan beberapa hewan bisa terbang, maka beberapa hewan yang terbang bukan burung."},
]

# ============================================================
# TKP — More Pelayanan Publik
# ============================================================
TKP_PELAYANAN_2 = [
    {"question_text": "Masyarakat mengeluh antrian terlalu panjang di kantor Anda. Solusi terbaik adalah...", "options": ["Menambah jam kerja tanpa koordinasi", "Menganalisis penyebab dan mengoptimalkan proses pelayanan", "Menutup layanan lebih awal", "Meminta masyarakat datang lain hari", "Mengurangi jumlah pelayanan"], "correct_answer": 1, "explanation": "Menganalisis dan mengoptimalkan proses adalah solusi sistemik untuk mengatasi antrian panjang."},
    {"question_text": "Anda diminta melayani di luar jam kerja untuk keperluan mendesak. Sikap Anda...", "options": ["Menolak karena di luar jam kerja", "Melayani dengan penuh tanggung jawab karena kebutuhan masyarakat", "Minta lembur yang tinggi", "Minta rekan lain", "Melayani asal ada kompensasi"], "correct_answer": 1, "explanation": "Pelayanan prima kadang memerlukan pengorbanan di luar jam kerja demi kepentingan masyarakat."},
    {"question_text": "Anda menemukan formulir pelayanan yang membingungkan bagi masyarakat. Tindakan Anda...", "options": ["Membiarkan karena bukan wewenang Anda", "Mengusulkan penyederhanaan formulir ke atasan", "Menjelaskan satu per satu ke setiap warga", "Mencetak panduan pengisian", "Mengabaikan keluhan warga"], "correct_answer": 1, "explanation": "Mengusulkan perbaikan sistem adalah tindakan proaktif yang berdampak luas."},
    {"question_text": "Warga datang dengan emosi tinggi karena dokumennya hilang di kantor Anda. Sikap Anda...", "options": ["Membalas emosi warga", "Tetap tenang, meminta maaf, dan mencari solusi", "Meminta satpam mengamankan", "Mengabaikan sampai warga tenang", "Menyalahkan rekan kerja"], "correct_answer": 1, "explanation": "Tetap tenang dan mencari solusi adalah sikap profesional dalam menghadapi keluhan."},
    {"question_text": "Anda mendapat tugas untuk meningkatkan kualitas pelayanan. Langkah pertama adalah...", "options": ["Langsung mengubah semua prosedur", "Melakukan survei kepuasan masyarakat", "Menambah jumlah petugas", "Membeli peralatan baru", "Meniru kantor lain"], "correct_answer": 1, "explanation": "Survei kepuasan masyarakat adalah langkah pertama untuk memahami kebutuhan dan area perbaikan."},
]

# ============================================================
# TKP — More Integritas
# ============================================================
TKP_INTEGRITAS_2 = [
    {"question_text": "Anda menemukan amplop berisi uang di meja kerja Anda tanpa pengirim yang jelas. Tindakan Anda...", "options": ["Mengambilnya", "Menyerahkan ke unit pengawasan atau keuangan", "Menyimpan dulu", "Membagikan ke rekan", "Mengembalikan ke meja"], "correct_answer": 1, "explanation": "Menyerahkan barang yang tidak jelas pemiliknya ke pihak berwenang adalah sikap berintegritas."},
    {"question_text": "Atasan meminta Anda untuk tidak melaporkan temuan audit yang merugikan. Sikap Anda...", "options": ["Menuruti atasan", "Menolak dan tetap melaporkan sesuai prosedur", "Melaporkan diam-diam", "Meminta imbalan", "Mengundurkan diri"], "correct_answer": 1, "explanation": "Integritas menuntut kita untuk melaporkan temuan audit secara jujur meskipun ada tekanan."},
    {"question_text": "Anda mengetahui ada rekan yang menggunakan fasilitas kantor untuk kepentingan pribadi. Sikap Anda...", "options": ["Ikut menggunakan", "Mengingatkan rekan dan melaporkan jika tidak berubah", "Mengabaikan", "Memanfaatkan situasi", "Menyebarkan gosip"], "correct_answer": 1, "explanation": "Mengingatkan terlebih dahulu, lalu melaporkan jika tidak ada perubahan, adalah sikap berintegritas."},
    {"question_text": "Anda diminta menandatangani dokumen yang isinya tidak sesuai fakta. Tindakan Anda...", "options": ["Menandatangani karena diminta atasan", "Menolak dan meminta dokumen yang sesuai fakta", "Menandatangani dengan catatan", "Menunda tanpa penjelasan", "Menandatangani asal ada paraf atasan"], "correct_answer": 1, "explanation": "Menandatangani dokumen palsu adalah pelanggaran hukum. Menolak adalah sikap berintegritas."},
    {"question_text": "Anda mendapat hadiah dari vendor setelah proses pengadaan selesai. Sikap Anda...", "options": ["Menerima karena proses sudah selesai", "Menolak karena termasuk gratifikasi", "Menerima tapi melaporkan", "Menerima dan menyumbangkan", "Menerima jika nilainya kecil"], "correct_answer": 1, "explanation": "Gratifikasi tetap dilarang meskipun proses sudah selesai. Menolak adalah sikap berintegritas."},
]

def insert_questions(section, topic, questions_list):
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    inserted = 0
    for q in questions_list:
        try:
            cursor.execute(
                "INSERT INTO questions (section, topic, year, difficulty, question_text, options, correct_answer, explanation) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (section, topic, 2024, "sedang", q["question_text"], json.dumps(q["options"], ensure_ascii=False), q["correct_answer"], q["explanation"])
            )
            inserted += 1
        except pymysql.err.IntegrityError:
            pass
    conn.commit()
    cursor.close()
    conn.close()
    return inserted

if __name__ == "__main__":
    total = 0
    total += insert_questions("TWK", "Hankam", TWK_HANKAM)
    total += insert_questions("TWK", "Sejarah Indonesia", TWK_SEJARAH)
    total += insert_questions("TWK", "Pancasila", TWK_PANCASILA)
    total += insert_questions("TIU", "Analogi", TIU_ANALOGI)
    total += insert_questions("TIU", "Silogisme", TIU_SILOGISME)
    total += insert_questions("TKP", "Pelayanan Publik", TKP_PELAYANAN_2)
    total += insert_questions("TKP", "Integritas", TKP_INTEGRITAS_2)
    
    print(f"✅ Batch 2: Inserted {total} new questions")
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("SELECT section, COUNT(*) FROM questions GROUP BY section")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}")
    cursor.execute("SELECT COUNT(*) FROM questions")
    print(f"  Total: {cursor.fetchone()[0]}")
    cursor.close()
    conn.close()
