#!/usr/bin/env python3
"""Bangun indeks Dalil al-Falihin -> nomor hadits al-Fahl.
Pakai: python3 sumber/index_dalil.py   (membaca sumber/dalil-falihin.txt dan data.json, menulis sumber/dalil-index.json)"""
import re, json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L = open(os.path.join(ROOT, 'sumber', 'dalil-falihin.txt'), encoding='utf-8').read().split('\n')
D = json.load(open(os.path.join(ROOT, 'data.json'), encoding='utf-8'))['DATA']

HAR = re.compile('[ً-ْٰـ]')
def norm(s):
    s = HAR.sub('', s)
    s = re.sub('[أإآٱ]', 'ا', s).replace('ى', 'ي').replace('ة', 'ه').replace('ؤ', 'و').replace('ئ', 'ي')
    return re.sub('[^ء-ي]', '', s)
def grams(s, n=5):
    return {s[i:i + n] for i in range(max(0, len(s) - n + 1))}

H = []  # (no, bn, gramset)
for g in D:
    for s in g['s']:
        if s['t'] == 'h':
            t = re.sub('<sup[^>]*>.*?</sup>', '', s['mt'])
            t = re.sub('<p class="sy">.*?</p>', '', t)
            H.append((s['no'], g['bn'], grams(norm(re.sub('<[^>]+>', ' ', t)))))

PAGE = re.compile(r'^\((\d+)/(\d+)\)$')
ENT = re.compile(r'^\s*\d+\s*[-ـ–]+\s*(?!\(?«?(?:باب|كت|والله أعلم|وأما|قال الله|وقال تعالى))')
LEADNUM = re.compile(r'^\s*(\d+)')
ENT2 = re.compile(r'^\s*\((?:و?عن\s|و?عَنْ\s|الحديث|فال?أول|ال(?:أول|ثاني|ثالث|رابع|خامس|سادس|سابع|ثامن|تاسع|عاشر|حادي|ثاني عشر)\S*\s*:?\s*عن)')
BAB = re.compile(r'^\s*\d+\s*[-ـ–]+\s*\(?«?(باب|كتَ?اب)')

# halaman tiap baris: penanda (j/p) ada di AKHIR halaman
page = [None] * len(L); cur = None
for i in range(len(L) - 1, -1, -1):
    m = PAGE.match(L[i].strip())
    if m: cur = '%s/%s' % (m.group(1), m.group(2))
    page[i] = cur

def frag(i):
    """ambil potongan dalam kurung (matan) dari awal entri"""
    head = re.sub(r'^\s*\d+\s*[-ـ–]+\s*', '', L[i])
    if not head.lstrip().startswith('(') and not head.lstrip().startswith('الحديث') and '(' not in head[:40]:
        return norm(head)[:260]
    t = ' '.join(L[i:i + 4])[:5000]
    parts = re.findall(r'\(([^()]{2,400})\)', t)
    parts = [x for x in parts if not re.match(r'^\s*[\d/:\s]+$', x)]
    s = norm(' '.join(parts))[:260]
    return s if len(s) > 12 else norm(t)[:220]

starts = {}  # no -> line
# --- pencocokan global: kandidat per entri lewat indeks n-gram, lalu rangkaian naik berskor maksimum ---
from collections import defaultdict
inv = defaultdict(list)
for j, h in enumerate(H):
    for gm in h[2]: inv[gm].append(j)
cands = []  # (line, [(j, score)])
NOIDX = {h[0]: j for j, h in enumerate(H)}
for i, l in enumerate(L):
    numbered = bool(ENT.match(l))
    if BAB.match(l) or not (numbered or ENT2.match(l)): continue
    f = grams(frag(i))
    if len(f) < 8: continue
    cnt = defaultdict(int)
    for gm in f:
        for j in inv.get(gm, ()): cnt[j] += 1
    mnum = LEADNUM.match(l)
    suf = set()
    if mnum:
        d = mnum.group(1)
        for k in range(1, min(4, len(d)) + 1): suf.add(int(d[-k:]))
    def bonus(j):
        no = H[j][0]
        if no in suf and len(str(no)) >= 2: return 0.25
        if any(abs(no - x) <= 2 for x in suf if x >= 10): return 0.05
        return 0.0
    for x in suf:
        for no in range(x - 2, x + 3):
            jj = NOIDX.get(no)
            if jj is not None and jj not in cnt: cnt[jj] = 0
    top = sorted((((c / len(f)) + bonus(j), j) for j, c in cnt.items()), reverse=True)[:6]
    top = [(j, sc) for sc, j in top if sc >= (0.3 if numbered else 0.45) and (cnt[j] / len(f)) >= 0.18]
    if top:
        b0 = top[0][1]
        top = [(j, sc) for j, sc in top if sc >= b0 - 0.12]
    if top: cands.append((i, top))
# Fenwick max untuk LIS berbobot (indeks hadits naik ketat)
M = len(H)
tree = [(0.0, -1)] * (M + 1)
def upd(pos, val):
    pos += 1
    while pos <= M:
        if val[0] > tree[pos][0]: tree[pos] = val
        pos += pos & -pos
def qry(pos):  # maksimum untuk indeks < pos
    r = (0.0, -1)
    while pos > 0:
        if tree[pos][0] > r[0]: r = tree[pos]
        pos -= pos & -pos
    return r
nodes = []  # (score_total, prev_node, line, j)
for i, top in cands:
    new = []
    for j, sc in top:
        best = qry(j)
        new.append((best[0] + sc, best[1], i, j))
    for nd in new:
        nodes.append(nd); upd(nd[3], (nd[0], len(nodes) - 1))
end = qry(M)[1]
while end != -1:
    tot, prev, i, j = nodes[end]
    starts[H[j][0]] = i
    end = prev
# --- isi celah: entri tak terpakai di antara dua hadits yang sudah cocok ---
used = set(starts.values())
entry_lines = [i for i, l in enumerate(L) if not BAB.match(l) and (ENT.match(l) or ENT2.match(l))]
seq = [h[0] for h in H]
filled = 0
known = sorted((starts[n], n) for n in starts)
pos_of = {n: k for k, n in enumerate(seq)}
for (la, na), (lb, nb) in zip(known, known[1:]):
    missing = seq[pos_of[na] + 1:pos_of[nb]]
    if not missing: continue
    free = [i for i in entry_lines if la < i < lb and i not in used]
    k = 0
    for n in missing:
        hg = H[pos_of[n]][2]
        while k < len(free):
            i = free[k]; k += 1
            f = grams(frag(i))
            if f and len(f & hg) / len(f) >= 0.2:
                starts[n] = i; used.add(i); filled += 1; break
print('celah terisi:', filled)
first_line = min(starts.values())

# bab: baris judul
babs = {}
for i, l in enumerate(L):
    m = BAB.match(l)
    if m and i >= first_line - 50:
        babs.setdefault('raw', []).append(i)

nos = [h[0] for h in H]
bn_of = {h[0]: h[1] for h in H}
idx = {'hadits': {}, 'bab': {}}
order = sorted(starts.items(), key=lambda x: x[1])
for k, (no, st) in enumerate(order):
    en = order[k + 1][1] if k + 1 < len(order) else len(L)
    # potong di judul bab berikutnya bila ada di antaranya
    for b in babs['raw']:
        if st < b < en: en = b; break
    idx['hadits'][no] = [st, en, page[st], page[min(en, len(L) - 1) - 1]]
# pengantar bab: dari judul bab sampai hadits pertama bab itu
first_of_bab = {}
for no in nos:
    first_of_bab.setdefault(bn_of[no], no)
for bn, no in first_of_bab.items():
    if no in idx['hadits']:
        st = idx['hadits'][no][0]
        hb = [b for b in babs['raw'] if b < st]
        if hb and st - hb[-1] < 400:
            idx['bab'][bn] = [hb[-1], st, page[hb[-1]]]
json.dump(idx, open(os.path.join(ROOT, 'sumber', 'dalil-index.json'), 'w', encoding='utf-8'))
miss = [n for n in nos if n not in idx['hadits']]
print('hadits terindeks: %d / %d; pengantar bab: %d' % (len(idx['hadits']), len(nos), len(idx['bab'])))
print('tanpa awal tersendiri (syarahnya menyatu dengan hadits sebelumnya):', len(miss), miss[:60])

# ---- hadits tanpa entri: cari di mana matannya dibahas ----
NL = [norm(l) for l in L]
offs = []; full = []; pos = 0
for i, l in enumerate(NL):
    offs.append(pos); full.append(l); pos += len(l)
FULL = ''.join(full)
import bisect
def line_of(off): return bisect.bisect_right(offs, off) - 1
spans = sorted((v[0], v[1], int(k)) for k, v in idx['hadits'].items())
def owner(line):
    for st, en, no in spans:
        if st <= line < en: return no
    return None
mt_of = {}
for g in D:
    for s in g['s']:
        if s['t'] == 'h':
            t = re.sub('<sup[^>]*>.*?</sup>', '', s['mt']); t = re.sub('<p class="sy">.*?</p>', '', t)
            q = re.findall(r'«([^«»]+)»', re.sub('<[^>]+>', '', t))
            mt_of[s['no']] = norm(' '.join(q) if q else re.sub('<[^>]+>', '', t))
idx['lain'] = {}
for n in miss:
    q = mt_of.get(n, '')
    hits = []
    for a in (0.15, 0.45, 0.75):
        k = int(len(q) * a); chunk = q[k:k + 22]
        if len(chunk) < 16: continue
        o = FULL.find(chunk)
        if o >= 0: hits.append(line_of(o))
    if hits:
        ln = min(hits); ow = owner(ln)
        idx['lain'][n] = ['menyatu' if ow == n - 1 or (ow and bn_of.get(ow) == bn_of[n]) else 'dibahas', ow, ln, page[ln]]
    else:
        idx['lain'][n] = ['tidak ada', None, None, None]
json.dump(idx, open(os.path.join(ROOT, 'sumber', 'dalil-index.json'), 'w', encoding='utf-8'))
import collections
print('status hadits tanpa entri:', dict(collections.Counter(v[0] for v in idx['lain'].values())))
