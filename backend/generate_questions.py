#!/usr/bin/env python3
"""Generate CPNS practice questions and insert into database."""
import json
import random
import pymysql

DB_CONFIG = {"host": "localhost", "user": "root", "database": "cpns", "charset": "utf8mb4"}

# ============================================================
# TKP QUESTIONS — Pelayanan Publik
# ============================================================
TKP_PELAYANAN_PUBLIK = [
    {
        "question_text": "Anda sedang melayani masyarakat di loket pelayanan. Seorang warga datang dengan keluhan yang sama untuk ketiga kalinya karena masalahnya belum terselesaikan. Sikap Anda adalah...",
        "options": [
            "Meminta maaf dan segera menyelesaikan masalah dengan koordinasi ke unit terkait",
            "Menjelaskan bahwa itu bukan bidang Anda dan mengarahkannya ke unit lain",
            "Melayani dengan sabar dan memberikan solusi konkret beserta estimasi waktu penyelesaian",
            "Mencatat keluhan dan menjanjikan akan ditindaklanjuti tanpa kejelasan waktu",
            "Meminta warga untuk mengisi form pengaduan resmi"
        ],
        "correct_answer": 2,
        "explanation": "Pelayanan prima memerlukan sikap proaktif, empati, dan memberikan solusi konkret dengan kejelasan waktu. Opsi C menunjukkan kesabaran, solusi konkret, dan transparansi waktu."
    },
    {
        "question_text": "Seorang warga mengeluh karena proses perizinan sudah berjalan 3 bulan tanpa kejelasan. Sebagai petugas pelayanan, Anda akan...",
        "options": [
            "Menjelaskan bahwa proses birokrasi memang membutuhkan waktu",
            "Mengecek status perizinan dan memberikan informasi progres terkini kepada warga",
            "Mengarahkan warga untuk menghubungi atasan Anda",
            "Membuat surat pengantar untuk mempercepat proses",
            "Menyarankan warga untuk menggunakan jalur percepatan khusus"
        ],
        "correct_answer": 1,
        "explanation": "Petugas pelayanan harus proaktif memberikan informasi dan transparansi. Mengecek status dan memberikan info terkini adalah bentuk pelayanan yang bertanggung jawab."
    },
    {
        "question_text": "Dalam melayani masyarakat, Anda menemukan dokumen yang kurang lengkap. Sikap terbaik adalah...",
        "options": [
            "Menolak dokumen dan meminta warga melengkapi terlebih dahulu",
            "Memberikan daftar dokumen yang kurang dan membantu proses pelengkapannya",
            "Menerima dokumen seadanya dan memprosesnya",
            "Meminta warga untuk datang kembali lain waktu",
            "Membantu mengisi kekurangan dokumen atas nama warga"
        ],
        "correct_answer": 1,
        "explanation": "Pelayanan prima melibatkan edukasi dan bimbingan kepada warga. Memberikan daftar lengkap dan membantu proses pelengkapan adalah sikap profesional."
    },
    {
        "question_text": "Seorang lansia datang ke kantor Anda untuk mengurus surat keterangan, namun ia kesulitan mengisi formulir. Yang Anda lakukan adalah...",
        "options": [
            "Meminta keluarga lansia yang mengurus",
            "Mengisi formulir untuk lansia tersebut dengan data yang diberikan",
            "Membiarkan lansia mengisi sendiri sambil menunggu giliran",
            "Mengarahkan ke petugas lain yang lebih berpengalaman",
            "Menolak karena lansia tidak bisa mengisi formulir sendiri"
        ],
        "correct_answer": 1,
        "explanation": "Melayani dengan empati dan membantu lansia yang kesulitan adalah bentuk pelayanan prima. Petugas harus proaktif membantu tanpa diminta."
    },
    {
        "question_text": "Anda mendapat keluhan dari masyarakat melalui media sosial tentang pelayanan yang lambat. Respons terbaik adalah...",
        "options": [
            "Mengabaikan karena bukan saluran resmi",
            "Membalas dengan permintaan maaf dan meminta kontak untuk ditindaklanjuti",
            "Menghapus komentar negatif tersebut",
            "Membalas dengan penjelasan panjang di kolom komentar",
            "Melaporkan akun tersebut ke admin media sosial"
        ],
        "correct_answer": 1,
        "explanation": "Keluhan melalui media sosial tetap harus ditanggapi dengan profesional. Meminta maaf dan menindaklanjuti secara pribadi menunjukkan responsivitas institusi."
    },
]

# ============================================================
# TKP QUESTIONS — Integritas
# ============================================================
TKP_INTEGRITAS = [
    {
        "question_text": "Anda mengetahui bahwa rekan kerja Anda menerima suap dari masyarakat untuk mempercepat proses pengurusan dokumen. Sikap Anda adalah...",
        "options": [
            "Melaporkan ke atasan atau unit pengawasan dengan bukti yang ada",
            "Menegur rekan tersebut secara pribadi",
            "Membiarkan karena itu urusan pribadi",
            "Ikut menerima suap karena sudah menjadi kebiasaan",
            "Mengancam akan melaporkan jika tidak diajak berbagi"
        ],
        "correct_answer": 0,
        "explanation": "Integritas menuntut kita untuk melawan korupsi. Melaporkan ke unit pengawasan adalah sikap yang benar sesuai prinsip integritas ASN."
    },
    {
        "question_text": "Atasan Anda meminta Anda untuk memanipulasi data laporan keuangan agar terlihat lebih baik. Anda akan...",
        "options": [
            "Menuruti permintaan atasan karena itu perintah",
            "Menolak dengan sopan dan menjelaskan konseksi hukumnya",
            "Melakukan sedikit manipulasi agar tidak mengecewakan atasan",
            "Mengundurkan diri dari pekerjaan",
            "Melaporkan atasan ke unit pengawasan"
        ],
        "correct_answer": 1,
        "explanation": "Menolak manipulasi data dengan sopan sambil menjelaskan konsekuensi hukum adalah sikap berintegritas. Kita harus tetap profesional tanpa melanggar etika."
    },
    {
        "question_text": "Anda menemukan dompet milik masyarakat yang tertinggal di ruang pelayanan. Tindakan Anda adalah...",
        "options": [
            "Mengambil dan menyimpannya karena tidak ada yang melihat",
            "Mengembalikan ke pemiliknya atau menyerahkan ke bagian kehilangan",
            "Membuka dompet untuk mencari identitas pemilik",
            "Menunggu pemiliknya mencari sendiri",
            "Menyerahkan ke rekan kerja untuk disimpan"
        ],
        "correct_answer": 1,
        "explanation": "Mengembalikan barang milik orang lain adalah sikap jujur yang mencerminkan integritas. Menyerahkan ke bagian kehilangan adalah prosedur yang benar."
    },
    {
        "question_text": "Seorang masyarakat menawarkan 'uang terima kasih' setelah Anda membantu menyelesaikan pengurusannya. Sikap Anda...",
        "options": [
            "Menerima karena itu bentuk terima kasih",
            "Menolak dengan sopan dan menjelaskan bahwa itu tidak diperbolehkan",
            "Menerima tapi melaporkan ke atasan",
            "Menolak kasar agar tidak ditawari lagi",
            "Menerima dan menyumbangkannya ke kas kantor"
        ],
        "correct_answer": 1,
        "explanation": "ASN dilarang menerima gratifikasi. Menolak dengan sopan sambil menjelaskan aturan adalah sikap berintegritas yang profesional."
    },
    {
        "question_text": "Anda diminta oleh teman untuk 'mengurus' dokumen perizinan di luar prosedur resmi karena ia kenal dekat dengan Anda. Sikap Anda...",
        "options": [
            "Membantu karena teman dekat",
            "Menolak dan mengarahkan ke prosedur resmi",
            "Membantu dengan catatan tidak melanggar aturan",
            "Mengarahkan ke petugas lain",
            "Menunda sampai teman mengurus sendiri"
        ],
        "correct_answer": 1,
        "explanation": "Integritas berarti memperlakukan semua orang sama tanpa memandang hubungan pribadi. Mengarahkan ke prosedur resmi adalah sikap yang benar."
    },
]

# ============================================================
# TKP QUESTIONS — Profesionalisme
# ============================================================
TKP_PROFESIONALISME = [
    {
        "question_text": "Anda mendapat tugas baru yang belum pernah Anda lakukan sebelumnya. Sikap profesional Anda adalah...",
        "options": [
            "Menolak tugas karena tidak sesuai bidang",
            "Belajar dan meminta bimbingan dari rekan yang lebih berpengalaman",
            "Mengerjakan asal-asalan karena tidak paham",
            "Mendelegasikan ke bawahan",
            "Menunggu instruksi lebih detail dari atasan"
        ],
        "correct_answer": 1,
        "explanation": "Profesionalisme meliputi kemauan belajar dan berkembang. Meminta bimbingan sambil tetap mengerjakan tugas menunjukkan sikap profesional."
    },
    {
        "question_text": "Anda melakukan kesalahan dalam penginputan data yang menyebabkan keterlambatan proses. Tindakan Anda...",
        "options": [
            "Menyalahkan sistem atau rekan kerja",
            "Mengakui kesalahan dan segera memperbaiki",
            "Menutupi kesalahan agar tidak ketahuan",
            "Menunggu atasan mengetahui sendiri",
            "Menginput data baru tanpa melaporkan kesalahan"
        ],
        "correct_answer": 1,
        "explanation": "Profesionalisme mencakup tanggung jawab. Mengakui kesalahan dan segera memperbaiki adalah sikap dewasa dan profesional."
    },
    {
        "question_text": "Rekan kerja Anda sering terlambat datang dan meninggalkan pekerjaan lebih awal. Sikap Anda...",
        "options": [
            "Ikut-ikutan karena merasa tidak adil",
            "Fokus pada kinerja sendiri dan memberikan contoh yang baik",
            "Melaporkan ke atasan",
            "Menegur rekan tersebut di depan umum",
            "Mengajak rekan untuk berdiskusi tentang kedisiplinan"
        ],
        "correct_answer": 1,
        "explanation": "Profesionalisme berarti fokus pada kinerja sendiri dan memberikan contoh positif. Sikap ini lebih efektif daripada mengkritik orang lain."
    },
    {
        "question_text": "Anda mendapat kritik dari masyarakat tentang cara Anda bekerja. Respons profesional Anda adalah...",
        "options": [
            "Merasa tersinggung dan membela diri",
            "Menerima kritik dengan terbuka dan memperbaiki kinerja",
            "Mengabaikan kritik tersebut",
            "Membalas kritik dengan menunjukkan kelebihan Anda",
            "Mengeluh ke rekan kerja tentang kritik tersebut"
        ],
        "correct_answer": 1,
        "explanation": "Profesionalisme mencakup kemampuan menerima kritik dengan terbuka dan menjadikannya motivasi untuk memperbaiki diri."
    },
    {
        "question_text": "Dalam rapat tim, Anda memiliki ide yang berbeda dengan mayoritas. Sikap profesional Anda...",
        "options": [
            "Diam saja karena takut dianggap berbeda",
            "Menyampaikan ide dengan argumen yang logis dan data pendukung",
            "Memaksakan pendapat karena yakin benar",
            "Mengikuti mayoritas tanpa memberikan masukan",
            "Walk out dari rapat karena merasa tidak dihargai"
        ],
        "correct_answer": 1,
        "explanation": "Profesionalisme berarti mampu menyampaikan pendapat dengan cara yang konstruktif, didukung data dan argumen logis."
    },
]

# ============================================================
# TKP QUESTIONS — Bela Negara
# ============================================================
TKP_BELA_NEGARA = [
    {
        "question_text": "Sebagai ASN, Anda melihat adanya upaya provokasi yang memecah belah persatuan di lingkungan kerja. Tindakan Anda...",
        "options": [
            "Ikut terprovokasi karena merasa benar",
            "Melaporkan ke pihak berwenang dan mengajak rekan untuk menjaga persatuan",
            "Mengabaikan karena bukan urusan Anda",
            "Meninggalkan lingkungan kerja tersebut",
            "Membalas provokasi dengan argumen yang lebih keras"
        ],
        "correct_answer": 1,
        "explanation": "Bela negara dalam konteks ASN adalah menjaga persatuan dan melaporkan ancaman terhadap keutuhan bangsa."
    },
    {
        "question_text": "Anda ditugaskan untuk bertugas di daerah terpencil yang jauh dari keluarga. Sikap Anda...",
        "options": [
            "Menolak karena tidak ingin jauh dari keluarga",
            "Menerima dengan penuh tanggung jawab sebagai bentuk pengabdian",
            "Menerima tapi terus mengeluh",
            "Mencari cara untuk dipindahkan",
            "Menerima asalkan ada tunjangan yang besar"
        ],
        "correct_answer": 1,
        "explanation": "Bela negara melalui ASN adalah siap ditugaskan di mana saja demi pelayanan kepada masyarakat dan negara."
    },
    {
        "question_text": "Dalam kegiatan upacara bendera, Anda melihat beberapa rekan tidak menghormati bendera dengan sikap yang tidak sopan. Tindakan Anda...",
        "options": [
            "Membiarkan karena itu urusan mereka",
            "Mengingatkan dengan sopan tentang pentingnya menghormati bendera",
            "Melaporkan ke atasan",
            "Mengabadikan untuk bukti",
            "Ikut tidak menghormati karena merasa tidak penting"
        ],
        "correct_answer": 1,
        "explanation": "Menghormati simbol negara adalah bentuk bela negara. Mengingatkan dengan sopan adalah tindakan yang tepat."
    },
    {
        "question_text": "Anda mengetahui ada rekan yang menyebarkan informasi negatif tentang Indonesia di media sosial. Sikap Anda...",
        "options": [
            "Mengabaikan karena itu hak pribadi",
            "Mengingatkan tentang dampak negatif dan pentingnya menjaga nama baik negara",
            "Ikut menyebarkan karena setuju",
            "Melaporkan ke polisi",
            "Memblokir akun rekan tersebut"
        ],
        "correct_answer": 1,
        "explanation": "Bela negara mencakup menjaga citra positif Indonesia. Mengingatkan rekan adalah tindakan yang tepat dan konstruktif."
    },
    {
        "question_text": "Sebagai ASN, Anda diminta untuk berpartisipasi dalam kegotongroyongan di lingkungan tempat tinggal. Sikap Anda...",
        "options": [
            "Menolak karena itu di luar jam kerja",
            "Berpartisipasi aktif sebagai wujud nilai kebersamaan",
            "Mengirimkan uang sebagai gantinya",
            "Hanya berpartisipasi jika ada pejabat yang hadir",
            "Menyuruh anggota keluarga untuk mewakili"
        ],
        "correct_answer": 1,
        "explanation": "Gotong royong adalah nilai luhur bangsa Indonesia. Partisipasi aktif ASN menunjukkan implementasi nilai bela negara."
    },
]

# ============================================================
# TKP QUESTIONS — Jejaring Kerja
# ============================================================
TKP_JEJARING_KERJA = [
    {
        "question_text": "Anda membutuhkan data dari instansi lain untuk menyelesaikan pekerjaan. Tindakan terbaik adalah...",
        "options": [
            "Meminta langsung ke individu di instansi tersebut",
            "Membuat surat permintaan resmi melalui jalur kelembagaan",
            "Mencari data sendiri meskipun membutuhkan waktu lama",
            "Menggunakan data lama yang sudah ada",
            "Meminta bantuan kenalan pribadi"
        ],
        "correct_answer": 1,
        "explanation": "Jejaring kerja profesional melalui jalur resmi kelembagaan memastikan data yang diperoleh valid dan dapat dipertanggungjawabkan."
    },
    {
        "question_text": "Dalam kerja sama antar instansi, terjadi perbedaan pendapat tentang pembagian tugas. Solusi terbaik adalah...",
        "options": [
            "Mempertahankan pendapat sendiri",
            "Melakukan musyawarah untuk mencapai mufakat dengan mempertimbangkan kepentingan bersama",
            "Mengalah demi menjaga hubungan",
            "Melaporkan ke atasan masing-masing",
            "Menarik diri dari kerja sama"
        ],
        "correct_answer": 1,
        "explanation": "Musyawarah mufakat adalah prinsip dasar dalam membangun jejaring kerja yang sehat dan produktif."
    },
    {
        "question_text": "Anda ditugaskan untuk berkolaborasi dengan instansi yang sebelumnya pernah konflik dengan instansi Anda. Sikap Anda...",
        "options": [
            "Menolak penugasan karena sejarah konflik",
            "Menerima dan fokus pada tujuan bersama tanpa membawa masalah lama",
            "Menerima tapi tetap waspada dan defensif",
            "Meminta rekan lain untuk menggantikan",
            "Menerima tapi mencari kelemahan instansi tersebut"
        ],
        "correct_answer": 1,
        "explanation": "Profesionalisme dalam jejaring kerja berarti mampu memisahkan masalah pribadi/kelembagaan lama dengan tujuan bersama saat ini."
    },
    {
        "question_text": "Anda menghadiri forum kerja sama antar daerah. Cara terbaik untuk membangun jejaring adalah...",
        "options": [
            "Hanya berbicara dengan pejabat setingkat",
            "Aktif berdiskusi dan berkenalan dengan berbagai pihak tanpa memandang jabatan",
            "Hanya datang dan diam saja",
            "Fokus pada materi presentasi tanpa berinteraksi",
            "Membagikan kartu nama sebanyak mungkin"
        ],
        "correct_answer": 1,
        "explanation": "Jejaring kerja yang efektif dibangun melalui interaksi aktif dan tulus dengan semua pihak tanpa memandang status."
    },
    {
        "question_text": "Rekan dari instansi lain meminta bantuan di luar jam kerja untuk keperluan tugas. Sikap Anda...",
        "options": [
            "Menolak karena di luar jam kerja",
            "Membantu sejauh kemampuan tanpa mengorbankan kewajiban utama",
            "Membantu tapi meminta imbalan",
            "Mengabaikan pesan tersebut",
            "Membantu dengan mengorbankan waktu istirahat sepenuhnya"
        ],
        "correct_answer": 1,
        "explanation": "Jejaring kerja yang baik melibatkan saling membantu dengan batasan yang wajar dan profesional."
    },
]

# ============================================================
# TKP QUESTIONS — Anti Radikalisme
# ============================================================
TKP_ANTI_RADIKALISME = [
    {
        "question_text": "Anda mengetahui ada rekan kerja yang mengikuti kelompok dengan paham radikal. Tindakan Anda...",
        "options": [
            "Mengabaikan karena itu urusan pribadi",
            "Melaporkan ke unit keamanan internal dan tetap menjaga hubungan baik",
            "Langsung memutus hubungan pertemanan",
            "Mengikuti kelompok tersebut untuk memahami",
            "Menyebarkan informasi tentang rekan tersebut"
        ],
        "correct_answer": 1,
        "explanation": "Anti radikalisme memerlukan kewaspadaan. Melaporkan ke pihak berwenang sambil tetap menjaga hubungan adalah sikap yang tepat."
    },
    {
        "question_text": "Di media sosial, Anda melihat konten yang mengajak untuk melakukan tindakan kekerasan atas nama agama. Respons Anda...",
        "options": [
            "Membagikan agar orang lain waspada",
            "Melaporkan konten tersebut dan tidak ikut menyebarkan",
            "Mengabaikan karena bukan urusan Anda",
            "Membalas dengan komentar yang memancing",
            "Memblokir akun tersebut"
        ],
        "correct_answer": 1,
        "explanation": "Melaporkan konten radikal adalah tindakan pencegahan yang tepat. Tidak menyebarkan mencegah penyebaran paham radikal."
    },
    {
        "question_text": "Seorang teman mengajak Anda untuk bergabung dengan organisasi yang mengajarkan intoleransi. Sikap Anda...",
        "options": [
            "Bergabung untuk mengetahui lebih dalam",
            "Menolak dengan tegas dan menjelaskan pentingnya toleransi",
            "Menolak tanpa penjelasan",
            "Mengajak teman untuk berdiskusi tentang bahaya intoleransi",
            "Mengabaikan ajakan tersebut"
        ],
        "correct_answer": 1,
        "explanation": "Menolak dengan tegas sambil menjelaskan nilai toleransi adalah sikap anti radikalisme yang konstruktif."
    },
    {
        "question_text": "Anda mendengar ceramah yang mengandung ujaran kebencian terhadap kelompok tertentu. Tindakan Anda...",
        "options": [
            "Mendengarkan karena itu hak berpendapat",
            "Meninggalkan tempat dan melaporkan ke pihak berwenang",
            "Merekam untuk dijadikan bukti",
            "Mendengarkan tapi tidak percaya",
            "Membantah langsung di tempat"
        ],
        "correct_answer": 1,
        "explanation": "Anti radikalisme berarti tidak memberikan ruang untuk ujaran kebencian. Melaporkan adalah tindakan yang tepat."
    },
    {
        "question_text": "Anda diminta untuk memberikan materi tentang Pancasila kepada generasi muda. Pendekatan terbaik adalah...",
        "options": [
            "Memberikan materi secara kaku dan formal",
            "Menggunakan pendekatan dialogis dengan contoh kehidupan sehari-hari",
            "Hanya membacakan teks Pancasila",
            "Memutar video tentang sejarah Pancasila",
            "Menghafalkan butir-butir Pancasila"
        ],
        "correct_answer": 1,
        "explanation": "Pendekatan dialogis dengan contoh konkret lebih efektif untuk menanamkan nilai Pancasila dan mencegah radikalisme."
    },
]

# ============================================================
# TKP QUESTIONS — Sosial Budaya
# ============================================================
TKP_SOSIAL_BUDAYA = [
    {
        "question_text": "Anda bekerja dengan rekan dari suku dan budaya yang berbeda. Sikap terbaik adalah...",
        "options": [
            "Hanya bergaul dengan rekan yang satu suku",
            "Menghargai perbedaan dan membangun kerja sama yang harmonis",
            "Memaksa rekan untuk mengikuti budaya Anda",
            "Menghindari interaksi untuk menghindari konflik",
            "Hanya berinteraksi dalam urusan pekerjaan"
        ],
        "correct_answer": 1,
        "explanation": "Keberagaman budaya adalah kekuatan bangsa. Menghargai perbedaan dan membangun kerja sama adalah sikap yang mencerminkan Bhinneka Tunggal Ika."
    },
    {
        "question_text": "Dalam pelayanan, Anda menemukan masyarakat dengan adat istiadat yang berbeda dengan Anda. Sikap Anda...",
        "options": [
            "Memperlakukan sama tanpa mempedulikan adat",
            "Menghormati adat istiadat mereka sambil tetap profesional dalam pelayanan",
            "Meminta mereka mengikuti prosedur yang berlaku tanpa pengecualian",
            "Mengkhususkan pelayanan berdasarkan adat",
            "Mengabaikan adat istiadat mereka"
        ],
        "correct_answer": 1,
        "explanation": "Pelayanan yang baik menghormati keberagaman budaya sambil tetap menjalankan prosedur secara profesional."
    },
    {
        "question_text": "Anda diundang untuk menghadiri upacara adat dari komunitas tertentu. Sikap Anda...",
        "options": [
            "Menolak karena tidak sesuai dengan budaya Anda",
            "Menghadiri dengan penuh penghormatan dan mengikuti prosesi yang berlaku",
            "Menghadiri tapi tidak mengikuti prosesinya",
            "Menghadiri dan mengkritik adat tersebut",
            "Hanya menghadiri jika ada pejabat lain yang hadir"
        ],
        "correct_answer": 1,
        "explanation": "Menghadiri dan menghormati upacara adat komunitas lain adalah wujud nyata toleransi dan penghargaan terhadap keberagaman."
    },
    {
        "question_text": "Seorang masyarakat datang dengan pakaian adat untuk mengurus dokumen. Sikap Anda...",
        "options": [
            "Menolak karena tidak sesuai dress code",
            "Melayani dengan baik tanpa memandang penampilan",
            "Meminta mereka ganti pakaian biasa",
            "Melayani tapi dengan sikap yang berbeda",
            "Mengarahkan ke petugas lain"
        ],
        "correct_answer": 1,
        "explanation": "Pelayanan prima tidak memandang penampilan atau pakaian. Semua warga berhak mendapat pelayanan yang sama."
    },
    {
        "question_text": "Anda mengetahui ada tradisi lokal yang bertentangan dengan peraturan nasional. Sikap Anda...",
        "options": [
            "Memaksakan peraturan nasional tanpa kompromi",
            "Mencari jalan tengah melalui dialog dengan tokoh masyarakat setempat",
            "Mengabaikan tradisi tersebut",
            "Melaporkan ke pihak berwenang",
            "Mendukung tradisi meskipun bertentangan"
        ],
        "correct_answer": 1,
        "explanation": "Penyelesaian konflik antara tradisi dan regulasi memerlukan dialog dan musyawarah dengan para pemangku kepentingan."
    },
]

# ============================================================
# TKP QUESTIONS — Teknologi Informasi
# ============================================================
TKP_TEKNOLOGI_INFORMASI = [
    {
        "question_text": "Anda menerima email yang meminta data pribadi dan password Anda dengan alasan verifikasi sistem. Tindakan Anda...",
        "options": [
            "Langsung memberikan data karena terlihat resmi",
            "Mengabaikan dan melaporkan email tersebut sebagai phishing",
            "Membalas untuk memastikan kebenarannya",
            "Meneruskan ke rekan kerja untuk diminta pendapat",
            "Memberikan data palsu"
        ],
        "correct_answer": 1,
        "explanation": "Email phishing adalah ancaman keamanan siber. Mengabaikan dan melaporkan adalah tindakan yang tepat untuk melindungi data."
    },
    {
        "question_text": "Anda diminta untuk menggunakan sistem informasi baru di kantor. Sikap Anda...",
        "options": [
            "Menolak karena sudah nyaman dengan sistem lama",
            "Mempelajari sistem baru dengan antusias dan meminta pelatihan jika diperlukan",
            "Menggunakan sistem lama secara diam-diam",
            "Menunggu rekan lain menggunakan dulu",
            "Mengeluh kepada atasan tentang perubahan tersebut"
        ],
        "correct_answer": 1,
        "explanation": "ASN harus adaptif terhadap perkembangan teknologi. Mempelajari sistem baru dengan antusias menunjukkan profesionalisme."
    },
    {
        "question_text": "Anda menemukan celah keamanan dalam sistem informasi kantor. Tindakan Anda...",
        "options": [
            "Memanfaatkan celah tersebut untuk kepentingan pribadi",
            "Melaporkan ke tim IT untuk segera diperbaiki",
            "Mengabaikan karena bukan bidang Anda",
            "Membagikan informasi tentang celah tersebut",
            "Mencoba memperbaiki sendiri"
        ],
        "correct_answer": 1,
        "explanation": "Menemukan celah keamanan harus dilaporkan ke tim IT. Ini adalah tanggung jawab bersama untuk menjaga keamanan data."
    },
    {
        "question_text": "Anda diminta untuk mempresentasikan data menggunakan aplikasi presentasi. Sikap Anda...",
        "options": [
            "Meminta rekan lain untuk membuatkan",
            "Membuat presentasi sendiri dengan desain yang menarik dan data yang akurat",
            "Menggunakan template lama tanpa perubahan",
            "Menolak karena tidak bisa menggunakan aplikasi",
            "Membaca langsung dari dokumen tanpa presentasi"
        ],
        "correct_answer": 1,
        "explanation": "Kemampuan menggunakan teknologi presentasi adalah keterampilan dasar ASN modern. Membuat presentasi yang baik menunjukkan profesionalisme."
    },
    {
        "question_text": "Anda mendapat tugas untuk mengelola data masyarakat dalam sistem digital. Sikap terkait keamanan data adalah...",
        "options": [
            "Menyimpan data di flashdisk untuk kemudahan akses",
            "Memastikan data terenkripsi dan hanya dapat diakses oleh pihak berwenang",
            "Membagikan akses data ke semua rekan kerja",
            "Mencetak semua data untuk cadangan",
            "Menyimpan data di email pribadi"
        ],
        "correct_answer": 1,
        "explanation": "Keamanan data masyarakat adalah prioritas. Data harus terenkripsi dan hanya dapat diakses oleh pihak yang berwenang."
    },
]

# ============================================================
# TIU QUESTIONS — Sinonim
# ============================================================
TIU_SINONIM = [
    {"question_text": "Sinonim dari kata 'ABSTRAK' adalah...", "options": ["Nyata", "Konkret", "Imajiner", "Tidak berwujud", "Riil"], "correct_answer": 3, "explanation": "Abstrak berarti tidak berwujud atau tidak dapat dilihat secara fisika. Sinonimnya adalah tidak berwujud."},
    {"question_text": "Sinonim dari kata 'AKOMODATIF' adalah...", "options": ["Kaku", "Tegas", "Fleksibel", "Sulit", "Tegas"], "correct_answer": 2, "explanation": "Akomodatif berarti mudah menyesuaikan diri atau fleksibel."},
    {"question_text": "Sinonim dari kata 'ADAPTIF' adalah...", "options": ["Kaku", "Menyesuaikan", "Menolak", "Menghindari", "Mempersulit"], "correct_answer": 1, "explanation": "Adaptif berarti mampu menyesuaikan diri dengan lingkungan atau keadaan."},
    {"question_text": "Sinonim dari kata 'KONTEMPLASI' adalah...", "options": ["Tindakan", "Perenungan", "Keputusan", "Pelaksanaan", "Pergerakan"], "correct_answer": 1, "explanation": "Kontemplasi berarti perenungan atau meditasi mendalam."},
    {"question_text": "Sinonim dari kata 'LEGISLASI' adalah...", "options": ["Eksekusi", "Perundang-undangan", "Peradilan", "Pengawasan", "Pemerintahan"], "correct_answer": 1, "explanation": "Legislasi berarti proses pembuatan undang-undang atau perundang-undangan."},
    {"question_text": "Sinonim dari kata 'DEGRADASI' adalah...", "options": ["Peningkatan", "Penurunan", "Perbaikan", "Pemeliharaan", "Penguatan"], "correct_answer": 1, "explanation": "Degradasi berarti penurunan kualitas atau mutu."},
    {"question_text": "Sinonim dari kata 'ESKALASI' adalah...", "options": ["Penurunan", "Peningkatan", "Penghentian", "Pengurangan", "Pelestarian"], "correct_answer": 1, "explanation": "Eskalasi berarti peningkatan atau perluasan secara bertahap."},
    {"question_text": "Sinonim dari kata 'KONSENSUS' adalah...", "options": ["Pertentangan", "Kesepakatan", "Perdebatan", "Perpecahan", "Penolakan"], "correct_answer": 1, "explanation": "Konsensus berarti kesepakatan bersama atau mufakat."},
    {"question_text": "Sinonim dari kata 'PROVOKASI' adalah...", "options": ["Perdamaian", "Hasutan", "Mediasi", "Negosiasi", "Kompromi"], "correct_answer": 1, "explanation": "Provokasi berarti hasutan atau ajakan untuk melakukan sesuatu (biasanya negatif)."},
    {"question_text": "Sinonim dari kata 'NEUTRALITAS' adalah...", "options": ["Keberpihakan", "Ketidakberpihakan", "Agresivitas", "Partisipansi", "Dominasi"], "correct_answer": 1, "explanation": "Netralitas berarti tidak berpihak atau ketidakberpihakan."},
]

# ============================================================
# TIU QUESTIONS — Antonim
# ============================================================
TIU_ANTONIM = [
    {"question_text": "Antonim dari kata 'PROGRESIF' adalah...", "options": ["Maju", "Regressif", "Dinamis", "Aktif", "Inovatif"], "correct_answer": 1, "explanation": "Progresif berarti maju atau berkembang. Antonimnya adalah regressif (mundur)."},
    {"question_text": "Antonim dari kata 'OPTIMIS' adalah...", "options": ["Pesimis", "Realistis", "Pragmatis", "Idealis", "Dogmatis"], "correct_answer": 0, "explanation": "Optimis berarti berpandangan positif. Antonimnya adalah pesimis."},
    {"question_text": "Antonim dari kata 'GENERIK' adalah...", "options": ["Umum", "Spesifik", "Biasa", "Normal", "Standar"], "correct_answer": 1, "explanation": "Generik berarti umum atau tidak spesifik. Antonimnya adalah spesifik."},
    {"question_text": "Antonim dari kata 'ELASTIS' adalah...", "options": ["Fleksibel", "Kaku", "Lentur", "Ringan", "Halus"], "correct_answer": 1, "explanation": "Elastis berarti mudah dibentuk atau lentur. Antonimnya adalah kaku."},
    {"question_text": "Antonim dari kata 'DINAMIS' adalah...", "options": ["Aktif", "Statis", "Cepat", "Efisien", "Produktif"], "correct_answer": 1, "explanation": "Dinamis berarti bergerak atau berubah. Antonimnya adalah statis (diam/tidak berubah)."},
    {"question_text": "Antonim dari kata 'AUTONOM' adalah...", "options": ["Mandiri", "Tergantung", "Bebas", "Merdeka", "Berdaulat"], "correct_answer": 1, "explanation": "Autonom berarti mandiri atau berdiri sendiri. Antonimnya adalah tergantung."},
    {"question_text": "Antonim dari kata 'HARMONIS' adalah...", "options": ["Rukun", "Konflik", "Damai", "Serasi", "Seimbang"], "correct_answer": 1, "explanation": "Harmonis berarti serasi atau rukun. Antonimnya adalah konflik."},
    {"question_text": "Antonim dari kata 'RASIONAL' adalah...", "options": ["Logis", "Irasional", "Objektif", "Ilmiah", "Sistematis"], "correct_answer": 1, "explanation": "Rasional berarti masuk akal atau logis. Antonimnya adalah irasional."},
    {"question_text": "Antonim dari kata 'EDUKATIF' adalah...", "options": ["Mendidik", "Merusak", "Membangun", "Mengajar", "Melatih"], "correct_answer": 1, "explanation": "Edukatif berarti bersifat mendidik. Antonimnya adalah merusak (destruktif)."},
    {"question_text": "Antonim dari kata 'KONSTRUKTIF' adalah...", "options": ["Membangun", "Destruktif", "Positif", "Produktif", "Efektif"], "correct_answer": 1, "explanation": "Konstruktif berarti bersifat membangun. Antonimnya adalah destruktif (merusak)."},
]

# ============================================================
# TIU QUESTIONS — Matematika Dasar
# ============================================================
TIU_MATEMATIKA = [
    {"question_text": "Jika 3x + 7 = 22, maka nilai x adalah...", "options": ["3", "5", "7", "9", "11"], "correct_answer": 1, "explanation": "3x + 7 = 22 → 3x = 15 → x = 5"},
    {"question_text": "Sebuah toko memberikan diskon 20% untuk barang seharga Rp500.000. Harga setelah diskon adalah...", "options": ["Rp350.000", "Rp400.000", "Rp420.000", "Rp450.000", "Rp480.000"], "correct_answer": 1, "explanation": "Diskon 20% = 20/100 × 500.000 = 100.000. Harga setelah diskon = 500.000 - 100.000 = 400.000"},
    {"question_text": "Jika 2/3 dari sebuah bilangan adalah 24, maka bilangan tersebut adalah...", "options": ["32", "36", "48", "72", "16"], "correct_answer": 1, "explanation": "2/3 × x = 24 → x = 24 × 3/2 = 36"},
    {"question_text": "Hasil dari 15% × 800 adalah...", "options": ["100", "120", "140", "160", "180"], "correct_answer": 1, "explanation": "15% × 800 = 15/100 × 800 = 120"},
    {"question_text": "Jika harga sebuah barang naik 10% dari harga awal Rp200.000, maka harga sekarang adalah...", "options": ["Rp210.000", "Rp220.000", "Rp230.000", "Rp240.000", "Rp250.000"], "correct_answer": 1, "explanation": "Kenaikan 10% = 10/100 × 200.000 = 20.000. Harga sekarang = 200.000 + 20.000 = 220.000"},
    {"question_text": "Rata-rata dari 5 bilangan 10, 20, 30, 40, 50 adalah...", "options": ["25", "30", "35", "40", "45"], "correct_answer": 1, "explanation": "Rata-rata = (10+20+30+40+50)/5 = 150/5 = 30"},
    {"question_text": "Jika sebuah pesawat terbang dengan kecepatan 800 km/jam selama 2,5 jam, jarak yang ditempuh adalah...", "options": ["1.500 km", "1.800 km", "2.000 km", "2.200 km", "2.400 km"], "correct_answer": 2, "explanation": "Jarak = kecepatan × waktu = 800 × 2,5 = 2.000 km"},
    {"question_text": "Seorang pedagang membeli 100 kg beras seharga Rp1.000.000 dan menjualnya dengan harga Rp12.000/kg. Keuntungannya adalah...", "options": ["Rp100.000", "Rp150.000", "Rp200.000", "Rp250.000", "Rp300.000"], "correct_answer": 2, "explanation": "Penjualan = 100 × 12.000 = 1.200.000. Keuntungan = 1.200.000 - 1.000.000 = 200.000"},
    {"question_text": "Jika x = 4 dan y = 3, maka nilai dari x² + y² adalah...", "options": ["12", "16", "20", "25", "49"], "correct_answer": 3, "explanation": "x² + y² = 4² + 3² = 16 + 9 = 25"},
    {"question_text": "Sebuah lingkaran memiliki jari-jari 7 cm. Luas lingkaran tersebut adalah... (π = 22/7)", "options": ["144 cm²", "154 cm²", "164 cm²", "174 cm²", "184 cm²"], "correct_answer": 1, "explanation": "Luas = π × r² = 22/7 × 7² = 22/7 × 49 = 154 cm²"},
]


def insert_questions(section, topic, questions_list):
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    inserted = 0
    for q in questions_list:
        try:
            cursor.execute(
                "INSERT INTO questions (section, topic, year, difficulty, question_text, options, correct_answer, explanation) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (
                    section,
                    topic,
                    2024,
                    "sedang",
                    q["question_text"],
                    json.dumps(q["options"], ensure_ascii=False),
                    q["correct_answer"],
                    q["explanation"]
                )
            )
            inserted += 1
        except pymysql.err.IntegrityError:
            pass  # duplicate, skip
    
    conn.commit()
    cursor.close()
    conn.close()
    return inserted


if __name__ == "__main__":
    total = 0
    
    # TKP
    total += insert_questions("TKP", "Pelayanan Publik", TKP_PELAYANAN_PUBLIK)
    total += insert_questions("TKP", "Integritas", TKP_INTEGRITAS)
    total += insert_questions("TKP", "Profesionalisme", TKP_PROFESIONALISME)
    total += insert_questions("TKP", "Bela Negara", TKP_BELA_NEGARA)
    total += insert_questions("TKP", "Jejaring Kerja", TKP_JEJARING_KERJA)
    total += insert_questions("TKP", "Anti Radikalisme", TKP_ANTI_RADIKALISME)
    total += insert_questions("TKP", "Sosial Budaya", TKP_SOSIAL_BUDAYA)
    total += insert_questions("TKP", "Teknologi Informasi", TKP_TEKNOLOGI_INFORMASI)
    
    # TIU
    total += insert_questions("TIU", "Sinonim", TIU_SINONIM)
    total += insert_questions("TIU", "Antonim", TIU_ANTONIM)
    total += insert_questions("TIU", "Matematika Dasar", TIU_MATEMATIKA)
    
    print(f"✅ Inserted {total} new questions")
    
    # Show updated counts
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("SELECT section, COUNT(*) FROM questions GROUP BY section")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}")
    cursor.execute("SELECT COUNT(*) FROM questions")
    print(f"  Total: {cursor.fetchone()[0]}")
    cursor.close()
    conn.close()
