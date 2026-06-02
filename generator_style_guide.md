# CPNS Question Generator Style Guide

Use this guide + `/root/cpns/generation_reference_pack.jsonl` before generating soal baru.

## Hard rules
- Generate exactly 5 unique non-empty options (A-E).
- `correct_answer` must be 0-indexed: A=0, B=1, C=2, D=3, E=4.
- Always write a specific explanation with the reasoning/legal basis/pattern; never placeholder.
- Do not copy PDF artifacts: page numbers, `KUNCI JAWABAN`, `INI HANYA SOAL LATIHAN`, source headers.
- Keep every question self-contained and classifiable into one CPNS section/topic.
- TKP answers should be scored by best ASN behavior: integrity, service orientation, professionalism, collaboration.

## Clean reference distribution from DB
- TIU/Analogi: 78 clean examples (20 in reference pack)
- TIU/Antonim: 31 clean examples (20 in reference pack)
- TIU/Matematika Dasar: 79 clean examples (20 in reference pack)
- TIU/Pemahaman Bacaan: 7 clean examples (7 in reference pack)
- TIU/Silogisme: 80 clean examples (20 in reference pack)
- TIU/Sinonim: 31 clean examples (20 in reference pack)
- TKP/Anti Radikalisme: 6 clean examples (6 in reference pack)
- TKP/Bela Negara: 4 clean examples (4 in reference pack)
- TKP/Integritas: 7 clean examples (7 in reference pack)
- TKP/Jejaring Kerja: 71 clean examples (20 in reference pack)
- TKP/Pelayanan Publik: 17 clean examples (17 in reference pack)
- TKP/Profesionalisme: 102 clean examples (20 in reference pack)
- TKP/Sosial Budaya: 9 clean examples (9 in reference pack)
- TKP/Teknologi Informasi: 7 clean examples (7 in reference pack)
- TWK/Bhinneka Tunggal Ika: 28 clean examples (20 in reference pack)
- TWK/Hankam: 15 clean examples (15 in reference pack)
- TWK/Pancasila: 69 clean examples (20 in reference pack)
- TWK/Sejarah Indonesia: 30 clean examples (20 in reference pack)
- TWK/UUD 1945: 71 clean examples (20 in reference pack)

## New PDF folder extraction summary
- PDFs considered: 31
- Clean extracted examples kept: 107
- Raw PDF corpus file: `/root/cpns/question_training_corpus.jsonl`
- Note: PDF extraction is supplemental only; production DB examples are the primary generation style reference.

## Few-shot examples by section/topic

### TIU / Analogi

Question: Matahari : Siang = Bulan : ...
A. Malam
B. Sore
C. Subuh
D. Pagi
E. Senja
Correct: A
Explanation: Matahari identik dengan siang, bulan identik dengan malam.

### TIU / Antonim

Question: Antonim dari kata 'KAYA' adalah...
A. Sejahtera
B. Kaya raya
C. Miskin
D. Berkecukupan
E. Makmur
Correct: C
Explanation: Kaya ↔ miskin.

### TIU / Matematika Dasar

Question: Hasil dari 15% dari 200 adalah...
A. 35
B. 20
C. 25
D. 15
E. 30
Correct: E
Explanation: 15/100 × 200 = 30.

### TIU / Pemahaman Bacaan

Question: Bacaan: 'Jakarta merupakan ibu kota Indonesia yang padat penduduk.' Kesimpulan yang tepat adalah...
A. Jakarta tidak padat
B. Jakarta adalah kota terpadat di Indonesia
C. Jakarta ibu kota Indonesia dan padat
D. Indonesia hanya punya Jakarta
E. Jakarta bukan ibu kota
Correct: C
Explanation: Dua informasi: Jakarta ibu kota + padat penduduk.

### TIU / Silogisme

Question: Semua kucing adalah hewan. Semua hewan butuh makan. Kesimpulan:...
A. Kucing bukan hewan
B. Tidak semua kucing butuh makan
C. Hewan tidak butuh makan
D. Semua hewan adalah kucing
E. Semua kucing butuh makan
Correct: E
Explanation: Sillogisme: Semua A adalah B, semua B adalah C, maka semua A adalah C.

### TIU / Sinonim

Question: Sinonim dari kata 'ABDI' adalah...
A. Pemimpin
B. Pelayan
C. Majikan
D. Tuan
E. Raja
Correct: B
Explanation: Abdi berarti pelayan atau hamba.

### TKP / Anti Radikalisme

Question: Anda mendengar seseorang menyebarkan paham radikal di lingkungan kerja. Tindakan terbaik adalah...
A. {'text': 'Mendengarkan saja', 'score': 3}
B. {'text': 'Mengabaikan karena bukan urusan Anda', 'score': 4}
C. {'text': 'Ikut mendengarkan dan menyebarluaskan', 'score': 2}
D. {'text': 'Mendukung paham tersebut', 'score': 1}
E. {'text': 'Melaporkan ke atasan dan BNPT/laporan resmi, serta mengingatkan rekan', 'score': 5}
Correct: E
Explanation: PNS wajib melawan paham radikal dan melapor ke pihak berwenang.

### TKP / Bela Negara

Question: Anda mendengar berita hoax tentang negara yang viral. Anda...
A. {'text': 'Membagikan untuk peringatan', 'score': 3}
B. {'text': 'Tidak mempercayai tapi tidak meluruskan', 'score': 4}
C. {'text': 'Mengecek kebenaran dari sumber resmi dan meluruskan informasi', 'score': 5}
D. {'text': 'Menciptakan berita serupa', 'score': 1}
E. {'text': 'Membagikan karena menarik', 'score': 2}
Correct: C
Explanation: Melawan hoax dengan fakta dari sumber resmi.

### TKP / Integritas

Question: Anda mengetahui rekan kerja melakukan korupsi. Tindakan terbaik adalah...
A. {'text': 'Mengancam akan melaporkan', 'score': 2}
B. {'text': 'Minta bagian dari hasil korupsi', 'score': 1}
C. {'text': 'Membiarkan karena bukan urusan Anda', 'score': 3}
D. {'text': 'Mengingatkan rekan secara pribadi', 'score': 4}
E. {'text': 'Melaporkan melalui saluran yang benar (whistleblowing system)', 'score': 5}
Correct: E
Explanation: Integritas: melaporkan melalui mekanisme resmi.

### TKP / Jejaring Kerja

Question: Anda diminta berkolaborasi dengan instansi lain untuk program bersama. Tindakan terbaik adalah...
A. {'text': 'Menerima dan mengikuti arahan instansi lain', 'score': 4}
B. {'text': 'Menyambut baik, membuat rencana kerja bersama, dan berkoordinasi aktif', 'score': 5}
C. {'text': 'Menolak karena bukan tugas Anda', 'score': 1}
D. {'text': 'Menolak karena merepotkan', 'score': 2}
E. {'text': 'Berpartisipasi pasif', 'score': 3}
Correct: B
Explanation: Jejaring kerja: kolaborasi aktif dan proaktif.

### TKP / Pelayanan Publik

Question: Seorang warga marah karena pelayanan lambat. Sikap terbaik adalah...
A. {'text': 'Mendengarkan keluhan dengan sabar', 'score': 4}
B. {'text': 'Mengabaikan kemarahan warga', 'score': 3}
C. {'text': 'Membalas dengan nada tinggi', 'score': 2}
D. {'text': 'Meminta maaf, menjelaskan penyebab, dan memberikan solusi', 'score': 5}
E. {'text': 'Memanggil satpam untuk mengusir', 'score': 1}
Correct: D
Explanation: Pelayanan prima: empati, penjelasan, dan solusi.

### TKP / Profesionalisme

Question: Anda mendapat tugas yang bukan bidang keahlian Anda. Sikap terbaik adalah...
A. {'text': 'Meminta bantuan rekan untuk mengerjakan', 'score': 3}
B. {'text': 'Menerima dan berusaha menyelesaikan dengan kemampuan terbaik', 'score': 4}
C. {'text': 'Mengerjakan asal-asalan', 'score': 1}
D. {'text': 'Menolak tugas tersebut', 'score': 2}
E. {'text': 'Mempelajari dan menyelesaikan tugas tersebut sambil berkonsultasi dengan rekan yang ahli', 'score': 5}
Correct: E
Explanation: Profesional: belajar dan berkonsultasi, bukan menolak atau asal-asalan.

### TKP / Sosial Budaya

Question: Dilingkungan tempat tinggal Anda terjadi konflik antar warga. Peran terbaik Anda adalah...
A. {'text': 'Melaporkan ke RT/RW', 'score': 3}
B. {'text': 'Menghindari konflik', 'score': 2}
C. {'text': 'Membela salah satu pihak', 'score': 1}
D. {'text': 'Menjadi mediator yang netral untuk memediasi perdamaian', 'score': 5}
E. {'text': 'Membantu pihak yang Anda anggap benar', 'score': 4}
Correct: D
Explanation: Peran aktif sebagai mediator netral untuk perdamaian.

### TKP / Teknologi Informasi

Question: Kantor Anda akan menerapkan sistem digitalisasi. Beberapa rekan menolak karena gaptek. Anda...
A. {'text': 'Meminta atasan yang mengajari', 'score': 2}
B. {'text': 'Tidak peduli dengan rekan lain', 'score': 1}
C. {'text': 'Hanya menggunakan sistem baru untuk diri sendiri', 'score': 4}
D. {'text': 'Ikut menolak karena banyak yang tidak setuju', 'score': 3}
E. {'text': 'Menawarkan diri menjadi mentor dan membantu rekan-rekan belajar sistem baru', 'score': 5}
Correct: E
Explanation: Leadership: menjadi mentor untuk membantu transformasi digital.

### TWK / Bhinneka Tunggal Ika

Question: Bhinneka Tunggal Ika berasal dari kitab...
A. Bharatayuddha
B. Sutasoma
C. Pararaton
D. Arjunawiwaha
E. Nagarakretagama
Correct: B
Explanation: Bhinneka Tunggal Ika berasal dari kitab Sutasoma karya Mpu Tantular.

### TWK / Hankam

Question: Sasaran dan tujuan dari pembangunan nasional jangka panjang adalah ...
A. Terciptanya masyarakat Indonesia yang mutu dan mandiri
B. Menciptakan stabilitas nasional yang stabil dan dinamis
C. Mewujudkan masyarakat yang adil dan makmur
D. Melaksanakan pembangunan di segala bidang
E. Meningkatkan pertahanan negara
Correct: A
Explanation: Pembahasan mengikuti materi TWK - Hankam.

### TWK / Pancasila

Question: Sila pertama Pancasila berbunyi...
A. Ketuhanan Yang Maha Esa
B. Kerakyatan yang dipimpin oleh hikmat kebijaksanaan
C. Keadilan sosial bagi seluruh rakyat Indonesia
D. Kemanusiaan yang adil dan beradab
E. Persatuan Indonesia
Correct: A
Explanation: Sila pertama: Ketuhanan Yang Maha Esa.

### TWK / Sejarah Indonesia

Question: Peletak dasar kerajaan Demak adalah
A. Raden Patah
B. Dipati Unus
C. Trenggana
D. Hadiwijaya
E. Sutawijaya 60
Correct: A
Explanation: Pembahasan mengikuti materi TWK - Sejarah Indonesia.

### TWK / UUD 1945

Question: UUD 1945 disahkan oleh PPKI pada tanggal...
A. 17 Agustus 1945
B. 29 Mei 1945
C. 1 Juni 1945
D. 18 Agustus 1945
E. 22 Juni 1945
Correct: D
Explanation: UUD 1945 disahkan oleh PPKI pada 18 Agustus 1945.
