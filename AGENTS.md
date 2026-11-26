# Aturan Wajib Proyek Syarah Riyadhus Shalihin (`c:\DATA\riyadh`)

Aturan ini melengkapi `PANDUAN.md` dan `PROGRES.md` (keduanya wajib dibaca di awal sesi; jangan pernah membaca `data.json` atau HTML hasil build secara langsung — gunakan `ambil.py`).

## 1. Gerbang Kualitas Wajib (Non-Negotiable)
- Setiap bab yang ditulis atau diubah **WAJIB lulus** `python cek_mutu.py <rentang_bab>` dengan hasil **`TOTAL ISSUES: 0`** sebelum menjalankan `python build.py`.
- `python build.py` wajib selesai dengan **0 galat**, lalu perbarui `PROGRES.md` di akhir sesi.

## 2. Standar Kedalaman Konten (Setara Bab 1: `h1`, `h2`, `h3`, `h12`)
Panjang prosa `ex` selalu dihitung **DI LUAR kode `<svg>...</svg>`**. Dilarang keras menyalin paragraf template/*boilerplate* antar-hadits.

- **Tier A (hadits pokok/kaidah besar):**
  - Prosa murni `ex` **≥ 8.500 karakter** (target 10K–16K), **≥ 8 subjudul bernomor `<h4>1. ...</h4>`**.
  - **≥ 3 kutipan verbatim** `<figure class="dalil">` (minimal 2 bila entri Dalil < 2.500c), **≥ 2 tabel `.tbl.cmp`**, **≥ 1 `<div class="irab">`**, **≥ 1 `.faidah`**, **≥ 1 `.viz`**.
  - `sb` ≥ 150c (latar/kisah + *fiqh tarajim* munasabah), `is` ≥ 1.200c (fawaid + `.cards` 3 peran + `.kasus`), `nt` `<section class="nb nb-k">` dengan **≥ 3 `.kr`** (*Keliru* vs *Yang benar*).
- **Tier B (hadits sedang):**
  - Prosa murni `ex` **≥ 3.400 karakter** (target 4K–6K), **≥ 4 `<h4>`**, **≥ 2 kutipan verbatim *Dalil*** (bila entri ≥ 1.800c; min 1 bila ≥ 350c).
  - `sb` ≥ 120c, **≥ 1 `.tbl.cmp`**, **≥ 1 `.viz`**, `is` ≥ 650c + `.cards`, `nt` `.nb-k` dengan **≥ 2 `.kr`**.
- **Tier C (hadits pendek/pengulangan):**
  - Prosa murni `ex` **≥ 1.600 karakter** (target 1,8K–3K), **≥ 2 `<h4>`**, **≥ 1 kutipan verbatim *Dalil*** (bila entri ≥ 400c), `sb` ringkas, `is` ≥ 220c, `nt` `.nb-k` (≥ 1 `.kr` pada ≥ 60% Tier C per bab).

## 3. Kosakata (`mf`) Standar Emas Bab 1
- Format wajib persis 3 kolom:
  `<table><tr><th>Lafaz</th><th>Arti</th><th>Keterangan</th></tr>`
- **DILARANG** memakai `<thead>` atau `<tbody>` (aturan mobile `.mft tr:first-child{display:none}` akan menyembunyikan baris data pertama).
- Kolom 1: `<span class="lf">...</span>` berharakat lengkap + `<span class="sr">...</span>` tashrif Arab 3 bentuk (`فَعَلَ – يَفْعُلُ – فَعْلًا` atau mufrad/jamak) pada ≥ 80% baris (target 95–100%).
- Kolom 2 (`Arti`): arti bahasa Indonesia ringkas tegas (2–6 kata), **bukan** transliterasi miring `<em>...</em>`.
- Kolom 3 (`Keterangan`): uraian bahasa/syariat/nahwu padat (rata-rata bab ≥ 75 karakter, tiap baris ≥ 40 karakter).
- Jumlah baris minimal: Tier A ≥ 5, Tier B ≥ 4, Tier C ≥ 3; `mfn` wajib sama persis dengan jumlah baris data.

## 4. Visual SVG Kreatif & Aman Mode Gelap
- Hindari diagram kotak-kotak monoton: padukan ilustrasi vektor tematik non-kotak (`<circle>`, `<ellipse>`, `<path>`, `<polygon>`, `<line>`) pada `viewBox="0 0 540 ..."`.
- **HANYA** gunakan kelas SVG resmi di `style.css`: `sv-box`, `sv-acc`, `sv-q`, `sv-bad`, `sv-gold`, `sv-ln`, `sv-t`, `sv-s`, `sv-n`, `sv-ar` (khusus teks Arab, bukan shape), `sv-acc-t`, `sv-bad-t`, `sv-q-t`, `sv-gold-t`, serta `fill="var(--ink-3)"` pada panah `<polygon>`.
- **DILARANG** memakai warna `#hex`, kelas buatan sendiri, `sv-cn`, atau shape tanpa kelas/fill/stroke (mencegah bentuk hitam pekat di mode terang/gelap). Pastikan 0 teks *overflow* desktop/ponsel.

## 5. Invarian Format, Nukilan, & Ejaan
- **Kutipan Arab (`<figure class="dalil">`):** wajib **100% verbatim** dari `sumber/dalil-falihin.txt` beserta nomor `jilid/halaman` yang akurat (ambil secara programatik, jangan diketik ulang dari ingatan).
- **Tata letak bab:** `id` harus judul bahasa Indonesia (bukan kode `bNN`); penutup `intro` wajib `<div class="peta">` dengan tag native `<div class="cNs"><b>...</b><small>...</small></div>` (tanpa `peta-card`, `<strong>`, `<br>`); `ks` diawali `<ol class="ksl">`.
- **Larangan keras:** jangan tulis field `mt`; jangan pakai `<a href="#...">`; selalu eja **taubat** (bukan "tobat").
- **Profil perawi (`rp`):** cek daftar di `PROGRES.md` — profil penuh hanya pada kemunculan pertama; selanjutnya cukup ringkas + `"lihat hadits N"`. Catat perbedaan matan/tahqiq al-Fahl (termasuk penilaian *dha'if*) secara jujur di `nt`, `catatan`, dan `PROGRES.md`.
