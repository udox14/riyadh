#!/usr/bin/env python3
"""Gabungkan kerangka (data.json) + syarah per bab (syarah/bab-NNN.json) menjadi HTML.

Pakai:
  python3 build.py            -> validasi + tulis dist/Riyadhus-Shalihin*.html + perbarui ringkasan PROGRES.md
  python3 build.py --cek      -> validasi saja, tidak menulis apa pun

Jilid: kalau ada jilid.json -> satu HTML per jilid. Formatnya:
  [{"nama": "Jilid 1", "file": "Riyadhus-Shalihin-1.html", "dari": 0, "sampai": 83}, ...]
  (dari/sampai = nomor bab; bab 0 = muqaddimah an-Nawawi)
Tanpa jilid.json -> satu file dist/Riyadhus-Shalihin.html.
"""
import json, os, re, sys, glob, datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
P = lambda *a: os.path.join(ROOT, *a)

# isian yang boleh ada di file syarah
UNIT_FIELDS = {'title', 'tier', 'mt', 'tr', 'nq', 'mf', 'mfn', 'rp', 'sb', 'ex', 'is', 'nt'}
BAB_FIELDS = {'bn', 'id', 'intro', 'ks', 'u', 'catatan'}
HTML_FIELDS = {'tr', 'nq', 'mf', 'rp', 'sb', 'ex', 'is', 'nt', 'intro', 'ks', 'mt'}
VOID = {'br', 'img', 'hr', 'rect', 'path', 'circle', 'line', 'ellipse', 'polygon', 'polyline', 'use', 'stop'}

def tag_balance(h):
    """Kembalikan daftar tag yang tidak seimbang (cek kasar)."""
    st = []
    errs = []
    for m in re.finditer(r'<(/?)([a-zA-Z][a-zA-Z0-9]*)\b[^>]*?(/?)>', h):
        close, name, selfc = m.group(1), m.group(2).lower(), m.group(3)
        if name in VOID or selfc:
            continue
        if not close:
            st.append(name)
        else:
            if st and st[-1] == name:
                st.pop()
            else:
                errs.append('</%s> tak berpasangan' % name)
                if name in st:
                    while st and st[-1] != name:
                        errs.append('<%s> tak ditutup' % st.pop())
                    st.pop()
    errs += ['<%s> tak ditutup' % t for t in st]
    return errs[:5]

def load():
    J = json.load(open(P('data.json'), encoding='utf-8'))
    D = J['DATA']
    byb = {g['bn']: g for g in D}
    keys = {}
    for g in D:
        for s in g['s']:
            k = 'h%d' % s['no'] if s['t'] == 'h' else 'a%d' % g['bn'] if s['t'] == 'a' else 'muqaddimah' if s['t'] == 'm' else 'penutup'
            keys[k] = (g, s)
    return J, D, byb, keys

def merge(J, D, byb, keys):
    errors, warns, done = [], [], []
    files = sorted(f for f in glob.glob(P('syarah', 'bab-*.json')))
    for f in files:
        name = os.path.basename(f)
        try:
            S = json.load(open(f, encoding='utf-8'))
        except Exception as e:
            errors.append('%s: JSON rusak (%s)' % (name, e)); continue
        bn = S.get('bn')
        m = re.match(r'bab-(\d+)\.json$', name)
        if not m or int(m.group(1)) != bn:
            errors.append('%s: nama file tidak cocok dengan "bn": %s' % (name, bn)); continue
        if bn not in byb:
            errors.append('%s: bab %s tidak ada' % (name, bn)); continue
        g = byb[bn]
        for k in S:
            if k not in BAB_FIELDS:
                errors.append('%s: isian bab tidak dikenal "%s"' % (name, k))
        for k in ('id', 'intro', 'ks'):
            if S.get(k):
                if k in HTML_FIELDS:
                    e = tag_balance(S[k])
                    if e: errors.append('%s %s: %s' % (name, k, '; '.join(e)))
                g[k] = S[k]
        for uk, U in (S.get('u') or {}).items():
            if uk not in keys:
                errors.append('%s: unit "%s" tidak dikenal' % (name, uk)); continue
            gg, s = keys[uk]
            if gg is not g:
                errors.append('%s: unit "%s" bukan milik Bab %s' % (name, uk, bn)); continue
            for fk, v in U.items():
                if fk not in UNIT_FIELDS:
                    errors.append('%s %s: isian tidak dikenal "%s"' % (name, uk, fk)); continue
                if fk in HTML_FIELDS and isinstance(v, str):
                    e = tag_balance(v)
                    if e: errors.append('%s %s.%s: %s' % (name, uk, fk, '; '.join(e)))
                if fk == 'mt':
                    a = re.findall(r'<sup class="fn">(\d+)</sup>', s['mt'])
                    b = re.findall(r'<sup class="fn">(\d+)</sup>', v)
                    if a != b:
                        errors.append('%s %s.mt: penanda catatan berubah %s -> %s' % (name, uk, a, b)); continue
                if fk == 'tier' and v not in ('A', 'B', 'C'):
                    errors.append('%s %s: tier harus A/B/C' % (name, uk)); continue
                s[fk] = v
            if s['t'] == 'h' and not U.get('tr'):
                warns.append('%s %s: belum ada terjemah (tr)' % (name, uk))
        done.append(bn)
    return errors, warns, done

def stats(D):
    H = [s for g in D for s in g['s'] if s['t'] == 'h']
    return {
        'bab_bersyarah': sum(1 for g in D if g['bn'] and (g.get('intro') or any(s.get('ex') or s.get('tr') for s in g['s']))),
        'hadits_terjemah': sum(1 for s in H if s.get('tr')),
        'hadits_syarah': sum(1 for s in H if s.get('ex')),
        'tier': {t: sum(1 for s in H if s.get('tier') == t) for t in 'ABC'},
        'total_hadits': len(H), 'total_bab': sum(1 for g in D if g['bn']),
    }

def js(o):
    return json.dumps(o, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')

def render(J, D, title=None):
    tpl = open(P('template.html'), encoding='utf-8').read()
    style = open(P('style.css'), encoding='utf-8').read()
    out = tpl.replace('{{STYLE}}', style).replace('{{KITAB}}', js(J['KITAB'])).replace('{{DATA}}', js(D))
    if title:
        out = out.replace('<title>Riyadhus Shalihin</title>', '<title>Riyadhus Shalihin · %s</title>' % title, 1)
        out = out.replace('<p class="brand-lat">Riyadhus Shalihin</p>', '<p class="brand-lat">Riyadhus Shalihin · %s</p>' % title, 1)
    return out

def update_progres(st, done):
    f = P('PROGRES.md')
    if not os.path.exists(f):
        return
    t = open(f, encoding='utf-8').read()
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).strftime('%Y-%m-%d %H:%M WIB')
    block = ('<!-- OTOMATIS:MULAI -->\n'
             '_Diperbarui build.py, %s_\n\n'
             '- Bab bersyarah: **%d / %d**\n'
             '- Hadits berterjemah: **%d / %d** · bersyarah: **%d**\n'
             '- Tingkat: A %d · B %d · C %d\n'
             '- File syarah: %s\n'
             '<!-- OTOMATIS:SELESAI -->') % (
        now, st['bab_bersyarah'], st['total_bab'], st['hadits_terjemah'], st['total_hadits'], st['hadits_syarah'],
        st['tier']['A'], st['tier']['B'], st['tier']['C'], ', '.join('bab-%03d' % b for b in done) or '(belum ada)')
    t = re.sub(r'<!-- OTOMATIS:MULAI -->.*?<!-- OTOMATIS:SELESAI -->', block, t, flags=re.S)
    open(f, 'w', encoding='utf-8').write(t)

def main():
    cek = '--cek' in sys.argv
    J, D, byb, keys = load()
    errors, warns, done = merge(J, D, byb, keys)
    st = stats(D)
    for w in warns[:20]:
        print('PERINGATAN', w)
    for e in errors:
        print('GALAT', e)
    print('Ringkasan:', json.dumps(st, ensure_ascii=False))
    if errors:
        print('Build dibatalkan: perbaiki galat di atas.'); sys.exit(1)
    if cek:
        print('Cek OK.'); return
    os.makedirs(P('dist'), exist_ok=True)
    jf = P('jilid.json')
    outs = []
    if os.path.exists(jf):
        for j in json.load(open(jf, encoding='utf-8')):
            sub = [g for g in D if j['dari'] <= g['bn'] <= j['sampai']]
            outs.append((j['file'], render(J, sub, j['nama'])))
    else:
        outs.append(('Riyadhus-Shalihin.html', render(J, D)))
    for fn, html in outs:
        open(P('dist', fn), 'w', encoding='utf-8').write(html)
        mb = len(html.encode('utf-8')) / 1e6
        print('Tulis dist/%s  %.2f MB%s' % (fn, mb, '  <-- MENDEKATI 5 MB, saatnya pecah jilid (buat/ubah jilid.json)' if mb > 4.5 else ''))
    update_progres(st, done)

if __name__ == '__main__':
    main()
