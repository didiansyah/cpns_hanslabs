#!/usr/bin/env python3
"""Second-pass high-confidence CPNS answer legitimacy fixes after 1:1 audit."""
from __future__ import annotations
import json, re
from datetime import datetime
from pathlib import Path
import pymysql

BACKUP = Path('/root/cpns/backups/answer_legitimacy_round2_2026_06_01.json')
REPORT = Path('/root/cpns/answer_legitimacy_round2_2026_06_01_report.json')

# 0-based correct_answer fixes from second-pass TWK/TIU audit.
ANSWER_FIXES = {
    # TWK objective/factual
    2119:1, 2120:1, 2121:1, 2130:1, 2134:4, 2137:3, 2138:4, 2139:4, 2143:4, 2145:2,
    2151:1, 2154:2, 2155:1, 2156:2, 2157:2, 2159:3, 2160:1, 2163:1, 2171:3, 2173:1,
    2174:1, 2175:2, 2176:1, 2177:2, 2180:2, 2186:2, 2187:4, 2188:2, 2189:2, 2191:2,
    2192:4, 2193:2, 2197:1, 2199:4, 2202:1, 2208:2, 2211:1, 2213:1, 2215:2, 2220:3,
    2221:2, 2222:4, 2291:2, 3026:2, 2296:3, 3031:3, 2302:4, 3037:4, 2303:4, 3038:4,
    2306:3, 3041:3, 2309:4, 3044:4, 2314:3, 3049:3, 2317:2, 3052:2, 2380:4, 2930:4,
    2381:1, 2931:1, 2382:4, 2932:4, 2384:3, 2934:3, 2385:2, 2935:2, 2389:4, 2939:4,
    2393:4, 2943:4, 2404:1, 2954:1, 2412:2, 2962:2, 2433:1, 2983:1, 2477:2,
    2582:2, 3301:2, 2587:2, 3306:2, 2588:2, 3307:2, 2592:3, 2593:2, 3312:2, 2596:2,
    3315:2, 2602:1, 3321:1, 2604:4, 2605:4, 3324:4, 2613:4, 3332:4, 3114:3, 3595:2,
    3115:1, 3116:2, 4341:3, 3118:4, 3119:4, 3122:2, 3124:2, 3125:1, 3130:2, 3134:4,
    3141:3, 3204:3, 3207:4, 3208:4, 3209:1, 3212:1, 3217:2, 3221:2, 3222:3, 3224:1,
    3227:1, 3229:1, 3230:1, 3232:2, 3394:1, 3395:2, 3397:2, 3398:4, 3400:2, 3401:1,
    3404:4, 3406:1, 3408:1, 3409:2, 3412:4, 3413:4, 3421:1, 3489:1, 3491:1, 3493:2,
    3498:1, 3504:1, 3505:4, 3507:4, 3515:2, 3520:3, 3579:3, 3581:4, 3582:4, 3586:2,
    3588:1, 3593:2, 3597:2, 3602:1, 3605:3, 3606:4, 3608:3, 3613:2, 3788:3, 3798:2,
    3799:2, 3802:1, 3806:3, 3807:3, 3808:2, 4384:0, 4396:0,
    # TWK currently non-TWK but key fix too
    2337:1, 2629:2, 2862:4, 2878:1, 2908:4, 2923:4, 3162:4, 3537:1,
    # TIU objective/math/verbal/logical
    2428:4, 2978:4, 2499:4, 2512:2, 2517:1, 2627:1, 3346:1, 2746:1, 2749:4, 2771:4,
    2760:1, 2764:4, 2767:1, 2769:3, 2779:2, 2780:1, 2789:1, 2796:1, 2800:1, 2822:1,
    2830:2, 2831:2, 2832:2, 2848:1, 2849:2, 2851:3, 2852:4, 2854:2, 2856:3, 2860:1,
    2872:4, 2976:3, 2977:4, 3064:3, 3068:2, 3072:1, 3153:1, 3156:2, 3260:1, 3349:2,
    3354:1, 3445:1, 3446:1, 3530:2, 3539:4, 3541:4, 3624:2, 3631:2, 3635:1, 3773:1,
    3784:1, 2417:1, 2967:1, 2432:2, 2982:2, 2514:1, 2528:4, 2861:4, 2883:4, 3543:4,
    2869:4, 2874:3, 2893:1, 2897:3, 2900:1, 2903:2, 2904:2, 2905:2, 2907:1, 3429:2,
    3430:4, 3636:2, 3775:2, 3777:1, 3778:1,
    # TKP clear rekeys where option index is known from audit/current duplicates
    2507:4,
}

DELETE_IDS = {
    # TWK malformed/missing context/no valid option
    2133, 2498, 3146, 3261, 3423, 3447, 3448, 3449, 3610, 3804, 2609, 3328, 2906,
    # TIU malformed/missing context/no valid option
    2129, 2158, 2162, 2169, 2170, 2219, 2316, 2424, 2974, 2462, 2479, 2480, 2518,
    2524, 2525, 2526, 2634, 2649, 2783, 2785, 2819, 2820, 2823, 2924, 3051, 3081,
    3158, 3435, 3443, 3532, 3630, 3772,
    # English/off-product rows remaining in TIU
    3968,3969,3970,3971,3989,3990,3991,3992,3993,3995,3996,3997,3998,4000,
    # TKP severe OCR/malformed or non-TKP not worth keeping
    2665, 3762, 4031, 4037,
}

RECAT = {
    # TWK -> TIU
    2337:('TIU','Matematika Dasar'),2629:('TIU','Matematika Dasar'),2862:('TIU','Silogisme'),2878:('TIU','Silogisme'),
    2908:('TIU','Silogisme'),2923:('TIU','Silogisme'),3162:('TIU','Matematika Dasar'),3537:('TIU','Matematika Dasar'),
    4408:('TIU','Pemahaman Bacaan'),
    # TWK -> TKP
    4270:('TKP','Jejaring Kerja'),4275:('TKP','Anti Radikalisme'),3223:('TKP','Pelayanan Publik'),
    # TIU -> TWK/economics/hukum as closest available TWK topic
    2155:('TWK','Hankam'),2163:('TWK','Hankam'),2177:('TWK','Hankam'),2188:('TWK','Hankam'),2191:('TWK','Hankam'),
    # TIU -> TKP
    2536:('TKP','Integritas'),3645:('TKP','Profesionalisme'),
    # TKP -> TIU
    2507:('TIU','Silogisme'),
}

# TKP best-answer phrase matching; safer than hardcoding indices when options vary across duplicates.
PHRASE_FIXES = {
    2350:['tidak berputus asa'], 3085:['tidak berputus asa'],
    2353:['belajar hal', 'hal positif'], 3088:['belajar hal','hal positif'],
    2360:['membantu mencari'], 3095:['membantu mencari'],
    2365:['menyapa'], 3100:['menyapa'],
    2368:['menyelesaikan pekerjaan','koordinasi'], 3103:['menyelesaikan pekerjaan','koordinasi'],
    2370:['menyiapkan payung','payung'], 3105:['menyiapkan payung','payung'],
    2375:['membantu', 'beradaptasi'], 3110:['membantu','beradaptasi'],
    2435:['sumber kegagalan','evaluasi'], 2985:['sumber kegagalan','evaluasi'],
    2437:['melayani', 'terbaik'], 2987:['melayani','terbaik'],
    2438:['meningkatkan kinerja','bekerja lebih giat'], 2988:['meningkatkan kinerja','bekerja lebih giat'],
    2443:['mempertimbangkan','keluarga'], 2993:['mempertimbangkan','keluarga'],
    2444:['mengangkat','memastikan'], 2994:['mengangkat','memastikan'],
    2445:['tetap bekerja'], 2995:['tetap bekerja'],
    2447:['meminta penjelasan'], 2997:['meminta penjelasan'],
    2454:['tidak membocorkan','diam'], 3004:['tidak membocorkan','diam'],
    2461:['profesional','menjaga sikap'], 3011:['profesional','menjaga sikap'],
    2465:['tertarik','menyelesaikan'], 3015:['tertarik','menyelesaikan'],
    2468:['koordinasi','izin'], 3018:['koordinasi','izin'], 3277:['koordinasi','izin'], 4027:['koordinasi','izin'],
    2531:['tenang','menyelesaikan'], 4008:['tenang','menyelesaikan'],
    2533:['bekerja lebih giat','meningkatkan'],
    2534:['membagi tugas','memotivasi'],
    2535:['turut bertanggung'], 4009:['turut bertanggung'],
    2537:['menjaga kerahasiaan','alternatif solusi'],
    2543:['sepenuh hati'],
    2544:['menerima aturan','mengenal'], 3283:['menerima aturan','mengenal'],
    2553:['menyelesaikan tugas','membujuk'],
    2559:['menemani','dukungan'], 2680:['menemani','dukungan'], 4023:['menemani','dukungan'],
    2562:['memenuhi target','senang hati'], 3291:['memenuhi target','senang hati'],
    2572:['menolak','mantap'], 4032:['menolak','mantap'],
    2574:['konsekuensi','tanggung jawab saya'], 3293:['konsekuensi','tanggung jawab saya'], 3736:['konsekuensi','tanggung jawab saya'],
    2642:['nomor urut','prosedur'], 3361:['nomor urut','prosedur'],
    2643:['tidak putus asa','berani mencoba'], 3362:['tidak putus asa','berani mencoba'], 3572:['tidak putus asa','berani mencoba'],
    2651:['menawarkan bantuan','meminta tugas'], 3370:['menawarkan bantuan','meminta tugas'],
    2661:['cukup tekun'], 3171:['cukup tekun'], 3380:['cukup tekun'],
    2664:['tertantang','menerima'], 3383:['tertantang','menerima'],
    2669:['mengatakan apa adanya','meminta saran'], 3388:['mengatakan apa adanya','meminta saran'],
    3267:['menyesuaikan diri'], 3268:['meminta maaf','laporan baru'], 3270:['menjelaskan duduk'], 3271:['introspeksi','memperbaiki'],
    3475:['diawasi maupun tidak','giat'], 3558:['meminta ganti','sesuai pesanan'], 3561:['mengajak serta keluarga','biaya pribadi'],
    3577:['profesional','jujur'], 3659:['termotivasi','melaporkan progres'], 3709:['koordinasi','langsung'],
    4010:['tidak ingin melakukannya'], 4016:['lapor pimpinan','menerima keputusan'], 4022:['berbaikan','minta maaf'],
    4028:['memperbaiki','ajukan kembali'], 4029:['mempertimbangkan pendapat'], 4035:['menerima teguran','pelajaran'], 4036:['menerima kritik','masukan'],
    4451:['solusi','pimpinan'],
}

CLEAN_REPLACEMENTS = [
    (re.compile(r'\bBAGIAN\s+KETIGA.*$', re.I|re.S), ''),
    (re.compile(r'\bBANK\s+SOAL.*$', re.I|re.S), ''),
    (re.compile(r'\bTES\s+(?:INTELEGENSI|KARAKTERISTIK).*$', re.I|re.S), ''),
    (re.compile(r'\bSOAL\s+DAN\s+PEMBAHASAN.*$', re.I|re.S), ''),
]


def load_opts(raw):
    return raw if isinstance(raw, list) else json.loads(raw)

def option_text(o):
    return o.get('text','') if isinstance(o, dict) else str(o)

def set_option_text(o, text):
    if isinstance(o, dict):
        o = dict(o); o['text'] = text; return o
    return text

def clean_text(s):
    old=s
    for pat,repl in CLEAN_REPLACEMENTS:
        s=pat.sub(repl,s)
    s=re.sub(r'\s+', ' ', s).strip()
    return s, s!=old

def find_phrase_index(opts, phrases):
    texts=[option_text(o).lower() for o in opts]
    for phrase in phrases:
        p=phrase.lower()
        for i,t in enumerate(texts):
            if p in t:
                return i
    return None

def main():
    conn=pymysql.connect(host='localhost',user='root',database='cpns',charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
    cur=conn.cursor()
    touched=set(ANSWER_FIXES)|DELETE_IDS|set(RECAT)|set(PHRASE_FIXES)
    placeholders=','.join(['%s']*len(touched))
    cur.execute(f'SELECT * FROM questions WHERE id IN ({placeholders}) ORDER BY id', list(touched))
    rows=cur.fetchall()
    BACKUP.parent.mkdir(parents=True,exist_ok=True)
    BACKUP.write_text(json.dumps(rows,ensure_ascii=False,indent=2,default=str),encoding='utf-8')
    report={'timestamp':datetime.utcnow().isoformat()+'Z','backup':str(BACKUP),'backed_up_rows':len(rows),'answer_fixed':0,'phrase_fixed':0,'phrase_missed':{},'recategorized':0,'cleaned_text':0,'deleted':0}

    # Clean obvious OCR headers/fragments in touched rows before rekeying.
    for r in rows:
        q_changed=False
        qtext,chg=clean_text(r['question_text'] or '')
        if chg:
            cur.execute('UPDATE questions SET question_text=%s WHERE id=%s',(qtext,r['id'])); report['cleaned_text']+=cur.rowcount
        try: opts=load_opts(r['options'])
        except Exception: opts=[]
        new=[]; opt_changed=False
        for o in opts if isinstance(opts,list) else []:
            t=option_text(o)
            nt,chg=clean_text(t)
            # common harmless truncation fixes
            if nt.strip().lower() in {'bertanggung','hal itu adalah tanggung','bekerja dengan penuh profesionalitas dan tanggung'}:
                nt = nt + ' jawab'
                chg=True
            new.append(set_option_text(o,nt) if chg else o)
            opt_changed = opt_changed or chg
        if opt_changed and len(new)==5:
            cur.execute('UPDATE questions SET options=%s WHERE id=%s',(json.dumps(new,ensure_ascii=False),r['id'])); report['cleaned_text']+=cur.rowcount

    for qid,ans in ANSWER_FIXES.items():
        cur.execute('UPDATE questions SET correct_answer=%s WHERE id=%s',(ans,qid)); report['answer_fixed']+=cur.rowcount

    for qid,(section,topic) in RECAT.items():
        cur.execute('UPDATE questions SET section=%s, topic=%s WHERE id=%s',(section,topic,qid)); report['recategorized']+=cur.rowcount

    # phrase-based TKP rekeys
    for qid,phrases in PHRASE_FIXES.items():
        cur.execute('SELECT id,options FROM questions WHERE id=%s',(qid,)); r=cur.fetchone()
        if not r: continue
        try: opts=load_opts(r['options'])
        except Exception: report['phrase_missed'][str(qid)]='bad_json'; continue
        idx=find_phrase_index(opts,phrases)
        if idx is None:
            report['phrase_missed'][str(qid)]=phrases
            continue
        cur.execute('UPDATE questions SET correct_answer=%s WHERE id=%s',(idx,qid)); report['phrase_fixed']+=cur.rowcount

    existing=[]
    if DELETE_IDS:
        placeholders=','.join(['%s']*len(DELETE_IDS))
        cur.execute(f'SELECT id FROM questions WHERE id IN ({placeholders})', list(DELETE_IDS))
        existing=[r['id'] for r in cur.fetchall()]
        if existing:
            placeholders=','.join(['%s']*len(existing))
            cur.execute(f'DELETE FROM questions WHERE id IN ({placeholders})', existing); report['deleted']=cur.rowcount

    conn.commit()
    REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    cur.close(); conn.close()

if __name__=='__main__':
    main()
