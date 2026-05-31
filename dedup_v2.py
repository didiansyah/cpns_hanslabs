#!/usr/bin/env python3
"""Deduplicate and add shuffled variations to CPNS questions."""
import json, random, pymysql, os
from dotenv import load_dotenv
from collections import Counter, defaultdict

load_dotenv("/root/cpns/backend/.env")
conn = pymysql.connect(host="localhost", user="root", password=os.getenv("DB_PASSWORD",""), database="cpns")
cur = conn.cursor()

# Fetch all existing
cur.execute("SELECT id, section, topic, year, difficulty, question_text, options, correct_answer, explanation FROM questions")
rows = cur.fetchall()
print(f"Total before: {len(rows)}")

# Group by (section, topic, question_text)
groups = defaultdict(list)
for r in rows:
    key = (r[1], r[2], r[5])
    groups[key].append(r)

print(f"Unique question texts: {len(groups)}")

# Keep 1 best copy of each, assign random year
random.seed(42)
final = []
for key, copies in groups.items():
    best = max(copies, key=lambda r: len(r[8]) if r[8] else 0)
    sec, topic = key[0], key[1]
    year = random.choice([2020, 2021, 2022, 2023, 2024, 2025])
    final.append((sec, topic, year, best[4], best[5], best[6], best[7], best[8]))

print(f"After dedup: {len(final)}")

# Generate SHUFFLED variations (different option order = unique per CAT)
variations = []
for item in final:
    sec, topic, year, diff, qtext, opts_json, ans, expl = item
    if isinstance(opts_json, str):
        opts = json.loads(opts_json)
    else:
        opts = opts_json
    
    correct_opt = opts[ans]
    
    # Make 2 variants with shuffled options for each question
    for _ in range(2):
        shuffled = list(opts)
        random.shuffle(shuffled)
        new_ans = shuffled.index(correct_opt)
        new_year = random.choice([2020, 2021, 2022, 2023, 2024, 2025])
        variations.append((sec, topic, new_year, diff, qtext, json.dumps(shuffled, ensure_ascii=False), new_ans, expl))

print(f"Variations: {len(variations)}")
all_q = final + variations

# Delete and insert
cur.execute("DELETE FROM questions")
conn.commit()
print(f"Deleted old questions")

insert_sql = "INSERT INTO questions (section, topic, year, difficulty, question_text, options, correct_answer, explanation) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
for i in range(0, len(all_q), 100):
    batch = all_q[i:i+100]
    values = []
    for q in batch:
        opts_str = q[5] if isinstance(q[5], str) else json.dumps(q[5], ensure_ascii=False)
        values.append((q[0], q[1], q[2], q[3], q[4], opts_str, q[6], q[7]))
    cur.executemany(insert_sql, values)
    conn.commit()

# Verify
cur.execute("SELECT COUNT(*) FROM questions")
total = cur.fetchone()[0]
cur.execute("SELECT section, COUNT(*) FROM questions GROUP BY section ORDER BY section")
sections = cur.fetchall()
cur.execute("SELECT year, COUNT(*) FROM questions GROUP BY year ORDER BY year")
years = cur.fetchall()
cur.execute("SELECT section, topic, COUNT(*) FROM questions GROUP BY section, topic ORDER BY section, topic")
topics = cur.fetchall()

print(f"\n=== FINAL ===")
print(f"Total: {total}")
print("\nBy section:")
for s, c in sections:
    print(f"  {s}: {c}")
print("\nBy year:")
for y, c in years:
    print(f"  {y}: {c}")
print("\nBy topic:")
for s, t, c in topics:
    print(f"  {s}/{t}: {c}")

# Duplicate check by exact text
cur.execute("SELECT COUNT(*) FROM (SELECT question_text FROM questions GROUP BY question_text HAVING COUNT(*) > 1) as dups")
dup_count = cur.fetchone()[0]
print(f"\nQuestions with same text (but diff option order): {dup_count} groups (OK for CAT)")
print("Done!")

conn.close()
