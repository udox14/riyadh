#!/usr/bin/env python3
"""Keluarkan isi satu atau beberapa bab dalam bentuk ringkas untuk dikerjakan.

Pakai:
  python3 ambil.py 1          -> bab 1: judul, ayat bab, matan tiap hadits, takhrij, catatan al-Fahl
  python3 ambil.py 5-7        -> bab 5 s.d. 7
  python3 ambil.py 1 --html   -> sertakan HTML matan apa adanya (perlu kalau mau menulis ulang mt berharakat penuh)
  python3 ambil.py 1 --dalil  -> sertakan syarah Dalil al-Falihin (Ibnu 'Allan) per unit, dengan penanda ‹jilid/halaman›
  python3 ambil.py h7 --dalil -> satu hadits saja (nomor al-Fahl)
  python3 ambil.py a1 --dalil -> ayat/pengantar Bab 1 saja
  python3 ambil.py --daftar   -> daftar semua bab: nomor, jumlah hadits, rentang nomor hadits, status syarah
"""
import json, os, re, sys, glob, signal
if hasattr(signal, 'SIGPIPE'): signal.signal(signal.SIGPIPE, signal.SIG_DFL)

ROOT = os.path.dirname(os.path.abspath(__file__))
J = json.load(open(os.path.join(ROOT, 'data.json'), encoding='utf-8'))
D = J['DATA']; K = J['KITAB']
DONE = {int(re.search(r'(\d+)', os.path.basename(f)).group(1)) for f in glob.glob(os.path.join(ROOT, 'syarah', 'bab-*.json'))}

def txt(h):
    h = re.sub(r'<sup class="fn">(\d+)</sup>', r'[\1]', h or '')
    h = re.sub(r'</p>\s*<p class="sy">', '\n  {an-Nawawi} ', h)
    h = re.sub(r'</p>\s*<p[^>]*>', '\n  ', h)
    h = re.sub(r'<br\s*/?>', '\n    ', h)
    return re.sub(r'<[^>]+>', '', h).strip()

args = [a for a in sys.argv[1:] if not a.startswith('--')]
DALIL = None
if '--dalil' in sys.argv:
    DL = open(os.path.join(ROOT, 'sumber', 'dalil-falihin.txt'), encoding='utf-8').read().split('\n')
    DI = json.load(open(os.path.join(ROOT, 'sumber', 'dalil-index.json'), encoding='utf-8'))
    DALIL = True
def dalil_lines(a, b):
    out = []
    for l in DL[a:b]:
        t = l.strip()
        if not t: continue
        m = re.match(r'^\((\d+)/(\d+)\)$', t)
        if m: out.append('    ‹akhir hlm. %s/%s›' % (m.group(1), m.group(2))); continue
        if t.startswith('______'): out.append('    [catatan pentahqiq Dalil:]'); continue
        out.append('    ' + t)
    return '\n'.join(out)
def dalil_unit(key, bn):
    if key.startswith('a'):
        v = DI['bab'].get(str(bn))
        return ('  >> DALIL AL-FALIHIN (pengantar bab, mulai hlm. %s)\n' % v[2] + dalil_lines(v[0], v[1])) if v else '  >> DALIL: pengantar bab tidak terindeks'
    n = key[1:]
    v = DI['hadits'].get(n)
    if v:
        return '  >> DALIL AL-FALIHIN (hlm. %s–%s)\n' % (v[2], v[3]) + dalil_lines(v[0], v[1])
    w = DI['lain'].get(n, ['tidak ada', None, None, None])
    if w[0] == 'tidak ada':
        return '  >> DALIL: tidak ada syarah untuk hadits ini di Dalil al-Falihin (kemungkinan pengulangan yang dilewati)'
    return ('  >> DALIL: %s %s, hlm. %s; kutipan sekitar:\n' % ('menyatu dengan syarah hadits' if w[0] == 'menyatu' else 'dibahas di bagian hadits', w[1], w[3])) + dalil_lines(max(0, w[2] - 1), w[2] + 6)
if '--daftar' in sys.argv:
    for g in D:
        if not g['bn']: continue
        hs = [s['no'] for s in g['s'] if s['t'] == 'h']
        rng = '%d-%d' % (hs[0], hs[-1]) if hs else '-'
        print('%3d  %-3s %2d hadits  no.%-10s %s %s' % (g['bn'], '✓' if g['bn'] in DONE else '', len(hs), rng, K[g['kt']]['id'][:22], re.sub('<[^>]+>', '', g['ar'])[:60]))
    sys.exit()
if not args:
    print(__doc__); sys.exit()
ONLY = None
if args[0].startswith('h'):
    ONLY = 'h' + args[0][1:]
    lo = hi = next(g['bn'] for g in D for s in g['s'] if s['t'] == 'h' and s['no'] == int(args[0][1:]))
elif args[0].startswith('a'):
    ONLY = args[0]; lo = hi = int(args[0][1:])
else:
    a, _, b = args[0].partition('-')
    lo, hi = int(a), int(b or a)
for g in D:
    if not (lo <= g['bn'] <= hi): continue
    print('=' * 70)
    print('BAB %d  ·  %s  ·  hlm. %s%s' % (g['bn'], K[g['kt']]['id'], g.get('pg'), '  ·  (file syarah sudah ada)' if g['bn'] in DONE else ''))
    print(re.sub('<[^>]+>', '', g['ar']))
    for i, t in enumerate(g.get('tfn') or [], 1):
        print('  catatan judul [%d] %s' % (i, txt(t)))
    for s in g['s']:
        key = 'h%d' % s['no'] if s['t'] == 'h' else 'a%d' % g['bn'] if s['t'] == 'a' else s['t']
        if ONLY and key != ONLY: continue
        print('-' * 70)
        if s['t'] == 'h':
            print('[%s] hlm.%s · rawi: %s · %s · takhrij: %s' % (key, s.get('pg'), s.get('rw'), ', '.join(s.get('src') or []) or '-',
                  ', '.join(('lihat no.' + x[1]) if x[0] == 'x' else '%s %s' % tuple(x) for x in s.get('tc') or []) or '-'))
        else:
            print('[%s] %s' % (key, 'Ayat & pengantar bab' if s['t'] == 'a' else s['t']))
        print('  ' + txt(s['mt']))
        for n in s.get('fn') or []:
            print('  (%s %d) %s' % ('takhrij' if n['k'] == 'tk' else 'tahqiq', n['n'], txt(n['h'])))
        if '--html' in sys.argv:
            print('  HTML: ' + s['mt'])
        if DALIL and key[0] in 'ah':
            print(dalil_unit(key, g['bn']))
