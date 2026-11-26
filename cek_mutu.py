#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pengunci Mutu Standar Emas Bab 1 — Syarah Riyadhus Shalihin (Universal Bab 1–372, Juz 1–8).

Wajib dijalankan sebelum `python build.py` pada setiap bab yang dikerjakan:
  python cek_mutu.py 84           -> cek Bab 84 saja
  python cek_mutu.py 84-90        -> cek Bab 84 s.d. 90
  python cek_mutu.py 6-83         -> cek rentang penuh

Memeriksa (dikalibrasi terhadap syarah/bab-001.json & PANDUAN.md §4–§8):
  1. Kedalaman prosa MURNI (diukur DI LUAR kode <svg>...</svg>):
     - Tier A: prosa >= 8.500c, >= 8 <h4>, >= 3 Dalil (bila panjang), sb >= 150c,
               >= 2 .tbl.cmp, >= 1 .irab, >= 1 .faidah, >= 1 .viz,
               is >= 1.200c (.cards + .kasus), nt .nb-k (>= 3 .kr)
     - Tier B: prosa >= 3.400c, >= 4 <h4>, >= 2 Dalil (bila panjang), sb >= 120c,
               >= 1 .tbl.cmp, >= 1 .viz, is >= 650c (.cards), nt .nb-k (>= 2 .kr)
     - Tier C: prosa >= 1.600c, >= 2 <h4>, >= 1 Dalil (bila tersedia),
               is >= 220c, nt .nb-k (>= 1 .kr pada >= 60% Tier C per bab)
  2. Kutipan Arab <figure class="dalil"> 100% verbatim & cocok nomor halaman (Juz 1–8)
  3. Kosakata (mf) Standar Emas Bab 1: 3 kolom Lafaz|Arti|Keterangan, 0 <thead>/<tbody>,
     mfn tepat, 0 transliterasi miring di kolom Arti, sr% >= 80%, rata-rata Keterangan >= 75c
  4. Visual SVG: whitelist kelas resmi style.css, 0 warna #hex, aman mode gelap,
     XML valid, bebas overflow teks desktop/ponsel
  5. Kebersihan: unit lengkap sesuai data.json, 0 mt, 0 <a href="#, 0 'tobat',
     .peta native (<b>+<small>), tag HTML seimbang, dan deteksi anti-boilerplate
"""
import json, math, pathlib, re, sys, xml.etree.ElementTree as ET
sys.stdout.reconfigure(encoding="utf-8")

ROOT = pathlib.Path(__file__).resolve().parent
SYARAH = ROOT / "syarah"
CSS = (ROOT / "style.css").read_text(encoding="utf-8")
VALID_SV = set(re.findall(r"\.(sv-[a-zA-Z0-9_-]+)", CSS))
TEXT_FILL_OK = {"sv-t", "sv-s", "sv-n", "sv-ar", "sv-acc-t", "sv-bad-t", "sv-q-t", "sv-gold-t"}
VOID = {'br', 'img', 'hr', 'rect', 'path', 'circle', 'line', 'ellipse', 'polygon', 'polyline', 'use', 'stop'}

def tag_balance(h):
    st, errs = [], []
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
                errs.append(f'</{name}> unmatched')
                if name in st:
                    while st and st[-1] != name:
                        errs.append(f'<{st.pop()}> unclosed')
                    st.pop()
    errs += [f'<{t}> unclosed' for t in st]
    return errs[:5]

def norm(s):
    return re.sub(r"\s+", " ", s).strip()

# Muat peta unit dari data.json agar otomatis berlaku untuk Bab 1–372
DATA_J = json.loads((ROOT / "data.json").read_text(encoding="utf-8"))
EXPECTED_UNITS = {}
for g in DATA_J["DATA"]:
    bn = g.get("bn")
    if not bn:
        continue
    EXPECTED_UNITS[bn] = [
        f"h{s['no']}" if s["t"] == "h" else f"a{bn}"
        for s in g["s"] if s["t"] in ("h", "a")
    ]

# Muat seluruh Dalil al-Falihin (Juz 1–8) & indeks per hadits
DALIL_LINES = (ROOT / "sumber" / "dalil-falihin.txt").read_text(encoding="utf-8").split("\n")
DALIL_INDEX = json.loads((ROOT / "sumber" / "dalil-index.json").read_text(encoding="utf-8"))

page_of_line = [None] * len(DALIL_LINES)
cur_start = 0
for i, l in enumerate(DALIL_LINES):
    m = re.match(r"^\((\d+/\d+)\)$", l.strip())
    if m:
        pg = m.group(1)
        for k in range(cur_start, i + 1):
            page_of_line[k] = pg
        cur_start = i + 1

page_text = {}
acc_parts = []
spans = []
pos_cur = 0
for i, txt in enumerate(DALIL_LINES):
    pg = page_of_line[i]
    if not pg:
        continue
    t = txt.strip()
    if not t or re.match(r"^\(\d+/\d+\)$", t):
        continue
    page_text.setdefault(pg, []).append(t)
    if acc_parts:
        pos_cur += 1
    s0 = pos_cur
    acc_parts.append(t)
    pos_cur += len(t)
    spans.append((s0, pos_cur, pg))
page_str = {pg: norm(" ".join(v)) for pg, v in page_text.items()}
acc_all = " ".join(acc_parts)

def dalil_len_for(uid):
    if not uid.startswith("h"):
        return 1000
    v = DALIL_INDEX.get("hadits", {}).get(uid[1:])
    if not v:
        return 0
    return sum(len(x) for x in DALIL_LINES[v[0]:v[1]])

def find_quote_pages(q, cite_pgs):
    if cite_pgs:
        for cp in cite_pgs:
            j, p = [int(x) for x in cp.split("/")]
            for dp in (0, -1, 1):
                p1 = f"{j}/{p+dp}"
                p2 = f"{j}/{p+dp+1}"
                if p1 in page_str and q in page_str[p1]:
                    return True, [p1]
                if p1 in page_str and p2 in page_str:
                    if q in (page_str[p1] + " " + page_str[p2]):
                        return True, [p1, p2]
    p0 = acc_all.find(q)
    if p0 == -1:
        return False, []
    pages = set()
    start = 0
    while True:
        idx = acc_all.find(q, start)
        if idx == -1:
            break
        # binary search spans
        lo_s, hi_s = 0, len(spans) - 1
        while lo_s <= hi_s:
            mid = (lo_s + hi_s) // 2
            if spans[mid][1] <= idx:
                lo_s = mid + 1
            elif spans[mid][0] > idx:
                hi_s = mid - 1
            else:
                lo_s = mid
                break
        k = max(0, lo_s - 1)
        while k < len(spans) and spans[k][0] < idx + len(q):
            if spans[k][1] > idx:
                pages.add(spans[k][2])
            k += 1
        start = idx + 1
        if len(pages) > 8:
            break
    return True, sorted(pages, key=lambda x: tuple(int(z) for z in x.split("/")))

AR_DIAC = re.compile(r'[\u064B-\u065F\u0670\u0640]')

def svg_text_box(text, cls, el, tx, ty, anchor):
    t = re.sub(r"<[^>]+>", "", text or "")
    st_low = (el.attrib.get("style", "") or "").lower()
    m_fs = re.search(r"font-size\s*:\s*([\d.]+)\s*px", st_low)
    c = (cls or "").split()
    if m_fs:
        fs = float(m_fs.group(1))
    elif "sv-ar" in c:
        fs = 22.0
    elif "sv-t" in c:
        fs = 15.5
    elif "sv-lb" in c:
        fs = 15.0
    elif "sv-s" in c or "sv-cn" in c:
        fs = 13.0
    elif "sv-n" in c:
        fs = 12.0
    else:
        fs = 13.0
    is_ar = ("sv-ar" in c)
    is_bold = ("sv-t" in c) or (el.attrib.get("font-weight", "") in ("600", "700", "bold"))
    ls_zero = bool(re.search(r"letter-spacing\s*:\s*0", st_low))
    extra_ls = (0.0 if ls_zero else 0.06 * fs) if "sv-n" in c else 0.0
    base = AR_DIAC.sub("", t)
    w = 0.0
    if is_ar:
        for ch in base:
            if ch == " ": w += fs * 0.28
            elif ch in "اأإآرذدزوةء": w += fs * 0.38
            elif ch in "سشصض": w += fs * 0.70
            elif "\u0600" <= ch <= "\u06FF": w += fs * 0.50
            else: w += fs * 0.55
    else:
        scale = 0.57 * (1.06 if is_bold else 1.0)
        for ch in base:
            if ch in " ilI1.,:;!'|()[]·-–": w += fs * scale * 0.52 + extra_ls
            elif ch in "MWm@—": w += fs * scale * 1.42 + extra_ls
            elif ch == "ﷺ": w += fs * 1.15
            elif "\u0600" <= ch <= "\u06FF": w += fs * 0.52
            else: w += fs * scale + extra_ls
    if anchor == "middle": x0, x1 = tx - w / 2.0, tx + w / 2.0
    elif anchor == "end": x0, x1 = tx - w, tx
    else: x0, x1 = tx, tx + w
    asc = fs * (0.76 if not is_ar else 0.72)
    desc = fs * (0.24 if not is_ar else 0.30)
    return x0, x1, ty - asc, ty + desc, w, fs

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)
    a, _, b = sys.argv[1].partition("-")
    lo, hi = int(a), int(b or a)

    tot_issues = 0
    tot_h = 0
    tot_q = 0
    tot_svg = 0
    tier_counts = {"A": 0, "B": 0, "C": 0}
    seen_paras = {}
    dup_paras = 0

    for bn in range(lo, hi + 1):
        p = SYARAH / f"bab-{bn:03d}.json"
        if not p.exists():
            print(f"  [MISSING FILE] bab-{bn:03d}.json")
            tot_issues += 1
            continue
        raw_json = p.read_text(encoding="utf-8")
        bab = json.loads(raw_json)
        bi = 0
        bq = 0
        bs = 0
        b_mf_rows = 0
        b_sr_rows = 0
        b_ket_sum = 0
        b_prose_a, b_prose_b, b_prose_c = [], [], []
        c_total = 0
        c_with_nb = 0

        if bab.get("bn") != bn:
            print(f"  [BN ERR] bab-{bn:03d}: bn={bab.get('bn')}"); bi += 1
        cid = bab.get("id", "")
        if len(cid) < 6 or re.match(r"^b\d+$", cid):
            print(f"  [TITLE ERR] bab-{bn:03d}: id={cid!r}"); bi += 1
        if '<a href="#' in raw_json:
            print(f"  [LINK ERR] bab-{bn:03d}: raw <a href=\"#...\">"); bi += 1
        if re.search(r"\btobat\b", raw_json, re.I):
            print(f"  [EJAAN ERR] bab-{bn:03d}: pakai 'tobat' (harus 'taubat')"); bi += 1
        for topk in ("intro", "ks"):
            tb = tag_balance(bab.get(topk, ""))
            if tb:
                print(f"  [HTML ERR] bab-{bn:03d}.{topk}: {tb}"); bi += 1
        peta_m = re.search(r'<div class="peta">(.*?)</div>\s*$', bab.get("intro", ""), re.S)
        if not peta_m:
            print(f"  [PETA ERR] bab-{bn:03d}: intro tidak ditutup <div class=\"peta\">"); bi += 1
        else:
            pi = peta_m.group(1)
            if "peta-card" in pi or "<strong>" in pi or "<br" in pi or "<b>" not in pi or "<small>" not in pi:
                print(f"  [PETA FORMAT ERR] bab-{bn:03d}: .peta harus memakai <b>+<small> native"); bi += 1
        if not bab.get("ks", "").startswith('<ol class="ksl">'):
            print(f"  [KS ERR] bab-{bn:03d}: ks tidak diawali <ol class=\"ksl\">"); bi += 1
        exp_u = set(EXPECTED_UNITS.get(bn, []))
        act_u = set(bab.get("u", {}).keys())
        if exp_u and act_u != exp_u:
            print(f"  [UNIT ERR] bab-{bn:03d}: missing={sorted(exp_u-act_u)} extra={sorted(act_u-exp_u)}"); bi += 1

        for uk, u in bab["u"].items():
            if "mt" in u:
                print(f"  [MT ERR] bab-{bn:03d} {uk}: jangan tulis field mt"); bi += 1
            for fk in ("tr", "nq", "mf", "rp", "sb", "ex", "is", "nt"):
                v = u.get(fk)
                if isinstance(v, str):
                    tb = tag_balance(v)
                    if tb:
                        print(f"  [HTML ERR] bab-{bn:03d} {uk}.{fk}: {tb}"); bi += 1

            # Kosakata (mf) Standar Emas Bab 1
            if u.get("mf"):
                mf = u["mf"]
                if "<thead" in mf or "<tbody" in mf:
                    print(f"  [MF THEAD] bab-{bn:03d} {uk}: dilarang pakai <thead>/<tbody>"); bi += 1
                if not mf.startswith("<table><tr><th>Lafaz</th><th>Arti</th><th>Keterangan</th></tr>"):
                    print(f"  [MF HDR] bab-{bn:03d} {uk}: header harus persis 3 kolom Lafaz|Arti|Keterangan"); bi += 1
                trs = [tr for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", mf, re.S) if "<td" in tr]
                if u.get("mfn") != len(trs):
                    print(f"  [MFN ERR] bab-{bn:03d} {uk}: mfn={u.get('mfn')} rows={len(trs)}"); bi += 1
                if uk.startswith("h"):
                    min_r = 5 if u.get("tier") == "A" else (4 if u.get("tier") == "B" else 3)
                    if len(trs) < min_r:
                        print(f"  [MF DEPTH] bab-{bn:03d} {uk} (Tier {u.get('tier')}): {len(trs)} < {min_r}"); bi += 1
                for r_idx, tr in enumerate(trs, 1):
                    tds = re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)
                    if len(tds) != 3:
                        print(f"  [MF COL] bab-{bn:03d} {uk} row {r_idx}: {len(tds)} kolom != 3"); bi += 1; continue
                    b_mf_rows += 1
                    if 'class="sr"' in tds[0]:
                        b_sr_rows += 1
                    arti = tds[1].strip()
                    if arti.startswith("<em>") and arti.endswith("</em>"):
                        print(f"  [MF ARTI ITALIC] bab-{bn:03d} {uk} row {r_idx}: {arti}"); bi += 1
                    ket = re.sub(r"<[^>]+>", "", tds[2]).strip()
                    b_ket_sum += len(ket)
                    if len(ket) < 40:
                        print(f"  [MF KET SHORT] bab-{bn:03d} {uk} row {r_idx}: len={len(ket)}"); bi += 1

            # Kutipan verbatim Dalil & SVG checks
            u_dalil_cnt = 0
            for fk, h in u.items():
                if not isinstance(h, str):
                    continue
                for m in re.finditer(r'<figure class="dalil"><p class="dq" lang="ar">(.*?)</p><figcaption>.*?</figcaption><cite>(.*?)</cite></figure>', h, re.S):
                    bq += 1; tot_q += 1; u_dalil_cnt += 1
                    q, cite = norm(m.group(1)), m.group(2)
                    cite_pgs = re.findall(r"[1-8]/\d+", cite)
                    ok, pages = find_quote_pages(q, cite_pgs)
                    if not ok:
                        print(f"  [QUOTE MISMATCH] bab-{bn:03d} {uk}.{fk}: cite={cite} q={q[:75]}"); bi += 1
                    elif cite_pgs and not any(cp in pages for cp in cite_pgs):
                        print(f"  [PAGE MISMATCH] bab-{bn:03d} {uk}.{fk}: cite={cite_pgs} actual={pages[:4]}"); bi += 1

                for sm in re.finditer(r"<svg\b.*?</svg>", h, re.S):
                    bs += 1; tot_svg += 1
                    raw = sm.group(0)
                    if re.search(r"#[0-9a-fA-F]{3,6}\b", raw):
                        print(f"  [HEX COLOR] bab-{bn:03d} {uk}.{fk}"); bi += 1
                    try:
                        root = ET.fromstring(raw)
                    except Exception as e:
                        print(f"  [SVG XML ERR] bab-{bn:03d} {uk}.{fk}: {e}"); bi += 1; continue
                    vb = [float(x) for x in root.attrib.get("viewBox", "0 0 540 200").split()]
                    vb_x, vb_y, vb_w, vb_h = vb[0], vb[1], vb[2], vb[3]
                    shapes, texts, issues_ref = [], [], [0]
                    def walk(el, dx=0.0, dy=0.0):
                        tr = el.attrib.get("transform", "")
                        m_tr = re.search(r"translate\(\s*([-\d.]+)\s*[,\s]\s*([-\d.]+)\s*\)", tr)
                        if m_tr:
                            dx += float(m_tr.group(1)); dy += float(m_tr.group(2))
                        tag = el.tag.split("}")[-1]
                        cs = el.attrib.get("class", "").split()
                        for c in cs:
                            if c not in VALID_SV:
                                print(f"  [UNKNOWN SVG CLS] bab-{bn:03d} {uk}.{fk}: <{tag} class='{c}'>"); issues_ref[0] += 1
                        if tag in ("rect", "circle", "ellipse", "path", "polygon", "line", "polyline"):
                            if "sv-ar" in cs:
                                print(f"  [SHAPE SV-AR] bab-{bn:03d} {uk}.{fk}"); issues_ref[0] += 1
                            if not cs and "fill" not in el.attrib and "stroke" not in el.attrib and "style" not in el.attrib:
                                print(f"  [SHAPE NO STYLE] bab-{bn:03d} {uk}.{fk}"); issues_ref[0] += 1
                        if tag == "rect":
                            rw, rh = float(el.attrib.get("width", 0)), float(el.attrib.get("height", 0))
                            rx, ry = float(el.attrib.get("x", 0)) + dx, float(el.attrib.get("y", 0)) + dy
                            if rw >= 16 and rh >= 12 and not (rw >= vb_w * 0.96 and rh >= vb_h * 0.90):
                                shapes.append(("rect", rw * rh, (rx, ry, rw, rh)))
                        elif tag == "circle":
                            cr = float(el.attrib.get("r", 0))
                            if cr >= 12:
                                shapes.append(("circle", math.pi * cr * cr,
                                               (float(el.attrib.get("cx", 0)) + dx, float(el.attrib.get("cy", 0)) + dy, cr)))
                        elif tag == "ellipse":
                            erx, ery = float(el.attrib.get("rx", 0)), float(el.attrib.get("ry", 0))
                            if erx >= 16 and ery >= 10:
                                shapes.append(("ellipse", math.pi * erx * ery,
                                               (float(el.attrib.get("cx", 0)) + dx, float(el.attrib.get("cy", 0)) + dy, erx, ery)))
                        elif tag == "text":
                            if not (set(cs) & TEXT_FILL_OK) and "fill" not in el.attrib and "style" not in el.attrib:
                                print(f"  [TEXT NO FILL] bab-{bn:03d} {uk}.{fk}"); issues_ref[0] += 1
                            t_str = "".join(el.itertext()).strip()
                            if t_str:
                                texts.append((t_str, el.attrib.get("class", ""), el,
                                              float(el.attrib.get("x", 0)) + dx, float(el.attrib.get("y", 0)) + dy,
                                              el.attrib.get("text-anchor", "start")))
                        for ch in el:
                            walk(ch, dx, dy)
                    walk(root)
                    bi += issues_ref[0]
                    tboxes = []
                    for txt, cls, tel, tx, ty, anchor in texts:
                        x0, x1, y0, y1, ew, fs = svg_text_box(txt, cls, tel, tx, ty, anchor)
                        tboxes.append((txt, x0, x1, y0, y1))
                        if x0 < vb_x + 1 or x1 > vb_x + vb_w - 1 or y0 < vb_y - 2 or y1 > vb_y + vb_h + 2:
                            print(f"  [TEXT OOB] bab-{bn:03d} {uk}.{fk}: '{txt}' x=[{x0:.0f}..{x1:.0f}] y=[{y0:.0f}..{y1:.0f}] vb=({vb_w:.0f},{vb_h:.0f})"); bi += 1
                        enclosing = []
                        for skind, sarea, sparams in shapes:
                            if skind == "rect":
                                rx, ry, rw, rh = sparams
                                if rx <= tx <= rx + rw and ry <= ty <= ry + rh:
                                    enclosing.append((sarea, skind, sparams))
                            elif skind == "circle":
                                cx, cy, cr = sparams
                                if (tx - cx) ** 2 + (ty - cy) ** 2 <= cr ** 2:
                                    enclosing.append((sarea, skind, sparams))
                            elif skind == "ellipse":
                                cx, cy, erx, ery = sparams
                                if ((tx - cx) / erx) ** 2 + ((ty - cy) / ery) ** 2 <= 1.0:
                                    enclosing.append((sarea, skind, sparams))
                        if enclosing:
                            enclosing.sort(key=lambda x: x[0])
                            _, skind, sparams = enclosing[0]
                            ym = (y0 + y1) / 2.0
                            if skind == "rect":
                                rx, ry, rw, rh = sparams
                                if x0 < rx + 3 or x1 > rx + rw - 3:
                                    print(f"  [RECT OVERFLOW] bab-{bn:03d} {uk}.{fk}: '{txt}' est={ew:.0f} rect=[{rx:.0f}..{rx+rw:.0f}]"); bi += 1
                            elif skind == "circle":
                                cx, cy, cr = sparams
                                dmax = max(
                                    math.hypot(x0 - cx, ym - cy), math.hypot(x1 - cx, ym - cy),
                                    math.hypot(x0 - cx, y1 - cy), math.hypot(x1 - cx, y1 - cy),
                                    math.hypot(x0 - cx, y0 - cy), math.hypot(x1 - cx, y0 - cy),
                                )
                                if dmax > cr - 2:
                                    print(f"  [CIRCLE OVERFLOW] bab-{bn:03d} {uk}.{fk}: '{txt}' dmax={dmax:.0f} > r={cr:.0f}"); bi += 1
                            elif skind == "ellipse":
                                cx, cy, erx, ery = sparams
                                nmax = max(
                                    ((x0 - cx) / erx) ** 2 + ((ym - cy) / ery) ** 2,
                                    ((x1 - cx) / erx) ** 2 + ((ym - cy) / ery) ** 2,
                                    ((x0 - cx) / erx) ** 2 + ((y1 - cy) / ery) ** 2,
                                    ((x1 - cx) / erx) ** 2 + ((y1 - cy) / ery) ** 2,
                                    ((x0 - cx) / erx) ** 2 + ((y0 - cy) / ery) ** 2,
                                    ((x1 - cx) / erx) ** 2 + ((y0 - cy) / ery) ** 2,
                                )
                                if nmax > 0.96:
                                    print(f"  [ELLIPSE OVERFLOW] bab-{bn:03d} {uk}.{fk}: '{txt}' norm={math.sqrt(nmax):.2f} ellipse=({erx:.0f}x{ery:.0f})"); bi += 1
                    for ti1 in range(len(tboxes)):
                        t1, ax0, ax1, ay0, ay1 = tboxes[ti1]
                        for ti2 in range(ti1 + 1, len(tboxes)):
                            t2, bx0, bx1, by0, by1 = tboxes[ti2]
                            if (min(ax1, bx1) - max(ax0, bx0)) > 3 and (min(ay1, by1) - max(ay0, by0)) > 3:
                                print(f"  [TEXT OVERLAP] bab-{bn:03d} {uk}.{fk}: '{t1}' x '{t2}'"); bi += 1

            if not uk.startswith("h"):
                continue
            tot_h += 1
            for reqf in ("title", "tr", "mf", "mfn", "rp", "ex", "is"):
                if not u.get(reqf):
                    print(f"  [FIELD MISSING] bab-{bn:03d} {uk}.{reqf}"); bi += 1

            # Cek anti-boilerplate lintas hadits
            for ptxt in re.findall(r"<p>(.*?)</p>", u.get("ex", "") + u.get("is", "") + u.get("nt", ""), re.S):
                tclean = norm(ptxt)
                if len(tclean) > 130:
                    if tclean in seen_paras:
                        dup_paras += 1
                        print(f"  [BOILERPLATE DUP] bab-{bn:03d} {uk} == {seen_paras[tclean]}: {tclean[:80]}")
                        bi += 1
                    else:
                        seen_paras[tclean] = f"bab-{bn:03d}/{uk}"

            t = u.get("tier", "C")
            tier_counts[t] = tier_counts.get(t, 0) + 1
            ex = u.get("ex", "")
            prose = len(re.sub(r"<svg\b.*?</svg>", "", ex, flags=re.S))
            h4_cnt = len(re.findall(r"<h4\b", ex))
            sb = u.get("sb", "")
            is_f = u.get("is", "")
            nt_f = u.get("nt", "")
            all_u = ex + sb + is_f + nt_f + u.get("rp", "")
            tbl_cnt = all_u.count('class="tbl')
            irab_cnt = ex.count('class="irab"')
            faid_cnt = all_u.count('class="faidah"')
            viz_cnt = ex.count('class="viz"')
            has_cards = 'class="cards"' in is_f
            has_kasus = 'class="kasus"' in is_f
            has_nb = 'class="nb nb-k"' in nt_f
            kr_cnt = nt_f.count('class="kr"')
            dlen = dalil_len_for(uk)

            if t == "A":
                b_prose_a.append(prose)
                if prose < 8500: print(f"  [A PROSE SHORT] bab-{bn:03d} {uk}: {prose} < 8500"); bi += 1
                if h4_cnt < 8: print(f"  [A H4 LOW] bab-{bn:03d} {uk}: {h4_cnt} < 8"); bi += 1
                min_dq = 3 if dlen >= 2500 else (2 if dlen >= 1000 else 1)
                if u_dalil_cnt < min_dq: print(f"  [A DALIL LOW] bab-{bn:03d} {uk}: {u_dalil_cnt} < {min_dq}"); bi += 1
                if len(sb) < 150: print(f"  [A SB SHORT] bab-{bn:03d} {uk}: {len(sb)} < 150"); bi += 1
                if tbl_cnt < 2: print(f"  [A TBL LOW] bab-{bn:03d} {uk}: {tbl_cnt} < 2"); bi += 1
                if irab_cnt < 1: print(f"  [A NO IRAB] bab-{bn:03d} {uk}"); bi += 1
                if faid_cnt < 1: print(f"  [A NO FAIDAH] bab-{bn:03d} {uk}"); bi += 1
                if viz_cnt < 1: print(f"  [A NO VIZ] bab-{bn:03d} {uk}"); bi += 1
                if len(is_f) < 1200 or not has_cards or not has_kasus:
                    print(f"  [A IS WEAK] bab-{bn:03d} {uk}: len={len(is_f)} cards={has_cards} kasus={has_kasus}"); bi += 1
                if not has_nb or kr_cnt < 3:
                    print(f"  [A NT WEAK] bab-{bn:03d} {uk}: nb={has_nb} kr={kr_cnt} < 3"); bi += 1
            elif t == "B":
                b_prose_b.append(prose)
                if prose < 3400: print(f"  [B PROSE SHORT] bab-{bn:03d} {uk}: {prose} < 3400"); bi += 1
                if h4_cnt < 4: print(f"  [B H4 LOW] bab-{bn:03d} {uk}: {h4_cnt} < 4"); bi += 1
                min_dq = 2 if dlen >= 1800 else (1 if dlen >= 350 else 0)
                if u_dalil_cnt < min_dq: print(f"  [B DALIL LOW] bab-{bn:03d} {uk}: {u_dalil_cnt} < {min_dq}"); bi += 1
                if len(sb) < 120: print(f"  [B SB SHORT] bab-{bn:03d} {uk}: {len(sb)} < 120"); bi += 1
                if tbl_cnt < 1: print(f"  [B NO TBL] bab-{bn:03d} {uk}"); bi += 1
                if viz_cnt < 1: print(f"  [B NO VIZ] bab-{bn:03d} {uk}"); bi += 1
                if len(is_f) < 650 or not has_cards:
                    print(f"  [B IS WEAK] bab-{bn:03d} {uk}: len={len(is_f)} cards={has_cards}"); bi += 1
                if not has_nb or kr_cnt < 2:
                    print(f"  [B NT WEAK] bab-{bn:03d} {uk}: nb={has_nb} kr={kr_cnt} < 2"); bi += 1
            else:
                b_prose_c.append(prose)
                c_total += 1
                if has_nb and kr_cnt >= 1:
                    c_with_nb += 1
                if prose < 1600: print(f"  [C PROSE SHORT] bab-{bn:03d} {uk}: {prose} < 1600"); bi += 1
                if h4_cnt < 2: print(f"  [C H4 LOW] bab-{bn:03d} {uk}: {h4_cnt} < 2"); bi += 1
                min_dq = 1 if dlen >= 400 else 0
                if u_dalil_cnt < min_dq: print(f"  [C DALIL LOW] bab-{bn:03d} {uk}: {u_dalil_cnt} < {min_dq}"); bi += 1
                if len(is_f) < 220: print(f"  [C IS SHORT] bab-{bn:03d} {uk}: {len(is_f)} < 220"); bi += 1

        if c_total > 0 and (c_with_nb / c_total) < 0.6:
            print(f"  [C NT LOW] bab-{bn:03d}: {c_with_nb}/{c_total} Tier C punya .nb-k (<60%)"); bi += 1
        sr_pct = int(round(100 * b_sr_rows / max(1, b_mf_rows))) if b_mf_rows else 100
        avg_k = int(round(b_ket_sum / max(1, b_mf_rows))) if b_mf_rows else 0
        if b_mf_rows and sr_pct < 75:
            print(f"  [MF SR LOW] bab-{bn:03d}: sr={sr_pct}% < 75%"); bi += 1
        if b_mf_rows and avg_k < 70:
            print(f"  [MF KET SHORT] bab-{bn:03d}: avgKet={avg_k} < 70"); bi += 1

        tot_issues += bi
        avg_s = lambda arr: f"{int(round(sum(arr)/len(arr)))}c" if arr else "-"
        print(f"bab-{bn:03d}: q={bq:2d} svg={bs:2d} mf={b_mf_rows:3d}(sr={sr_pct:3d}%,k={avg_k:3d}) | prose A={avg_s(b_prose_a):>6s} B={avg_s(b_prose_b):>6s} C={avg_s(b_prose_c):>6s} | {bi} issues")

    print(f"\nSUMMARY Bab {lo}-{hi} ({tot_h} hadits, {tier_counts}): {tot_q} quotes, {tot_svg} SVGs, dups={dup_paras}, TOTAL ISSUES: {tot_issues}")
    sys.exit(1 if tot_issues else 0)

if __name__ == "__main__":
    main()
