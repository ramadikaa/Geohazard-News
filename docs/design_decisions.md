# Keputusan Desain Pipeline Geolocation2

## Struktur dan alur data

- `data/raw/` menyimpan semua CSV sumber scraping (saat ini 14 file dari 8 kelompok bahaya). File di sini tidak diedit oleh skrip pipeline.
- `data/interim/consolidation/` berisi hasil concat, agregasi artikel, dan pemetaan artikel-kueri.
- `data/interim/quality_control/` berisi data QC baris-per-baris dan laporan profiling.
- `data/interim/deduplication/` berisi relasi duplikat, sampel review manual, distribusi, serta laporan/grafik kualitas.
- `data/processed/` berisi tabel bersih siap analisis. Artikel yang tidak berbahasa Indonesia tetap tersimpan di `articles_clean.csv`.
- `src/` berisi skrip transformasi yang dapat dijalankan ulang. Notebook disimpan untuk eksplorasi, bukan sebagai satu-satunya implementasi pipeline.

Urutan pemrosesan:

1. `src/gabungkan_news_watch.py`: concat CSV raw, standarisasi kolom, normalisasi URL, buat ID artikel, tabel artikel dan article-query map.
2. `src/preprocessing_qc_news_watch.py`: anotasi kualitas metadata, tanggal, panjang konten, dan duplikasi tanpa membuang baris.
3. `src/clean_deduplicate_articles.py`: simpan konten raw/bersih, deteksi bahasa, deduplikasi bertingkat, serta hasil siap pakai dan laporan.

## Keputusan pembersihan

- Nilai sumber tidak ditimpa. Dataset akhir menyimpan `content_raw` dan `content_clean`.
- Pembersihan menghapus markup HTML, spasi berlebih, karakter kontrol/mojibake yang dikenal, label rekomendasi baca, dan footer umum. Pembersihan boilerplate menggunakan pola konservatif agar teks berita utama tidak sengaja terpotong.
- `content_clean_hash` dihitung setelah pembersihan untuk mendukung pemeriksaan exact-content.

## Keputusan deduplikasi

- Identitas URL dan `article_id` dari fase konsolidasi tetap menjadi acuan utama.
- Exact-content diperiksa dari `content_hash` sumber dan fingerprint konten bersih.
- Near-duplicate menggunakan TF-IDF unigram sparse dan cosine similarity dengan ambang default `0.90`; fitur judul diberi bobot lebih tinggi.
- Tidak ada artikel yang dihapus. Relasi ditulis pada `duplicate_of`, `duplicate_type`, dan `duplicate_similarity`.
- Pasangan near-duplicate bersifat kandidat sampai diperiksa. Sampel manual mencatat `confirmed`, `rejected`, atau `pending`; gunakan kembali file review saat menjalankan ulang skrip.

## Bahasa dan cakupan

- Deteksi bahasa merupakan heuristik kata umum Indonesia/Inggris; bukan model bahasa terlatih dan confidence-nya bukan probabilitas terkalibrasi.
- Bahasa tidak pasti (`und`) dipertahankan pada `articles_indonesia.csv` agar artikel lokal tidak terbuang hanya karena bukti bahasa kurang.
- Artikel yang terdeteksi Inggris atau bahasa lain tetap berada di `articles_clean.csv`, tetapi tidak masuk ke `articles_indonesia.csv`.

## Menjalankan pipeline

Jalankan dari folder `geolocation2`:

```powershell
python .\src\gabungkan_news_watch.py
python .\src\preprocessing_qc_news_watch.py
python .\src\clean_deduplicate_articles.py
```

Setelah mengisi keputusan pada sampel near-duplicate, terapkan keputusan itu saat proses ulang:

```powershell
python .\src\clean_deduplicate_articles.py --manual-review-file .\data\interim\deduplication\near_duplicate_manual_review.csv
```

Path input/output dan ambang cosine dapat diubah lewat opsi CLI masing-masing skrip.
