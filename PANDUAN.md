# PANDUAN Syarah Riyadhus Shalihin

> **Status: DIKUNCI (2026-11-15).** Contoh Bab 1 (`syarah/bab-001.json`: intro, ks, a1, h1–h3) disetujui Udox. Ubah panduan ini hanya bila Udox minta.

## 1. Tujuan

Buku digital *Riyadhus Shalihin* (an-Nawawi) untuk pembaca web Maktabah: matan Arab, terjemah, dan syarah mendalam bergaya Tafsir Jalalain al-Kahfi (visual, tabel, kasus, kekeliruan), merujuk kitab-kitab syarah hadits. Dikerjakan bab per bab, lintas chat.

## 2. Isi folder `C:\DATA\riyadh` (di shell: `$HOME/mnt/riyadh`)

| File | Fungsi | Diubah? |
|---|---|---|
| `PANDUAN.md` | aturan ini | hanya bila Udox minta |
| `PROGRES.md` | status dan catatan antar-chat | **ya, tiap akhir chat** |
| `data.json` | kerangka: 372 bab, 1.896 hadits, takhrij dan catatan al-Fahl | jangan (hasil `sumber/parse.py`) |
| `syarah/bab-NNN.json` | hasil kerja, satu file per bab (`bab-001.json`) | **ya, ini kerjanya** |
| `ambil.py` | menampilkan isi satu bab saja | tidak |
| `build.py` | validasi + gabung → `dist/*.html` + perbarui ringkasan PROGRES | tidak |
| `template.html`, `style.css` | pembaca (CSS dari Tafsir al-Kahfi + tambahan hadits) | hanya bila perlu fitur baru |
| `sumber/` | `riyadh-alfahl.txt` (matan Syamilah) + `parse.py`; `dalil-falihin.txt` (Dalil al-Falihin lengkap 8 juz, Syamilah) + `dalil-index.json` (peta hadits → baris/halaman) + `index_dalil.py` | sumber baru disimpan di sini |
| `jilid.json` | (belum ada) pembagian jilid, dibuat saat file mendekati 5 MB | nanti |

## 3. Alur satu chat

1. Baca `PANDUAN.md` dan `PROGRES.md` (cukup dua ini, **jangan** baca `data.json` atau HTML hasil build).
2. `cd $HOME/mnt/riyadh && python3 ambil.py N` → ikhtisar bab N (matan, takhrij, catatan). Pakai `--html` hanya bila menulis ulang `mt`.
3. Syarah Ibnu 'Allan **per unit**, jangan sekaligus satu bab (Bab 1 saja ±150 ribu karakter):
   `python3 ambil.py aN --dalil` (pengantar/ayat bab), `python3 ambil.py hK --dalil` (hadits K). Kerjakan unit itu, simpan, lalu ambil unit berikutnya.
   Bila keluarannya "tidak ada / dibahas di bagian hadits …": cari manual, `grep -n "potongan lafaz tanpa harakat" sumber/dalil-falihin.txt`, lalu baca baris itu (`sed -n 'A,Bp'`). Selalu cocokkan baris pertama keluaran Dalil dengan matan hadits; kalau isinya hadits lain (pemetaan otomatis bisa meleset satu, terutama di juz 7–8), cari manual. Sekitar 92% hadits sudah terpetakan otomatis; sisanya kebanyakan di juz 7–8, termasuk hadits berulang yang memang tidak disyarah ulang oleh Ibnu 'Allan.
4. Tulis `syarah/bab-NNN.json` (lihat §4). Bab panjang boleh ditulis bertahap: simpan, build, lanjut hadits berikutnya.
5. `python3 build.py` → harus tanpa GALAT. Perbaiki sampai bersih.
6. Perbarui `PROGRES.md`: bab selesai, catatan lanjutan (istilah yang sudah dibakukan, rawi yang sudah diprofilkan, hal yang ditunda).
7. Laporkan singkat ke Udox. File hasil: `dist/Riyadhus-Shalihin.html` (dia yang memasang ke Maktabah).

Target per chat: 1–3 bab (±10–30 hadits). Kalau bab besar (mis. Bab 3 Sabar, 29 hadits), pecah ke beberapa chat dan catat posisi terakhir di PROGRES.

## 4. Format `syarah/bab-NNN.json`

```json
{
  "bn": 1,
  "id": "Ikhlas dan Menghadirkan Niat dalam Seluruh Amal, Ucapan, dan Keadaan",
  "intro": "<p>…pengantar bab…</p>",
  "ks": "<ol class=\"ksl\"><li>…</li></ol>",
  "catatan": "bebas, tidak ditampilkan",
  "u": {
    "a1":  { "tr": "…terjemah ayat-ayat bab…", "ex": "…tafsir ringkas ayat…" },
    "h1":  { "title": "Amal Tergantung Niat", "tier": "A", "tr": "…", "mf": "<table>…</table>", "mfn": 6,
             "rp": "…", "sb": "…", "ex": "…", "is": "…", "nt": "…" }
  }
}
```

Kunci unit: `aN` = ayat/pengantar Bab N (ada di 188 bab), `hN` = hadits nomor N (nomor al-Fahl, sama dengan yang dicetak).

| Isian | Tampil sebagai | Isi |
|---|---|---|
| `id` | judul bab terjemahan | dipakai di daftar isi |
| `intro` | Pengantar Bab | makna judul, alasan penyusunan an-Nawawi, peta isi bab (pakai `.peta`) |
| `ks` | Kesimpulan Bab | 3–6 butir |
| `title` | judul hadits (menggantikan cuplikan Arab di daftar isi) | 2–6 kata, tema hadits |
| `tier` | **tidak ditampilkan** di pembaca (hanya untuk statistik build dan pembagian kerja model) | `A` / `B` / `C` (§5) |
| `mt` | matan | **opsional**: matan berharakat penuh. Penanda `<sup class="fn">n</sup>` wajib tetap sama (build menolak bila berubah). Pertahankan `<span class="hd">` untuk sabda, `<span class="q">` untuk ayat, `<p class="sy">` untuk keterangan an-Nawawi. **Bawaan: tidak ditulis**; harakat naskah dibiarkan, harakat yang salah dibetulkan di kosakata (`mf`) dan dicatat di PROGRES. |
| `tr` | Terjemah | `<p>`; sabda Nabi diberi tanda petik; keterangan an-Nawawi diterjemahkan juga, diawali *(An-Nawawi:)* |
| `mf` + `mfn` | Kosakata | tabel seperti contoh §7, `mfn` = jumlah lafaz |
| `rp` | Profil Perawi | hanya di kemunculan pertama sahabat; berikutnya cukup satu kalimat + "lihat hadits N" |
| `sb` | Sabab Wurud dan Munasabah | latar hadits + mengapa an-Nawawi menaruhnya di bab ini (fiqh tarajim) + kaitan dengan hadits sebelumnya |
| `ex` | Penjelasan | `<h4>1. …</h4>` bernomor; makna, khilaf ulama, i'rab bagian kunci, nukilan syarah, visual |
| `is` | Fawaid dan Penerapan Masa Kini | fawaid klasik ("di dalamnya terdapat…") + `.cards`/`.kasus` untuk konteks santri/madrasah/masyarakat kini |
| `nt` | Miskonsepsi | `<section class="nb nb-k">` berisi `.kr` (Keliru / Yang benar) |

## 5. Tingkat kedalaman (dikalibrasi dari contoh Bab 1: h1 = A, h2 = B, h3 = C)

Ukuran contoh Bab 1 sebagai patokan: **A** ±31 ribu karakter, 13 subjudul, 2 visual + beberapa tabel, 4 kotak kutipan · **B** ±10 ribu karakter, 4 subjudul, 1 visual, 2 kotak kutipan · **C** ±5 ribu karakter, 3 subjudul, 1 kotak kutipan. Label tingkat tidak tampil di pembaca.

| | Kapan | Isi | Panjang `ex` kira-kira |
|---|---|---|---|
| **A** | hadits pokok/kaidah besar (innamal a'mal, Jibril, tiga orang di gua, 'man hasuna islamu'…) | semua isian, ≥2 visual, khilaf ulama, i'rab, nukilan beberapa syarah | 8–14 subjudul |
| **B** | hadits sedang | semua isian, 1 visual | 4–7 subjudul |
| **C** | hadits pendek / tema berulang | `title`, `tr`, `mf`, `ex` ringkas (2–3 subjudul), `is` singkat; `rp`/`sb`/`nt` hanya bila ada yang penting | 2–3 subjudul |

Perkiraan sebaran: A ±15%, B ±35%, C ±50%. Hadits yang sudah dibahas dalam di bab lain (pengulangan) → C + rujukan "lihat hadits N".

## 6. Rujukan dan aturan nukilan

- **Syarah induk:** *Dalil al-Falihin li Thuruq Riyadh ash-Shalihin*, Ibnu 'Allan ash-Shiddiqi (w. 1057 H), ed. Khalil Ma'mun Syiha, Dar al-Ma'rifah, cet. IV 1425 H, 8 jilid (`sumber/dalil-falihin.txt`).
  - Halaman: penanda `‹akhir hlm. j/p›` di keluaran `ambil.py` menutup halaman itu, jadi teks di atasnya ada di halaman j/p. Kutip sebagai *Dalil al-Falihin*, j/p.
  - Ciri teks Syamilah ini: lafaz Allah sering terpotong ("عبد ا" = عبد الله, "وا" = والله, "با" = بالله) dan "صلى الله عليه وسلم" sering hilang setelah "رسول الله". Pulihkan saat mengutip; jangan menyalin kesalahan ketik.
  - Ibnu 'Allan banyak menukil al-Kirmani, Ibnu Hajar, al-Qurthubi, ath-Thibi, dan "al-Mushannif" (= an-Nawawi, terutama Syarh Muslim). Nukilan bertingkat seperti ini boleh dikutip dengan menyebut keduanya ("dinukil Ibnu 'Allan dari Ibnu Hajar").
  - Catatan kaki pentahqiq Dalil (bagian sesudah `[catatan pentahqiq Dalil:]`) berisi takhrij edisi itu; bukan perkataan Ibnu 'Allan.
- **Pendamping:** Syarh Riyadh Ibnu 'Utsaimin; *Nuzhat al-Muttaqin* (Musthafa al-Khin dkk.); *Bahjat an-Nazhirin* (Salim al-Hilali).
- **Induk:** Fath al-Bari, Syarh Shahih Muslim an-Nawawi, 'Umdat al-Qari, Ikmal al-Mu'lim, al-Mufhim, Jami' al-'Ulum wal-Hikam, an-Nihayah (gharib).
- **Kotak kutipan Arab (`figure.dalil`) hanya dari teks yang ada di `sumber/`**, disalin persis, dengan `<cite>` nama kitab (+ jilid/halaman bila tertera di sumber). Jangan pernah mengarang nukilan Arab atau nomor halaman.
- Rujukan dari luar `sumber/` → parafrase Indonesia dengan atribusi ("Ibnu Hajar menjelaskan…"), tanpa kutipan Arab dan tanpa nomor halaman.
- Takhrij tambahan (derajat dari al-Albani/al-Arna'uth) hanya bila yakin; kalau ragu, cukup takhrij al-Fahl yang sudah tampil.
- Ayat dikutip dengan rujukan surah:ayat. Hadits pendukung disebut sumber kitabnya.

## 7. Gaya bahasa

- Bahasa Indonesia baku, mengalir, tidak kaku; sapaan netral. Konteks pembaca: santri, guru madrasah, masyarakat umum.
- Transliterasi miring `<em>` gaya al-Kahfi: *'ain* = ', *hamzah* = ', *al-* bersambung (*ash-Shalihin*, *an-Nawawi*), tanpa titik/garis diakritik. Nama yang sudah lazim pakai ejaan Indonesia (Umar, Aisyah, Abu Hurairah).
- Arab di dalam prosa: `<span lang="ar">…</span>`; lafaz yang dibahas di tabel: `<span class="ai" lang="ar">`.
- ﷺ untuk Nabi; *radhiyallahu 'anhu/'anha/'anhuma* ditulis lengkap di terjemah.
- Hindari klaim berlebihan dan istilah yang terlalu teknis tanpa penjelasan.

## 8. Katalog komponen (CSS sudah ada di `style.css`)

**Kotak nukilan**
```html
<figure class="dalil"><p class="dq" lang="ar">…teks Arab persis…</p><figcaption>"…terjemah…"</figcaption><cite>Dalil al-Falihin, 1/…</cite></figure>
```
**Alur / tangga** (`.st` warna: `a` biru, `g` hijau, `y` kuning, `r` merah; `.ar` = panah, isi `<span>` untuk label panah)
```html
<figure class="viz"><p class="vt">Judul visual</p>
<div class="flow"><div class="st a"><b>Langkah</b><small>keterangan</small></div><div class="ar"><span>melahirkan</span></div><div class="st g"><b>…</b><small>…</small></div></div>
<figcaption>keterangan</figcaption></figure>
```
Cabang dua: `<div class="fork">` berisi dua `.st`. Tangga bertingkat: `<ol class="ladder" style="direction:ltr"><li><span><b>…</b><small>…</small></span></li>…</ol>`.

**Tabel perbandingan** (khilaf ulama/madzhab, perbedaan riwayat)
```html
<div class="tbl cmp"><table><tr><th>Pendapat</th><th>Tokoh</th><th>Dalil</th></tr><tr><td>…</td><td>…</td><td>…</td></tr></table></div>
```
**Kosakata (`mf`)**
```html
<table><tr><th>Lafaz</th><th>Arti</th><th>Keterangan</th></tr>
<tr><td><span class="lf">النِّيَّاتُ</span><span class="sr">نَوَى – يَنْوِي – نِيَّةً</span></td><td>niat-niat</td><td>…</td></tr></table>
```
**I'rab**
```html
<div class="irab"><span class="ib k1"><b lang="ar">إِنَّمَا</b><small>adat hashr</small></span><span class="ib k2"><b lang="ar">الْأَعْمَالُ</b><small>mubtada'</small></span><span class="ib k3"><b lang="ar">بِالنِّيَّاتِ</b><small>khabar (muta'alliq)</small></span></div>
```
**Faidah / kisah / kasus / kartu**
```html
<div class="faidah"><b>Judul</b><p>…</p></div>
<div class="kisah"><b>"Judul kisah"</b><p>…</p><p class="src">HR. …</p></div>
<div class="kasus"><b>Contoh kasus</b><p>…</p></div>
<div class="cards"><div><b>…</b><p>…</p></div><div><b>…</b><p>…</p></div></div>
```
**Miskonsepsi (`nt`)**
```html
<section class="nb nb-k"><h5>Kekeliruan yang sering terjadi</h5>
<div class="kr"><div class="k-x"><span class="tag">Keliru</span><p>…</p></div><div class="k-b"><span class="tag">Yang benar</span><p>…</p></div></div></section>
```
**Peta isi bab (`intro`)**: `<div class="peta"><div class="c2s"><b>Hadits 1–3</b><small>…</small></div><div class="now c1s">…</div><div class="c3s">…</div></div>`
**Kesimpulan (`ks`)**: `<ol class="ksl"><li>…</li></ol>`. **Label kecil**: `<span class="pill p-good|p-bad|p-acc|p-mid">…</span>`.

**SVG** (bila alur/tabel tidak cukup: peta lokasi, jalur sanad, garis waktu, pohon akar kata)
```html
<figure class="viz"><p class="vt">Judul</p>
<svg viewBox="0 0 420 236" role="img" aria-label="…">
<rect x="150" y="14" width="120" height="54" rx="10" class="sv-acc"/>
<text x="210" y="44" text-anchor="middle" class="sv-ar">نِيَّة</text>
<text x="210" y="61" text-anchor="middle" class="sv-s sv-cn">keterangan</text>
<path d="M180 68 C150 100 90 100 72 128" class="sv-ln"/></svg>
<figcaption>…</figcaption></figure>
```
Kelas SVG: kotak `sv-box sv-acc sv-q sv-gold sv-bad`; teks `sv-t` (judul), `sv-s` (sedang), `sv-n` (kecil), `sv-ar` (Arab), `sv-cn` (rata tengah), warna teks `sv-acc-t sv-q-t sv-gold-t sv-bad-t`; garis `sv-ln`. Jangan pakai warna hardcode, supaya mode gelap tetap benar.

**Ide visual khas hadits:** jalur takhrij (sahabat → perawi → Bukhari/Muslim), peta lokasi (Baida', Tabuk, Madinah), garis waktu sirah, bagan konsep (niat → amal → balasan), tabel pendapat madzhab, perbandingan lafaz antar-riwayat.

## 9. Sebelum menutup chat

- [ ] `python3 build.py` tanpa GALAT
- [ ] `PROGRES.md` diperbarui (bab selesai, posisi terakhir, istilah baku baru, rawi yang sudah diprofilkan)
- [ ] Lapor ke Udox: bab yang selesai, ukuran file, hal yang perlu keputusannya

## 10. Model dan pembagian kerja

**Diubah atas permintaan Udox (2026-11-15):** semua bab dan semua tingkat (A/B/C) dikerjakan Sonnet 5.5 saja, tanpa pindah model. Tingkat A tetap ditulis penuh sesuai §5 (patokan ukuran Bab 1).

- Bab berisi hadits tingkat A tidak lagi dibagi antar-model; kerjakan langsung dalam satu chat.
- **Contoh rujukan gaya:** `syarah/bab-001.json` (disetujui 2026-11-15). Bila ragu, cukup baca satu hadits dengan tingkat yang sama dari file ini, bukan seluruh bab lain.
- build.py hanya memeriksa format. Kebenaran isi (terjemah, harakat, atribusi pendapat) tetap dicek sampel oleh Udox, terutama pada Bab 2–3 yang digarap Sonnet.
