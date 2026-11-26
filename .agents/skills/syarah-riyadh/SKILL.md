---
name: syarah-riyadh
description: >-
  Prosedur kerja lengkap untuk menyusun, memperkaya, memverifikasi, dan mem-build
  bab-bab Syarah Riyadhus Shalihin di c:\DATA\riyadh (Bab 84-372 dan perbaikan bab)
  sesuai standar emas Bab 1. Aktifkan setiap kali pengguna meminta melanjutkan bab baru,
  mengedit syarah, memecah jilid, atau mengaudit mutu hadits Riyadhus Shalihin.
---

# Prosedur Penyusunan Syarah *Riyadhus Shalihin*

## Langkah 1: Orientasi Sesi
1. Baca `PANDUAN.md` dan `PROGRES.md` (cek bab terakhir, istilah baku, dan daftar perawi `rp` yang sudah diprofilkan agar tidak duplikat).
2. Bila ragu format atau kedalaman, lihat contoh acuan di `syarah/bab-001.json` (`h1` = Tier A, `h2`/`h4`/`h6` = Tier B, `h3`/`h5` = Tier C).
3. Jangan pernah membaca `data.json` atau HTML hasil `dist/` langsung.

## Langkah 2: Ekstrak Matan & *Dalil al-Falihin*
1. Jalankan ekstraksi per rentang bab ke folder kerja sementara:
   `python ambil.py <awal>-<akhir> --dalil`
2. Pecah keluaran menjadi file per unit (`aN.txt`, `hK.txt`) dan periksa apakah ada unit dengan pesan `tidak terindeks` / `tidak ada syarah` / nomor *Dalil* bergeser (terutama Juz 7–8).
3. Jika ada unit tidak terindeks atau menyatu pada entri lain, cari langsung di `sumber/dalil-falihin.txt` menggunakan potongan lafaz tanpa harakat dan simpan ke file unitnya dengan penanda `‹akhir hlm. j/p›` utuh.

## Langkah 3: Penyusunan Terprogram (Anti-Salah Kutip & Anti-Degradasi)
1. Tulis generator Python yang memuat dua helper wajib:
   - `grab(unit_id, start_key, end_key)`: mengiris teks Arab **100% verbatim** dari file unit *Dalil* (menghapus marker `‹akhir hlm. ...›`, menormalkan spasi) untuk `<figure class="dalil">`.
   - `mf_gold(rows)`: menghasilkan tabel Kosakata 3 kolom standar Bab 1 (`Lafaz` + `<span class="sr">` | `Arti` | `Keterangan`) tanpa `<thead>`/`<tbody>` sekaligus mengisi `mfn` otomatis.
2. Terapkan seluruh ambang kedalaman & komponen wajib di `AGENTS.md` (Tier A/B/C, SVG kreatif `style.css`-compliant, `.peta` native, `sb`, `.tbl.cmp`, `irab`, `.faidah`, `.cards`, `.kasus`, `.nb-k`).
3. **Bila menggarap banyak bab sekaligus lewat `run_workflow`:**
   - Bagi menjadi kelompok kecil (±15–25 hadits per agen) dengan file output `bab-NNN.json` yang terpisah.
   - Jalankan bertahap **maksimal 2–4 agen paralel per tahap** dengan pengecekan *auto-skip* (`cek_mutu.py` exit 0) agar aman dari batas kuota (HTTP 429) dan bisa dilanjutkan tanpa mengulang bab yang sudah lulus.

## Langkah 4: Verifikasi Mutu & Build
1. Jalankan pengunci mutu universal:
   `python cek_mutu.py <awal>-<akhir>`
   Perbaiki seluruh temuan sampai keluar **`TOTAL ISSUES: 0`**.
2. Jalankan build:
   `python build.py`
   Pastikan keluar **0 galat**. Perhatikan ukuran HTML hasil build (batas unggah Kitabuna **10 MB per file**); bila sudah masuk Jilid 2 (Bab 84+), tambahkan entri jilid baru pada `jilid.json`.
3. Perbarui `PROGRES.md` (daftar bab selesai, istilah baku baru, perawi baru yang diprofilkan, catatan tahqiq/naskah penting, dan baris baru di `Log chat`).
