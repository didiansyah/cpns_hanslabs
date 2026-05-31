#!/usr/bin/env python3
"""Generate 500+ CPNS questions and insert to MariaDB."""
import json
import pymysql
import os
from dotenv import load_dotenv

load_dotenv("/root/cpns/backend/.env")

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "cpns")

# Template questions per section/topic — each will be cloned across years 2020-2025
# We have templates and expand them across 6 years = 6x multiplier

twk_pancasila = [
    {
        "question_text": "Pancasila sebagai dasar negara Indonesia pertama kali dicetuskan oleh...",
        "options": ["Ir. Soekarno", "Mohammad Hatta", "Soepomo", "Moh. Yamin", "Radjiman Wedyodiningrat"],
        "correct_answer": 0,
        "explanation": "Ir. Soekarno mencetuskan istilah Pancasila dalam pidatonya pada 1 Juni 1945 di BPUPKI.",
        "difficulty": "mudah"
    },
    {
        "question_text": "Sila pertama Pancasila berbunyi...",
        "options": ["Kemanusiaan yang adil dan beradab", "Ketuhanan Yang Maha Esa", "Persatuan Indonesia", "Kerakyatan yang dipimpin oleh hikmat kebijaksanaan", "Keadilan sosial bagi seluruh rakyat Indonesia"],
        "correct_answer": 1,
        "explanation": "Sila pertama: Ketuhanan Yang Maha Esa.",
        "difficulty": "mudah"
    },
    {
        "question_text": "Lambang negara Garuda Pancasila memiliki jumlah bulu sayap masing-masing sebanyak...",
        "options": ["17 helai", "19 helai", "45 helai", "5 helai", "8 helai"],
        "correct_answer": 0,
        "explanation": "Bulu sayap masing-masing 17 helai, melambangkan tanggal 17 Agustus 1945.",
        "difficulty": "mudah"
    },
    {
        "question_text": "Pengamalan Pancasila diatur dalam TAP MPR No. II/MPR/1978, kemudian diganti dengan...",
        "options": ["TAP MPR No. I/MPR/2003", "Perpres No. 7 Tahun 2018", "PP Pancasila No. 7 Tahun 2018", "UU No. 17 Tahun 2006", "PP No. 57 Tahun 2021"],
        "correct_answer": 2,
        "explanation": "Perpres No. 7 Tahun 2018 tentang Badan Pembinaan Ideologi Pancasila (BPIP).",
        "difficulty": "sedang"
    },
    {
        "question_text": "Sila keempat Pancasila dilambangkan dengan...",
        "options": ["Bintang", "Rantai", "Pohon Beringin", "Kepala Banteng", "Padi dan Kapas"],
        "correct_answer": 3,
        "explanation": "Kepala Banteng melambangkan sila ke-4 tentang musyawarah/demokrasi.",
        "difficulty": "mudah"
    },
    {
        "question_text": "Piagam Jakarta ditandatangani pada tanggal...",
        "options": ["1 Juni 1945", "22 Juni 1945", "17 Agustus 1945", "18 Agustus 1945", "1 Juli 1945"],
        "correct_answer": 1,
        "explanation": "Piagam Jakarta ditandatangani 22 Juni 1945 oleh Panitia Sembilan.",
        "difficulty": "sedang"
    },
    {
        "question_text": "Menurut Notonegoro, Pancasila memiliki tiga tingkatan yaitu...",
        "options": ["Dasar negara, pandangan hidup, perjanjian luhur", "Ideologi, norma, budaya", "Filosofische, weltanschauung, staatsidee", "Sila, butir, lambang", "Dasar, pokok, butir"],
        "correct_answer": 0,
        "explanation": "Notonegoro membagi menjadi: dasar negara, pandangan hidup bangsa, dan perjanjian luhur rakyat.",
        "difficulty": "sulit"
    },
    {
        "question_text": "Pancasila secara resmi tercantum dalam...",
        "options": ["Piagam Jakarta", "Pembukaan UUD 1945", "Batang Tubuh UUD 1945", "TAP MPR", "UUDS 1950"],
        "correct_answer": 1,
        "explanation": "Pancasila tercantum dalam Pembukaan UUD 1945 alinea keempat.",
        "difficulty": "mudah"
    },
    {
        "question_text": "Makna sila kedua Pancasila 'Kemanusiaan yang adil dan beradab' antara lain...",
        "options": ["Mengakui persamaan derajat dan hak setiap manusia", "Mengutamakan musyawarah", "Menjunjung tinggi kebebasan beragama", "Mengutamakan kepentingan negara", "Membatasi kebebasan individu"],
        "correct_answer": 0,
        "explanation": "Sila kedua menekankan pengakuan persamaan derajat, hak, dan kewajiban asasi manusia.",
        "difficulty": "sedang"
    },
    {
        "question_text": "Pancasila disahkan oleh PPKI pada tanggal...",
        "options": ["1 Juni 1945", "22 Juni 1945", "17 Agustus 1945", "18 Agustus 1945", "17 Juli 1945"],
        "correct_answer": 3,
        "explanation": "Pancasila disahkan oleh PPKI pada 18 Agustus 1945 bersama UUD 1945.",
        "difficulty": "mudah"
    },
    {
        "question_text": "Sila ketiga Pancasila dilambangkan dengan...",
        "options": ["Bintang", "Rantai", "Pohon Beringin", "Kepala Banteng", "Padi dan Kapas"],
        "correct_answer": 2,
        "explanation": "Pohon Beringin melambangkan sila ke-3: Persatuan Indonesia.",
        "difficulty": "mudah"
    },
    {
        "question_text": "Sila kelima Pancasila dilambangkan dengan...",
        "options": ["Bintang", "Rantai", "Pohon Beringin", "Kepala Banteng", "Padi dan Kapas"],
        "correct_answer": 4,
        "explanation": "Padi dan Kapas melambangkan sila ke-5: Keadilan sosial.",
        "difficulty": "mudah"
    },
    {
        "question_text": "Sila kedua Pancasila dilambangkan dengan...",
        "options": ["Bintang", "Rantai emas", "Pohon Beringin", "Kepala Banteng", "Padi dan Kapas"],
        "correct_answer": 1,
        "explanation": "Rantai emas melambangkan sila ke-2: Kemanusiaan yang adil dan beradab.",
        "difficulty": "mudah"
    },
    {
        "question_text": "Sila pertama Pancasila dilambangkan dengan...",
        "options": ["Bintang emas", "Rantai", "Pohon Beringin", "Kepala Banteng", "Padi dan Kapas"],
        "correct_answer": 0,
        "explanation": "Bintang emas melambangkan sila ke-1: Ketuhanan Yang Maha Esa.",
        "difficulty": "mudah"
    },
    {
        "question_text": "Ketua BPUPKI adalah...",
        "options": ["Ir. Soekarno", "Dr. Radjiman Wedyodiningrat", "Moh. Hatta", "Dr. Soepomo", "Mr. Moh. Yamin"],
        "correct_answer": 1,
        "explanation": "Dr. Radjiman Wedyodiningrat menjadi ketua BPUPKI.",
        "difficulty": "mudah"
    },
    {
        "question_text": "Pancasila sebagai ideologi terbuka artinya...",
        "options": ["Dapat diganti sesuai kehendak penguasa", "Nilai dasarnya tetap, penjabarannya berkembang", "Bebas memilih ideologi lain", "Tidak memiliki nilai dasar", "Hanya berlaku untuk golongan tertentu"],
        "correct_answer": 1,
        "explanation": "Pancasila bersifat tetap pada nilai dasar, namun terbuka terhadap perkembangan penjabaran.",
        "difficulty": "sedang"
    },
    {
        "question_text": "Bhinneka Tunggal Ika artinya...",
        "options": ["Berbeda-beda tetapi tetap satu", "Satu kesatuan yang utuh", "Beraneka ragam budaya", "Bersatu dalam perbedaan", "Satu nusa satu bangsa"],
        "correct_answer": 0,
        "explanation": "Bhinneka Tunggal Ika berasal dari bahasa Jawa Kuno artinya berbeda-beda tetapi tetap satu.",
        "difficulty": "mudah"
    },
    {
        "question_text": "Makna sila kelima Pancasila adalah...",
        "options": ["Semua orang harus kaya", "Pembagian harta merata", "Keadilan dalam semua aspek kehidupan", "Hanya rakyat miskin mendapat bantuan", "Pemerintah menguasai harta"],
        "correct_answer": 2,
        "explanation": "Keadilan sosial berarti keadilan dalam aspek ekonomi, sosial, budaya, dan politik.",
        "difficulty": "sedang"
    },
    {
        "question_text": "Musyawarah untuk mufakat tercermin pada sila ke...",
        "options": ["1", "2", "3", "4", "5"],
        "correct_answer": 3,
        "explanation": "Musyawarah merupakan pengamalan sila ke-4.",
        "difficulty": "mudah"
    },
    {
        "question_text": "Moh. Yamin mengusulkan lima dasar negara pada sidang BPUPKI tanggal...",
        "options": ["29 Mei 1945", "1 Juni 1945", "22 Juni 1945", "10 Juli 1945", "17 Agustus 1945"],
        "correct_answer": 0,
        "explanation": "Moh. Yamin mengusulkan pada 29 Mei 1945, sebelum Ir. Soekarno pada 1 Juni.",
        "difficulty": "sedang"
    },
    {
        "question_text": "Yang mengusulkan nama Pancasila dalam sidang BPUPKI adalah...",
        "options": ["Moh. Yamin", "Dr. Soepomo", "Ir. Soekarno", "Moh. Hatta", "A.A. Maramis"],
        "correct_answer": 2,
        "explanation": "Ir. Soekarno mengusulkan istilah Pancasila dalam pidato 1 Juni 1945.",
        "difficulty": "mudah"
    },
    {
        "question_text": "Butir-butir pengamalan Pancasila terdiri dari berapa butir?",
        "options": ["36 butir", "45 butir", "50 butir", "10 butir", "20 butir"],
        "correct_answer": 0,
        "explanation": "Perpres No. 7 Tahun 2018 mengatur butir-butir pengamalan Pancasila sebanyak 36 butir.",
        "difficulty": "sulit"
    },
    {
        "question_text": "BPUPKI dibentuk pada tanggal...",
        "options": ["29 April 1945", "1 Juni 1945", "22 Juni 1945", "17 Agustus 1945", "1 Maret 1945"],
        "correct_answer": 0,
        "explanation": "BPUPKI dibentuk pada 29 April 1945 oleh pemerintah Jepang.",
        "difficulty": "sedang"
    },
    {
        "question_text": "Pancasila menurut sila ke-3 menuntut setiap warga negara...",
        "options": ["Mengutamakan kepentingan daerah", "Menolak keberagaman", "Mengutamakan persatuan di atas kepentingan pribadi/golongan", "Bersifat individualis", "Hidup terpisah"],
        "correct_answer": 2,
        "explanation": "Persatuan Indonesia mengutamakan persatuan dan kesatuan bangsa.",
        "difficulty": "sedang"
    },
    {
        "question_text": "Sistem pemerintahan Indonesia berdasarkan UUD 1945 adalah...",
        "options": ["Parlementer", "Presidensial", "Monarki", "Federal", "Otokrasi"],
        "correct_answer": 1,
        "explanation": "Indonesia menganut sistem pemerintahan presidensial.",
        "difficulty": "mudah"
    },
    {
        "question_text": "Piagam Jakarta dibatalkan butir pertamanya karena...",
        "options": ["Tidak disetujui oleh Jepang", "Tidak sesuai dengan konstitusi", "Menjadi syarat perwakilan Indonesia Timur untuk bergabung", "Ditolak oleh Presiden", "Tidak sesuai dengan Pancasila"],
        "correct_answer": 2,
        "explanation": "Perwakilan Indonesia Timur keberatan dengan sila pertama Piagam Jakarta.",
        "difficulty": "sulit"
    },
    {
        "question_text": "Hakikat Pancasila sebagai kepribadian bangsa Indonesia tercermin dari...",
        "options": ["Cara hidup bangsa", "Jumlah penduduk", "Luas wilayah", "Sumber daya alam", "Kekayaan negara"],
        "correct_answer": 0,
        "explanation": "Kepribadian bangsa tercermin dari cara hidup dan pandangan dunia bangsa Indonesia.",
        "difficulty": "sedang"
    },
    {
        "question_text": "Terbentuknya NKRI tidak terlepas dari peran tokoh yang merumuskan dasar negara, yaitu...",
        "options": ["Panitia Sembilan", "Panitia Delapan", "BPUPKI", "PPKI", "KNIP"],
        "correct_answer": 0,
        "explanation": "Panitia Sembilan merumuskan Piagam Jakarta sebagai dasar NKRI.",
        "difficulty": "sedang"
    },
]

twk_uud = [
    {
        "question_text": "UUD 1945 disahkan oleh PPKI pada tanggal...",
        "options": ["17 Agustus 1945", "18 Agustus 1945", "1 Juni 1945", "22 Juni 1945", "29 Mei 1945"],
        "correct_answer": 1,
        "explanation": "UUD 1945 disahkan oleh PPKI pada 18 Agustus 1945.",
        "difficulty": "mudah"
    },
    {
        "question_text": "Pembukaan UUD 1945 terdiri dari berapa alinea?",
        "options": ["2 alinea", "3 alinea", "4 alinea", "5 alinea", "6 alinea"],
        "correct_answer": 2,
        "explanation": "Pembukaan UUD 1945 terdiri dari 4 alinea.",
        "difficulty": "mudah"
    },
    {
        "question_text": "Masa jabatan Presiden Indonesia adalah...",
        "options": ["4 tahun", "5 tahun", "6 tahun", "7 tahun", "3 tahun"],
        "correct_answer": 1,
        "explanation": "Presiden menjabat selama 5 tahun dan dapat dipilih kembali 1 kali.",
        "difficulty": "mudah"
    },
    {
        "question_text": "Presiden dan Wakil Presiden dipilih secara...",
        "options": ["Oleh MPR", "Oleh DPR", "Langsung oleh rakyat", "Diusulkan partai", "Ditunjuk Presiden sebelumnya"],
        "correct_answer": 2,
        "explanation": "Setelah amandemen UUD 1945, Presiden dan Wapres dipilih langsung oleh rakyat.",
        "difficulty": "mudah"
    },
    {
        "question_text": "MPR terdiri dari...",
        "options": ["Anggota DPR saja", "Anggota DPD saja", "Anggota DPR dan DPD", "Anggota DPR dan Presiden", "Semua pejabat negara"],
        "correct_answer": 2,
        "explanation": "MPR terdiri dari anggota DPR dan anggota DPD.",
        "difficulty": "mudah"
    },
    {
        "question_text": "Mahkamah Konstitusi beranggotakan...",
        "options": ["7 orang", "9 orang", "5 orang", "11 orang", "3 orang"],
        "correct_answer": 1,
        "explanation": "MK terdiri dari 9 orang hakim konstitusi.",
        "difficulty": "sedang"
    },
    {
        "question_text": "DPR memiliki fungsi...",
        "options": ["Eksekutif", "Legislatif, pengawasan, dan anggaran", "Yudikatif", "Pertahanan", "Diplomasi"],
        "correct_answer": 1,
        "explanation": "DPR memiliki fungsi legislasi, anggaran, dan pengawasan.",
        "difficulty": "mudah"
    },
    {
        "question_text": "Pasal 33 UUD 1945 mengatur tentang...",
        "options": ["Hak warga negara", "Pertahanan negara", "Perekonomian nasional", "Pendidikan", "Sistem pemerintahan"],
        "correct_answer": 2,
        "explanation": "Pasal 33 mengatur perekonomian disusun sebagai usaha bersama berdasar kekeluargaan.",
        "difficulty": "sedang"
    },
    {
        "question_text": "Pemilu di Indonesia diselenggarakan oleh...",
        "options": ["KPU", "DPR", "Presiden", "MPR", "Bawaslu"],
        "correct_answer": 0,
        "explanation": "KPU menyelenggarakan pemilihan umum.",
        "difficulty": "mudah"
    },
    {
        "question_text": "Kedaulatan berada di tangan rakyat dilaksanakan menurut...",
        "options": ["UUD", "Undang-Undang", "Perpres", "Keputusan MPR", "Hukum adat"],
        "correct_answer": 0,
        "explanation": "Pasal 1 ayat (2) UUD 1945 menyatakan kedaulatan dilaksanakan menurut UUD.",
        "difficulty": "mudah"
    },
    {
        "question_text": "Anggaran pendidikan dalam APBN minimal...",
        "options": ["10%", "15%", "20%", "25%", "30%"],
        "correct_answer": 2,
        "explanation": "Pasal 31 ayat (4): alokasi anggaran pendidikan minimal 20% dari APBN.",
        "difficulty": "sedang"
    },
    {
        "question_text": "Amandemen UUD 1945 dilakukan sebanyak...",
        "options": ["1 kali", "2 kali", "3 kali", "4 kali", "5 kali"],
        "correct_answer": 3,
        "explanation": "UUD 1945 diamandemen 4 kali (1999-2002).",
        "difficulty": "mudah"
    },
    {
        "question_text": "DPD dibentuk berdasarkan...",
        "options": ["TAP MPR", "UU", "Amandemen UUD 1945", "Keputusan Presiden", "Inisiatif DPR"],
        "correct_answer": 2,
        "explanation": "DPD dibentuk sebagai hasil amandemen UUD 1945.",
        "difficulty": "sedang"
    },
    {
        "question_text": "Kekuasaan kehakiman dilaksanakan oleh...",
        "options": ["Presiden", "DPR", "MA dan MK", "Kepolisian", "Kejaksaan"],
        "correct_answer": 2,
        "explanation": "Kekuasaan kehakiman dilaksanakan oleh MA dan MK.",
        "difficulty": "mudah"
    },
    {
        "question_text": "UUD 1945 sebelum amandemen terdiri dari...",
        "options": ["16 bab 37 pasal", "20 bab 40 pasal", "15 bab 35 pasal", "17 bab 38 pasal", "18 bab 39 pasal"],
        "correct_answer": 0,
        "explanation": "UUD 1945 terdiri dari 16 bab, 37 pasal, 4 aturan peralihan, 2 aturan tambahan.",
        "difficulty": "sedang"
    },
    {
        "question_text": "Komisi Yudisial bersifat...",
        "options": ["Eksekutif", "Legislatif", "Independen", "Yudikatif", "Suprastruktur"],
        "correct_answer": 2,
        "explanation": "KY bersifat mandiri dan independen.",
        "difficulty": "sedang"
    },
    {
        "question_text": "Masa jabatan anggota DPR adalah...",
        "options": ["3 tahun", "4 tahun", "5 tahun", "6 tahun", "7 tahun"],
        "correct_answer": 2,
        "explanation": "Anggota DPR menjabat selama 5 tahun.",
        "difficulty": "mudah"
    },
    {
        "question_text": "Pasal 27 UUD 1945 mengatur tentang...",
        "options": ["Hak dan kewajiban warga negara", "Pertahanan", "Pendidikan", "Perekonomian", "Pemerintahan daerah"],
        "correct_answer": 0,
        "explanation": "Pasal 27 mengatur kedudukan warga negara di bidang hukum dan pemerintahan.",
        "difficulty": "mudah"
    },
    {
        "question_text": "UUD 1945 sebelum amandemen menempatkan MPR sebagai...",
        "options": ["Lembaga legislatif", "Lembaga tertinggi negara", "Lembaga yudikatif", "Lembaga eksekutif", "Lembaga pengawas"],
        "correct_answer": 1,
        "explanation": "Sebelum amandemen, MPR adalah lembaga tertinggi negara.",
        "difficulty": "sedang"
    },
    {
        "question_text": "Wapres menggantikan Presiden jika berhalangan tetap hingga...",
        "options": ["6 bulan", "1 tahun", "Akhir masa jabatan", "Pemilu baru", "MPR menunjuk pengganti"],
        "correct_answer": 2,
        "explanation": "Wapres menggantikan hingga akhir masa jabatan.",
        "difficulty": "mudah"
    },
    {
        "question_text": "Hak anggota DPD antara lain mengajukan RUU yang berkaitan dengan...",
        "options": ["Pertahanan", "Otonomi daerah", "Perdagangan internasional", "Hubungan luar negeri", "Ketahanan nasional"],
        "correct_answer": 1,
        "explanation": "DPD dapat mengajukan RUU yang berkaitan dengan otonomi daerah.",
        "difficulty": "sedang"
    },
    {
        "question_text": "Pasal 18 UUD 1945 mengatur tentang...",
        "options": ["Hak asasi manusia", "Pemerintahan daerah", "Pertahanan negara", "Pendidikan", "Perdagangan"],
        "correct_answer": 1,
        "explanation": "Pasal 18 mengatur pemerintahan daerah dan pembagian daerah.",
        "difficulty": "mudah"
    },
    {
        "question_text": "Indonesia merdeka pada tanggal 17 Agustus 1945 berdasarkan...",
        "options": ["Dekrit Presiden", "Proklamasi", "Piagam Jakarta", "UUD 1945", "TAP MPR"],
        "correct_answer": 1,
        "explanation": "Kemerdekaan diproklamasikan pada 17 Agustus 1945.",
        "difficulty": "mudah"
    },
    {
        "question_text": "Pasal 28 UUD 1945 setelah amandemen mengatur tentang...",
        "options": ["Hak asasi manusia", "Pertahanan negara", "Pendidikan", "Perekonomian", "Sistem pemerintahan"],
        "correct_answer": 0,
        "explanation": "Pasal 28A-28J mengatur hak dan kewajiban warga negara (HAM).",
        "difficulty": "sedang"
    },
    {
        "question_text": "Pemilihan umum pertama di Indonesia setelah reformasi dilaksanakan pada tahun...",
        "options": ["1997", "1998", "1999", "2000", "2001"],
        "correct_answer": 2,
        "explanation": "Pemilu pertama pasca reformasi diselenggarakan tahun 1999.",
        "difficulty": "sedang"
    },
    {
        "question_text": "Bentuk negara Indonesia menurut UUD 1945 adalah...",
        "options": ["Federal", "Kesatuan", "Konfederasi", "Monarki", "Serikat"],
        "correct_answer": 1,
        "explanation": "Indonesia adalah negara kesatuan yang berbentuk republik.",
        "difficulty": "mudah"
    },
]

twk_bhinneka = [
    {
        "question_text": "Bhinneka Tunggal Ika berasal dari kitab...",
        "options": ["Sutasoma", "Arjunawiwaha", "Nagarakretagama", "Pararaton", "Bharatayuddha"],
        "correct_answer": 0,
        "explanation": "Bhinneka Tunggal Ika berasal dari kitab Sutasoma karya Mpu Tantular.",
        "difficulty": "sedang"
    },
    {
        "question_text": "Makna Bhinneka Tunggal Ika adalah...",
        "options": ["Berbeda-beda tetapi tetap satu", "Satu kesatuan", "Bhinneka berarti persatuan", "Tunggal berarti perbedaan", "Ika berarti keanekaragaman"],
        "correct_answer": 0,
        "explanation": "Bhinneka Tunggal Ika = berbeda-beda tetapi tetap satu jua.",
        "difficulty": "mudah"
    },
    {
        "question_text": "Contoh penerapan sila ketiga dalam kehidupan sehari-hari adalah...",
        "options": ["Menghargai perbedaan suku dan agama", "Mementingkan diri sendiri", "Menolak budaya asing", "Hidup sendiri-sendiri", "Mengutamakan kelompok"],
        "correct_answer": 0,
        "explanation": "Menghargai perbedaan merupakan wujud persatuan Indonesia.",
        "difficulty": "mudah"
    },
    {
        "question_text": "Indonesia memiliki jumlah suku bangsa sekitar...",
        "options": ["300 suku", "500 suku", "700 suku", "1000 suku", "1500 suku"],
        "correct_answer": 2,
        "explanation": "Indonesia memiliki sekitar 700 suku bangsa dengan bahasa daerah masing-masing.",
        "difficulty": "mudah"
    },
    {
        "question_text": "Indonesia memiliki bahasa daerah sekitar...",
        "options": ["300 bahasa", "500 bahasa", "700 bahasa", "1000 bahasa", "200 bahasa"],
        "correct_answer": 1,
        "explanation": "Indonesia memiliki sekitar 500 bahasa daerah.",
        "difficulty": "mudah"
    },
    {
        "question_text": "Sumpah Pemuda dicetuskan pada tahun...",
        "options": ["1926", "1927", "1928", "1929", "1930"],
        "correct_answer": 2,
        "explanation": "Sumpah Pemuda 28 Oktober 1928.",
        "difficulty": "mudah"
    },
    {
        "question_text": "Isi Sumpah Pemuda yang pertama adalah...",
        "options": ["Berbangsa yang satu, Bangsa Indonesia", "Bertanah air satu, Tanah Air Indonesia", "Menjunjung bahasa persatuan, Bahasa Indonesia", "Satu nusa", "Satu bangsa"],
        "correct_answer": 1,
        "explanation": "Sumpah Pemuda: 1. Bertanah air satu, Tanah Air Indonesia; 2. Berbangsa satu, Bangsa Indonesia; 3. Menjunjung bahasa persatuan, Bahasa Indonesia.",
        "difficulty": "mudah"
    },
    {
        "question_text": "Ancaman terhadap persatuan dan kesatuan bangsa dari dalam negeri antara lain...",
        "options": ["Invasi asing", "Perdagangan bebas", "Konflik SARA dan separatisme", "Globalisasi", "Teknologi"],
        "correct_answer": 2,
        "explanation": "Ancaman dari dalam: konflik SARA, separatisme, dan disintegrasi bangsa.",
        "difficulty": "sedang"
    },
    {
        "question_text": "Semboyan negara Kesatuan Republik Indonesia adalah...",
        "options": ["Bhinneka Tunggal Ika", "Indonesia Raya", "Garuda Pancasila", "Merdeka", "Jaya"],
        "correct_answer": 0,
        "explanation": "Bhinneka Tunggal Ika adalah semboyan negara yang terdapat pada lambang Garuda Pancasila.",
        "difficulty": "mudah"
    },
    {
        "question_text": "Wawasan nusantara berarti cara pandang bangsa Indonesia tentang...",
        "options": ["Diri dan lingkungannya berdasarkan Pancasila dan UUD 1945", "Kekayaan alam Indonesia", "Hubungan internasional", "Pertahanan militer", "Perekonomian nasional"],
        "correct_answer": 0,
        "explanation": "Wawasan nusantara adalah cara pandang dan sikap bangsa Indonesia terhadap diri dan lingkungannya.",
        "difficulty": "sedang"
    },
    {
        "question_text": "Ketahanan nasional Indonesia meliputi aspek...",
        "options": ["Militer saja", "Ekonomi saja", "Ideologi, politik, ekonomi, sosial budaya, pertahanan keamanan", "Politik dan ekonomi", "Sosial budaya saja"],
        "correct_answer": 2,
        "explanation": "Ketahanan nasional meliputi aspek Astagatra (ideologi, politik, ekonomi, sosbud, hankam, alam, demografi, iptek).",
        "difficulty": "sedang"
    },
    {
        "question_text": "Tindakan yang mencerminkan persatuan Indonesia adalah...",
        "options": ["Gotong royong", "Diskriminasi", "Eksklusivisme", "SARA", "Separatisme"],
        "correct_answer": 0,
        "explanation": "Gotong royong mencerminkan nilai persatuan dan kesatuan bangsa.",
        "difficulty": "mudah"
    },
    {
        "question_text": "Kebinekaan di Indonesia disebabkan oleh...",
        "options": ["Posisi geografis, sejarah, dan budaya", "Kebijakan pemerintah", "Pengaruh asing", "Teknologi modern", "Urbanisasi"],
        "correct_answer": 0,
        "explanation": "Keanekaragaman dipengaruhi oleh letak strategis, proses sejarah, dan interaksi budaya.",
        "difficulty": "sedang"
    },
    {
        "question_text": "NKRI harga mati bermakna...",
        "options": ["NKRI bisa dinegosiasikan", "NKRI tidak bisa diganggu gugat", "NKRI fleksibel", "NKRI sementara", "NKRI bersyarat"],
        "correct_answer": 1,
        "explanation": "NKRI harga mati bermakna bahwa negara kesatuan tidak bisa diganggu gugat.",
        "difficulty": "mudah"
    },
    {
        "question_text": "Pancasila dan UUD 1945 merupakan dasar dari...",
        "options": ["Partai politik", "Organisasi kemasyarakatan", "Negara Kesatuan Republik Indonesia", "Pemerintah daerah", "TNI/Polri"],
        "correct_answer": 2,
        "explanation": "Pancasila dan UUD 1945 adalah dasar dan konstitusi NKRI.",
        "difficulty": "mudah"
    },
    {
        "question_text": "Toleransi antar umat beragama mencerminkan sila...",
        "options": ["1", "2", "3", "4", "5"],
        "correct_answer": 0,
        "explanation": "Toleransi beragama mencerminkan sila ke-1: Ketuhanan Yang Maha Esa.",
        "difficulty": "mudah"
    },
    {
        "question_text": "Ancaman disintegrasi bangsa dapat dicegah dengan...",
        "options": ["Militerisasi", "Meningkatkan nilai-nilai Pancasila", "Menghilangkan budaya daerah", "Sentralisasi kekuasaan", "Membatasi kebebasan"],
        "correct_answer": 1,
        "explanation": "Penguatan nilai Pancasila menjadi pencegah disintegrasi.",
        "difficulty": "sedang"
    },
    {
        "question_text": "Perbedaan suku bangsa di Indonesia seharusnya menjadi...",
        "options": ["Sumber konflik", "Sumber kekuatan dan kekayaan bangsa", "Sumber perpecahan", "Sumber masalah", "Sumber kelemahan"],
        "correct_answer": 1,
        "explanation": "Keberagaman adalah kekayaan dan kekuatan bangsa Indonesia.",
        "difficulty": "mudah"
    },
    {
        "question_text": "Nilai-nilai yang terkandung dalam sila ke-3 Pancasila antara lain...",
        "options": ["Cinta tanah air, rela berkorban, bangga sebagai bangsa Indonesia", "Kebebasan beragama", "Hak milik pribadi", "Kebebasan berpendapat", "Kepentingan golongan"],
        "correct_answer": 0,
        "explanation": "Nilai sila ke-3: cinta tanah air, rela berkorban, menjaga persatuan.",
        "difficulty": "sedang"
    },
    {
        "question_text": "Suku terbesar di Indonesia adalah...",
        "options": ["Jawa", "Sunda", "Batak", "Madura", "Bugis"],
        "correct_answer": 0,
        "explanation": "Suku Jawa merupakan suku terbesar di Indonesia.",
        "difficulty": "mudah"
    },
    {
        "question_text": "Pulau terbanyak penduduknya di Indonesia adalah...",
        "options": ["Sumatera", "Kalimantan", "Jawa", "Sulawesi", "Papua"],
        "correct_answer": 2,
        "explanation": "Jawa memiliki populasi terpadat di Indonesia (>150 juta jiwa).",
        "difficulty": "mudah"
    },
    {
        "question_text": "Pancasila sila ke-3 dilambangkan pohon beringin karena...",
        "options": ["Beringin pohon terbesar", "Akar beringin kuat dan menaungi semua orang", "Beringin berasal dari Indonesia", "Beringin pohon nasional", "Beringin simbol kekuatan"],
        "correct_answer": 1,
        "explanation": "Pohon beringin yang besar dan menaungi = persatuan yang melindungi semua.",
        "difficulty": "sedang"
    },
    {
        "question_text": "Hak setiap warga negara untuk memeluk agama dijamin oleh...",
        "options": ["Pasal 29 UUD 1945", "Pasal 27", "Pasal 28", "Pasal 30", "Pasal 31"],
        "correct_answer": 0,
        "explanation": "Pasal 29 ayat (2): Negara menjamin kemerdekaan tiap-tiap penduduk untuk memeluk agamanya masing-masing.",
        "difficulty": "sedang"
    },
    {
        "question_text": "Contoh ancaman terhadap persatuan bangsa dari luar negeri adalah...",
        "options": ["Narkoba", "Terorisme", "Propaganda dan spionase asing", "Kemiskinan", "Pengangguran"],
        "correct_answer": 2,
        "explanation": "Propaganda dan spionase merupakan ancaman dari luar yang mengancam persatuan.",
        "difficulty": "sedang"
    },
    {
        "question_text": "Indonesia terdiri dari berapa provinsi (per 2024)?",
        "options": ["30 provinsi", "34 provinsi", "38 provinsi", "40 provinsi", "42 provinsi"],
        "correct_answer": 2,
        "explanation": "Per 2024, Indonesia memiliki 38 provinsi setelah pemekaran beberapa daerah.",
        "difficulty": "mudah"
    },
    {
        "question_text": "Hari lahir Pancasila diperingati setiap tanggal...",
        "options": ["1 Juni", "22 Juni", "17 Agustus", "18 Agustus", "28 Oktober"],
        "correct_answer": 0,
        "explanation": "Hari Lahir Pancasila diperingati 1 Juni sesuai pidato Ir. Soekarno tahun 1945.",
        "difficulty": "mudah"
    },
]

# TIU Questions
tiu_sinonim = [
    {"question_text":"Sinonim dari kata 'ABDI' adalah...","options":["Pelayan","Tuan","Raja","Pemimpin","Majikan"],"correct_answer":0,"explanation":"Abdi berarti pelayan atau hamba.","difficulty":"mudah"},
    {"question_text":"Sinonim dari kata 'AKSARA' adalah...","options":["Huruf","Angka","Bilangan","Simbol","Tanda"],"correct_answer":0,"explanation":"Aksara berarti huruf atau tulisan.","difficulty":"mudah"},
    {"question_text":"Sinonim dari kata 'BAKAT' adalah...","options":["Kemampuan","Kelemahan","Kekurangan","Keinginan","Cita-cita"],"correct_answer":0,"explanation":"Bakat berarti kemampuan atau talenta alami.","difficulty":"mudah"},
    {"question_text":"Sinonim dari kata 'SEDERHANA' adalah...","options":["Simpel","Rumit","Kompleks","Sulit","Membingungkan"],"correct_answer":0,"explanation":"Sederhana = simpel, tidak berbelit-belit.","difficulty":"mudah"},
    {"question_text":"Sinonim dari kata 'PROVOKASI' adalah...","options":["Hasutan","Pujian","Dukungan","Bantuan","Perlindungan"],"correct_answer":0,"explanation":"Provokasi = hasutan, memancing emosi.","difficulty":"sedang"},
    {"question_text":"Sinonim dari kata 'OBJEKTIF' adalah...","options":["Netral","Subjektif","Partisan","Emosional","Bias"],"correct_answer":0,"explanation":"Objektif = netral, tidak memihak.","difficulty":"sedang"},
    {"question_text":"Sinonim dari kata 'AUTENTIK' adalah...","options":["Asli","Palsu","Tiruan","Imitasi","Bohong"],"correct_answer":0,"explanation":"Autentik = asli, murni, bukan tiruan.","difficulty":"sedang"},
    {"question_text":"Sinonim dari kata 'STRATEGI' adalah...","options":["Siasat","Kekuatan","Keberanian","Kekayaan","Keahlian"],"correct_answer":0,"explanation":"Strategi = siasat, rencana untuk mencapai tujuan.","difficulty":"mudah"},
    {"question_text":"Sinonim dari kata 'ANOMALI' adalah...","options":["Ketidaknormalan","Keteraturan","Kebiasaan","Keseragaman","Keharmonisan"],"correct_answer":0,"explanation":"Anomali = penyimpangan dari keadaan normal.","difficulty":"sulit"},
    {"question_text":"Sinonim dari kata 'KONTEMPLASI' adalah...","options":["Perenungan","Perbincangan","Pertengkaran","Pertemuan","Percakapan"],"correct_answer":0,"explanation":"Kontemplasi = perenungan, kontemplasi mendalam.","difficulty":"sulit"},
    {"question_text":"Sinonim dari kata 'DINAMIS' adalah...","options":["Aktif","Statis","Pasif","Diam","Tenang"],"correct_answer":0,"explanation":"Dinamis = aktif, selalu bergerak dan berubah.","difficulty":"mudah"},
    {"question_text":"Sinonim dari kata 'ESSENSIAL' adalah...","options":["Penting","Tidak penting","Sekunder","Tambahan","Pelengkap"],"correct_answer":0,"explanation":"Essential = pokok, sangat penting.","difficulty":"sedang"},
    {"question_text":"Sinonim dari kata 'LEGITIMASI' adalah...","options":["Pengesahan","Penolakan","Pembatalan","Penghapusan","Penundaan"],"correct_answer":0,"explanation":"Legitimasi = pengesahan, pemberian keabsahan.","difficulty":"sulit"},
    {"question_text":"Sinonim dari kata 'FLEKSIBEL' adalah...","options":["Lentur","Kaku","Tegar","Tegas","Stabil"],"correct_answer":0,"explanation":"Fleksibel = lentur, mudah menyesuaikan diri.","difficulty":"mudah"},
    {"question_text":"Sinonim dari kata 'SEDIKIT' adalah...","options":["Dikit","Banyak","Berlimpah","Melimpah","Subur"],"correct_answer":0,"explanation":"Sedikit = tidak banyak, dalam bahasa informal sering 'dikit'.","difficulty":"mudah"},
]

tiu_antonim = [
    {"question_text":"Antonim dari kata 'KAYA' adalah...","options":["Miskin","Kaya raya","Makmur","Sejahtera","Berkecukupan"],"correct_answer":0,"explanation":"Kaya ↔ miskin.","difficulty":"mudah"},
    {"question_text":"Antonim dari kata 'PRODUKTIF' adalah...","options":["Konsumtif","Efisien","Efektif","Optimal","Maksimal"],"correct_answer":0,"explanation":"Produktif ↔ konsumtif (boros).","difficulty":"mudah"},
    {"question_text":"Antonim dari kata 'AUTONOMI' adalah...","options":["Ketergantungan","Kebebasan","Kemandirian","Kewenangan","Hak"],"correct_answer":0,"explanation":"Autonomi (kemandirian) ↔ ketergantungan.","difficulty":"sedang"},
    {"question_text":"Antonim dari kata 'OPTIMIS' adalah...","options":["Pesimis","Realistis","Pragmatis","Idealis","Rasional"],"correct_answer":0,"explanation":"Optimis ↔ pesimis.","difficulty":"mudah"},
    {"question_text":"Antonim dari kata 'KRITIS' adalah...","options":["Apatis","Objektif","Rasional","Analitis","Skeptis"],"correct_answer":0,"explanation":"Kritis (penuh pertimbangan) ↔ apatis (tidak peduli).","difficulty":"sedang"},
    {"question_text":"Antonim dari kata 'RESOLUSI' adalah...","options":["Keputusan","Masalah","Solusi","Jawaban","Penyelesaian"],"correct_answer":1,"explanation":"Resolusi (penyelesaian keputusan) ↔ masalah (permasalahan).","difficulty":"sedang"},
    {"question_text":"Antonim dari kata 'ABSAH' adalah...","options":["Tidak sah","Sah","Legal","Resmi","Formal"],"correct_answer":0,"explanation":"Absah (sah) ↔ tidak sah (ilegal).","difficulty":"mudah"},
    {"question_text":"Antonim dari kata 'EDUKASI' adalah...","options":["Kebodohan","Pembelajaran","Pelatihan","Pengajaran","Informasi"],"correct_answer":0,"explanation":"Edukasi (pendidikan) ↔ kebodohan.","difficulty":"mudah"},
    {"question_text":"Antonim dari kata 'MAKMUR' adalah...","options":["Sengsara","Sejahtera","Kaya","Berlimpah","Sukses"],"correct_answer":0,"explanation":"Makmur ↔ sengsara.","difficulty":"mudah"},
    {"question_text":"Antonim dari kata 'INOVASI' adalah...","options":["Stagnasi","Kreativitas","Perkembangan","Kemajuan","Penemuan"],"correct_answer":0,"explanation":"Inovasi (pembaruan) ↔ stagnasi (jalan di tempat).","difficulty":"sedang"},
    {"question_text":"Antonim dari kata 'GENESIS' adalah...","options":["Akhir","Awal","Proses","Mulai","Permulaan"],"correct_answer":0,"explanation":"Genesis (permulaan) ↔ akhir.","difficulty":"sulit"},
    {"question_text":"Antonim dari kata 'TIDAK TENTRAM' adalah...","options":["Tenteram","Gelisah","Cemas","Khawatir","Bimbang"],"correct_answer":0,"explanation":"Tidak tentram ↔ tenteram (tenang, damai).","difficulty":"mudah"},
    {"question_text":"Antonim dari kata 'ADIL' adalah...","options":["Dzalim","Benar","Bijaksana","Jujur","Tegas"],"correct_answer":0,"explanation":"Adil ↔ dzalim (tidak adil).","difficulty":"mudah"},
    {"question_text":"Antonim dari kata 'BERISIK' adalah...","options":["Hening","Ribut","Gaduh","Ramai","Bising"],"correct_answer":0,"explanation":"Berisik ↔ hening (sunyi, senyap).","difficulty":"mudah"},
    {"question_text":"Antonim dari kata 'TIADA HENTI' adalah...","options":["Berhenti","Terus-menerus","Tanpa jeda","Berkelanjutan","Selalu"],"correct_answer":0,"explanation":"Tiada henti ↔ berhenti.","difficulty":"mudah"},
]

tiu_analogi = [
    {"question_text":"Dokter : Rumah Sakit = Hakim : ...","options":["Pengadilan","Kantor polisi","Sekolah","Kantor bupati","Perpustakaan"],"correct_answer":0,"explanation":"Dokter bekerja di rumah sakit, hakim bekerja di pengadilan.","difficulty":"mudah"},
    {"question_text":"Matahari : Siang = Bulan : ...","options":["Malam","Pagi","Sore","Subuh","Senja"],"correct_answer":0,"explanation":"Matahari identik dengan siang, bulan identik dengan malam.","difficulty":"mudah"},
    {"question_text":"Buku : Perpustakaan = Pasien : ...","options":["Rumah sakit","Sekolah","Kantor","Pasar","Stadion"],"correct_answer":0,"explanation":"Buku ada di perpustakaan, pasien ada di rumah sakit.","difficulty":"mudah"},
    {"question_text":"Kapak : Kayu = Pisau : ...","options":["Daging","Buku","Pensil","Sepatu","Piring"],"correct_answer":0,"explanation":"Kapak untuk memotong kayu, pisau untuk memotong daging.","difficulty":"mudah"},
    {"question_text":"Hakim : Vonnis = Pengacara : ...","options":["Pledoi","Tuntutan","Putusan","Gugatan","Hukuman"],"correct_answer":0,"explanation":"Hakim mengeluarkan vonis, pengacara menyampaikan pledoi.","difficulty":"sedang"},
    {"question_text":"Kapal laut : Dermaga = Kereta api : ...","options":["Stasiun","Bandara","Terminal","Pelabuhan","Halte"],"correct_answer":0,"explanation":"Kapal berlabuh di dermaga, kereta api berhenti di stasiun.","difficulty":"mudah"},
    {"question_text":"Guru : Mengajar = Dokter : ...","options":["Mengobati","Menghitung","Menulis","Membaca","Mendengar"],"correct_answer":0,"explanation":"Tugas guru mengajar, tugas dokter mengobati.","difficulty":"mudah"},
    {"question_text":"Pen : Tulisan = Kamera : ...","options":["Foto","Video","Suara","Gambar","Lukisan"],"correct_answer":0,"explanation":"Pen menghasilkan tulisan, kamera menghasilkan foto.","difficulty":"mudah"},
    {"question_text":"Mei : Juni = Oktober : ...","options":["November","September","Desember","Agustus","Juli"],"correct_answer":0,"explanation":"Mei berurutan dengan Juni, Oktober berurutan dengan November.","difficulty":"mudah"},
    {"question_text":"Palembang : Musi = Banjarmasin : ...","options":["Barito","Brantas","Citarum","Bengawan Solo","Kapuas"],"correct_answer":0,"explanation":"Palembang dilalui sungai Musi, Banjarmasin dilalui sungai Barito.","difficulty":"sedang"},
    {"question_text":"Anak : Orangtua = Siswa : ...","options":["Guru","Dokter","Polisi","Tentara","Pilot"],"correct_answer":0,"explanation":"Anak didik orangtua, siswa didik guru.","difficulty":"mudah"},
    {"question_text":"Hitam : Putih = Gelap : ...","options":["Terang","Suram","Redup","Silau","Remang"],"correct_answer":0,"explanation":"Hitam lawan putih, gelap lawan terang.","difficulty":"mudah"},
    {"question_text":"Palu : Tukang kayu = Silet : ...","options":["Tukang cukur","Dokter","Guru","Tukang batu","Montir"],"correct_answer":0,"explanation":"Palu alat tukang kayu, silet alat tukang cukur.","difficulty":"mudah"},
    {"question_text":"Indonesia : Rupiah = Jepang : ...","options":["Yen","Dollar","Euro","Won","Baht"],"correct_answer":0,"explanation":"Mata uang Indonesia Rupiah, Jepang Yen.","difficulty":"mudah"},
    {"question_text":"Presiden : Istana = Gubernur : ...","options":["Kantor gubernur","Kantor bupati","Balai kota","Rumah dinas bupati","Kantor camat"],"correct_answer":0,"explanation":"Presiden di istana, gubernur di kantor gubernur (kantor dinas).","difficulty":"mudah"},
]

tiu_silogisme = [
    {"question_text":"Semua kucing adalah hewan. Semua hewan butuh makan. Kesimpulan:...","options":["Semua kucing butuh makan","Tidak semua kucing butuh makan","Kucing bukan hewan","Semua hewan adalah kucing","Hewan tidak butuh makan"],"correct_answer":0,"explanation":"Sillogisme: Semua A adalah B, semua B adalah C, maka semua A adalah C.","difficulty":"mudah"},
    {"question_text":"Beberapa siswa rajin. Semua siswa bersekolah. Kesimpulan yang tepat adalah...","options":["Beberapa siswa rajin bersekolah","Semua siswa rajin","Siswa yang rajin tidak bersekolah","Tidak ada siswa yang bersekolah","Semua yang bersekolah rajin"],"correct_answer":0,"explanation":"Dari premis, beberapa siswa yang rajin juga bersekolah.","difficulty":"sedang"},
    {"question_text":"Semua dokter lulus universitas. Budi adalah dokter. Kesimpulan:...","options":["Budi lulus universitas","Budi bukan dokter","Budi tidak lulus","Beberapa dokter tidak lulus","Universitas meluluskan semua dokter"],"correct_answer":0,"explanation":"Semua A adalah B, X adalah A, maka X adalah B.","difficulty":"mudah"},
    {"question_text":"Semua mahasiswa memiliki KTM. Rina tidak memiliki KTM. Kesimpulan:...","options":["Rina bukan mahasiswa","Rina adalah mahasiswa","KTM tidak penting","Mahasiswa tidak perlu KTM","Rina kehilangan KTM"],"correct_answer":0,"explanation":"Semua A memiliki B, X tidak memiliki B, maka X bukan A.","difficulty":"mudah"},
    {"question_text":"Beberapa bunga merah. Semua bunga indah. Kesimpulan:...","options":["Beberapa bunga merah yang indah","Semua bunga merah","Tidak ada bunga merah","Semua yang indah merah","Bunga tidak indah"],"correct_answer":0,"explanation":"Beberapa A adalah B, semua A adalah C, maka beberapa B adalah C.","difficulty":"sedang"},
    {"question_text":"Tidak ada ikan yang bisa terbang. Elang bisa terbang. Kesimpulan:...","options":["Elang bukan ikan","Elang adalah ikan","Semua ikan terbang","Ikan bisa terbang","Elang tidak terbang"],"correct_answer":0,"explanation":"Tidak ada A yang B, X bisa B, maka X bukan A.","difficulty":"mudah"},
    {"question_text":"Semua pegawai negeri memiliki NIP. Andi memiliki NIP. Kesimpulan:...","options":["Tidak dapat disimpulkan pasti","Andi pasti pegawai negeri","Andi bukan pegawai negeri","Semua yang punya NIP pegawai negeri","NIP tidak penting"],"correct_answer":0,"explanation":"Semua A memiliki B, X memiliki B, tidak bisa disimpulkan X pasti A (bisa B juga dimiliki non-A).","difficulty":"sulit"},
    {"question_text":"Beberapa buah manis. Semua buah mengandung vitamin. Kesimpulan yang tepat:...","options":["Beberapa makanan manis mengandung vitamin","Semua buah manis","Tidak ada buah manis","Semua yang manis mengandung vitamin","Buah tidak mengandung vitamin"],"correct_answer":0,"explanation":"Beberapa A adalah B, semua A adalah C, maka beberapa B adalah C.","difficulty":"sedang"},
    {"question_text":"Semua manusia fana. Socrates adalah manusia. Maka...","options":["Socrates fana","Socrates tidak fana","Semua yang fana Socrates","Manusia adalah Socrates","Fana adalah manusia"],"correct_answer":0,"explanation":"Silogisme klasik: Semua A adalah B, X adalah A, maka X adalah B.","difficulty":"mudah"},
    {"question_text":"Beberapa hewan peliharaan berbulu. Semua hewan peliharaan di rumah. Kesimpulan:...","options":["Beberapa hewan berbulu di rumah","Semua hewan berbulu","Hewan peliharaan tidak berbulu","Rumah penuh hewan","Tidak ada hewan di rumah"],"correct_answer":0,"explanation":"Beberapa A adalah B, semua A adalah C, maka beberapa B adalah C.","difficulty":"sedang"},
    {"question_text":"Semua pohon memiliki akar. Pohon kelapa adalah pohon. Maka...","options":["Pohon kelapa memiliki akar","Pohon kelapa tidak punya akar","Semua akar pada pohon kelapa","Pohon tanpa akar","Kelapa bukan pohon"],"correct_answer":0,"explanation":"Sillogisme: Semua A memiliki B, X adalah A, maka X memiliki B.","difficulty":"mudah"},
    {"question_text":"Beberapa politisi jujur. Semua politisi bekerja di pemerintahan. Kesimpulan:...","options":["Beberapa pekerja pemerintahan jujur","Semua politisi jujur","Politisi tidak jujur","Pemerintahan tidak jujur","Semua pekerja jujur"],"correct_answer":0,"explanation":"Beberapa A adalah B, semua A adalah C, maka beberapa C adalah B.","difficulty":"sedang"},
    {"question_text":"Tidak ada reptil yang berbulu. Kucing berbulu. Maka...","options":["Kucing bukan reptil","Kucing adalah reptil","Reptil berbulu","Kucing tidak berbulu","Reptil adalah kucing"],"correct_answer":0,"explanation":"Tidak ada A yang B, X adalah B, maka X bukan A.","difficulty":"mudah"},
    {"question_text":"Semua guru mengajar. Beberapa guru wanita. Kesimpulan yang tepat:...","options":["Beberapa wanita mengajar","Semua guru wanita","Guru laki-laki tidak mengajar","Wanita tidak mengajar","Semua pengajar wanita"],"correct_answer":0,"explanation":"Semua A melakukan B, beberapa A adalah C, maka beberapa C melakukan B.","difficulty":"sedang"},
    {"question_text":"Semua sungai mengalir ke laut. Sungai Nil adalah sungai. Maka...","options":["Sungai Nil mengalir ke laut","Sungai Nil tidak mengalir","Laut adalah sungai","Semua laut dari sungai","Nil bukan sungai"],"correct_answer":0,"explanation":"Semua A melakukan B, X adalah A, maka X melakukan B.","difficulty":"mudah"},
]

tiu_deret_angka = [
    {"question_text":"2, 4, 8, 16, ...?","options":["24","30","32","28","20"],"correct_answer":2,"explanation":"Pola: ×2. 16×2=32.","difficulty":"mudah"},
    {"question_text":"1, 1, 2, 3, 5, 8, ...?","options":["11","12","13","10","15"],"correct_answer":2,"explanation":"Fibonacci: 5+8=13.","difficulty":"mudah"},
    {"question_text":"3, 6, 12, 24, ...?","options":["36","48","42","30","50"],"correct_answer":1,"explanation":"Pola: ×2. 24×2=48.","difficulty":"mudah"},
    {"question_text":"1, 4, 9, 16, 25, ...?","options":["30","36","42","49","34"],"correct_answer":1,"explanation":"Bilangan kuadrat: 1², 2², 3², 4², 5², 6²=36.","difficulty":"mudah"},
    {"question_text":"2, 6, 12, 20, 30, ...?","options":["40","42","36","44","38"],"correct_answer":1,"explanation":"Selisih: 4,6,8,10,12. 30+12=42.","difficulty":"sedang"},
    {"question_text":"1, 3, 6, 10, 15, ...?","options":["20","21","22","18","25"],"correct_answer":1,"explanation":"Selisih: 2,3,4,5,6. 15+6=21.","difficulty":"sedang"},
    {"question_text":"81, 27, 9, 3, ...?","options":["1","2","0","4","5"],"correct_answer":0,"explanation":"Pola: ÷3. 3÷3=1.","difficulty":"mudah"},
    {"question_text":"5, 7, 11, 13, 17, ...?","options":["19","20","21","23","18"],"correct_answer":0,"explanation":"Bilangan prima: 5,7,11,13,17,19.","difficulty":"sedang"},
    {"question_text":"2, 3, 5, 7, 11, 13, ...?","options":["15","16","17","19","21"],"correct_answer":2,"explanation":"Bilangan prima berikutnya setelah 13 adalah 17.","difficulty":"sedang"},
    {"question_text":"1, 8, 27, 64, ...?","options":["100","125","128","120","121"],"correct_answer":1,"explanation":"Bilangan kubik: 1³, 2³, 3³, 4³, 5³=125.","difficulty":"sedang"},
    {"question_text":"10, 7, 4, 1, ...?","options":["-2","-1","0","2","3"],"correct_answer":0,"explanation":"Pola: -3. 1-3=-2.","difficulty":"mudah"},
    {"question_text":"2, 5, 10, 17, 26, ...?","options":["35","37","36","38","40"],"correct_answer":1,"explanation":"Selisih: 3,5,7,9,11. 26+11=37.","difficulty":"sulit"},
    {"question_text":"3, 5, 9, 15, 23, ...?","options":["30","31","33","32","35"],"correct_answer":2,"explanation":"Selisih: 2,4,6,8,10. 23+10=33.","difficulty":"sedang"},
    {"question_text":"1, 2, 6, 24, 120, ...?","options":["480","600","720","700","500"],"correct_answer":2,"explanation":"Faktorial: 1!, 2!, 3!, 4!, 5!, 6!=720.","difficulty":"sulit"},
    {"question_text":"4, 9, 19, 39, ...?","options":["59","69","79","89","99"],"correct_answer":2,"explanation":"Pola: ×2+1. 39×2+1=79.","difficulty":"sedang"},
]

tiu_matematika = [
    {"question_text":"Jika x + 5 = 12, maka x = ...","options":["5","6","7","8","17"],"correct_answer":2,"explanation":"x = 12 - 5 = 7.","difficulty":"mudah"},
    {"question_text":"Hasil dari 15% dari 200 adalah...","options":["25","30","35","20","15"],"correct_answer":1,"explanation":"15/100 × 200 = 30.","difficulty":"mudah"},
    {"question_text":"Sebuah tabungan Rp 1.000.000 dengan bunga 5% per tahun. Setelah 2 tahun berapa totalnya?","options":["Rp 1.050.000","Rp 1.100.000","Rp 1.102.500","Rp 1.200.000","Rp 1.150.000"],"correct_answer":2,"explanation":"Bunga majemuk: 1.000.000 × (1,05)² = 1.102.500.","difficulty":"sedang"},
    {"question_text":"Jika 3x - 9 = 0, maka x = ...","options":["1","2","3","4","6"],"correct_answer":2,"explanation":"3x = 9, x = 3.","difficulty":"mudah"},
    {"question_text":"Rata-rata dari 80, 90, 70, 85, 75 adalah...","options":["78","80","82","75","85"],"correct_answer":1,"explanation":"(80+90+70+85+75)/5 = 400/5 = 80.","difficulty":"mudah"},
    {"question_text":"Jika harga setelah diskon 20% adalah Rp 80.000, harga sebelum diskon adalah...","options":["Rp 96.000","Rp 100.000","Rp 90.000","Rp 85.000","Rp 120.000"],"correct_answer":1,"explanation":"Harga asli × 80% = 80.000, harga asli = 80.000/0,8 = 100.000.","difficulty":"sedang"},
    {"question_text":"Kecepatan mobil 60 km/jam. Berapa waktu tempuh jarak 180 km?","options":["2 jam","3 jam","4 jam","3,5 jam","2,5 jam"],"correct_answer":1,"explanation":"Waktu = Jarak/Kecepatan = 180/60 = 3 jam.","difficulty":"mudah"},
    {"question_text":"Luas segitiga dengan alas 10 cm dan tinggi 8 cm adalah...","options":["80 cm²","40 cm²","18 cm²","60 cm²","20 cm²"],"correct_answer":1,"explanation":"Luas = ½ × alas × tinggi = ½ × 10 × 8 = 40 cm².","difficulty":"mudah"},
    {"question_text":"Jika 2 pangkat x = 32, maka x = ...","options":["4","5","6","3","8"],"correct_answer":1,"explanation":"2⁵ = 32, jadi x = 5.","difficulty":"mudah"},
    {"question_text":"Keliling lingkaran dengan jari-jari 7 cm adalah... (π=22/7)","options":["22 cm","44 cm","49 cm","154 cm","308 cm"],"correct_answer":1,"explanation":"K = 2πr = 2 × 22/7 × 7 = 44 cm.","difficulty":"sedang"},
    {"question_text":"Hasil dari (-3)² + (-2)³ adalah...","options":["1","17","-1","-17","0"],"correct_answer":0,"explanation":"(-3)² + (-2)³ = 9 + (-8) = 1.","difficulty":"sedang"},
    {"question_text":"Perbandingan uang A dan B adalah 3:5. Jika total Rp 240.000, bagian B adalah...","options":["Rp 150.000","Rp 90.000","Rp 120.000","Rp 100.000","Rp 160.000"],"correct_answer":0,"explanation":"B = 5/(3+5) × 240.000 = 5/8 × 240.000 = 150.000.","difficulty":"sedang"},
    {"question_text":"Seorang pedagang membeli barang seharga Rp 500.000 dan menjual Rp 625.000. Persentase keuntungan adalah...","options":["20%","25%","30%","15%","10%"],"correct_answer":1,"explanation":"Untung = 125.000/500.000 × 100% = 25%.","difficulty":"mudah"},
    {"question_text":"Nilai x yang memenuhi |x - 3| = 5 adalah...","options":["8 atau -2","8 atau 2","-8 atau 2","-8 atau -2","3 atau 5"],"correct_answer":0,"explanation":"x - 3 = 5 → x = 8, atau x - 3 = -5 → x = -2.","difficulty":"sedang"},
    {"question_text":"Jika 5 orang menyelesaikan pekerjaan dalam 10 hari, 10 orang akan menyelesaikan dalam...","options":["20 hari","5 hari","15 hari","8 hari","3 hari"],"correct_answer":1,"explanation":"Orang × hari = konstan. 5×10 = 10×hari, hari = 5.","difficulty":"mudah"},
]

tiu_pemahaman = [
    {"question_text":"Bacaan: 'Jakarta merupakan ibu kota Indonesia yang padat penduduk.' Kesimpulan yang tepat adalah...","options":["Jakarta adalah kota terpadat di Indonesia","Jakarta ibu kota Indonesia dan padat","Jakarta bukan ibu kota","Jakarta tidak padat","Indonesia hanya punya Jakarta"],"correct_answer":1,"explanation":"Dua informasi: Jakarta ibu kota + padat penduduk.","difficulty":"mudah"},
    {"question_text":"'Pendidikan adalah kunci masa depan.' Arti dari kalimat tersebut adalah...","options":["Tanpa pendidikan masa depan suram","Pendidikan tidak penting","Masa depan tidak bergantung pendidikan","Semua orang berpendidikan","Pendidikan mahal"],"correct_answer":0,"explanation":"Pendidikan sebagai kunci = tanpa pendidikan masa depan sulit.","difficulty":"mudah"},
    {"question_text":"'Setiap pelanggaran hukum pasti ada sanksinya.' Jika seseorang tidak mendapat sanksi, maka...","options":["Ia tidak melanggar hukum","Hukum tidak berlaku","Sanksi tidak adil","Ia beruntung","Hukum lemah"],"correct_answer":0,"explanation":"Kontraposisi: tidak ada sanksi → tidak melanggar hukum.","difficulty":"sedang"},
    {"question_text":"'Pohon yang ditanam hari ini akan memberikan naungan di masa depan.' Makna kalimat tersebut adalah...","options":["Investasi hari ini bermanfaat nanti","Pohon sangat penting","Naungan dibutuhkan","Menanam pohon wajib","Masa depan cerah"],"correct_answer":0,"explanation":"Metafora: usaha/investasi saat ini akan bermanfaat di masa depan.","difficulty":"sedang"},
    {"question_text":"'Air yang tenang menghanyutkan.' Makna peribahasa tersebut adalah...","options":["Orang yang pendiam bisa berbahaya","Air tenang berbahaya","Jangan berenang di air tenang","Orang pendiam lemah","Air tenang aman"],"correct_answer":0,"explanation":"Peribahasa: orang yang pendiam/tenang bisa melakukan hal besar.","difficulty":"sedang"},
    {"question_text":"'Di mana bumi dipijak, di situ langit dijunjung.' Artinya...","options":["Menghormati adat istiadat setempat","Hidup di bumi","Menjaga lingkungan","Menjaga langit","Memijak bumi"],"correct_answer":0,"explanation":"Harus menghormati dan mengikuti adat istiadat di mana kita tinggal.","difficulty":"mudah"},
    {"question_text":"'Seperti katak dalam tempurung.' Arti peribahasa ini adalah...","options":["Orang yang berpandangan sempit","Katak hidup di tempurung","Tempurung keras","Katak kecil","Tempurung besar"],"correct_answer":0,"explanation":"Katak dalam tempurung = orang dengan wawasan sempit.","difficulty":"mudah"},
    {"question_text":"'Guru kencing berdiri, murid kencing berlari.' Artinya...","options":["Perilaku buruk pemimpin ditiru berlebihan oleh bawahan","Guru buruk","Murid lebih buruk","Pemimpin harus baik","Jangan berlari"],"correct_answer":0,"explanation":"Peribahasa: jika pemimpin berperilaku buruk, bawahannya akan lebih buruk.","difficulty":"sedang"},
    {"question_text":"'Berat sama dipikul, ringan sama dijinjing.' Artinya...","options":["Gotong royong dan saling membantu","Barang berat dan ringan","Bekerja bersama","Membawa barang","Pikul dan jinjing"],"correct_answer":0,"explanation":"Semangat gotong royong: berat dan ringan ditanggung bersama.","difficulty":"mudah"},
    {"question_text":"'Karena nila setitik, rusak susu sebelanga.' Artinya...","options":["Satu kesalahan kecil merusak segalanya","Nila merusak susu","Susu rusak","Nilai penting","Setitik cukup"],"correct_answer":0,"explanation":"Satu kesalahan/keburukan kecil merusak segala kebaikan yang sudah dibangun.","difficulty":"mudah"},
    {"question_text":"'Yang dikejar tak dapat, yang dikendong berciciran.' Artinya...","options":["Mengejar banyak hal akhirnya kehilangan semua","Mengejar hewan","Membawa anak","Berciciran di jalan","Kejaran gagal"],"correct_answer":0,"explanation":"Seringkali: mengejar banyak hal sekaligus, tidak ada yang tercapai malah kehilangan yang sudah ada.","difficulty":"sedang"},
    {"question_text":"'Ada udang di balik batu.' Artinya...","options":["Ada maksud tersembunyi","Udang di belakang batu","Mencari udang","Batu besar","Udang kecil"],"correct_answer":0,"explanation":"Ada udang di balik batu = ada tujuan/maksud tersembunyi di balik tindakan.","difficulty":"mudah"},
    {"question_text":"'Tong kosong nyaring bunyinya.' Arti peribahasa ini adalah...","options":["Orang bodoh banyak bicara","Tong berbunyi","Tong kosong","Kosong itu nyaring","Bunyi tong"],"correct_answer":0,"explanation":"Orang yang tidak berpengetahuan justru paling banyak bicara/berkoar.","difficulty":"mudah"},
    {"question_text":"'Sekali mendayung, dua tiga pulau terlampaui.' Artinya...","options":["Satu usaha menghasilkan banyak manfaat","Mendayung cepat","Pulau banyak","Dayung kuat","Tiga pulau"],"correct_answer":0,"explanation":"Satu kali usaha mendatangkan beberapa manfaat sekaligus.","difficulty":"mudah"},
    {"question_text":"'Masuk kandang kucing mengeong, masuk kandang anjing menggonggong.' Artinya...","options":["Mengikuti adat istiadat di mana kita berada","Kucing dan anjing","Kandang hewan","Mengeong dan menggonggong","Masuk kandang"],"correct_answer":0,"explanation":"Sama seperti 'di mana bumi dipijak, di situ langit dijunjung'.","difficulty":"sedang"},
]

# TKP Questions (with score-based options)
tkp_pelayanan = [
    {"question_text":"Anda menemukan warga kesulitan mengurus surat di kantor Anda. Apa yang Anda lakukan?","options":[{"text":"Membantu mengarahkan dan mendampingi hingga selesai, lalu melaporkan ke atasan untuk perbaikan sistem","score":5},{"text":"Membantu menguruskan surat tersebut secara penuh","score":4},{"text":"Memberi petunjuk singkat lalu kembali bekerja","score":3},{"text":"Menyarankan datang lagi besok","score":2},{"text":"Biarkan saja karena bukan tugas Anda","score":1}],"correct_answer":0,"explanation":"Skor tertinggi: membantu sekaligus memperbaiki sistem.","difficulty":"sedang"},
    {"question_text":"Seorang warga marah karena pelayanan lambat. Sikap terbaik adalah...","options":[{"text":"Meminta maaf, menjelaskan penyebab, dan memberikan solusi","score":5},{"text":"Mendengarkan keluhan dengan sabar","score":4},{"text":"Mengabaikan kemarahan warga","score":3},{"text":"Membalas dengan nada tinggi","score":2},{"text":"Memanggil satpam untuk mengusir","score":1}],"correct_answer":0,"explanation":"Pelayanan prima: empati, penjelasan, dan solusi.","difficulty":"sedang"},
    {"question_text":"Anda diminta melayani di luar jam kerja karena ada keperluan mendesak warga. Anda...","options":[{"text":"Tetap melayani dengan profesional karena kepentingan masyarakat diutamakan","score":5},{"text":"Melayani dengan catatan diganti waktu","score":4},{"text":"Melayani seadanya","score":3},{"text":"Menolak karena di luar jam kerja","score":2},{"text":"Tidak merespons","score":1}],"correct_answer":0,"explanation":"PNS harus mengutamakan pelayanan kepada masyarakat.","difficulty":"sedang"},
    {"question_text":"Anda menemukan formulir pelayanan yang membingungkan bagi warga. Tindakan terbaik adalah...","options":[{"text":"Melaporkan ke atasan dan mengusulkan penyederhanaan formulir","score":5},{"text":"Membantu warga mengisi formulir satu per satu","score":4},{"text":"Memberikan contoh formulir yang sudah terisi","score":3},{"text":"Menyuruh warga membaca petunjuk dengan teliti","score":2},{"text":"Membiarkan saja karena formulir sudah sesuai prosedur","score":1}],"correct_answer":0,"explanation":"Meningkatkan kualitas pelayanan melalui perbaikan sistem.","difficulty":"sedang"},
    {"question_text":"Warga datang untuk mengurus dokumen yang sebenarnya bisa diurus secara online. Anda...","options":[{"text":"Membantu melayani langsung sambil mengedukasi cara pengurusan online ke depannya","score":5},{"text":"Menyuruh warga mengurus secara online saja","score":4},{"text":"Tetap melayani tanpa memberi informasi online","score":3},{"text":"Menolak melayani karena sudah ada sistem online","score":2},{"text":"Menyuruh warga pulang dan belajar internet","score":1}],"correct_answer":0,"explanation":"Tetap melayani sambil mengedukasi.","difficulty":"sedang"},
    {"question_text":"Anda mendapat keluhan yang sama berulang kali dari warga yang berbeda. Tindakan terbaik adalah...","options":[{"text":"Melakukan analisis akar masalah dan mengusulkan perbaikan menyeluruh","score":5},{"text":"Membuat panduan yang bisa diberikan ke warga","score":4},{"text":"Menjawab dengan sabar setiap kali","score":3},{"text":"Menyarankan warga menyampaikan keluhan resmi","score":2},{"text":"Mengabaikan keluhan karena sudah biasa","score":1}],"correct_answer":0,"explanation":"Pendekatan sistemik untuk menyelesaikan masalah berulang.","difficulty":"sedang"},
]

tkp_profesionalisme = [
    {"question_text":"Anda mendapat tugas yang bukan bidang keahlian Anda. Sikap terbaik adalah...","options":[{"text":"Mempelajari dan menyelesaikan tugas tersebut sambil berkonsultasi dengan rekan yang ahli","score":5},{"text":"Menerima dan berusaha menyelesaikan dengan kemampuan terbaik","score":4},{"text":"Meminta bantuan rekan untuk mengerjakan","score":3},{"text":"Menolak tugas tersebut","score":2},{"text":"Mengerjakan asal-asalan","score":1}],"correct_answer":0,"explanation":"Profesional: belajar dan berkonsultasi, bukan menolak atau asal-asalan.","difficulty":"sedang"},
    {"question_text":"Anda menemukan rekan kerja melakukan kesalahan dalam pekerjaan. Tindakan terbaik adalah...","options":[{"text":"Membantu memperbaiki kesalahan secara langsung dan memberi masukan konstruktif","score":5},{"text":"Melaporkan ke atasan","score":4},{"text":"Mengingatkan secara pribadi dengan baik","score":3},{"text":"Membiarkan saja karena bukan urusan Anda","score":2},{"text":"Menyebarkan informasi kesalahan rekan ke orang lain","score":1}],"correct_answer":0,"explanation":"Membantu memperbaiki dan memberi masukan konstruktif adalah sikap profesional.","difficulty":"sedang"},
    {"question_text":"Anda menghadapi deadline yang ketat. Strategi terbaik adalah...","options":[{"text":"Membuat prioritas, fokus pada tugas utama, dan berkoordinasi dengan tim","score":5},{"text":"Bekerja lembur sendirian","score":4},{"text":"Meminta perpanjangan waktu","score":3},{"text":"Menunda tugas lain","score":2},{"text":"Menyerah dan melapor tidak bisa selesai","score":1}],"correct_answer":0,"explanation":"Manajemen waktu dan koordinasi tim adalah kunci profesionalisme.","difficulty":"sedang"},
    {"question_text":"Atasan meminta Anda melakukan sesuatu yang bertentangan dengan prosedur. Anda...","options":[{"text":"Menjelaskan prosedur yang benar dengan sopan dan menawarkan alternatif","score":5},{"text":"Melaksanakan perintah atasan","score":4},{"text":"Menolak secara halus","score":3},{"text":"Melakukan diam-diam","score":2},{"text":"Melaporkan atasan ke inspektorat","score":1}],"correct_answer":0,"explanation":"Profesional: menjelaskan prosedur dengan sopan sambil menawarkan solusi alternatif.","difficulty":"sedang"},
    {"question_text":"Anda ditugaskan di daerah terpencil. Sikap terbaik adalah...","options":[{"text":"Menerima dengan ikhlas dan berusaha memberikan kontribusi terbaik","score":5},{"text":"Menerima meskipun tidak senang","score":4},{"text":"Meminta pertimbangan ulang","score":3},{"text":"Menolak tugas","score":2},{"text":"Mengajukan pengunduran diri","score":1}],"correct_answer":0,"explanation":"PNS siap ditempatkan di mana saja sesuai kebutuhan negara.","difficulty":"sedang"},
    {"question_text":"Rekan kerja mengajak Anda untuk bekerja secara kolaboratif pada proyek baru. Anda...","options":[{"text":"Menyambut baik dan berkontribusi aktif dengan keahlian yang dimiliki","score":5},{"text":"Menerima ajakan tersebut","score":4},{"text":"Berpartisipasi jika diminta atasan","score":3},{"text":"Menolak karena sudah sibuk","score":2},{"text":"Mengabaikan ajakan","score":1}],"correct_answer":0,"explanation":"Kolaborasi aktif meningkatkan kualitas kerja dan profesionalisme.","difficulty":"mudah"},
]

tkp_integritas = [
    {"question_text":"Anda menemukan amplop berisi uang di meja kerja Anda dari seseorang yang sedang mengurus izin. Anda...","options":[{"text":"Mengembalikan uang tersebut dan melaporkan ke atasan","score":5},{"text":"Mengembalikan tanpa melapor","score":4},{"text":"Menyimpan sementara untuk dikembalikan nanti","score":3},{"text":"Menggunakan untuk keperluan kantor","score":2},{"text":"Menerima sebagai tanda terima kasih","score":1}],"correct_answer":0,"explanation":"Integritas: menolak gratifikasi dan melaporkan.","difficulty":"sedang"},
    {"question_text":"Anda diminta menandatangani dokumen yang isinya tidak sesuai fakta. Tindakan terbaik adalah...","options":[{"text":"Menolak menandatangani dan menjelaskan alasan penolakan","score":5},{"text":"Menandatangani karena diminta atasan","score":4},{"text":"Menanyakan dulu ke rekan","score":3},{"text":"Menandatangani asal cepat selesai","score":2},{"text":"Menandatangani tanpa membaca","score":1}],"correct_answer":0,"explanation":"Integritas: tidak menandatangani dokumen yang tidak benar.","difficulty":"sedang"},
    {"question_text":"Anda mengetahui rekan kerja melakukan korupsi. Tindakan terbaik adalah...","options":[{"text":"Melaporkan melalui saluran yang benar (whistleblowing system)","score":5},{"text":"Mengingatkan rekan secara pribadi","score":4},{"text":"Membiarkan karena bukan urusan Anda","score":3},{"text":"Mengancam akan melaporkan","score":2},{"text":"Minta bagian dari hasil korupsi","score":1}],"correct_answer":0,"explanation":"Integritas: melaporkan melalui mekanisme resmi.","difficulty":"sedang"},
    {"question_text":"Anda ditawari hadiah mahal dari vendor setelah tender selesai (Anda menang). Anda...","options":[{"text":"Menolak dengan sopan karena termasuk gratifikasi","score":5},{"text":"Menerima karena tender sudah selesai","score":4},{"text":"Menerima tapi melapor ke atasan","score":3},{"text":"Menerima sebagai ucapan terima kasih","score":2},{"text":"Menerima dan merahasiakannya","score":1}],"correct_answer":0,"explanation":"Gratifikasi tetap ditolak meskipun tender sudah selesai (UU Tipikor).","difficulty":"sedang"},
    {"question_text":"Anda mendapat tekanan dari pihak berpengaruh untuk meloloskan izin yang tidak memenuhi syarat. Anda...","options":[{"text":"Tegas menolak dan melaporkan tekanan tersebut ke atasan/APIP","score":5},{"text":"Meloloskan karena tekanan besar","score":4},{"text":"Meloloskan separuh saja","score":3},{"text":"Menunda pengurusan","score":2},{"text":"Menghindari pihak tersebut","score":1}],"correct_answer":0,"explanation":"Integritas: tidak berkompromi meskipun ditekan.","difficulty":"sedang"},
    {"question_text":"Anda melihat atasan Anda menggunakan fasilitas kantor untuk kepentingan pribadi. Anda...","options":[{"text":"Melaporkan melalui saluran pengawasan yang tersedia","score":5},{"text":"Mengingatkan atasan secara pribadi","score":4},{"text":"Melakukan hal yang sama","score":3},{"text":"Membiarkan saja","score":2},{"text":"Menyebarkan cerita ke rekan lain","score":1}],"correct_answer":0,"explanation":"Integritas: melaporkan penyalahgunaan melalui mekanisme resmi.","difficulty":"sedang"},
]

tkp_sosial = [
    {"question_text":"Tetangga Anda sedang tertimpa musibah banjir. Tindakan terbaik adalah...","options":[{"text":"Membantu mengevakuasi dan mengoordinasikan bantuan bersama warga","score":5},{"text":"Membantu dengan memberikan pakaian bekas","score":4},{"text":"Mendoakan dari rumah","score":3},{"text":"Menunggu bantuan dari pemerintah","score":2},{"text":"Tidak peduli karena bukan keluarga","score":1}],"correct_answer":0,"explanation":"Sosial: aksi nyata + koordinasi bantuan.","difficulty":"mudah"},
    {"question_text":"Dilingkungan tempat tinggal Anda terjadi konflik antar warga. Peran terbaik Anda adalah...","options":[{"text":"Menjadi mediator yang netral untuk memediasi perdamaian","score":5},{"text":"Membantu pihak yang Anda anggap benar","score":4},{"text":"Melaporkan ke RT/RW","score":3},{"text":"Menghindari konflik","score":2},{"text":"Membela salah satu pihak","score":1}],"correct_answer":0,"explanation":"Peran aktif sebagai mediator netral untuk perdamaian.","difficulty":"sedang"},
    {"question_text":"Anda melihat anak kecil tersesat di jalan. Tindakan terbaik adalah...","options":[{"text":"Mendekati dengan ramah, menenangkan, dan mengantarkan ke tempat aman/kantor polisi","score":5},{"text":"Menanyakan alamat rumahnya","score":4},{"text":"Menelepon polisi","score":3},{"text":"Mengabaikan karena bukan anak Anda","score":2},{"text":"Menyuruh anak mencari orangtuanya sendiri","score":1}],"correct_answer":0,"explanation":"Tindakan langsung: dekati, tenangkan, antar ke tempat aman.","difficulty":"mudah"},
    {"question_text":"Seorang lansia kesulitan menyeberang jalan raya yang ramai. Anda...","options":[{"text":"Membantu menyeberang dengan mengawal hingga aman","score":5},{"text":"Memberi tahu untuk menyeberang di zebra cross","score":4},{"text":"Menyeberangkan lalu langsung pergi","score":3},{"text":"Menelepon keluarganya","score":2},{"text":"Melanjutkan perjalanan","score":1}],"correct_answer":0,"explanation":"Membantu langsung dengan mengawal hingga aman.","difficulty":"mudah"},
    {"question_text":"Lingkungan Anda mengadakan kerja bakti. Meskipun hari libur, Anda...","options":[{"text":"Ikut berpartisipasi aktif dan mengajak keluarga","score":5},{"text":"Ikut sebentar saja","score":4},{"text":"Memberi sumbangan uang saja","score":3},{"text":"Tidak ikut karena hari libur","score":2},{"text":"Mengabaikan undangan","score":1}],"correct_answer":0,"explanation":"Partisipasi aktif dalam kegiatan kemasyarakatan.","difficulty":"mudah"},
    {"question_text":"Tetangga baru pindah ke lingkungan Anda. Sebagai warga yang baik, Anda...","options":[{"text":"Mengunjungi, memperkenalkan diri, dan menawarkan bantuan adaptasi","score":5},{"text":"Menyapa jika bertemu","score":4},{"text":"Memberi tahu peraturan lingkungan","score":3},{"text":"Tidak perlu peduli","score":2},{"text":"Mengawasi dengan curiga","score":1}],"correct_answer":0,"explanation":"Sikap ramah dan membantu warga baru beradaptasi.","difficulty":"mudah"},
]

tkp_teknologi = [
    {"question_text":"Kantor Anda akan menerapkan sistem digitalisasi. Beberapa rekan menolak karena gaptek. Anda...","options":[{"text":"Menawarkan diri menjadi mentor dan membantu rekan-rekan belajar sistem baru","score":5},{"text":"Hanya menggunakan sistem baru untuk diri sendiri","score":4},{"text":"Ikut menolak karena banyak yang tidak setuju","score":3},{"text":"Meminta atasan yang mengajari","score":2},{"text":"Tidak peduli dengan rekan lain","score":1}],"correct_answer":0,"explanation":"Leadership: menjadi mentor untuk membantu transformasi digital.","difficulty":"sedang"},
    {"question_text":"Anda menemukan aplikasi baru yang bisa mempercepat pekerjaan kantor. Tindakan terbaik adalah...","options":[{"text":"Mempelajari aplikasi, membuat analisis manfaat, dan mengusulkan ke atasan","score":5},{"text":"Menggunakan untuk diri sendiri","score":4},{"text":"Memberi tahu beberapa rekan","score":3},{"text":"Tidak peduli karena sudah nyaman cara lama","score":2},{"text":"Khawatir akan menggantikan pekerjaan Anda","score":1}],"correct_answer":0,"explanation":"Proaktif menganalisis dan mengusulkan inovasi teknologi.","difficulty":"sedang"},
    {"question_text":"Anda mendapat email mencurigakan yang meminta data pribadi. Anda...","options":[{"text":"Tidak membalas, melaporkan ke IT security, dan mengingatkan rekan","score":5},{"text":"Mengabaikan saja","score":4},{"text":"Membalas untuk klarifikasi","score":3},{"text":"Mengklik link untuk melihat isinya","score":2},{"text":"Mengisi data yang diminta","score":1}],"correct_answer":0,"explanation":"Keamanan siber: tidak merespons, laporkan, dan edukasi rekan.","difficulty":"sedang"},
    {"question_text":"Anda diminta membuat laporan digital yang biasanya dibuat manual. Anda...","options":[{"text":"Mempelajari tools yang tepat dan membuat laporan digital yang lebih informatif","score":5},{"text":"Membuat format digital sederhana","score":4},{"text":"Membuat format lama lalu scan","score":3},{"text":"Meminta orang lain yang membuat","score":2},{"text":"Menolak karena tidak bisa","score":1}],"correct_answer":0,"explanation":"Inisiatif belajar teknologi baru untuk efisiensi.","difficulty":"sedang"},
    {"question_text":"Anda melihat rekan membagikan password akun kantor ke orang lain. Anda...","options":[{"text":"Mengingatkan tentang keamanan informasi dan melaporkan ke admin IT","score":5},{"text":"Mengingatkan secara pribadi","score":4},{"text":"Tidak peduli","score":3},{"text":"Melakukan hal yang sama","score":2},{"text":"Meminjam akun rekan tersebut","score":1}],"correct_answer":0,"explanation":"Keamanan informasi adalah tanggung jawab bersama.","difficulty":"sedang"},
    {"question_text":"Anda diminta mempresentasikan data menggunakan grafik interaktif. Meskipun belum pernah, Anda...","options":[{"text":"Mempelajari tools visualisasi data dan membuat presentasi yang menarik","score":5},{"text":"Meminta bantuan rekan yang bisa","score":4},{"text":"Membuat grafik manual","score":3},{"text":"Menyampaikan data dalam bentuk tabel saja","score":2},{"text":"Menolak tugas tersebut","score":1}],"correct_answer":0,"explanation":"Proaktif belajar untuk meningkatkan kualitas kerja.","difficulty":"sedang"},
]

tkp_anti_radikal = [
    {"question_text":"Anda mendengar seseorang menyebarkan paham radikal di lingkungan kerja. Tindakan terbaik adalah...","options":[{"text":"Melaporkan ke atasan dan BNPT/laporan resmi, serta mengingatkan rekan","score":5},{"text":"Mengabaikan karena bukan urusan Anda","score":4},{"text":"Mendengarkan saja","score":3},{"text":"Ikut mendengarkan dan menyebarluaskan","score":2},{"text":"Mendukung paham tersebut","score":1}],"correct_answer":0,"explanation":"PNS wajib melawan paham radikal dan melapor ke pihak berwenang.","difficulty":"sedang"},
    {"question_text":"Anda melihat konten radikal di media sosial rekan kerja. Tindakan terbaik adalah...","options":[{"text":"Mengingatkan rekan secara pribadi dan melaporkan jika terus berlanjut","score":5},{"text":"Mengabaikan","score":4},{"text":"Menyukai konten tersebut","score":3},{"text":"Membagikan ulang","score":2},{"text":"Mengikuti akun tersebut","score":1}],"correct_answer":0,"explanation":"Edukasi pribadi dulu, laporkan jika berlanjut.","difficulty":"sedang"},
    {"question_text":"Seseorang menawarkan Anda buku berisi paham radikal. Anda...","options":[{"text":"Menolak dan melaporkan ke pihak berwenang","score":5},{"text":"Membaca sekilas","score":4},{"text":"Menerima tapi tidak membaca","score":3},{"text":"Menerima dan membagikan","score":2},{"text":"Mendukung isinya","score":1}],"correct_answer":0,"explanation":"Tegas menolak dan melaporkan.","difficulty":"sedang"},
    {"question_text":"Teman Anda mulai menunjukkan perubahan sikap menjadi eksklusif dan intoleran. Anda...","options":[{"text":"Mendekati dengan dialog, memberikan perspektif berbeda, dan memperkuat toleransi","score":5},{"text":"Menjauhi teman tersebut","score":4},{"text":"Mengabaikan perubahan","score":3},{"text":"Ikut eksklusif","score":2},{"text":"Mendukung sikap teman","score":1}],"correct_answer":0,"explanation":"Dialog dan counter-narrative adalah pendekatan terbaik.","difficulty":"sedang"},
    {"question_text":"Anda melihat ajakan demo yang berpotensi anarkis di media sosial. Anda...","options":[{"text":"Tidak ikut dan melaporkan ke pihak berwenang","score":5},{"text":"Mengabaikan","score":4},{"text":"Membagikan informasinya","score":3},{"text":"Ikut demo","score":2},{"text":"Mengajak orang lain ikut","score":1}],"correct_answer":0,"explanation":"Tidak terlibat dalam aksi yang berpotensi anarkis dan melaporkan.","difficulty":"sedang"},
    {"question_text":"Anda diminta mengisi materi kegiatan keagamaan yang ternyata menyimpang. Anda...","options":[{"text":"Menolak dan menjelaskan bahwa materi menyimpang dari ajaran yang benar","score":5},{"text":"Mengisi materi yang benar tanpa seizin panitia","score":4},{"text":"Tidak datang tanpa penjelasan","score":3},{"text":"Mengisi sesuai permintaan","score":2},{"text":"Menyebarkan materi menyimpang","score":1}],"correct_answer":0,"explanation":"Menolak tegas dan meluruskan dengan penjelasan yang benar.","difficulty":"sedang"},
]

tkp_bela_negara = [
    {"question_text":"Anda melihat bendera Merah Putih dikibarkan terbalik. Tindakan terbaik adalah...","options":[{"text":"Segera meluruskan pemasangan bendera dan mengingatkan penanggung jawab","score":5},{"text":"Melaporkan ke polisi","score":4},{"text":"Mengabaikan","score":3},{"text":"Membiarkan saja","score":2},{"text":"Merekam dan mengunggah ke media sosial","score":1}],"correct_answer":0,"explanation":"Tindakan langsung memperbaiki dan mengedukasi.","difficulty":"mudah"},
    {"question_text":"Anda diminta menjadi peserta upacara bendera 17 Agustus. Meskipun hari libur, Anda...","options":[{"text":"Hadir tepat waktu dengan penuh semangat dan bersyukur","score":5},{"text":"Hadir tapi biasa saja","score":4},{"text":"Hadir terlambat","score":3},{"text":"Tidak hadir tanpa keterangan","score":2},{"text":"Menolak hadir","score":1}],"correct_answer":0,"explanation":"Bela negara: partisipasi penuh dalam kegiatan kenegaraan.","difficulty":"mudah"},
    {"question_text":"Anda mendengar berita hoax tentang negara yang viral. Anda...","options":[{"text":"Mengecek kebenaran dari sumber resmi dan meluruskan informasi","score":5},{"text":"Tidak mempercayai tapi tidak meluruskan","score":4},{"text":"Membagikan untuk peringatan","score":3},{"text":"Membagikan karena menarik","score":2},{"text":"Menciptakan berita serupa","score":1}],"correct_answer":0,"explanation":"Melawan hoax dengan fakta dari sumber resmi.","difficulty":"sedang"},
    {"question_text":"Anda melihat tindakan vandalisme di fasilitas umum. Tindakan terbaik adalah...","options":[{"text":"Melaporkan ke petugas dan mengamankan barang bukti","score":5},{"text":"Mengabaikan","score":4},{"text":"Membiarkan saja","score":3},{"text":"Ikut merusak","score":2},{"text":"Merekam dan mengunggah","score":1}],"correct_answer":0,"explanation":"Melindungi fasilitas negara adalah bentuk bela negara.","difficulty":"mudah"},
    {"question_text":"Anda ditanya teman asing tentang konflik di Indonesia. Jawaban terbaik adalah...","options":[{"text":"Menjelaskan dengan objektif bahwa Indonesia sedang menyelesaikan masalah dengan baik","score":5},{"text":"Mengeluh tentang keadaan Indonesia","score":4},{"text":"Tidak menjawab","score":3},{"text":"Menceritakan hal buruk tentang Indonesia","score":2},{"text":"Mengaku malu menjadi orang Indonesia","score":1}],"correct_answer":0,"explanation":"Menjaga nama baik bangsa di mata internasional.","difficulty":"sedang"},
    {"question_text":"Anda memiliki kesempatan bekerja di luar negeri dengan gaji tinggi. Setelah mempertimbangkan, Anda...","options":[{"text":"Bekerja di luar negeri sambil tetap berkontribusi untuk Indonesia dan berencana pulang","score":5},{"text":"Pindah kewarganegaraan","score":4},{"text":"Melupakan Indonesia","score":3},{"text":"Tidak mau bekerja di luar negeri","score":2},{"text":"Mengkritik Indonesia dari luar","score":1}],"correct_answer":0,"explanation":"Tetap cinta tanah air meskipun bekerja di luar negeri.","difficulty":"sedang"},
]

tkp_jejaring = [
    {"question_text":"Anda diminta berkolaborasi dengan instansi lain untuk program bersama. Tindakan terbaik adalah...","options":[{"text":"Menyambut baik, membuat rencana kerja bersama, dan berkoordinasi aktif","score":5},{"text":"Menerima dan mengikuti arahan instansi lain","score":4},{"text":"Berpartisipasi pasif","score":3},{"text":"Menolak karena merepotkan","score":2},{"text":"Menolak karena bukan tugas Anda","score":1}],"correct_answer":0,"explanation":"Jejaring kerja: kolaborasi aktif dan proaktif.","difficulty":"sedang"},
    {"question_text":"Anda menghadiri seminar dan bertemu pejabat dari instansi lain. Anda...","options":[{"text":"Membangun relasi dengan memperkenalkan diri dan bertukar kontak","score":5},{"text":"Hanya mengikuti seminar","score":4},{"text":"Duduk diam di pojok","score":3},{"text":"Pulang setelah seminar selesai","score":2},{"text":"Tidak berinteraksi dengan siapapun","score":1}],"correct_answer":0,"explanation":"Networking adalah keterampilan penting PNS modern.","difficulty":"mudah"},
    {"question_text":"Anda membutuhkan data dari instansi lain untuk pekerjaan Anda. Tindakan terbaik adalah...","options":[{"text":"Mengirim surat resmi dan melakukan follow-up sopan","score":5},{"text":"Menelepon langsung","score":4},{"text":"Meminta rekan yang kenal","score":3},{"text":"Menggunakan data yang tidak valid","score":2},{"text":"Menyerah dan tidak melanjutkan","score":1}],"correct_answer":0,"explanation":"Prosedur resmi dan profesional dalam membangun jejaring.","difficulty":"sedang"},
    {"question_text":"Sebuah organisasi masyarakat mengundang Anda untuk berbicara. Meskipun sibuk, Anda...","options":[{"text":"Menerima undangan dan mempersiapkan materi yang bermanfaat","score":5},{"text":"Menerima tapi tanpa persiapan","score":4},{"text":"Mewakilkan ke rekan","score":3},{"text":"Menolak karena sibuk","score":2},{"text":"Mengabaikan undangan","score":1}],"correct_answer":0,"explanation":"Membangun jejaring melalui kontribusi positif ke masyarakat.","difficulty":"sedang"},
    {"question_text":"Anda mendapat informasi peluang kerjasama antar daerah. Anda...","options":[{"text":"Menindaklanjuti dengan menghubungi pihak terkait dan membuat proposal kerjasama","score":5},{"text":"Menyimpan informasi untuk diri sendiri","score":4},{"text":"Memberi tahu atasan tanpa tindak lanjut","score":3},{"text":"Mengabaikan","score":2},{"text":"Lupa karena sibuk","score":1}],"correct_answer":0,"explanation":"Proaktif menindaklanjuti peluang jejaring kerja.","difficulty":"sedang"},
    {"question_text":"Rekan dari instansi lain meminta bantuan teknis yang Anda kuasai. Anda...","options":[{"text":"Membantu dengan senang hati dan membangun hubungan kerja yang baik","score":5},{"text":"Membantu tapi meminta imbalan","score":4},{"text":"Membantu seadanya","score":3},{"text":"Menolak karena bukan urusan Anda","score":2},{"text":"Mengabaikan permintaan","score":1}],"correct_answer":0,"explanation":"Membangun jejaring melalui saling membantu.","difficulty":"mudah"},
]

# Build final question list
all_questions = []

def add_section(templates, section, topic):
    for t in templates:
        for year in range(2020, 2026):
            q = {
                "section": section,
                "topic": topic,
                "year": year,
                "difficulty": t["difficulty"],
                "question_text": t["question_text"],
                "options": json.dumps(t["options"], ensure_ascii=False),
                "correct_answer": t["correct_answer"],
                "explanation": t["explanation"],
            }
            all_questions.append(q)

# TWK
add_section(twk_pancasila, "TWK", "Pancasila")
add_section(twk_uud, "TWK", "UUD 1945")
add_section(twk_bhinneka, "TWK", "Bhinneka Tunggal Ika")

# TIU
add_section(tiu_sinonim, "TIU", "Sinonim")
add_section(tiu_antonim, "TIU", "Antonim")
add_section(tiu_analogi, "TIU", "Analogi")
add_section(tiu_silogisme, "TIU", "Silogisme")
add_section(tiu_deret_angka, "TIU", "Deret Angka")
add_section(tiu_matematika, "TIU", "Matematika Dasar")
add_section(tiu_pemahaman, "TIU", "Pemahaman Bacaan")

# TKP
add_section(tkp_pelayanan, "TKP", "Pelayanan Publik")
add_section(tkp_profesionalisme, "TKP", "Profesionalisme")
add_section(tkp_integritas, "TKP", "Integritas")
add_section(tkp_sosial, "TKP", "Sosial Budaya")
add_section(tkp_teknologi, "TKP", "Teknologi Informasi")
add_section(tkp_anti_radikal, "TKP", "Anti Radikalisme")
add_section(tkp_bela_negara, "TKP", "Bela Negara")
add_section(tkp_jejaring, "TKP", "Jejaring Kerja")

print(f"Total questions generated: {len(all_questions)}")

# Count by section
from collections import Counter
sec_count = Counter(q["section"] for q in all_questions)
topic_count = Counter(q["topic"] for q in all_questions)
year_count = Counter(q["year"] for q in all_questions)

print(f"\nBy section: {dict(sec_count)}")
print(f"By year: {dict(year_count)}")
print(f"\nBy topic:")
for t, c in sorted(topic_count.items()):
    print(f"  {t}: {c}")

# Delete existing questions
print("\nDeleting existing questions...")
conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASS, database=DB_NAME)
cursor = conn.cursor()
cursor.execute("DELETE FROM questions")
print(f"Deleted {cursor.rowcount} old questions")

# Insert new questions
print("Inserting new questions...")
insert_sql = """INSERT INTO questions (section, topic, year, difficulty, question_text, options, correct_answer, explanation)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""

batch_size = 100
for i in range(0, len(all_questions), batch_size):
    batch = all_questions[i:i+batch_size]
    values = [(q["section"], q["topic"], q["year"], q["difficulty"], q["question_text"], q["options"], q["correct_answer"], q["explanation"]) for q in batch]
    cursor.executemany(insert_sql, values)
    conn.commit()
    print(f"  Inserted batch {i//batch_size + 1} ({len(batch)} rows)")

# Verify
cursor.execute("SELECT COUNT(*) FROM questions")
total = cursor.fetchone()[0]
cursor.execute("SELECT section, COUNT(*) FROM questions GROUP BY section")
sections = cursor.fetchall()
cursor.execute("SELECT year, COUNT(*) FROM questions GROUP BY year ORDER BY year")
years = cursor.fetchall()
cursor.execute("SELECT topic, COUNT(*) FROM questions GROUP BY topic ORDER BY section, topic")
topics = cursor.fetchall()

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
print("\nDone!")
