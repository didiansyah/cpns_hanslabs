# CPNS Question Bank Answer Legitimacy Audit — 2026-06-01

Scope: full DB audit by section after previous structural cleanup.
DB: MariaDB `cpns.questions`.
Total rows at audit time: 1,929.

## Verdict
Not fully legit yet for production if judged question-by-question with answer correctness.

The newly generated/reference-enhanced batch is structurally clean, but the legacy imported/OCR rows still contain many high-confidence issues:

- TWK: many rows have wrong `correct_answer`, factual questions in wrong topics, and some malformed/context-missing rows.
- TIU: many rows are not TIU (TKP/TWK/English mixed in), many numeric/deret/logic answer keys are wrong, and several OCR rows are malformed.
- TKP: many rows are situational but stored as simple single-answer strings instead of weighted TKP scoring. Several specific TKP rows also have wrong best-answer keys or truncated options.

## High-confidence example issues

### TWK answer key wrong
- ID 2124: "Iuran yang diberikan rakyat kepada negara..." current answer Retribusi; correct should be Pajak.
- ID 2131: Irian Barat command current Dwi Komando Rakyat; correct should be Trikora.
- ID 2135: Amnesti/abolisi current MPR; correct should be DPR.
- ID 2136: Grasi/rehabilitasi current MPR; correct should be MA.
- ID 2147: ZEE current 350 mil laut; correct should be 200 mil laut.
- ID 2203: Portugis merebut Malaka current Cornelis de Houtman; correct should be Alfonso de Albuquerque.
- ID 2214: Ketua BPUPKI current Soekarno; correct should be Radjiman Wedyodiningrat.
- ID 2289/3024: Hari Kesaktian Pancasila current 1 Juni; correct should be 1 Oktober.
- ID 3117: Pidato dasar negara Soekarno current 29 Mei; correct should be 1 Juni 1945.
- ID 4342: Maklumat 3 November 1945 current KNIP; correct should be pembentukan partai politik.

### TIU answer key wrong / malformed
- ID 2516: Deret 5,8,13,21,34,55,89,144 current 203; correct 233.
- ID 2530: a+b=30 max product current 175; correct 225.
- ID 2743: 4,8,_,_,64,128 current 28 24; correct 16 32.
- ID 2803: 15 is 37.5% of current 20; correct 40.
- ID 2826: sepatu+sandal 1200, sepatu 4x sandal current 1000; correct 960.
- ID 2833: susul kendaraan current 10.20; correct 09.40.
- ID 3163: 65,58,51,44 current 41; correct 37.
- ID 3626: x=-(2)^8, y=(-2)^8 current x>y; correct x<y.
- ID 2522/2927/3675/3677/4492/4495: OCR/extraction malformed; should delete or rebuild.

### TKP issues
- 469 TKP rows are still plain string options, not weighted TKP option objects with score 1–5. Backend can score them as single-correct, but this is not real CPNS TKP scoring.
- ID 2570/4030: notulen Baperjakat best answer should be menjaga rahasia, current key points to leaking/incorrect option.
- ID 3812: asks about "teks di atas" but no text stimulus exists.
- ID 4486/4487/4493/4494: truncated/malformed options.
- ID 2118/2308/2391/2590/3223/3225/3309/3806/4388: factual TWK rows sitting in TKP.

## Recommended cleanup policy

1. Backup affected rows.
2. Delete malformed/context-missing/OCR-contaminated rows instead of trying to guess.
3. Update high-confidence wrong answer keys.
4. Recategorize obvious TWK/TIU/TKP pollution.
5. Convert TKP rows to weighted scoring only when each option can be ranked 1–5 confidently; otherwise keep only the generated/validated TKP set.
6. Re-run structural audit and API leak checks.

## Current conclusion

The bank is structurally clean, but content-answer correctness is not yet fully legit. It needs a second cleanup pass focused on answer keys and malformed legacy rows before calling it production-grade.
