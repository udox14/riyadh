# PROGRES Syarah Riyadhus Shalihin

<!-- OTOMATIS:MULAI -->
_Diperbarui build.py, 2026-11-15 22:39 WIB_

- Bab bersyarah: **2 / 372**
- Hadits berterjemah: **20 / 1896** · bersyarah: **20**
- Tingkat: A 2 · B 11 · C 7
- File syarah: bab-001, bab-002
<!-- OTOMATIS:SELESAI -->

## Langkah berikutnya

1. ~~Upload Dalil al-Falihin~~ ✓ sudah di `sumber/dalil-falihin.txt` + indeks `dalil-index.json` (2026-11-15).
2. ~~Contoh **Bab 1**~~ ✓ (2026-11-15): `intro`, `ks`, `a1`, h1 (A), h2 (B), h3 (C) di `syarah/bab-001.json`. **Disetujui Udox** (2026-11-15); label tingkat disembunyikan dari tampilan (template.html), `mt` bawaan tidak ditulis.
   - **Bab 1 selesai lengkap** (2026-11-15): h1–h12. Tingkat: A = h1, h12 · B = h2, h4, h6, h8, h9, h10, h11 · C = h3, h5, h7 (Udox bisa mengubah).
3. ~~Kunci PANDUAN~~ ✓ dan ~~skill "syarah-riyadh"~~ ✓ (2026-11-15).
4. **Bab 2 (at-Taubah) sebagian** (2026-11-15): `a2` + h13–h20 selesai di `syarah/bab-002.json` (A 0 · B h15, h18, h19, h20 · C h13, h14, h16, h17).
   - **Berikutnya: h21** (Ka'b bin Malik, Tabuk). Teks Dalil-nya ±115 ribu karakter: baca per bagian dengan `head -c`/`tail -c`, jangan sekaligus. Lalu h22 (al-Ghamidiyyah), h23, h24.
   - Setelah h24: tulis `intro` (peta isi: h13–14 istighfar Nabi; h15 kegembiraan Allah; h16–19 pintu dan batas taubat; h20–21 kisah-kisah taubat; h22 al-Ghamidiyyah; h23–24), `ks`, dan `catatan` Bab 2. `intro`/`ks` sengaja belum ditulis karena peta isi bergantung pada h21–h24.

## Keputusan yang sudah diambil

- Satu hadits = satu pembahasan; bab = kelompok; 19 kitab + al-Muqaddimat (Bab 1–83) + muqaddimah an-Nawawi.
- Nomor hadits dan halaman ikut cetakan al-Fahl (Dar Ibn Katsir). Bab 277 di Syamilah tertulis "227", sudah dibetulkan di parse.
- Kedalaman bertingkat A/B/C; tingkat ditentukan Claude per hadits dan dilaporkan di akhir bab, Udox bisa mengubah. Label tingkat **tidak ditampilkan** di pembaca (keputusan Udox 2026-11-15).
- Isian `mt` bawaan tidak ditulis; salah harakat naskah dibetulkan di kosakata.
- Model: Sonnet 5.5 untuk semua bab dan semua tingkat, termasuk A (keputusan Udox 2026-11-15, PANDUAN §10 diperbarui; sebelumnya Opus untuk Bab 1–5 dan tingkat A).
- Satu file HTML sampai mendekati 5 MB, lalu dipecah jilid (`jilid.json`).
- Kerangka (matan + takhrij) sudah lengkap; harakat masih bawaan naskah. Harakat penuh ditambahkan saat hadits digarap (isian `mt`).

## Istilah baku

- `إنما الأعمال بالنيات` → "Sesungguhnya amal-amal itu hanyalah dengan niat"; `لكل امرئ ما نوى` → "setiap orang hanya mendapatkan apa yang ia niatkan".
- `متفق على صحته` → "Disepakati keshahihannya"; `متفق عليه` → "Muttafaq 'alaih" (tidak diterjemahkan); `هذا لفظ البخاري` → "Ini lafaz al-Bukhari".
- Gelar: *Amirul Mukminin*, *Ummul Mukminin* (tidak diterjemahkan di terjemah); Fathu Makkah; hijrah.
- *Al-Mushannif* dalam Dalil = an-Nawawi. Nukilan bertingkat: "Ibnu 'Allan menukil dari X"; cite `Dalil al-Falihin, j/p (menukil X)`.
- `تكثير السواد` → "memperbanyak barisan" (pelaku maksiat).
- `مهاجر أم قيس` → "Muhajir Ummu Qais" (disebut "kisah yang semakna", bukan dipastikan sabab wurud; Ibnu Rajab & Ibnu Hajar).
- `في سبيل الله` → "di jalan Allah"; `كلمة الله هي العليا` → "kalimat Allah itulah yang paling tinggi"; `حمية` → "fanatisme"; `رياء` → "riya'".
- `همّ` → "berkeinginan"; tingkatan bisikan: *hajis, khathir, hadits an-nafs, hamm, 'azm* (h11).
- `ابتغاء وجهك` → "karena mencari wajah-Mu"; `الغبوق` → "minum (susu) sore".
- Istilah nahwu/ushul dibiarkan dengan *em*: *hal*, *mubtada'*, *khabar*, *hashr*, *gharib*, *masyhur*, *ta'yin*.

- Ejaan **taubat** (bukan "tobat") dipakai di seluruh buku; *taubat nashuha*; *had qadzf*; *ahlul haq* = Ahlus Sunnah (Ibnu 'Allan).
- `يغرغر` → "ruhnya sampai di tenggorokan" (*ghargharah*); `يبسط يده` → "membentangkan tangan-Nya" (dijelaskan sebagai kiasan, lihat h16).
- `أفرح` (sifat Allah) → "lebih gembira", dijelaskan Ibnu 'Allan sebagai ridha; di `nt` h15 disebut pula pandangan ulama lain yang menetapkan sifat tanpa tasybih (parafrase, bukan dari `sumber/`, perlu dicek Udox).
- `حديث حسن صحيح` → dijelaskan di h19 (tabel); `صحيح` dalam mukadimah an-Nawawi vs hadits hasan → dijelaskan di h18.

## Perawi yang sudah diprofilkan (`rp`)

- 'Umar bin al-Khaththab → h1 (plus profil ringkas al-Bukhari & Muslim di h1)
- 'Aisyah binti Abu Bakr → h2
- Jabir bin 'Abdillah → h4; Anas bin Malik → h4 (ringkas, lengkapi saat Anas jadi perawi utama pertama kali)
- Ma'n bin Yazid → h5
- Sa'd bin Abi Waqqash → h6 (plus daftar 10 yang dijamin surga)
- Abu Hurairah → h7
- Abu Musa al-Asy'ari → h8
- Abu Bakrah ats-Tsaqafi → h9
- 'Abdullah bin 'Abbas → h11
- 'Abdullah bin 'Umar → h12
- Anas bin Malik → h15 (profil penuh; menggantikan yang ringkas di h4)
- al-Agharr bin Yasar al-Muzani → h14
- Zirr bin Hubaisy dan Shafwan bin 'Assal → h19
- Abu Sa'id al-Khudri → h20
- Abu Hurairah/Abu Musa/Ibnu 'Umar di h13, h16, h17, h18 cukup "lihat hadits 7/8/12"

## Catatan sumber

- Hadits tanpa takhrij al-Fahl di sumber: no. 604, 1608, 1867.
- Dalil al-Falihin terpetakan: 1.672 hadits punya entri sendiri, 27 menyatu dengan hadits sebelumnya, 48 dibahas di bagian lain, 149 perlu dicari manual (kebanyakan juz 7–8). Penomoran Dalil di juz 7–8 bergeser 1–2 dari al-Fahl; selalu pegang nomor al-Fahl.
- Naskah Riyadh yang disyarah Ibnu 'Allan kadang beda dengan al-Fahl: Bab 1 memuat Ali 'Imran 92 (tidak ada di al-Fahl). Pegang matan al-Fahl, sebut bedanya sebagai faidah.
- Salah ketik Syamilah yang dibetulkan saat menukil di Bab 1: التقربّ→التقرّب, الحملة→الجملة, تحصيل الخبر→تحصيل الخير, syair as-Subki "لله أخلص ما نوى" (lafaz Allah hilang). Riwayat Muslim di Dalil 1/62 tertulis المستنصر (Shahih Muslim: المستبصر).
- Harakat naskah ada yang salah (h1: يَنْكَحُهَا → mestinya يَنْكِحُهَا). Relevan untuk keputusan `mt`.
- Salah ketik Dalil lain di Bab 1: wafat Ibnu 'Abbas tertulis 58 H (mestinya 68 H); (هود: 14) mestinya Hud 114. Klaim Ibnu 'Abbas buta karena melihat Jibril tidak dimuat.
- h7: lafaz al-Fahl memuat "وأعمالكم", lafaz yang disyarah Dalil tidak; keduanya ada di Shahih Muslim.
- `ambil.py --html` ditolak oleh pemeriksa izin sesi Cowork (dikira membaca file HTML), jadi `mt` belum ditulis.
- 7 hadits tanpa nama perawi otomatis (no. 128, 129, 131, 133, 135, 136, 711), tidak masalah karena matan tetap utuh.

- Bab 2: nomor Dalil h13 = 141, h14 = 152, h15 = 163, h16 = 174, h17 = 185, h18 = 196, h19 = 207, h20 = 8 (nomor di sumber tertulis "8", isi sesuai hadits ini, hlm. 1/108–1/112).
- Bab 2 h15: angka riwayat Anas dari Bukhari-sendiri dan Muslim-sendiri di Dalil tampak rusak ("ثمانية", "سبعين") sehingga tidak dikutip; hanya 2.286 total dan 168 muttafaq yang ditulis.
- Bab 2 h19: kosakata memakai catatan tahqiq al-Fahl (an-Nihayah). Di h15, hadits tambahan Ibnu 'Asakir dan at-Ta'ibin di h15 dibawakan Ibnu 'Allan dari as-Suyuthi, derajat tidak dinilai.
- Bab 2 `rp` h14 mengutip "kitab as-Silah" dari Dalil tanpa nama pengarang (nama kitab seperti tertulis di sumber).

## Log chat

| Tanggal | Bab | Catatan |
|---|---|---|
| 2026-11-15 | – | Kerangka lengkap, paket kerja dipasang di C:\DATA\riyadh |
| 2026-11-15 | – | Dalil al-Falihin (8 juz) masuk `sumber/`, diindeks per hadits; `ambil.py --dalil` |
| 2026-11-15 | 1 (sebagian) | Contoh Bab 1: intro, ks, a1, h1 A, h2 B, h3 C. Kutipan Arab dicocokkan otomatis dengan sumber + halaman. Lanjut h4. |
| 2026-11-15 | – | Contoh Bab 1 disetujui; label Tingkat dihapus dari template; PANDUAN dikunci. |
| 2026-11-15 | 1 (selesai) | h4–h12 digarap (A: h12; B: h4, h6, h8–h11; C: h5, h7). 20 kutipan Arab dicek otomatis + halaman. dist 2,80 MB. Skill syarah-riyadh dibuat. |
| 2026-11-15 | 2 (sebagian) | a2, h13–h20 digarap (chat Sonnet; mutu perlu dicek Udox). 23 kutipan Arab cocok dengan sumber + halaman. dist 2,88 MB. Lanjut h21. |
