#!/usr/bin/env python3
import json, re, sys, time
from pathlib import Path
import pymysql

DRY = '--apply' not in sys.argv

BACKUP_DIR = Path('/root/cpns/backups')
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

def norm(s): return (s or '').lower()

def classify(row):
    t = norm(row['question_text'])
    opts = row['options'] if isinstance(row['options'], list) else json.loads(row['options'])
    opt_text = ' '.join([o.get('text','') if isinstance(o,dict) else str(o) for o in opts]).lower()
    alltxt = t + ' ' + opt_text

    # TIU verbal
    if 'antonim' in alltxt or 'lawan kata' in alltxt or '> <' in row['question_text']:
        return 'TIU', 'Antonim', 'antonim marker'
    if 'sinonim' in alltxt or 'persamaan kata' in alltxt or re.match(r'^[A-ZÀ-Ü][A-ZÀ-Ü\s-]{3,}\s*=\s*_+', row['question_text']):
        return 'TIU', 'Sinonim', 'sinonim marker'
    if re.search(r'\b(silogisme|semua |sebagian |tidak ada |kesimpulan)\b', t) and not re.search(r'pasal|uud|pancasila', t):
        return 'TIU', 'Silogisme', 'logic marker'
    if (':' in row['question_text'] and not re.search(r'\d\s*:', row['question_text']) and not re.search(r'pasal|uud|pancasila|presiden|menteri|undang', t)) or 'analogi' in alltxt or 'padanan kata' in alltxt:
        return 'TIU', 'Analogi', 'analogy marker'

    # TIU numeric
    if re.match(r'^\s*[-\d¼½¾,.;/\s]+(\.\.\.|…|\?)?', row['question_text']) and re.search(r'\d', row['question_text']):
        return 'TIU', 'Deret Angka', 'number-sequence marker'
    math_words = r'\b(berapa|hitung|nilai dari|rata-rata|perbandingan|persentase|persen|luas|volume|tabung|umur|usia|jarak|kecepatan|km/jam|kg|liter|harga|membeli|menjual|untung|rugi|campuran|himpunan|penyelesaian|bilangan|pecahan|skala|median)\b'
    math_symbols = re.search(r'(\d\s*[+×x*/:=]\s*\d|x\s*[=<>]|y\s*[=<>]|\d+\s*/\s*\d+)', row['question_text'])
    if (re.search(math_words, t) or math_symbols) and not re.search(r'pasal|uud 1945|tahun 1945|proklamasi|bpupki|pancasila|mewujudkan indonesia', t):
        return 'TIU', 'Matematika Dasar', 'math marker'

    # TKP scenario
    if re.search(r'\b(anda|saya)\b', t) and re.search(r'\b(sikap|lakukan|akan|memilih|rekan|atasan|kantor|pegawai|pelayanan|cuti|deadline|rapat|pelanggan|masyarakat|kerja|tugas)\b', alltxt):
        if re.search(r'jujur|korup|suap|curang|presensi|integritas', alltxt): return 'TKP','Integritas','tkp integrity'
        if re.search(r'pelanggan|masyarakat|layanan|pelayanan|publik', alltxt): return 'TKP','Pelayanan Publik','tkp public service'
        if re.search(r'rekan|tim|atasan|rapat|kerja sama|koordinasi', alltxt): return 'TKP','Jejaring Kerja','tkp networking'
        if re.search(r'teknologi|komputer|aplikasi|digital|internet', alltxt): return 'TKP','Teknologi Informasi','tkp tech'
        if re.search(r'budaya|suku|agama|tetangga|lingkungan', alltxt): return 'TKP','Sosial Budaya','tkp social'
        if re.search(r'radikal|teror|intoleran', alltxt): return 'TKP','Anti Radikalisme','tkp anti radical'
        return 'TKP','Profesionalisme','tkp scenario'

    # TWK markers
    if re.search(r'pancasila|sila ke|garuda|dasar negara|ideologi', alltxt): return 'TWK','Pancasila','twk pancasila'
    if re.search(r'uud|undang-undang dasar|pasal|mpr|dpr|dpd|mk\b|ma\b|konstitusi|piagam jakarta|pemerintah daerah|otonomi|presiden|menteri', alltxt): return 'TWK','UUD 1945','twk constitution'
    if re.search(r'proklamasi|bpupki|ppki|sumpah pemuda|voc|kerajaan|majapahit|sriwijaya|kutai|diponegoro|jepang|belanda|kemerdekaan|reformasi|soeharto|soekarno|hatta', alltxt): return 'TWK','Sejarah Indonesia','twk history'
    if re.search(r'tni|polri|hankam|pertahanan|keamanan|militer|bela negara|kopassus|angkatan darat|angkatan laut|angkatan udara', alltxt): return 'TWK','Hankam','twk hankam'
    if re.search(r'bhinneka|tunggal ika|suku|budaya|toleransi|keberagaman|persatuan|gotong royong', alltxt): return 'TWK','Bhinneka Tunggal Ika','twk bhinneka'

    if re.search(r'kalimat|paragraf|wacana|kata ganti|makna kata|bacaan|gagasan utama|inti dari kalimat', alltxt):
        return 'TIU','Pemahaman Bacaan','reading marker'
    return row['section'], row['topic'], ''

conn=pymysql.connect(host='localhost', user='root', database='cpns', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor, autocommit=False)
with conn.cursor() as cur:
    cur.execute('SELECT * FROM questions')
    rows=cur.fetchall()
updates=[]
for r in rows:
    ns, nt, reason = classify(r)
    if (ns,nt)==(r['section'],r['topic']) or not reason:
        continue
    # Conservative mode: fix obvious cross-section pollution only.
    # Avoid noisy same-section topic reshuffles (e.g. TKP Integritas vs Jejaring) unless manually reviewed.
    if ns == r['section']:
        continue
    # Keep hand-authored early rows stable unless they clearly contain extraction artifacts/mismatched markers.
    updates.append({**r, 'new_section':ns, 'new_topic':nt, 'reason':reason})

backup = BACKUP_DIR / f'recategorized_questions_{time.strftime("%Y%m%d_%H%M%S")}.json'
with open(backup,'w',encoding='utf-8') as f: json.dump(updates,f,ensure_ascii=False,indent=2,default=str)
print(f'dry_run={DRY} candidates={len(updates)} backup={backup}')
from collections import Counter
for (old,new), cnt in Counter(((u['section']+'/'+u['topic'], u['new_section']+'/'+u['new_topic']) for u in updates)).most_common(25):
    print(f'{cnt:4d} {old} -> {new}')
if not DRY:
    with conn.cursor() as cur:
        for u in updates:
            cur.execute('UPDATE questions SET section=%s, topic=%s WHERE id=%s', (u['new_section'], u['new_topic'], u['id']))
    conn.commit()
    print(f'applied={len(updates)}')
else:
    conn.rollback()
conn.close()
