#!/usr/bin/env python3
import json, re, sys, urllib.request, datetime, time
from html import unescape
from collections import Counter, defaultdict

sys.path.insert(0, '/root/cpns/backend')
from db import SessionLocal
from models import Question

SOURCES = [
    {'section':'TWK','kind':'tempo','url':'https://www.tempo.co/politik/50-contoh-soal-twk-skd-cpns-2024-dan-kunci-jawabannya-8936','name':'Tempo - 50 Contoh Soal TWK SKD CPNS 2024'},
    {'section':'TKP','kind':'tempo','url':'https://www.tempo.co/politik/50-contoh-soal-tkp-skd-cpns-2024-dan-kunci-jawabannya-8913','name':'Tempo - 50 Contoh Soal TKP SKD CPNS 2024'},
    {'section':'TIU','kind':'skillacademy','url':'https://blog.skillacademy.com/soal-latihan-cpns-tiu-dan-pembahasan','name':'Skill Academy - Contoh Soal Latihan CPNS TIU'},
]

TWK_TOPICS = {
    'Pancasila':['pancasila','sila','bpupki','ppki','piagam jakarta','ideologi','dasar negara','sutasoma'],
    'UUD 1945':['uud','pasal','mpr','dpr','dpd','presiden','mahkamah','konstitusi','amandemen','hak asasi','ham','undang-undang','peraturan'],
    'Bhinneka Tunggal Ika':['bhinneka','bhineka','tunggal ika','toleransi','suku','budaya','persatuan','keragaman','keanekaragaman'],
    'Sejarah Indonesia':['proklamasi','soekarno','hatta','kerajaan','majapahit','sriwijaya','demak','voc','penjajahan','sumpah pemuda','orde baru','reformasi','dekrit','agresi militer'],
    'Hankam':['tni','polri','pertahanan','keamanan','hankam','militer','bela negara','ancaman','wajib militer'],
}
TIU_TOPICS = {
    'Sinonim':['sinonim','persamaan kata','searti','padanan kata'],
    'Antonim':['antonim','lawan kata','berlawanan'],
    'Analogi':['analogi','hubungan kata'],
    'Silogisme':['semua ','beberapa','sebagian','kesimpulan','simpulan','premis','berkuantor'],
    'Deret Angka':['deret','barisan','angka berikut','pola bilangan'],
    'Matematika Dasar':['hitung','hasil dari','persen','luas','volume','perbandingan','rata-rata','aljabar','numerik','kuantitatif','pekerja','bilangan'],
    'Pemahaman Bacaan':['bacaan','paragraf','wacana','ide pokok'],
}
TKP_TOPICS = {
    'Pelayanan Publik':['pelayanan','masyarakat','warga','loket','publik','keluhan','instansi'],
    'Integritas':['suap','gratifikasi','jujur','korupsi','manipulasi','integritas','uang','fasilitas'],
    'Profesionalisme':['deadline','tugas','atasan','laporan','kinerja','profesional','pekerjaan','kantor'],
    'Bela Negara':['bendera','negara','bangsa','hoax tentang negara','upacara','nasionalisme'],
    'Jejaring Kerja':['tim','rekan','kolaborasi','koordinasi','kerja sama','teman'],
    'Sosial Budaya':['tetangga','lingkungan','budaya','gotong royong','perbedaan','sosial'],
    'Teknologi Informasi':['teknologi','aplikasi','digital','komputer','internet','media sosial'],
    'Anti Radikalisme':['radikal','teror','intoleran','ekstrem','kebencian'],
}

def clean(s):
    s = unescape(str(s or '')).replace('\xa0',' ')
    s = re.sub(r'\s+', ' ', s).strip()
    return s.strip(' \t\n\r')

def norm(s):
    return re.sub(r'\W+', '', clean(s).lower())[:180]

def fetch(url):
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (compatible; CPNSQuestionAudit/1.0)'})
    with urllib.request.urlopen(req, timeout=45) as r:
        return r.read().decode('utf-8','ignore')

def html_lines(html):
    html = re.sub(r'<(script|style|noscript).*?</\1>', ' ', html, flags=re.S|re.I)
    html = re.sub(r'<br\s*/?>', '\n', html, flags=re.I)
    text = unescape(re.sub(r'<[^>]+>', '\n', html))
    lines = [clean(x) for x in re.split(r'[\r\n]+', text)]
    bad_exact = {'Iklan','ADVERTISEMENT','Scroll ke bawah untuk melanjutkan membaca','BACA JUGA','Bagikan','Menu','TEMPO.CO',','}
    return [x for x in lines if x and x not in bad_exact and not x.startswith('http')]

def topic_for(section, text):
    mapping = {'TWK':TWK_TOPICS,'TIU':TIU_TOPICS,'TKP':TKP_TOPICS}[section]
    tl = text.lower(); best=None; bs=-1
    for topic,kws in mapping.items():
        score=sum(1 for k in kws if k in tl)
        if score>bs:
            best,bs=topic,score
    defaults={'TWK':'UUD 1945','TIU':'Matematika Dasar','TKP':'Profesionalisme'}
    return best if bs>0 else defaults[section]

def valid_option_text(s):
    if not s or len(s) < 2: return False
    junk = ['jawaban:', 'pembahasan:', 'baca juga', 'iklan', 'tempo.co']
    return not any(j in s.lower() for j in junk)

def parse_tempo(lines, section, source):
    out=[]
    answer_idxs=[]
    for i,l in enumerate(lines):
        m=re.match(r'^Jawaban\s*:\s*([A-E])\.?$', l, re.I)
        if m: answer_idxs.append((i,m.group(1).upper()))
    prev=-1
    for idx, ans in answer_idxs:
        seg=[x for x in lines[prev+1:idx] if valid_option_text(x)]
        # Remove common article/meta lines before the actual list by taking tail before answer.
        if len(seg) < 6:
            prev=idx; continue
        opts=seg[-5:]
        qparts=seg[:-5]
        # Tempo renders each option as its own line and the actual question is the
        # last content line before the five options. Avoid pulling article intro or
        # recommendation links ("Baca juga") into the question text.
        qtext=clean(qparts[-1] if qparts else '')
        if qparts and (len(qtext) < 25 or (qtext[:1].islower() and len(qparts) >= 2)):
            take = 3 if len(qparts) >= 3 and len(qparts[-2].split()) <= 3 else 2
            qtext=clean(' '.join(qparts[-take:]))
        qtext=re.sub(r'^(\d+\s*[.)]\s*)','',qtext)
        if len(qtext)<25 or len(opts)!=5:
            prev=idx; continue
        out.append({'section':section,'topic':topic_for(section,qtext+' '+' '.join(opts)),'year':2024,'difficulty':'sedang','question_text':qtext,'options':opts,'correct_answer':ord(ans)-65,'explanation':f'Kunci jawaban {ans} dari artikel {source["name"]}. Sumber: {source["url"]}' ,'source_url':source['url'],'source_name':source['name']})
        prev=idx
    return out

def parse_skillacademy(lines, section, source):
    out=[]
    starts=[i for i,l in enumerate(lines) if re.match(r'^Soal\s+\d+\b',l,re.I)]
    starts.append(len(lines))
    for a,b in zip(starts, starts[1:]):
        seg=lines[a:b]
        ans_idx=None; ans=None
        for i,l in enumerate(seg):
            m=re.match(r'^Jawaban\s*:\s*([A-E])\.?$',l,re.I)
            if m: ans_idx=i; ans=m.group(1).upper(); break
        if ans_idx is None: continue
        opt_pos=[]
        for i,l in enumerate(seg[:ans_idx]):
            if re.match(r'^[A-E]\.\s*\S+',l): opt_pos.append(i)
        if len(opt_pos)!=5: continue
        opts=[clean(re.sub(r'^[A-E]\.\s*','',seg[i])) for i in opt_pos]
        q_lines=[]
        for l in seg[:opt_pos[0]]:
            if re.match(r'^Soal\s+\d+',l,re.I): continue
            if l.lower().startswith(('topik:','subtopik:')): continue
            if re.match(r'^[A-Z]{2,}-',l): continue
            q_lines.append(l)
        qtext=clean(' '.join(q_lines))
        # explanation until next soal
        exp=[]; in_exp=False
        for l in seg[ans_idx+1:]:
            if l.lower().startswith('pembahasan'):
                in_exp=True; continue
            if in_exp: exp.append(l)
        explanation=clean(' '.join(exp))
        if len(qtext)<25 or not explanation: continue
        out.append({'section':section,'topic':topic_for(section,qtext+' '+' '.join(opts)),'year':2026,'difficulty':'sedang','question_text':qtext,'options':opts,'correct_answer':ord(ans)-65,'explanation':f'{explanation} Sumber: {source["url"]}','source_url':source['url'],'source_name':source['name']})
    return out

def load_local_candidates():
    path='/root/cpns/candidates_from_new_extracted.json'
    try: data=json.load(open(path))
    except FileNotFoundError: return []
    out=[]
    for q in data:
        q=dict(q)
        q['source_url']='local-extracted-pdf'
        q['source_name']='Local extracted PDF: '+str(q.get('source_file','bank soal CPNS'))
        out.append(q)
    return out

def quality_filter(cands):
    s=SessionLocal()
    existing={norm(q.question_text) for q in s.query(Question.question_text).all()}
    s.close()
    seen=set(); good=[]; reject=Counter()
    for q in cands:
        qt=clean(q.get('question_text'))
        opts=[clean(o) for o in q.get('options') or []]
        ans=q.get('correct_answer')
        key=norm(qt)
        if q.get('section') not in ('TWK','TIU','TKP'): reject['bad_section']+=1; continue
        if len(qt)<25: reject['short_question']+=1; continue
        if len(opts)!=5: reject['bad_option_count']+=1; continue
        if any(not valid_option_text(o) for o in opts): reject['bad_option_text']+=1; continue
        if len(set(o.lower() for o in opts))!=5: reject['duplicate_options']+=1; continue
        if not isinstance(ans,int) or ans<0 or ans>4: reject['bad_answer']+=1; continue
        if key in existing: reject['already_in_db']+=1; continue
        if key in seen: reject['duplicate_candidate']+=1; continue
        if not clean(q.get('explanation')): reject['missing_explanation']+=1; continue
        q['question_text']=qt; q['options']=opts; q['topic']=q.get('topic') or topic_for(q['section'], qt+' '+' '.join(opts))
        seen.add(key); good.append(q)
    return good,reject

def main(insert=False):
    raw=[]; source_stats={}
    for src in SOURCES:
        html=fetch(src['url']); lines=html_lines(html)
        if src['kind']=='tempo': items=parse_tempo(lines,src['section'],src)
        elif src['kind']=='skillacademy': items=parse_skillacademy(lines,src['section'],src)
        else: items=[]
        source_stats[src['name']]=len(items); raw.extend(items)
        time.sleep(1)
    local=load_local_candidates(); raw.extend(local); source_stats['Local extracted PDFs']=len(local)
    good,reject=quality_filter(raw)
    ts=datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    outpath=f'/root/cpns/scraped_legit_candidates_{ts}.json'
    json.dump({'sources':source_stats,'reject':dict(reject),'count':len(good),'items':good}, open(outpath,'w'), ensure_ascii=False, indent=2)
    print('raw_source_stats',source_stats)
    print('clean_new',len(good),'reject',dict(reject),'backup',outpath)
    print('by_section',dict(Counter(q['section'] for q in good)))
    print('by_topic',Counter((q['section'],q['topic']) for q in good).most_common(30))
    for q in good[:5]: print('SAMPLE',q['section'],q['topic'],q['question_text'][:120], 'ans',q['correct_answer'], q['source_name'])
    if insert and good:
        s=SessionLocal(); inserted=0
        for q in good:
            s.add(Question(section=q['section'],topic=q['topic'],year=q.get('year',2024),difficulty=q.get('difficulty','sedang'),question_text=q['question_text'],options=q['options'],correct_answer=q['correct_answer'],explanation=q['explanation']))
            inserted+=1
        s.commit(); s.close(); print('inserted',inserted)

if __name__=='__main__':
    main(insert='--insert' in sys.argv)
