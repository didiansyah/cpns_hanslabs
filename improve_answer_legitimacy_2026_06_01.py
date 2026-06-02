#!/usr/bin/env python3
"""High-confidence CPNS question-bank improvement pass.

- Backup touched rows
- Fix answer keys where audit found clear objective error
- Strip embedded "Jawaban: X" artifacts from options and align key when present
- Delete malformed/context-missing OCR rows
- Recategorize obvious section pollution
"""
from __future__ import annotations
import json, re
from datetime import datetime
from pathlib import Path
import pymysql

BACKUP = Path('/root/cpns/backups/answer_legitimacy_improve_2026_06_01.json')
REPORT = Path('/root/cpns/answer_legitimacy_improve_2026_06_01_report.json')

# Manual high-confidence answer-key fixes from per-section audit.
ANSWER_FIXES = {
    # TWK
    1659: 2, 2123: 1, 2124: 1, 2131: 1, 2135: 2, 2136: 4, 2147: 4, 2172: 3,
    2196: 2, 2203: 2, 2214: 2, 2226: 2, 2289: 3, 3024: 3, 2295: 2, 3030: 2,
    2299: 4, 3034: 4, 2305: 1, 3040: 1, 2312: 3, 3047: 3, 2386: 4, 2936: 4,
    2387: 2, 2937: 2, 2390: 1, 2940: 1, 2396: 3, 2946: 3, 2399: 4, 2949: 4,
    2400: 2, 2950: 2, 4484: 2, 2401: 2, 2951: 2, 2402: 3, 2952: 3, 2403: 4,
    2953: 4, 2405: 4, 2955: 4, 2406: 2, 2956: 2, 2471: 2, 2475: 2, 2476: 3,
    2477: 4, 2481: 2, 2484: 3, 2488: 1, 2490: 3, 2492: 1, 2493: 1, 2494: 3,
    2594: 1, 3313: 1, 2600: 4, 3319: 4, 2601: 1, 3320: 1, 2606: 3, 3325: 3,
    2395: 1, 2945: 1, 2411: 4, 2961: 4, 2970: 3, 2287: 4, 3022: 4, 3117: 3,
    3138: 3, 3213: 4, 3218: 3, 3233: 2, 3236: 1, 2581: 1, 3300: 1, 2584: 2,
    3303: 2, 2585: 2, 3304: 2, 3415: 1, 3417: 3, 3418: 3, 3496: 2, 3501: 2,
    3517: 3, 3580: 2, 3585: 4, 3592: 1, 3596: 4, 3601: 1, 3603: 1, 3637: 3,
    3786: 2, 3791: 3, 3797: 4, 3983: 4, 4342: 4, 4483: 4, 4488: 0,
    # TIU / verbal / math
    2162: 1, 2230: 3, 2245: 4, 2247: 1, 2253: 3, 2319: 2, 3054: 2,
    2501: 2, 2509: 2, 2516: 3, 2520: 2, 2527: 3, 2530: 1, 2614: 1, 3333: 1,
    2699: 1, 2720: 2, 2721: 4, 2725: 2, 2732: 3, 2733: 2, 2734: 3, 2738: 3,
    2743: 1, 2745: 2, 2782: 2, 2753: 2, 2758: 1, 2768: 4, 2771: 1, 2778: 1,
    2787: 1, 2792: 4, 2801: 2, 2803: 4, 2826: 1, 2828: 1, 2829: 2, 2833: 2,
    2865: 2, 2870: 1, 2879: 3, 2881: 1, 2882: 1, 2884: 3, 2885: 1, 2895: 2,
    2896: 4, 2913: 4, 2917: 1, 2919: 4, 2920: 4, 3058: 1, 3059: 1, 3065: 2,
    3069: 4, 3071: 1, 3073: 2, 3150: 1, 3152: 2, 3160: 4, 3161: 4, 3163: 2,
    3167: 1, 3242: 3, 3244: 3, 3245: 2, 3247: 1, 3248: 1, 3252: 1, 3253: 2,
    3334: 3, 3343: 1, 3348: 2, 3432: 1, 3433: 2, 3436: 4, 3437: 3, 3441: 4,
    3523: 4, 3524: 2, 3525: 1, 3526: 1, 3534: 4, 3536: 1, 3618: 3, 3619: 2,
    3620: 3, 3622: 1, 3625: 1, 3626: 2, 3633: 2, 3766: 3, 3774: 2, 3781: 4,
    3968: 2, 3969: 1, 3970: 4, 3989: 1, 3991: 4, 3993: 4, 4000: 1,
    # TKP specific key fixes (single-answer rows)
    2308: 3, 2391: 4, 2590: 3, 3309: 3, 3223: 4, 2570: 1, 4030: 2, 3721: 1,
}

# Delete only rows that audit marked malformed/context-missing/unrecoverable or clearly off-product.
DELETE_IDS = {
    2485, 2834, 2824, 3050, 2315, 3972, 4404, 4405, 4406, 4407,
    2523, 3262, 3078, 3533, 2522, 2927, 4007, 4495, 4492, 3675, 3677, 3678,
    3814, 3815, 2916, 3145, 3424, 3425, 3611, 3811, 4485, 3157, 2973, 2423,
    2794, 2795, 2798, 2821, 3154, 3434, 3528, 3535, 4491, 3540, 2431, 2981,
    2873, 2914, 2894, 2877, 2888, 2892, 2902, 2921, 2922, 4368, 3812, 4486,
    4487, 4493, 4494, 3972, 3983,
}

# Obvious recategorization only; avoid mass reshuffling noisy rows.
RECAT = {
    # current TKP factual -> TWK
    **{i: ('TWK', None) for i in [2118, 2308, 2391, 2590, 3223, 3225, 3309, 3806, 4388]},
    # current TIU factual -> TWK
    **{i: ('TWK', None) for i in [1787, 1809, 2142, 2145, 2194, 2593, 3125, 3312, 3514, 3807, 3808, 3809]},
    # current TWK numeric/logical -> TIU
    **{i: ('TIU', None) for i in [2331,2631,2633,2761,2762,2851,2852,2856,2860,2864,2868,2872,2876,2915,3066,3068,3072,3257,3435,3443,3624]},
    # current TWK/TIU situational -> TKP
    **{i: ('TKP', None) for i in [2345,2348,2354,2435,2436,2440,2445,2451,2452,2458,2467,2643,2664,2665,2673,3002,3080,3083,3086,3089,3192,3194,3273,3283,3296,3362,3454,3547,3549,3553,3556,3569,3572,3575,3644,3648,3801,4460,4471,
                                 2531,2532,2535,2537,2538,2541,2543,2547,2548,2552,2553,2555,2557,2559,2563,2567,2568,2573,2574,2580,2680,2985,2986,3012,3298,3360,3368,3381,3383,3385,3701,3729,3730,3732,3733,3734,3738,3740,3741,3742,3743,3744,3745,3746,3748,3749,3750,3752,3753,3756,3761,3762,4008,4009,4010,4011,4012,4013,4014,4016,4017,4018,4019,4020,4021,4022,4023,4024,4025,4026,4031,4035,4037,4456]},
}

RECAT_TOPIC_HINTS = {
    'TWK': 'UUD 1945',
    'TIU': 'Matematika Dasar',
    'TKP': 'Profesionalisme',
}

ANSWER_RE = re.compile(r"\s*(?:Kunci\s+)?Jawab(?:an|annya)?\s*:?\s*(?:\[?\s*)?([A-Ea-e])(?:\s*\]?|\.|\s|$).*$", re.I | re.S)
TRAILING_JAWAB_RE = re.compile(r"\s*(?:Kunci\s+)?Jawab(?:an|annya)?\s*:?.*$", re.I | re.S)
LETTER_TO_IDX = {c: i for i, c in enumerate('ABCDE')}


def load_options(raw):
    if isinstance(raw, list):
        return raw
    return json.loads(raw)


def dump_rows(cur, ids):
    if not ids:
        return []
    placeholders = ','.join(['%s'] * len(ids))
    cur.execute(f"SELECT * FROM questions WHERE id IN ({placeholders}) ORDER BY id", list(ids))
    return cur.fetchall()


def main():
    conn = pymysql.connect(host='localhost', user='root', database='cpns', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
    cur = conn.cursor()

    # Scan rows with embedded answer artifacts in options.
    cur.execute("SELECT id,options FROM questions ORDER BY id")
    embedded_fix_ids = set()
    embedded_answer = {}
    cleaned_options = {}
    for row in cur.fetchall():
        try:
            opts = load_options(row['options'])
        except Exception:
            continue
        if not isinstance(opts, list):
            continue
        new_opts = []
        changed = False
        found_letter = None
        for opt in opts:
            if isinstance(opt, str):
                m = ANSWER_RE.search(opt)
                if m:
                    found_letter = m.group(1).upper()
                    opt = ANSWER_RE.sub('', opt).strip()
                    changed = True
                elif TRAILING_JAWAB_RE.search(opt):
                    opt = TRAILING_JAWAB_RE.sub('', opt).strip()
                    changed = True
            new_opts.append(opt)
        if changed:
            embedded_fix_ids.add(row['id'])
            cleaned_options[row['id']] = new_opts
            if found_letter in LETTER_TO_IDX:
                embedded_answer[row['id']] = LETTER_TO_IDX[found_letter]

    touched_ids = set(ANSWER_FIXES) | set(DELETE_IDS) | set(RECAT) | embedded_fix_ids
    rows = dump_rows(cur, sorted(touched_ids))
    BACKUP.parent.mkdir(parents=True, exist_ok=True)
    BACKUP.write_text(json.dumps(rows, ensure_ascii=False, indent=2, default=str), encoding='utf-8')

    report = {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'backup': str(BACKUP),
        'planned_touched_ids': len(touched_ids),
        'backed_up_rows': len(rows),
        'embedded_option_cleaned': 0,
        'embedded_answer_aligned': 0,
        'manual_answer_fixed': 0,
        'recategorized': 0,
        'deleted': 0,
    }

    # Clean embedded answer artifacts first.
    for qid, opts in cleaned_options.items():
        cur.execute("UPDATE questions SET options=%s WHERE id=%s", (json.dumps(opts, ensure_ascii=False), qid))
        report['embedded_option_cleaned'] += cur.rowcount
        if qid in embedded_answer:
            cur.execute("UPDATE questions SET correct_answer=%s WHERE id=%s", (embedded_answer[qid], qid))
            report['embedded_answer_aligned'] += cur.rowcount

    # Manual answer fixes override embedded extraction when audit was explicit.
    for qid, ans in ANSWER_FIXES.items():
        cur.execute("UPDATE questions SET correct_answer=%s WHERE id=%s", (ans, qid))
        report['manual_answer_fixed'] += cur.rowcount

    # Recategorize obvious rows, with broad topic defaults only when current topic is generic/off-section.
    for qid, (section, topic) in RECAT.items():
        topic = topic or RECAT_TOPIC_HINTS[section]
        cur.execute("UPDATE questions SET section=%s, topic=%s WHERE id=%s", (section, topic, qid))
        report['recategorized'] += cur.rowcount

    # Delete malformed/context-missing rows last.
    existing_delete = set(r['id'] for r in dump_rows(cur, sorted(DELETE_IDS)))
    if existing_delete:
        placeholders = ','.join(['%s'] * len(existing_delete))
        cur.execute(f"DELETE FROM questions WHERE id IN ({placeholders})", list(existing_delete))
        report['deleted'] = cur.rowcount

    conn.commit()
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))
    cur.close(); conn.close()

if __name__ == '__main__':
    main()
