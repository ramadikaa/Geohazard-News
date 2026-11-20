# Data Dictionary Geolocation2

## Data raw

`data/raw/` berisi CSV hasil scraping Newswatch. Skema utama Newswatch:

| Kolom | Arti |
|---|---|
| `title` | Judul berita |
| `publish_date` | Waktu/tanggal publikasi sumber |
| `author` | Penulis yang dilaporkan scraper |
| `content` | Konten hasil scraping, sebelum pembersihan fase berikutnya |
| `keyword` | Kata kunci yang cocok |
| `category` | Kategori sumber |
| `source` | Nama/domain media |
| `link` | URL artikel |
| `hazard_type` | Label bahaya dari pipeline scraping, jika tersedia |

Sebagian kategori memiliki file scraping tambahan dengan akhiran `2`; seluruh file sumber disimpan, bukan hanya satu file per kategori.

## Data interim

| File | Grain | Kolom/isi penting |
|---|---|---|
| `data/interim/consolidation/newswatch_long.csv` | Satu baris per rekaman sumber | Kolom raw standar ditambah `query_group`, `sourcefile`, `scraped_at`, `url_normalized`, `article_id`, `content_hash` |
| `data/interim/consolidation/articles.csv` | Satu baris per URL artikel | Record utama dengan konten terlengkap; `query_group` berisi daftar JSON |
| `data/interim/consolidation/article_query_map.csv` | Satu baris per pasangan artikel-kueri | `article_id`, `query_group` |
| `data/interim/consolidation/content_duplicate_groups.csv` | Satu baris per kelompok konten sama lintas-URL | `content_hash`, daftar ID, URL, dan kueri |
| `data/interim/quality_control/newswatch_preprocessed.csv` | Satu baris per rekaman panjang | Kolom sumber plus kolom hasil normalisasi/profil QC |
| `data/interim/quality_control/qc_issues.csv` | Satu baris per rekaman yang perlu ditinjau | Identitas sumber, status, dan flag QC |
| `data/interim/deduplication/duplicate_pairs.csv` | Satu baris per relasi duplikat/kandidat | Artikel, `duplicate_of`, jenis, skor, status review |
| `data/interim/deduplication/near_duplicate_manual_review.csv` | Satu baris per pasangan sampel | ID pasangan, skor, cuplikan isi, status dan catatan review |

Flag QC dan status duplikat adalah anotasi; keduanya tidak menghapus rekaman.

## Data processed

`data/processed/articles_clean.csv` menyimpan semua artikel input fase deduplikasi dengan kolom utama:

| Kolom | Arti |
|---|---|
| `content_raw` | Konten sumber, tidak ditimpa |
| `content_clean` | Konten setelah pembersihan markup, boilerplate, spasi, dan karakter |
| `content_clean_hash` | Fingerprint konten bersih |
| `title_clean` | Judul dengan pembersihan tekstual ringan |
| `language_code` | `id`, `en`, `other`, atau `und` (tidak pasti) |
| `language_confidence` | Skor heuristik bahasa, bukan probabilitas terkalibrasi |
| `in_scope` | `true` untuk `id` dan `und`; `false` untuk bahasa yang dikeluarkan dari subset Indonesia |
| `duplicate_of` | ID artikel representatif; kosong jika tidak terhubung |
| `duplicate_type` | `exact_url`, `exact_content_hash`, `exact_clean_content`, `transitive_exact_content`, atau `near_duplicate` |
| `duplicate_similarity` | Skor cosine near-duplicate atau `1.0` untuk relasi exact |
| `duplicate_review_status` | Status relasi yang diterapkan: `confirmed_exact`, `confirmed`, `pending`, atau kosong. Kandidat yang ditolak tercatat pada tabel review/pasangan, bukan sebagai relasi artikel. |

`data/processed/articles_indonesia.csv` adalah subset dengan `language_code` `id` atau `und`. Artikel lain tetap tersedia di `articles_clean.csv`.

Laporan serta tabel distribusi sumber/bulan/bahasa dan grafik SVG berada di `data/interim/deduplication/`.
