# CPNS Answer Legitimacy Audit Round 2 — 2026-06-01

Scope: second-pass 1:1 audit of remaining questions after first cleanup.
DB: MariaDB `cpns.questions`.

## Starting point
- Total before round 2: 1,866
- TIU: 589
- TKP: 614
- TWK: 663

## Audit method
- Split audit by section: TWK, TIU, TKP.
- Reviewed question text, options, answer key, explanation, and category.
- Only high-confidence issues were applied automatically. Subjective/minor wording was not changed.

## Round 2 actions

Main script:
- `/root/cpns/improve_answer_legitimacy_round2_2026_06_01.py`

Backups:
- `/root/cpns/backups/answer_legitimacy_round2_2026_06_01.json`
- `/root/cpns/backups/round2_final_dedup_header_2026_06_01.json`

Report:
- `/root/cpns/answer_legitimacy_round2_2026_06_01_report.json`

Applied:
- Objective answer-key fixes: 250
- TKP phrase-based best-answer fixes: 74
- Additional manual TKP key fixes after phrase misses: 13
- Recategorized obvious wrong-section rows: 20
- Deleted malformed/context-missing/off-product rows: 64 total
- Cleaned OCR/header fragments in question/options: 10 total
- Removed final duplicate: 1

## Final DB state
- Total: 1,802
- TWK: 643
- TIU: 546
- TKP: 613

## Final verification
- Exact duplicates: 0
- Missing explanations: 0
- Bad answer indices: 0
- Bad option count / bad JSON: 0
- Embedded `Jawaban:` / `Kunci Jawaban` artifacts in options: 0
- OCR headers (`BANK SOAL`, `TES INTELEGENSI`, etc.): 0
- User-facing source/PDF/generated artifacts: 0
- Dash placeholder options: 0
- Short missing-context references: 0
- API random TWK/TIU/TKP: OK
- API random does not leak `correct_answer` / `explanation`: OK

## Verdict
Round 2 makes the bank significantly more legitimate than before. Remaining caveat: TKP still contains many legacy plain-string single-answer rows instead of full 1–5 weighted scoring. They are now cleaner and many obvious bad keys were corrected, but for CPNS-style scoring perfection, TKP should eventually be converted row-by-row into weighted option objects.
