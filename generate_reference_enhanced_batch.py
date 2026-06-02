#!/usr/bin/env python3
"""Generate and insert a clean reference-enhanced CPNS batch.

Uses patterns distilled from /root/cpns/generator_style_guide.md and existing clean
reference pack. Deterministic, no external API.
"""
import json, re, pymysql
from datetime import date

DB={"host":"localhost","user":"root","database":"cpns","charset":"utf8mb4","cursorclass":pymysql.cursors.DictCursor}
YEAR=2026
SRC="Generated from CPNS reference pack and bank-soal style guide (2026-06)."

def q(section, topic, text, options, ans, explanation, difficulty='sedang'):
    assert len(options)==5 and len(set(o.strip().lower() for o in options))==5, text
    assert 0 <= ans < 5
    return dict(section=section, topic=topic, year=YEAR, difficulty=difficulty,
                question_text=text, options=options, correct_answer=ans,
                explanation=explanation)

def norm(s): return re.sub(r'\W+','',s.lower())[:220]

QUESTIONS=[]

# --- TIU Verbal: Sinonim / Antonim ---
synonyms=[
('ABSTRAK','Tidak berwujud','Nyata','Kaku','Sempit','Biasa'),
('AKURAT','Tepat','Cepat','Ringkas','Luas','Tajam'),
('KONVENSIONAL','Tradisional','Modern','Eksperimental','Rahasia','Bebas'),
('KOMPREHENSIF','Menyeluruh','Sebagian','Sementara','Kecil','Cepat'),
('IMPLIKASI','Dampak','Alasan','Tujuan','Syarat','Awal'),
('KOHESI','Keterpaduan','Perpecahan','Perlawanan','Perubahan','Perhitungan'),
('KONSISTEN','Tetap','Berubah','Ragu','Lemah','Acak'),
('MANDIRI','Independen','Tergantung','Pasif','Terpaksa','Tertutup'),
('VALID','Sah','Batal','Samar','Lama','Keras'),
('EFISIEN','Hemat guna','Boros','Lambat','Berlebihan','Rumit'),
]
for word,correct,*distr in synonyms:
    QUESTIONS.append(q('TIU','Sinonim',f"Sinonim dari kata '{word}' adalah...",[distr[0],correct,distr[1],distr[2],distr[3]],1,f"{word.lower().capitalize()} berarti {correct.lower()}.", 'mudah'))

antonyms=[
('PROGRESIF','Konservatif','Maju','Dinamis','Inovatif','Aktif'),
('OPTIMIS','Pesimis','Yakin','Antusias','Berharap','Semangat'),
('KONKRET','Abstrak','Nyata','Terukur','Jelas','Tampak'),
('STABIL','Labil','Tetap','Seimbang','Kokoh','Konsisten'),
('INKLUSIF','Eksklusif','Terbuka','Merangkul','Umum','Menerima'),
('MAJEMUK','Tunggal','Beragam','Banyak','Plural','Campuran'),
('PASIF','Aktif','Diam','Menunggu','Lamban','Tunduk'),
('SUBJEKTIF','Objektif','Pribadi','Sepihak','Relatif','Bias'),
('SPESIFIK','Umum','Khusus','Tertentu','Detail','Terarah'),
('RIGID','Fleksibel','Kaku','Ketat','Tegas','Beku'),
]
for word,correct,*distr in antonyms:
    QUESTIONS.append(q('TIU','Antonim',f"Antonim dari kata '{word}' adalah...",[correct,distr[0],distr[1],distr[2],distr[3]],0,f"Antonim {word.lower()} adalah {correct.lower()}.", 'mudah'))

# --- TIU Analogi ---
analogies=[
('Dokter','Pasien','Guru','Murid','Sekolah','Buku','Kelas'),
('Kunci','Pintu','Password','Akun','Layar','Jaringan','Komputer'),
('Benih','Pohon','Ide','Program','Rapat','Kertas','Meja'),
('Kompas','Arah','Jam','Waktu','Angka','Suara','Baterai'),
('Hakim','Putusan','Penulis','Naskah','Kertas','Pembaca','Penerbit'),
('Nelayan','Ikan','Petani','Padi','Sawah','Pupuk','Traktor'),
('Apoteker','Obat','Pustakawan','Buku','Rak','Kartu','Gedung'),
('Arsitek','Bangunan','Sutradara','Film','Kamera','Aktor','Panggung'),
('Termometer','Suhu','Barometer','Tekanan udara','Angin','Hujan','Awan'),
('Rem','Kecepatan','Filter','Kotoran','Mesin','Jalan','Bensin'),
]
for a,b,c,d,x,y,z in analogies:
    QUESTIONS.append(q('TIU','Analogi',f"{a} : {b} = {c} : ...",[x,d,y,z,'Tidak berhubungan'],1,f"Hubungannya adalah {a.lower()} berhubungan langsung dengan {b.lower()}; {c.lower()} berhubungan dengan {d.lower()}.", 'mudah'))

# --- TIU Silogisme ---
silog=[
('Semua arsip penting harus disimpan rapi. Sebagian dokumen proyek adalah arsip penting.', 'Sebagian dokumen proyek harus disimpan rapi'),
('Semua peserta yang lulus administrasi boleh mengikuti SKD. Rani lulus administrasi.', 'Rani boleh mengikuti SKD'),
('Tidak ada pegawai disiplin yang sering terlambat. Sebagian staf bagian umum sering terlambat.', 'Sebagian staf bagian umum bukan pegawai disiplin'),
('Semua laporan resmi memiliki nomor surat. Dokumen ini tidak memiliki nomor surat.', 'Dokumen ini bukan laporan resmi'),
('Semua aplikasi yang aman memerlukan autentikasi. Sistem X adalah aplikasi yang aman.', 'Sistem X memerlukan autentikasi'),
('Sebagian pelatihan ASN dilakukan secara daring. Semua pelatihan daring membutuhkan koneksi internet.', 'Sebagian pelatihan ASN membutuhkan koneksi internet'),
('Semua warga negara wajib menaati hukum. Andi adalah warga negara.', 'Andi wajib menaati hukum'),
('Tidak ada keputusan penting yang dibuat tanpa data. Rapat ini menghasilkan keputusan penting.', 'Rapat ini dibuat dengan data'),
('Semua kendaraan dinas tercatat dalam inventaris. Mobil A tidak tercatat dalam inventaris.', 'Mobil A bukan kendaraan dinas'),
('Semua peserta yang membawa kartu ujian dapat masuk ruangan. Sinta membawa kartu ujian.', 'Sinta dapat masuk ruangan'),
]
for premise, conclusion in silog:
    opts=[conclusion, 'Semua pernyataan pasti salah', 'Tidak dapat ditarik kesimpulan apa pun', 'Kesimpulan berlawanan dengan premis', 'Hanya sebagian premis yang benar']
    QUESTIONS.append(q('TIU','Silogisme',premise+' Kesimpulan yang tepat adalah...',opts,0,'Kesimpulan mengikuti hubungan logis langsung dari premis yang diberikan.', 'sedang'))

# --- TIU Math / Sequences / Reading ---
seqs=[([3,6,12,24],48,'pola dikali 2'),([5,9,17,33],65,'selisih 4, 8, 16, berikutnya 32'),([2,5,10,17],26,'pola n²+1: 1²+1, 2²+1, ...'),([81,27,9,3],1,'pola dibagi 3'),([4,7,13,25],49,'selisih 3, 6, 12, berikutnya 24'),([1,4,9,16],25,'bilangan kuadrat berurutan'),([2,6,18,54],162,'pola dikali 3'),([100,95,85,70],50,'selisih -5, -10, -15, berikutnya -20'),([7,14,28,56],112,'pola dikali 2'),([11,13,17,23],31,'bilangan prima berurutan setelah 23 adalah 29? wait')]
# fix last manually
seqs[-1]=([11,13,17,19],23,'bilangan prima berurutan')
for arr,ans,expl in seqs:
    opts=[str(ans),str(ans+2),str(ans-2),str(ans*2),str(max(0,ans-5))]
    # ensure unique
    seen=[]
    for o in opts:
        if o not in seen: seen.append(o)
    while len(seen)<5: seen.append(str(ans+len(seen)+7))
    QUESTIONS.append(q('TIU','Deret Angka',', '.join(map(str,arr))+', ...?',seen,0,f"Deret mengikuti {expl}, sehingga jawaban berikutnya adalah {ans}.", 'mudah'))

maths=[
('Jika 12 pekerja menyelesaikan pekerjaan dalam 10 hari, berapa hari yang dibutuhkan 20 pekerja dengan kemampuan sama?', ['6 hari','8 hari','10 hari','12 hari','5 hari'],0,'Total beban 12×10=120 pekerja-hari. 120÷20=6 hari.'),
('Harga sebuah barang Rp80.000 naik 25%. Harga barunya adalah...', ['Rp90.000','Rp100.000','Rp105.000','Rp110.000','Rp120.000'],1,'25% dari 80.000 adalah 20.000, jadi harga baru 100.000.'),
('Rata-rata 5 bilangan adalah 18. Jika empat bilangan berjumlah 70, bilangan kelima adalah...', ['16','18','20','22','24'],2,'Total lima bilangan 5×18=90. Bilangan kelima 90-70=20.'),
('Perbandingan uang Ani dan Budi 3:5. Jika jumlah uang mereka Rp160.000, uang Budi adalah...', ['Rp60.000','Rp80.000','Rp100.000','Rp120.000','Rp140.000'],2,'Total rasio 8 bagian; 1 bagian=20.000. Budi 5 bagian=100.000.'),
('Sebuah mobil menempuh 180 km dalam 3 jam. Kecepatan rata-ratanya adalah...', ['45 km/jam','50 km/jam','55 km/jam','60 km/jam','65 km/jam'],3,'Kecepatan = jarak/waktu = 180/3 = 60 km/jam.'),
('Luas persegi panjang dengan panjang 18 cm dan lebar 7 cm adalah...', ['96 cm²','112 cm²','126 cm²','144 cm²','156 cm²'],2,'Luas = panjang × lebar = 18×7 = 126 cm².'),
('Jika 3x + 7 = 25, maka nilai x adalah...', ['4','5','6','7','8'],2,'3x=18, maka x=6.'),
('Sebuah tabungan Rp2.000.000 mendapat bunga 6% per tahun. Bunga selama setahun adalah...', ['Rp60.000','Rp90.000','Rp120.000','Rp150.000','Rp180.000'],2,'6%×2.000.000 = 120.000.'),
('Nilai 2/5 dari 150 adalah...', ['45','50','55','60','65'],3,'2/5×150 = 60.'),
('Sebuah peta berskala 1:200.000. Jarak 4 cm pada peta sama dengan jarak sebenarnya...', ['4 km','6 km','8 km','10 km','12 km'],2,'4×200.000 cm = 800.000 cm = 8 km.'),
]
for text,opts,ans,expl in maths:
    QUESTIONS.append(q('TIU','Matematika Dasar',text,opts,ans,expl,'sedang'))

readings=[
("Bacaan: 'Penggunaan layanan digital pemerintah meningkat karena masyarakat membutuhkan proses yang cepat dan transparan.' Kesimpulan yang tepat adalah...", ['Layanan digital selalu menggantikan semua petugas','Masyarakat menolak layanan digital','Layanan digital pemerintah diminati karena cepat dan transparan','Proses manual lebih transparan','Pemerintah tidak perlu evaluasi layanan'],2,'Kesimpulan harus memuat alasan utama: kebutuhan proses cepat dan transparan.'),
("Bacaan: 'Kedisiplinan pegawai berpengaruh pada kualitas pelayanan publik.' Gagasan utama kalimat tersebut adalah...", ['Kualitas pelayanan tidak penting','Kedisiplinan pegawai memengaruhi pelayanan publik','Pegawai tidak perlu disiplin','Pelayanan publik hanya soal teknologi','Kedisiplinan menghambat layanan'],1,'Gagasan utama terletak pada hubungan kedisiplinan dengan kualitas pelayanan.'),
("Bacaan: 'Program pelatihan ASN dilakukan berkala untuk meningkatkan kompetensi.' Tujuan program pelatihan tersebut adalah...", ['Mengurangi jumlah ASN','Meningkatkan kompetensi ASN','Mengganti aturan kerja','Memperpanjang jam kerja','Membatasi pelayanan'],1,'Tujuan disebut eksplisit: meningkatkan kompetensi.'),
("Bacaan: 'Arsip digital memudahkan pencarian dokumen dan mengurangi risiko kehilangan data.' Manfaat arsip digital adalah...", ['Mempersulit pencarian dokumen','Menghapus semua dokumen lama','Memudahkan pencarian dan mengurangi risiko kehilangan','Menghilangkan kebutuhan keamanan data','Mengurangi tanggung jawab pegawai'],2,'Manfaat disebut langsung dalam bacaan.'),
("Bacaan: 'Evaluasi pelayanan dilakukan agar instansi mengetahui kekurangan dan memperbaiki prosedur.' Alasan evaluasi pelayanan adalah...", ['Menambah antrean masyarakat','Mencari kesalahan warga','Mengetahui kekurangan dan memperbaiki prosedur','Mengurangi transparansi','Menghapus standar pelayanan'],2,'Evaluasi berguna untuk menemukan kekurangan dan perbaikan prosedur.'),
]
for text,opts,ans,expl in readings:
    QUESTIONS.append(q('TIU','Pemahaman Bacaan',text,opts,ans,expl,'mudah'))

# --- TWK facts ---
twk_items=[
('TWK','Pancasila','Nilai musyawarah untuk mufakat terutama mencerminkan sila ke...', ['Pertama','Kedua','Ketiga','Keempat','Kelima'],3,'Sila keempat menekankan kerakyatan dan permusyawaratan/perwakilan.'),
('TWK','Pancasila','Contoh pengamalan sila kedua Pancasila adalah...', ['Menghormati martabat manusia','Memilih produk lokal saja','Mengutamakan kepentingan pribadi','Menolak pendapat berbeda','Membayar pajak kendaraan'],0,'Sila kedua berisi kemanusiaan yang adil dan beradab.'),
('TWK','Pancasila','Pancasila sebagai dasar negara berarti...', ['Menjadi sumber nilai dan dasar penyelenggaraan negara','Hanya semboyan sosial','Hanya berlaku saat upacara','Dapat diganti setiap pemilu','Tidak terkait hukum'],0,'Sebagai dasar negara, Pancasila menjadi landasan penyelenggaraan negara dan sumber nilai hukum.'),
('TWK','Pancasila','Lambang sila kelima Pancasila adalah...', ['Bintang','Rantai','Pohon beringin','Kepala banteng','Padi dan kapas'],4,'Padi dan kapas melambangkan keadilan sosial bagi seluruh rakyat Indonesia.'),
('TWK','Pancasila','Sila ketiga Pancasila menekankan nilai...', ['Persatuan Indonesia','Keadilan sosial','Ketuhanan','Musyawarah','Kemanusiaan'],0,'Sila ketiga berbunyi Persatuan Indonesia.'),
('TWK','UUD 1945','Menurut UUD 1945, kedaulatan berada di tangan rakyat dan dilaksanakan menurut...', ['Undang-undang dasar','Keputusan presiden','Peraturan daerah','Kebiasaan politik','Instruksi menteri'],0,'Pasal 1 ayat (2) UUD 1945 menyatakan kedaulatan berada di tangan rakyat dan dilaksanakan menurut UUD.'),
('TWK','UUD 1945','Lembaga yang berwenang mengubah dan menetapkan UUD adalah...', ['DPR','MPR','DPD','MA','BPK'],1,'MPR memiliki kewenangan mengubah dan menetapkan UUD.'),
('TWK','UUD 1945','Hak DPR untuk meminta keterangan kepada pemerintah disebut hak...', ['Angket','Interpelasi','Imunitas','Budget','Inisiatif'],1,'Hak interpelasi adalah hak DPR meminta keterangan kepada pemerintah.'),
('TWK','UUD 1945','Pasal 27 ayat (1) UUD 1945 menegaskan prinsip...', ['Persamaan kedudukan dalam hukum dan pemerintahan','Kebebasan pers sepenuhnya','Pembentukan kementerian','Hak memilih presiden','Pembagian wilayah'],0,'Pasal 27 ayat (1) memuat persamaan kedudukan warga negara di dalam hukum dan pemerintahan.'),
('TWK','UUD 1945','Mahkamah Konstitusi berwenang menguji undang-undang terhadap...', ['Pancasila saja','UUD 1945','Peraturan menteri','Peraturan desa','Keputusan kepala daerah'],1,'MK menguji undang-undang terhadap UUD 1945.'),
('TWK','Bhinneka Tunggal Ika','Makna Bhinneka Tunggal Ika adalah...', ['Berbeda-beda tetapi tetap satu','Satu suku satu bangsa','Persamaan tanpa perbedaan','Perbedaan harus dihapus','Keseragaman budaya'],0,'Bhinneka Tunggal Ika berarti berbeda-beda tetapi tetap satu.'),
('TWK','Bhinneka Tunggal Ika','Sikap yang mencerminkan Bhinneka Tunggal Ika adalah...', ['Menghargai perbedaan suku dan agama','Memaksakan budaya sendiri','Menolak kerja sama lintas daerah','Menghindari musyawarah','Mengutamakan kelompok sendiri'],0,'Menghargai keberagaman merupakan inti Bhinneka Tunggal Ika.'),
('TWK','Bhinneka Tunggal Ika','Keberagaman budaya Indonesia harus dipandang sebagai...', ['Ancaman persatuan','Kekayaan bangsa','Hambatan pembangunan','Alasan pemisahan','Masalah pemerintahan'],1,'Keberagaman adalah kekayaan bangsa yang memperkuat identitas nasional.'),
('TWK','Sejarah Indonesia','BPUPKI dibentuk untuk...', ['Mempersiapkan kemerdekaan Indonesia','Membentuk VOC','Mengatur tanam paksa','Mendirikan ASEAN','Membubarkan PPKI'],0,'BPUPKI bertugas menyelidiki usaha-usaha persiapan kemerdekaan Indonesia.'),
('TWK','Sejarah Indonesia','Proklamasi Kemerdekaan Indonesia dibacakan pada tanggal...', ['1 Juni 1945','17 Agustus 1945','18 Agustus 1945','28 Oktober 1928','10 November 1945'],1,'Proklamasi dibacakan pada 17 Agustus 1945.'),
('TWK','Sejarah Indonesia','Sumpah Pemuda terjadi pada tahun...', ['1908','1928','1945','1949','1955'],1,'Sumpah Pemuda dicetuskan pada Kongres Pemuda II tahun 1928.'),
('TWK','Sejarah Indonesia','PPKI mengesahkan UUD 1945 pada tanggal...', ['17 Agustus 1945','18 Agustus 1945','1 Juni 1945','22 Juni 1945','10 November 1945'],1,'PPKI mengesahkan UUD 1945 pada 18 Agustus 1945.'),
('TWK','Hankam','Sistem pertahanan Indonesia menganut sistem...', ['Pertahanan rakyat semesta','Pertahanan aliansi tunggal','Pertahanan kolonial','Pertahanan privat','Pertahanan sektoral'],0,'Indonesia menganut sistem pertahanan dan keamanan rakyat semesta.'),
('TWK','Hankam','Komponen utama pertahanan negara adalah...', ['TNI','Polri','Pemerintah daerah','Organisasi masyarakat','Perusahaan swasta'],0,'TNI merupakan komponen utama pertahanan negara.'),
('TWK','Hankam','Bela negara dapat diwujudkan warga negara dengan cara...', ['Menaati hukum dan menjaga persatuan','Menghindari pajak','Menyebarkan hoaks','Mengutamakan kelompok sendiri','Menolak musyawarah'],0,'Bela negara mencakup taat hukum, cinta tanah air, dan menjaga persatuan.'),
]
for item in twk_items:
    QUESTIONS.append(q(*item, difficulty='mudah'))

# --- TKP scenarios ---
tkp=[
('Pelayanan Publik','Warga lanjut usia kesulitan mengisi formulir layanan. Sikap terbaik Anda adalah...', ['Meminta warga datang bersama keluarga','Membantu mengisi berdasarkan data yang diberikan dan menjelaskan prosesnya','Menyuruh warga membaca petunjuk sendiri','Mengalihkan ke loket lain tanpa penjelasan','Menunda layanan sampai antrean sepi'],1,'Pelayanan publik menuntut empati, bantuan aktif, dan penjelasan prosedur.'),
('Pelayanan Publik','Antrean layanan menjadi panjang karena sistem lambat. Anda sebaiknya...', ['Diam menunggu sistem normal','Mengumumkan kondisi, meminta maaf, dan mengatur prioritas layanan','Menutup loket tanpa penjelasan','Menyalahkan bagian IT di depan warga','Melayani kenalan terlebih dahulu'],1,'Transparansi, permintaan maaf, dan pengaturan prioritas menjaga kualitas layanan.'),
('Integritas','Rekan meminta Anda menandatangani daftar hadir padahal ia belum datang. Anda akan...', ['Menolak dan mengingatkan aturan presensi','Menandatangani karena teman dekat','Menunggu sampai ia datang lalu menandatangani','Meminta imbalan kecil','Membiarkan kolomnya kosong tanpa bicara'],0,'Integritas menuntut kejujuran dan menolak pemalsuan presensi.'),
('Integritas','Atasan meminta data laporan dibuat lebih baik dari kondisi sebenarnya. Sikap Anda...', ['Mengubah data agar atasan puas','Menolak dengan sopan dan menawarkan perbaikan berbasis data nyata','Menghapus data yang buruk','Meminta rekan lain mengubahnya','Diam dan mengikuti instruksi'],1,'Data harus akurat; penolakan perlu disampaikan profesional dengan solusi.'),
('Profesionalisme','Anda mendapat tugas baru yang belum dikuasai. Tindakan paling tepat adalah...', ['Menolak karena belum mampu','Mempelajari tugas dan meminta arahan seperlunya','Mengerjakan asal cepat selesai','Menunda sampai ada pelatihan resmi','Meminta rekan mengerjakan semuanya'],1,'Profesionalisme mencakup kemauan belajar dan tanggung jawab menyelesaikan tugas.'),
('Profesionalisme','Anda menyadari ada kesalahan input yang memengaruhi laporan. Anda sebaiknya...', ['Segera melapor dan memperbaiki data','Menunggu ditemukan auditor','Menghapus jejak kesalahan','Menyalahkan sistem','Membuat laporan baru tanpa penjelasan'],0,'Mengakui dan memperbaiki kesalahan adalah sikap profesional.'),
('Jejaring Kerja','Tim lintas unit berbeda pendapat tentang jadwal program. Anda akan...', ['Memaksakan jadwal unit sendiri','Mengajak diskusi untuk mencari jadwal yang paling realistis','Mundur dari koordinasi','Menunggu atasan memutuskan tanpa masukan','Menyalahkan unit lain'],1,'Jejaring kerja menekankan koordinasi aktif dan solusi bersama.'),
('Jejaring Kerja','Instansi lain meminta data pendukung program bersama. Sikap Anda...', ['Memberikan data sesuai prosedur dan menjaga koordinasi','Menolak semua permintaan','Memberikan seluruh data rahasia','Mengabaikan permintaan','Meminta imbalan kerja sama'],0,'Kerja sama perlu responsif tetapi tetap sesuai prosedur dan keamanan data.'),
('Bela Negara','Anda menemukan konten yang memecah belah persatuan di grup kantor. Anda akan...', ['Meneruskan agar ramai','Mengabaikan sepenuhnya','Mengingatkan dengan sopan dan melaporkan jika mengandung provokasi berbahaya','Membalas dengan ujaran keras','Keluar dari grup tanpa klarifikasi'],2,'Bela negara mencakup menjaga persatuan dan melawan provokasi secara tepat.'),
('Anti Radikalisme','Seorang rekan mengajak mengikuti kegiatan yang mengarah pada intoleransi. Sikap Anda...', ['Menolak, mengingatkan, dan melapor melalui kanal resmi bila berbahaya','Ikut karena solidaritas','Diam agar tidak konflik','Menyebarkan ajakan itu ke orang lain','Menghadiri sekali untuk coba-coba'],0,'Anti-radikalisme menuntut penolakan terhadap intoleransi dan pelaporan sesuai mekanisme.'),
('Sosial Budaya','Di lingkungan kerja ada rekan dari budaya berbeda yang kurang dipahami tim. Anda sebaiknya...', ['Mendorong komunikasi saling menghormati','Menertawakan kebiasaannya','Menghindari bekerja dengannya','Meminta ia menyesuaikan seluruhnya','Membatasi pergaulan'],0,'Sosial budaya menekankan toleransi dan komunikasi inklusif.'),
('Teknologi Informasi','Aplikasi layanan baru membuat sebagian warga bingung. Anda akan...', ['Membuat panduan singkat dan membantu warga menggunakan aplikasi','Menyuruh warga belajar sendiri','Menolak layanan manual tanpa penjelasan','Mengkritik aplikasi di depan warga','Mengabaikan keluhan'],0,'Pemanfaatan TI harus disertai edukasi agar layanan tetap inklusif.'),
]
for topic,text,opts,ans,expl in tkp:
    QUESTIONS.append(q('TKP',topic,text,opts,ans,expl,'sedang'))

# Insert
conn=pymysql.connect(**DB)
inserted=skipped=0
by_topic={}
with conn.cursor() as cur:
    cur.execute('SELECT question_text FROM questions')
    existing={norm(r['question_text']) for r in cur.fetchall()}
    for item in QUESTIONS:
        key=norm(item['question_text'])
        if key in existing:
            skipped+=1; continue
        cur.execute("""INSERT INTO questions(section,topic,year,difficulty,question_text,options,correct_answer,explanation)
                       VALUES(%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (item['section'],item['topic'],item['year'],item['difficulty'],item['question_text'],json.dumps(item['options'],ensure_ascii=False),item['correct_answer'],item['explanation']+' '+SRC))
        existing.add(key); inserted+=1
        by_topic[f"{item['section']}/{item['topic']}"]=by_topic.get(f"{item['section']}/{item['topic']}",0)+1
conn.commit(); conn.close()
print(json.dumps({'generated':len(QUESTIONS),'inserted':inserted,'skipped_duplicates':skipped,'by_topic':by_topic},ensure_ascii=False,indent=2))
