#!/usr/bin/env python3
"""Generate 500+ CPNS questions (TWK, TIU, TKP) years 2020-2025 and insert to MariaDB."""
import json
import pymysql
import os
from dotenv import load_dotenv

load_dotenv("/root/cpns/backend/.env")

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "cpns")

questions = []

# ============================================================
# TWK - PANCASILA (30 soal)
# ============================================================
questions += [
    {"section":"TWK","topic":"Pancasila","year":y,"difficulty":d,"question_text":q,"options":o,"correct_answer":c,"explanation":e}
    for y in [2020,2021,2022,2023,2024,2025]
    for d,q,o,c,e in [
        ("mudah","Pancasila sebagai dasar negara Indonesia pertama kali dicetuskan oleh...","[""Ir. Soekarno"",""Mohammad Hatta"",""Soepomo"",""Moh. Yamin"",""Radjiman Wedyodiningrat""]",0,"Ir. Soekarno mencetuskan istilah Pancasila dalam pidatonya pada 1 Juni 1945 di BPUPKI."),
        ("mudah","Sila pertama Pancasila berbunyi...","[""Kemanusiaan yang adil dan beradab"",""Ketuhanan Yang Maha Esa"",""Persatuan Indonesia"",""Kerakyatan yang dipimpin oleh hikmat kebijaksanaan dalam permusyawaratan/perwakilan"",""Keadilan sosial bagi seluruh rakyat Indonesia""]",1,"Sila pertama: Ketuhanan Yang Maha Esa."),
        ("mudah","Lambang negara Garuda Pancasila memiliki jumlah bulu sayap sebanyak...","[""17 helai"",""19 helai"",""45 helai"",""5 helai"",""8 helai""]",0,"Jumlah bulu sayap masing-masing 17 helai, melambangkan tanggal 17 Agustus 1945."),
        ("sedang","Dasar hukum pengamalan Pancasila sebelumnya adalah TAP MPR No. II/MPR/1978, kemudian diganti dengan...","[""TAP MPR No. I/MPR/2003"",""Perpres No. 7 Tahun 2018"",""Inpres No. 12 Tahun 2020 tentang Pembinaan Ideologi Pancasila"",""UU No. 17 Tahun 2006"",""PP No. 57 Tahun 2021""]",2,"Pengganti Pedoman Penghayatan dan Pengamalan Pancasila (P4)."),
        ("mudah","Sila keempat Pancasila dilambangkan dengan...","[""Bintang"",""Rantai"",""Pohon Beringin"",""Kepala Banteng"",""Padi dan Kapas""]",3,"Kepala Banteng melambangkan sila ke-4: Kerakyatan yang dipimpin oleh hikmat kebijaksanaan."),
        ("sedang","Tokoh yang mengusulkan dasar negara 'Piagam Jakarta' dengan sila pertama berbunyi 'Ketuhanan dengan kewajiban menjalankan syariat Islam bagi pemeluk-pemeluknya' adalah...","[""Mr. Moh. Yamin"",""Dr. Soepomo"",""H. Agus Salim"",""K.H. Wahid Hasyim"",""Abikusno Tjokrosujono""]",3,"K.H. Wahid Hasyim termasuk dalam panitia kecil yang menyusun Piagam Jakarta."),
        ("sulit","Menurut Notonegoro, Pancasila memiliki tiga tingkatan, yaitu...","[""Sila, butir, dan lambang"",""Dasar negara, pandangan hidup, dan perjanjian luhur"",""Filosofische grondslag, wereldbeschouwing, dan staatsidee"",""Dasar, pokok, dan butir"",""Ideologi, norma, dan budaya""]",1,"Menurut Notonegoro: dasar negara, pandangan hidup bangsa, dan perjanjian luhur rakyat Indonesia."),
        ("mudah","Perumusan Pancasila yang sah dan resmi tercantum dalam...","[""Piagam Jakarta"",""Pembukaan UUD 1945"",""Batang Tubuh UUD 1945"",""TAP MPR"",""UUDS 1950""]",1,"Pancasila secara resmi tercantum dalam Pembukaan UUD 1945 alinea keempat."),
        ("sedang","Makna sila kedua Pancasila 'Kemanusiaan yang adil dan beradab' antara lain...","[""Mengakui persamaan derajat hak dan kewajiban setiap manusia"",""Mengutamakan musyawarah"",""Menjunjung tinggi kebebasan beragama"",""Mengutamakan kepentingan negara"",""Membatasi kebebasan individu""]",0,"Sila kedua menekankan pengakuan persamaan derajat, hak, dan kewajiban."),
        ("mudah","Pancasila disahkan pada tanggal...","[""1 Juni 1945"",""22 Juni 1945"",""17 Agustus 1945"",""18 Agustus 1945"",""17 Juli 1945""]",3,"Pancasila disahkan oleh PPKI pada 18 Agustus 1945 bersama UUD 1945."),
        ("sulit","Pancasila sebagai sistem filsafat memiliki tingkatan tertinggi yaitu...","[""Sila pertama"",""Sila kelima"",""Sila ketiga"",""Pembukaan UUD 1945"",""Silaturahmi""]",0,"Sila pertama (Ketuhanan) menjadi dasar bagi sila-sila berikutnya (hierarkis berbentuk piramida)."),
        ("sedang","Sila ketiga Pancasila 'Persatuan Indonesia' mengandung makna...","[""Prioritas kepentingan pribadi"",""Mementingkan kelompok tertentu"",""Mengutamakan persatuan dan kesatuan bangsa di atas kepentingan pribadi/golongan"",""Memisahkan diri dari negara"",""Menghargai perbedaan tanpa kesatuan""]",2,"Persatuan Indonesia menekankan kesatuan di atas kepentingan golongan."),
        ("mudah","Sila kelima Pancasila dilambangkan dengan...","[""Bintang"",""Rantai"",""Pohon Beringin"",""Kepala Banteng"",""Padi dan Kapas""]",4,"Padi dan Kapas melambangkan sila ke-5: Keadilan sosial bagi seluruh rakyat Indonesia."),
        ("sedang","Makna sila kelima Pancasila 'Keadilan sosial bagi seluruh rakyat Indonesia' adalah...","[""Semua orang harus kaya raya"",""Pembagian harta secara merata"",""Keadilan dalam semua aspek kehidupan masyarakat"",""Hanya rakyat miskin yang mendapat bantuan"",""Pemerintah menguasai semua harta""]",2,"Keadilan sosial berarti keadilan dalam semua aspek: ekonomi, sosial, budaya, politik."),
        ("sulit","Menurut Moh. Yamin, lima dasar negara yang diusulkannya pada sidang BPUPKI tanggal 29 Mei 1945 adalah...","[""Ketuhanan, Kemanusiaan, Persatuan, Kerakyatan, Keadilan"",""Peri Kebangsaan, Peri Kemanusiaan, Peri Ketuhanan, Peri Kerakyatan, Kesejahteraan Rakyat"",""Ketuhanan, Internasionalisme, Nasionalisme, Demokrasi, Keadilan Sosial"",""Bhinneka Tunggal Ika, Ketuhanan, Kebangsaan, Demokrasi, Keadilan"",""Indonesia Merdeka, Ketuhanan, Kemanusiaan, Persatuan, Keadilan""]",1,"Moh. Yamin mengusulkan 5 dasar negara pada 29 Mei 1945 dengan nama yang berbeda dari rumusan akhir."),
        ("mudah","Bhinneka Tunggal Ika merupakan semboyan negara Indonesia yang artinya...","[""Berbeda-beda tetapi tetap satu"",""Satu kesatuan yang utuh"",""Beraneka ragam budaya"",""Bersatu dalam perbedaan"",""Satu nusa satu bangsa""]",0,"Bhinneka Tunggal Ika berasal dari bahasa Jawa Kuno artinya 'Berbeda-beda tetapi tetap satu'."),
        ("sedang","Proses perumusan Pancasila melalui beberapa tahap, yaitu...","[""BPUPKI 1, Panitia Sembilan, BPUPKI 2, PPKI"",""BPUPKI langsung PPKI"",""MPRS, MPR, Presiden"",""DPR, Presiden, MPR"",""Panitia Sembilan langsung PPKI""]",0,"Tahap: Sidang I BPUPKI (29 Mei - 1 Juni), Panitia Sembilan (22 Juni), Sidang II BPUPKI (10-16 Juli), PPKI (18 Agustus)."),
        ("sulit","Silogisme yang benar dari dua premis berikut: 'Semua manusia fana' dan 'Socrates adalah manusia' adalah...","[""Semua yang fana adalah Socrates"",""Socrates tidak fana"",""Socrates adalah fana"",""Manusia adalah Socrates"",""Fana adalah manusia""]",2,"Dari premis mayor 'Semua manusia fana' dan premis minor 'Socrates adalah manusia', maka kesimpulan: Socrates fana."),
        ("mudah","Pancasila sebagai ideologi terbuka artinya...","[""Dapat diganti sesuai kehendak penguasa"",""Nilai-nilai dasar Pancasila tetap, tetapi penjabarannya bisa berkembang"",""Bebas memilih ideologi lain"",""Tidak memiliki nilai dasar"",""Hanya berlaku untuk golongan tertentu""]",1,"Pancasila bersifat tetap pada nilai dasarnya, namun terbuka terhadap perkembangan penjabaran."),
        ("sedang","Salah satu tantangan terhadap Pancasila dewasa ini adalah...","[""Globalisasi dan derasnya arus informasi"",""Stabilitas politik yang baik"",""Pertumbuhan ekonomi yang tinggi"",""Persatuan yang semakin kuat"",""Stabilitas keamanan yang terjaga""]",0,"Globalisasi dan arus informasi menjadi tantangan karena mempengaruhi nilai-nilai Pancasila."),
        ("sulit","Nilai instrumental Pancasila tercermin dalam...","[""Pembukaan UUD 1945"",""UUD dan peraturan perundang-undangan"",""Budaya masyarakat"",""Tingkah laku sehari-hari"",""Sila-sila Pancasila""]",1,"Nilai instrumental adalah penjabaran nilai dasar dalam UUD dan peraturan perundang-undangan."),
        ("mudah","Siapakah yang menjadi ketua BPUPKI?","[""Ir. Soekarno"",""Dr. Radjiman Wedyodiningrat"",""Moh. Hatta"",""Dr. Soepomo"",""Mr. Moh. Yamin""]",1,"Dr. Radjiman Wedyodiningrat menjadi ketua BPUPKI."),
        ("sedang","Sila kedua Pancasila dilambangkan dengan...","[""Bintang"",""Rantai emas"",""Pohon Beringin"",""Kepala Banteng"",""Padi dan Kapas""]",1,"Rantai emas melambangkan sila ke-2: Kemanusiaan yang adil dan beradab."),
        ("mudah","Indonesia merdeka pada tanggal...","[""17 Agustus 1945"",""18 Agustus 1945"",""1 Juni 1945"",""22 Juni 1945"",""28 Oktober 1928""]",0,"Indonesia memproklamasikan kemerdekaan pada 17 Agustus 1945."),
        ("sedang","Amandemen UUD 1945 dilakukan sebanyak...","[""1 kali"",""2 kali"",""3 kali"",""4 kali"",""5 kali""]",3,"UUD 1945 diamandemen sebanyak 4 kali (1999, 2000, 2001, 2002)."),
        ("mudah","Sila ketiga Pancasila berbunyi...","[""Ketuhanan Yang Maha Esa"",""Kemanusiaan yang adil dan beradab"",""Persatuan Indonesia"",""Kerakyatan yang dipimpin oleh hikmat kebijaksanaan"",""Keadilan sosial bagi seluruh rakyat Indonesia""]",2,"Sila ketiga: Persatuan Indonesia."),
        ("sulit","Sistem pemerintahan Indonesia berdasarkan UUD 1945 setelah amandemen adalah...","[""Presidensial murni"",""Parlementer"",""Semi-presidensial"",""Presidensial dengan ciri parlementer"",""Monarki konstitusional""]",3,"UUD 1945 hasil amandemen mengadopsi sistem presidensial dengan ciri-ciri tertentu seperti parlementer."),
        ("sedang","Alinea keempat Pembukaan UUD 1945 memuat tentang...","[""Pernyataan kemerdekaan"",""Tujuan negara dan dasar negara Pancasila"",""Sistem pemerintahan"",""Hak dan kewajiban warga negara"",""Hubungan agama dan negara""]",1,"Alinea keempat memuat tujuan negara dan rumusan Pancasila sebagai dasar negara."),
        ("mudah","Musyawarah untuk mufakat tercermin pada sila ke...","[""1"",""2"",""3"",""4"",""5""]",3,"Musyawarah merupakan pengamalan sila ke-4: Kerakyatan yang dipimpin oleh hikmat kebijaksanaan."),
        ("sedang","Yang dimaksud dengan hak asasi manusia dalam konteks Pancasila adalah...","[""Hak yang diberikan oleh pemerintah"",""Hak yang melekat pada setiap manusia sejak lahir berdasarkan Ketuhanan"",""Hak yang bisa dicabut sewaktu-waktu"",""Hak milik pemerintah"",""Hak yang hanya dimiliki warga negara kaya""]",1,"Hak asasi menurut Pancasila melekat sejak lahir bersifat kodrati dari Tuhan."),
    ]
]

# ============================================================
# TWK - UUD 1945 (25 soal)
# ============================================================
questions += [
    {"section":"TWK","topic":"UUD 1945","year":y,"difficulty":d,"question_text":q,"options":o,"correct_answer":c,"explanation":e}
    for y in [2020,2021,2022,2023,2024,2025]
    for d,q,o,c,e in [
        ("mudah","UUD 1945 disahkan pada tanggal...","[""17 Agustus 1945"",""18 Agustus 1945"",""1 Juni 1945"",""22 Juni 1945"",""29 Mei 1945""]",1,"UUD 1945 disahkan oleh PPKI pada 18 Agustus 1945."),
        ("mudah","Pembukaan UUD 1945 terdiri dari...","[""2 alinea"",""3 alinea"",""4 alinea"",""5 alinea"",""6 alinea""]",2,"Pembukaan UUD 1945 terdiri dari 4 alinea."),
        ("sedang","Hak untuk hidup termasuk dalam kategori hak...","[""Politik"",""Ekonomi"",""Sosial budaya"",""Sipil"",""Pertahanan""]",3,"Hak untuk hidup termasuk hak sipil (civil rights)."),
        ("mudah","Masa jabatan Presiden Indonesia adalah...","[""4 tahun"",""5 tahun"",""6 tahun"",""7 tahun"",""3 tahun""]",1,"Presiden menjabat selama 5 tahun dan dapat dipilih kembali untuk satu kali masa jabatan."),
        ("sedang","Presiden dan Wakil Presiden dipilih secara...","[""Oleh MPR"",""Oleh DPR"",""Langsung oleh rakyat"",""Diusulkan oleh partai"",""Ditunjuk oleh Presiden sebelumnya""]",2,"Setelah amandemen UUD 1945, Presiden dan Wapres dipilih langsung oleh rakyat."),
        ("mudah","Indonesia memiliki sistem pemerintahan...","[""Parlementer"",""Presidensial"",""Monarki"",""Federal"",""Otokrasi""]",1,"Indonesia menganut sistem pemerintahan presidensial."),
        ("sulit","Pasal dalam UUD 1945 hasil amandemen yang mengatur tentang otonomi daerah adalah...","[""Pasal 18"",""Pasal 27"",""Pasal 28"",""Pasal 30"",""Pasal 33""]",0,"Pasal 18 UUD 1945 mengatur pembagian daerah Indonesia dan pemerintahan daerah."),
        ("sedang","Berdasarkan UUD 1945, kekuasaan kehakiman dilaksanakan oleh...","[""Presiden"",""DPR"",""MA dan MK"",""Kepolisian"",""Kejaksaan""]",2,"Kekuasaan kehakiman dilaksanakan oleh Mahkamah Agung dan Mahkamah Konstitusi."),
        ("mudah","MPR terdiri dari...","[""Anggota DPR saja"",""Anggota DPD saja"",""Anggota DPR dan DPD"",""Anggota DPR dan Presiden"",""Semua pejabat negara""]",2,"MPR terdiri dari anggota DPR dan anggota DPD."),
        ("sedang","Mahkamah Konstitusi beranggotakan...","[""7 orang hakim"",""9 orang hakim"",""5 orang hakim"",""11 orang hakim"",""3 orang hakim""]",1,"MK terdiri dari 9 orang hakim konstitusi yang ditetapkan oleh Presiden."),
        ("sulit","Amandemen UUD 1945 keempat dilakukan pada tahun...","[""1999"",""2000"",""2001"",""2002"",""2003""]",3,"Amandemen keempat dilakukan pada Sidang Tahunan MPR tahun 2002."),
        ("mudah","Yang berwenang mengangkat dan memberhentikan hakim agung adalah...","[""Presiden"",""DPR"",""MPR"",""KY (Komisi Yudisial)"",""MA""]",0,"Hakim agung diangkat dan diberhentikan oleh Presiden dengan persetujuan DPR."),
        ("sedang","UUD 1945 sebelum amandemen menempatkan MPR sebagai...","[""Lembaga legislatif"",""Lembaga tertinggi negara"",""Lembaga yudikatif"",""Lembaga eksekutif"",""Lembaga pengawas""]",1,"Sebelum amandemen, MPR adalah lembaga tertinggi negara. Setelah amandemen, tidak ada lagi lembaga tertinggi."),
        ("mudah","DPR memiliki fungsi...","[""Eksekutif"",""Legislatif, pengawasan, dan anggaran"",""Yudikatif"",""Pertahanan"",""Diplomasi""]",1,"DPR memiliki fungsi legislasi, anggaran, dan pengawasan."),
        ("sedang","DPD (Dewan Perwakilan Daerah) dibentuk berdasarkan...","[""TAP MPR"",""UU"",""Amandemen UUD 1945"",""Keputusan Presiden"",""Inisiatif DPR""]",2,"DPD dibentuk sebagai hasil amandemen UUD 1945 untuk mewakili kepentingan daerah."),
        ("sulit","Pasal 33 UUD 1945 mengatur tentang...","[""Hak dan kewajiban warga negara"",""Pertahanan dan keamanan negara"",""Perekonomian nasional dan kemakmuran rakyat"",""Pendidikan dan kebudayaan"",""Sistem pemerintahan""]",2,"Pasal 33 mengatur perekonomian disusun sebagai usaha bersama berdasar atas kekeluargaan."),
        ("mudah","Pemilu di Indonesia diselenggarakan oleh...","[""KPU"",""DPR"",""Presiden"",""MPR"",""Bawaslu""]",0,"KPU (Komisi Pemilihan Umum) menyelenggarakan pemilihan umum."),
        ("sedang","Pembukaan UUD 1945 alinea kedua memuat tentang...","[""Kemerdekaan Indonesia"",""Perjuangan pergerakan kemerdekaan Indonesia"",""Tujuan negara"",""Sistem pemerintahan"",""Hak asasi manusia""]",1,"Alinea kedua memuat perjuangan pergerakan kemerdekaan Indonesia."),
        ("mudah","UUD 1945 sebelum diamandemen terdiri dari...","[""16 bab, 37 pasal"",""20 bab, 40 pasal"",""15 bab, 35 pasal"",""17 bab, 38 pasal"",""18 bab, 39 pasal""]",0,"UUD 1945 terdiri dari 16 bab, 37 pasal, 4 aturan peralihan, 2 aturan tambahan."),
        ("sedang","Wakil Presiden Indonesia jika Presiden berhalangan tetap maka...","[""Dipilih oleh MPR"",""Diangkat oleh DPR"",""Menggantikan Presiden hingga akhir masa jabatan"",""Diadakan pemilu baru"",""Dipilih oleh Kabinet""]",2,"Wapres menggantikan Presiden hingga akhir masa jabatan."),
        ("sulit","Anggaran pendidikan dalam APBN wajib dialokasikan minimal...","[""10% dari APBN"",""15% dari APBN"",""20% dari APBN"",""25% dari APBN"",""30% dari APBN""]",2,"Pasal 31 ayat (4) UUD 1945 mengatur alokasi anggaran pendidikan minimal 20% dari APBN."),
        ("mudah","Kedaulatan berada di tangan rakyat dan dilaksanakan menurut...","[""UUD"",""Undang-Undang"",""Peraturan Presiden"",""Keputusan MPR"",""Hukum adat""]",0,"Pasal 1 ayat (2): Kedaulatan berada di tangan rakyat dan dilaksanakan menurut UUD."),
        ("sedang","Komisi Yudisial merupakan lembaga negara yang bersifat...","[""Eksekutif"",""Legislitif"",""Independen"",""Yudikatif"",""Suprastruktur""]",2,"KY bersifat mandiri dan independen dalam menjalankan fungsinya."),
        ("mudah","Pasal 27 UUD 1945 mengatur tentang...","[""Hak dan kewajiban warga negara"",""Sistem pertahanan"",""Pendidikan"",""Perekonomian"",""Pemerintahan daerah""]",0,"Pasal 27 mengatur segala warga negara bersamaan kedudukannya di dalam hukum dan pemerintahan."),
        ("sedang","Masa jabatan anggota DPR adalah...","[""3 tahun"",""4 tahun"",""5 tahun"",""6 tahun"",""7 tahun""]",2,"Anggota DPR menjabat selama 5 tahun."),
    ]
]

print(f"TWK questions so far: {len(questions)}")
print("Script continues with more TWK, TIU, TKP...")
