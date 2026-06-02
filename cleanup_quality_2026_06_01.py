#!/usr/bin/env python3
"""Quality cleanup for CPNS question bank: remove user-facing source/PDF artifacts and recategorize obvious TKP scenarios."""
import json
import re
from pathlib import Path
import pymysql

BACKUP = Path('/root/cpns/backups/question_quality_cleanup_2026_06_01.json')
BACKUP.parent.mkdir(parents=True, exist_ok=True)

conn = pymysql.connect(host='localhost', user='root', database='cpns', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
cur = conn.cursor()

cur.execute("""
SELECT * FROM questions
WHERE explanation LIKE '%PDF%'
   OR explanation LIKE '%Kunci jawaban%'
   OR explanation LIKE '%http%'
   OR explanation LIKE '%www.%'
   OR (
        section IN ('TIU','TWK') AND (
          question_text LIKE 'Anda %'
          OR question_text LIKE '% sikap Anda%'
          OR question_text LIKE '%Sikap saya%'
          OR question_text LIKE '%Respon saya%'
          OR question_text LIKE '%yang Anda lakukan%'
          OR question_text LIKE '%anda akan%'
          OR question_text LIKE '%Anda akan%'
          OR question_text LIKE '%rekan kerja%'
          OR question_text LIKE '%atasan%'
        )
      )
ORDER BY id
""")
rows = cur.fetchall()
BACKUP.write_text(json.dumps(rows, ensure_ascii=False, indent=2, default=str), encoding='utf-8')
print(f'backup_rows={len(rows)} path={BACKUP}')

# Clean explanation/source artifacts. Keep explanations user-facing and neutral.
cur.execute("""
UPDATE questions
SET explanation = CONCAT('Pembahasan mengikuti materi ', section, ' - ', topic, '.')
WHERE explanation LIKE '%PDF%'
   OR explanation LIKE '%Kunci jawaban%'
   OR explanation LIKE '%http%'
   OR explanation LIKE '%www.%'
""")
print('cleaned_explanations=', cur.rowcount)

# Recategorize obvious situational judgment questions accidentally imported under TIU/TWK.
cur.execute("""
UPDATE questions
SET section = 'TKP',
    topic = CASE
      WHEN question_text LIKE '%korupsi%' OR question_text LIKE '%rahasia%' OR question_text LIKE '%narkoba%' OR question_text LIKE '%lapor%' THEN 'Integritas'
      WHEN question_text LIKE '%warga%' OR question_text LIKE '%pelayanan%' OR question_text LIKE '%KTP%' OR question_text LIKE '%keluhan%' THEN 'Pelayanan Publik'
      WHEN question_text LIKE '%tim%' OR question_text LIKE '%rekan%' OR question_text LIKE '%atasan%' OR question_text LIKE '%bawahan%' THEN 'Jejaring Kerja'
      WHEN question_text LIKE '%digital%' OR question_text LIKE '%program%' OR question_text LIKE '%data%' THEN 'Teknologi Informasi'
      ELSE 'Profesionalisme'
    END
WHERE section IN ('TIU','TWK') AND (
      question_text LIKE 'Anda %'
      OR question_text LIKE '% sikap Anda%'
      OR question_text LIKE '%Sikap saya%'
      OR question_text LIKE '%Respon saya%'
      OR question_text LIKE '%yang Anda lakukan%'
      OR question_text LIKE '%anda akan%'
      OR question_text LIKE '%Anda akan%'
      OR question_text LIKE '%rekan kerja%'
      OR question_text LIKE '%atasan%'
)
""")
print('recategorized_tkp_like=', cur.rowcount)

conn.commit()
cur.close(); conn.close()
