#!/usr/bin/env python3
"""Pengurai Riyadhus Shalihin (Syamilah, tahqiq Mahir al-Fahl) -> data.json
Struktur: KITAB -> BAB (grup) -> unit (ayat bab / hadits / penutup)."""
import re, json, sys, html

SRC = sys.argv[1]
OUT = sys.argv[2]

HAR = re.compile('[ً-ْٰـ]')
def bare(s): return HAR.sub('', s)

raw = open(SRC, encoding='utf-8-sig').read().replace('\r', '')
lines = raw.split('\n')

# mulai dari muqaddimah an-Nawawi
start = next(i for i, l in enumerate(lines) if bare(l).strip().startswith('مقدمة المؤلف'))
lines = lines[start:]

PAGE = re.compile(r'^\((\d*)/(\d*)\)$')
SEP = '__________'

# ---------- 1. pecah per halaman cetak ----------
blocks = []  # {pg, text:[...], fn:{n:txt}, fnorder:[n]}
cur = {'text': [], 'fnl': [], 'pg': None}
mode = 'text'
for l in lines:
    s = l.strip()
    m = PAGE.match(s)
    if m:
        cur['pg'] = int(m.group(2)) if m.group(2) else None
        blocks.append(cur); cur = {'text': [], 'fnl': [], 'pg': None}; mode = 'text'; continue
    if s.startswith(SEP):
        mode = 'fn'; continue
    if mode == 'text':
        cur['text'].append(s)
    else:
        cur['fnl'].append(s)
if cur['text'] or cur['fnl']:
    blocks.append(cur)

# footnote per blok
FNSTART = re.compile(r'^\((\d+)\)\s*(.*)$')
orphan_cont = 0
for bi, b in enumerate(blocks):
    fn = {}; order = []; last = None; expect = 1
    for s in b['fnl']:
        if not s:
            continue
        m = FNSTART.match(s)
        if m and int(m.group(1)) == expect:
            last = int(m.group(1)); fn[last] = m.group(2); order.append(last); expect += 1
        elif last is not None:
            fn[last] += '<br>' + s
        else:
            # sambungan catatan dari halaman sebelumnya
            pb = next((blocks[j] for j in range(bi - 1, -1, -1) if blocks[j].get('fnorder')), None)
            if pb:
                pb['fn'][pb['fnorder'][-1]] += '<br>' + s
            orphan_cont += 1
    b['fn'] = fn; b['fnorder'] = order

# ---------- 2. aliran baris dengan token catatan ----------
MARK = re.compile(r'\s?\((\d{1,2})\)')
STRAY = []
KIT = re.compile(r'^\(?(\d+)\)?\s*-\s*كِ?تَ?ابُ?\s')
stream = []  # (text, block_index)
KGLUE = re.compile(r'(\d)?\((\d{1,2})\)\s*-\s*(كِ?تَ?ابُ?\s.*)$')
for b in blocks:
    nt = []
    for s in b['text']:
        m = KGLUE.search(s)
        if m and m.start() > 0:
            head = s[:m.start()] + ('(%s)' % m.group(1) if m.group(1) else '')
            nt += [head, '%s - %s' % (m.group(2), m.group(3))]
        else:
            nt.append(s)
    b['text'] = nt
for bi, b in enumerate(blocks):
    def rep(m, bi=bi, b=b):
        n = int(m.group(1))
        if n in b['fn']:
            b.setdefault('used', set()).add(n)
            return '\x01%d:%d\x02' % (bi, n)
        return m.group(0)
    BARE = re.compile(r'(?<=[\u0621-\u064A\u064B-\u0652.»])(\d{1,2})(?=[\s.،]|$)')
    def rep2(m, bi=bi, b=b):
        n = int(m.group(1))
        if n in b['fn'] and n not in b.get('used', set()):
            b['used'].add(n) if 'used' in b else b.setdefault('used', {n})
            STRAY.append(n)
            return '\x01%d:%d\x02' % (bi, n)
        return m.group(0)
    tx = [MARK.sub(rep, s) for s in b['text']]
    tx = [s if KIT.match(s) else BARE.sub(rep2, s) for s in tx]
    for s in tx:
        stream.append((s, bi))

# ---------- 3. kitab ----------
KITAB = [
    ('مُقَدِّمَةُ الْمُؤَلِّفِ', "Muqaddimah al-Mu'allif", None),
    ('الْمُقَدِّمَاتُ', "Bab-bab Pembuka (al-Muqaddimat)", 1),
    ('كِتَابُ الْأَدَبِ', 'Kitab al-Adab', 84),
    ('كِتَابُ أَدَبِ الطَّعَامِ', "Kitab Adab ath-Tha'am", 100),
    ('كِتَابُ اللِّبَاسِ', 'Kitab al-Libas', 117),
    ('كِتَابُ آدَابِ النَّوْمِ وَالِاضْطِجَاعِ وَالْقُعُودِ وَالْمَجْلِسِ وَالْجَلِيسِ وَالرُّؤْيَا', "Kitab Adab an-Naum", 127),
    ('كِتَابُ السَّلَامِ', 'Kitab as-Salam', 131),
    ('كِتَابُ عِيَادَةِ الْمَرِيضِ وَتَشْيِيعِ الْمَيِّتِ وَالصَّلَاةِ عَلَيْهِ وَحُضُورِ دَفْنِهِ وَالْمُكْثِ عِنْدَ قَبْرِهِ بَعْدَ دَفْنِهِ', "Kitab 'Iyadat al-Maridh", 144),
    ('كِتَابُ آدَابِ السَّفَرِ', 'Kitab Adab as-Safar', 166),
    ('كِتَابُ الْفَضَائِلِ', "Kitab al-Fadha'il", 180),
    ('كِتَابُ الِاعْتِكَافِ', "Kitab al-I'tikaf", 232),
    ('كِتَابُ الْحَجِّ', 'Kitab al-Hajj', 233),
    ('كِتَابُ الْجِهَادِ', 'Kitab al-Jihad', 234),
    ('كِتَابُ الْعِلْمِ', "Kitab al-'Ilm", 241),
    ('كِتَابُ حَمْدِ اللَّهِ تَعَالَى وَشُكْرِهِ', 'Kitab Hamdillah wa Syukrih', 242),
    ('كِتَابُ الصَّلَاةِ عَلَى رَسُولِ اللَّهِ ﷺ', "Kitab ash-Shalah 'ala Rasulillah ﷺ", 243),
    ('كِتَابُ الْأَذْكَارِ', 'Kitab al-Adzkar', 244),
    ('كِتَابُ الدَّعَوَاتِ', "Kitab ad-Da'awat", 250),
    ('كِتَابُ الْأُمُورِ الْمَنْهِيِّ عَنْهَا', "Kitab al-Umur al-Manhiy 'anha", 254),
    ('كِتَابُ الْمَنْثُورَاتِ وَالْمُلَحِ', 'Kitab al-Mantsurat wal-Mulah', 370),
    ('كِتَابُ الِاسْتِغْفَارِ', 'Kitab al-Istighfar', 371),
]
def kitab_of(bn):
    k = 1
    for i, (_, _, b) in enumerate(KITAB):
        if b is not None and bn >= b:
            k = i
    return k

# ---------- 4. unit ----------
BAB = re.compile(r'^(\d+)\s*-\s*(بابُ?.*)$')
HAD = re.compile(r'^(\d+)\s*-\s*(.*)$')

FIX = []
KSEEN = []
groups = []
g = {'bn': 0, 'kt': 0, 'ar': 'مُقَدِّمَةُ الْمُؤَلِّفِ', 'tfn': [], 's': []}
unit = {'t': 'm', 'lines': [], 'blocks': set()}
g['s'].append(unit); groups.append(g)
last_h = 0
khatimah = False
for text, bi in stream:
    t = text.strip()
    if not t:
        continue
    if KIT.match(t):
        KSEEN.append([int(KIT.match(t).group(1)), t.split('-', 1)[1].strip(), g['bn'] + 1]); continue
    m = BAB.match(t)
    if m:
        bn = g['bn'] + 1
        if int(m.group(1)) != bn: FIX.append('bab %s tertulis %s' % (bn, m.group(1)))
        g = {'bn': bn, 'kt': kitab_of(bn), 'ar': m.group(2), 'tfn': [], 's': [], 'pg': blocks[bi]['pg']}
        groups.append(g); unit = None; continue
    m = HAD.match(t)
    if m and int(m.group(1)) == last_h + 1 and g['bn'] > 0:
        last_h += 1
        unit = {'t': 'h', 'no': last_h, 'lines': [m.group(2)], 'pg': blocks[bi]['pg'], 'blocks': {bi}}
        g['s'].append(unit); continue
    if last_h == 1896 and unit and unit['t'] == 'h' and bare(t).startswith('قال الله تعالى'):
        unit = {'t': 'x', 'lines': [], 'pg': blocks[bi]['pg'], 'blocks': set()}
        g['s'].append(unit)
    if unit is None:
        unit = {'t': 'a', 'lines': [], 'pg': blocks[bi]['pg'], 'blocks': set()}
        g['s'].insert(0, unit)
    unit['lines'].append(t); unit['blocks'].add(bi)

# judul bab: token catatan -> catatan bab
TOK = re.compile('\x01(\\d+):(\\d+)\x02')
for g in groups:
    fns = []
    def rep(m):
        fns.append(blocks[int(m.group(1))]['fn'][int(m.group(2))]); return ''
    g['ar'] = TOK.sub(rep, g['ar']).strip()
    g['tfn'] = fns

# ---------- 5. format HTML ----------
SAW = re.compile(r'\s*-\s*صلى الله عليه وسلم\s*-?')
def fmt(s):
    s = re.sub(r'\[ص:\s*\d+\]\s*', '', s)
    s = html.escape(s, quote=False)
    s = SAW.sub(' ﷺ ', s).replace(' ﷺ  ', ' ﷺ ').replace('ﷺ :', 'ﷺ:').replace('ﷺ ،', 'ﷺ،').replace('ﷺ .', 'ﷺ.')
    s = re.sub(r'\{([^{}]+)\}', r'<span class="q">﴿\1﴾</span>', s)
    s = re.sub(r'(\[[^\[\]]{2,40}:\s*[\d\s\-–]+\])', r'<span class="ref">\1</span>', s)
    s = re.sub(r'«([^«»]+)»', r'<span class="hd">«\1»</span>', s)
    return s

GLOSS = re.compile(r'^(و?معناه|و?معنى|و?قوله|قال العلماء|قال أهل اللغة|قلت|قال المصنف|«[^»]{1,60}»\s*(هو|بفتح|بضم|بكسر|بالفتح|بالضم|بالكسر|معناه|أي|:))')
RIW = re.compile(r'^(وفي رواية|وفي روايةٍ|ورواه|وفي لفظ|وفي حديث|وزاد)')

def build_unit(u):
    # kumpulkan catatan berurutan
    fnmap = {}; fnl = []
    def rep(m):
        key = (int(m.group(1)), int(m.group(2)))
        if key not in fnmap:
            fnl.append(blocks[key[0]]['fn'][key[1]]); fnmap[key] = len(fnl)
        return '<sup class="fn">%d</sup>' % fnmap[key]
    paras = []
    for i, l in enumerate(u['lines']):
        b = bare(l)
        cls = ''
        if u['t'] == 'h' and i > 0:
            if GLOSS.match(b): cls = 'sy'
            elif RIW.match(b): cls = 'rw'
        h = TOK.sub(rep, fmt(l))
        paras.append('<p%s>%s</p>' % (' class="%s"' % cls if cls else '', h))
    # catatan yang tidak tertaut (tak ada penanda di teks)
    for bi in sorted(u.get('blocks', ())):
        for n in blocks[bi]['fnorder']:
            if n not in blocks[bi].get('used', set()):
                blocks[bi].setdefault('used', set()).add(n)
                fnl.append(blocks[bi]['fn'][n]); fnmap[(bi, n)] = len(fnl)
                u['orph'] = u.get('orph', 0) + 1
    notes = []
    for i, f in enumerate(fnl, 1):
        kind = 'tk' if re.search(r'أخرجه|انظر الحديث|انظر حديث|سبق تخريجه|تقدم تخريجه', bare(f)) else 'ta'
        notes.append({'n': i, 'k': kind, 'h': TOK.sub('', fmt_fn(f))})
    return ''.join(paras), notes

def fmt_fn(f):
    parts = f.split('<br>')
    return '<br>'.join(fmt(p) for p in parts)

SRCMAP = [('البخاري', 'al-Bukhari'), ('مسلم', 'Muslim'), ('أبو داود', 'Abu Dawud'), ('الترمذي', 'at-Tirmidzi'),
          ('النسائي', "an-Nasa'i"), ('ابن ماجه', 'Ibnu Majah'), ('أحمد', 'Ahmad'), ('مالك', 'Malik'),
          ('الدارمي', 'ad-Darimi'), ('ابن حبان', 'Ibnu Hibban'), ('الحاكم', 'al-Hakim'), ('البيهقي', 'al-Baihaqi'),
          ('ابن خزيمة', 'Ibnu Khuzaimah'), ('الطبراني', 'ath-Thabarani'), ('الحميدي', 'al-Humaidi'), ('الطيالسي', 'ath-Thayalisi'),
          ('عبد الرزاق', "'Abdurrazzaq"), ('ابن أبي شيبة', 'Ibnu Abi Syaibah'), ('أبو يعلى', "Abu Ya'la")]
TK = re.compile(r'(' + '|'.join(re.escape(a) for a, _ in SRCMAP) + r')\s*(?:في\s+[^\d،,()]{2,40}?\s*)?(?:\d+\s*/\s*\d+(?:\s*[-–]\s*\d+)?\s*)?\((\d+)\)')
def chips_takhrij(notes):
    seen = []; out = []
    for n in notes:
        if n['k'] != 'tk': continue
        txt = bare(re.sub('<[^>]+>', '', n['h']))
        for m in TK.finditer(txt):
            name = dict(SRCMAP)[m.group(1)]
            key = (name, m.group(2))
            if key not in seen:
                seen.append(key); out.append([name, m.group(2)])
        for m in re.finditer(r'انظر\s+(?:الحديث|حديث)\s*(?:رقم)?\s*\((\d+)\)', txt):
            key = ('x', m.group(1))
            if key not in seen:
                seen.append(key); out.append(['x', m.group(1)])
    return out

ATTR = [('متفق عليه', "Muttafaq 'alaih"), ('رواه البخاري', 'Riwayat al-Bukhari'), ('رواه مسلم', 'Riwayat Muslim')]
def attrib(mt):
    b = bare(re.sub('<[^>]+>', '', mt))
    out = []
    if 'متفق عليه' in b or 'متفق على صحته' in b: out.append("Muttafaq 'alaih")
    m = re.search(r'رواه\s+([^.«»]{2,80})', b)
    if m:
        seg = m.group(1)
        for a, lat in SRCMAP:
            if re.search(r'(^|\s|و)' + re.escape(a), seg[:60]) and lat not in out:
                out.append(lat)
    for p, lab in [('حسن صحيح', 'hasan shahih'), ('حديث حسن', 'hasan'), ('حديث صحيح', 'shahih'), ('إسناد صحيح', 'sanad shahih'), ('إسناد حسن', 'sanad hasan')]:
        if p in b:
            out.append('Dinilai ' + lab); break
    return out

def snippet(mt):
    ps = re.findall(r'<p[^>]*>(.*?)</p>', mt)
    t = ps[0] if ps else mt
    t = re.sub('<sup[^>]*>.*?</sup>', '', t)
    t = re.sub('<[^>]+>', '', t)
    qs = re.findall(r'«([^«»]+)»', t)
    long = [q for q in qs if len(q.split()) >= 3]
    seg = long[0] if long else (max(qs, key=len) if qs and len(max(qs, key=len).split()) >= 2 else re.sub(r'^.*?ق[\u064b-\u0652]*ا[\u064b-\u0652]*ل[\u064b-\u0652]*(?:ت[\u064b-\u0652]*)?\s*:\s*', '', t, count=1))
    w = seg.split()
    s = ' '.join(w[:7]).rstrip('،,.:؛')
    return s + ('…' if len(w) > 7 else '')

def rawi(first):
    t = bare(re.sub('<[^>]+>', '', first))
    t = re.sub(r'^ف?ال(أول|ثاني|ثالث|رابع|خامس|سادس|سابع|ثامن|تاسع|عاشر)\S*\s*:?\s*', '', t)
    if re.match(r'^و?عنه(ا|ما|م)?\b', t): return '(rawi yang sama)'
    m = re.search(r'(?:^|\s)و?عن\s+(.+?)(?:\s*-?\s*رضي\s|\s+قال|\s*:|،|\s+أن)', t)
    if not m: return ''
    w = m.group(1).split()
    return ' '.join(w[:6]) + ('…' if len(w) > 6 else '')

groups[0]['s'][0]['lines'] = [l for l in groups[0]['s'][0]['lines'] if not bare(l).startswith('مقدمة المؤلف')]
PREV_RW = ''
DATA = []
stats = {'hadits': 0, 'bab': 0, 'orph': 0, 'tk': 0, 'ta': 0, 'unmarked_paren': 0}
for g in groups:
    S = []
    for u in g['s']:
        mt, notes = build_unit(u)
        stats['orph'] += u.get('orph', 0)
        for n in notes: stats[n['k']] += 1
        d = {'t': u['t'], 'mt': mt, 'fn': notes}
        if u.get('pg'): d['pg'] = u['pg']
        if u['t'] == 'h':
            stats['hadits'] += 1
            d['no'] = u['no']; d['tar'] = snippet(mt); d['src'] = attrib(mt); d['tc'] = chips_takhrij(notes)
            d['rw'] = rawi(u['lines'][0])
            if d['rw'] == '(rawi yang sama)':
                d['rw'] = PREV_RW
            elif d['rw']:
                PREV_RW = d['rw']
        S.append(d)
    if g['bn'] > 0: stats['bab'] += 1
    DATA.append({'bn': g['bn'], 'kt': g['kt'], 'ar': html.escape(g['ar'], quote=False), 'tfn': [fmt_fn(f) for f in g['tfn']], 'pg': g.get('pg'), 's': S})

json.dump({'KITAB': [{'ar': a, 'id': b, 'from': c} for a, b, c in KITAB], 'DATA': DATA}, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False)

# ---------- cek ----------
nums = [s['no'] for g in DATA for s in g['s'] if s['t'] == 'h']
stats['hadits_seq_ok'] = nums == list(range(1, len(nums) + 1))
stats['orphan_cont'] = orphan_cont
stats['bab_seq_ok'] = [g['bn'] for g in DATA] == list(range(0, len(DATA)))
stats['no_takhrij'] = [s['no'] for g in DATA for s in g['s'] if s['t'] == 'h' and not any(n['k'] == 'tk' for n in s['fn'])][:40]
stats['no_chip'] = sum(1 for g in DATA for s in g['s'] if s['t'] == 'h' and not s['tc'])
stats['no_rawi'] = [s['no'] for g in DATA for s in g['s'] if s['t'] == 'h' and not s['rw']][:30]
stats['bab_tanpa_hadits'] = [g['bn'] for g in DATA if g['bn'] and not any(s['t'] == 'h' for s in g['s'])]
stats['bab_tanpa_ayat'] = sum(1 for g in DATA if g['bn'] and not any(s['t'] == 'a' for s in g['s']))
leftover = sum(len(re.findall(r'\(\d{1,2}\)', s['mt'])) for g in DATA for s in g['s'])
stats['penanda_tak_tertaut'] = leftover
stats['fix']=FIX
stats['penanda_tanpa_kurung']=len(STRAY)
stats['kitab_ditemukan']=KSEEN
print(json.dumps(stats, ensure_ascii=False, indent=1))
