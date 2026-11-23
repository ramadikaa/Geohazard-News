# Pedoman Anotasi Geohazard-News

Versi: 1.0

## Tujuan

Pedoman ini digunakan untuk memberi label pada artikel berita geohazard. Satu baris sama dengan satu artikel unik; tidak ada anotasi per kueri pencarian atau per laporan yang sama.

## Rentang label

### A. Relevansi

Pilih satu label:

| Label | Definisi |
|---|---|
| `actual_event` | Artikel melaporkan kejadian aktual, aktual yang baru dilaporkan, atau peristiwa berpotensi terjadi dalam jangka dekat. |
| `non_event` | Artikel membahas edukasi, mitigasi, opini, sejarah, analisis umum, peringatan permanen, atau kiasan tanpa melaporkan kejadian aktual sebagai inti berita. |
| `irrelevant` | Artikel tidak membahas geohazard yang menjadi cakupan atau hanya menyebut istilah secara tidak substantif. |

Gunakan `actual_event` hanya jika isi artikel menunjukkan kejadian atau dampaknya dalam kerangka waktu nyata. Judul yang sensasional tidak boleh mengubah label bila isi artikelnya edukatif atau tidak relevan.

Contoh positif:

- Gempa terjadi di wilayah tertentu dan warga merasakan getaran.
- Gunung api menaikkan status dan menunjukkan peningkatan aktivitas terkini.
- Banjir memicu longsor yang merusak rumah pada hari kejadian.

Contoh negatif:

- Artikel cara menghadapi gempa atau membuat tas siaga.
- Sejarah letusan gunung api pada periode lampau.
- Opini tentang perlunya kebijakan mitigasi.
- Ungkapan kiasan seperti “gempa politik”.
- Artikel banjir atau cuaca yang sama sekali tidak mengaitkan bencana pada kecamatan yang dituju.

### B. Jenis bencana

Gunakan format multi-label. Pilih setiap jenis yang benar-benar dibahas sebagai kejadian atau subjek utama. Jangan menandai hanya karena kata muncul sekali.

1. `gunungapi`
2. `gempabumi`
3. `tsunami`
4. `tanah_longsor`
5. `likuefaksi`
6. `abrasi_pantai`
7. `penurunan_tanah`
8. `semburan_gas_lumpur`

Contoh multi-label:

- Gempa memicu tanah longsor: tandai `gempabumi` dan `tanah_longsor`.
- Erupsi gunung api menimbulkan tsunami: tandai `gunungapi` dan `tsunami`.
- Artikel gempa yang hanya menyebut kemungkinan tsunami sebagai konteks edukatif, tetapi bukan kejadian aktual: untuk relevansi tetap `actual_event` dan tsunami hanya ditandai jika ada laporan tsunami aktual.

Jika artikel tidak relevan atau `non_event`, kolom jenis bencana tetap dapat diisi berdasarkan subjek utama. Untuk analisis evaluasi nantinya, relevansi digunakan sebagai filter utama.

### C. Konteks pemberitaan

Pilih satu label utama:

| Label | Definisi |
|---|---|
| `new_event` | Berita baru mengenai kejadian atau status pertama yang dilaporkan. |
| `update` | Perkembangan lanjutan: korban, intensitas, status, pencarian, evakuasi, atau situasi yang berubah. |
| `impact_report` | Fokus utama pada kerusakan, korban, atau dampak sosial-ekonomi. |
| `aid_response` | Fokus utama pada bantuan, evakuasi, relokasi, pemulihan, atau respons pemerintah. |
| `expert_analysis` | Fokus utama pada analisis, penjelasan mekanisme, atau kutipan ahli. |

Pilih label yang paling dominan. Jika sama kuat, pilih urutan: `impact_report`, `aid_response`, `expert_analysis`, `update`, `new_event`.

## Aturan kasus ambigu

1. Judul aktual tetapi isi hanya edukasi: label relevansi mengikuti isi utama, yaitu `non_event`.
2. Peristiwa masa lalu diberitakan ulang karena dampaknya kini: `actual_event` hanya jika konteks aktual/dampak aktual jelas; jika hanya narasi sejarah, gunakan `non_event`.
3. Prediksi atau potensi bahaya: gunakan `actual_event` hanya jika ada kejadian/potensi yang dilaporkan sebagai status terkini; artikel teoretis umum adalah `non_event`.
4. Peristiwa dari negara lain: relevan jika termasuk salah satu dari 8 jenis bencana.
5. Berita multi-bencana: pilih semua jenis yang dideskripsikan sebagai kejadian aktual.
6. Artikel potongan atau kandungan tidak lengkap: tandai `ambiguous=true` dan beri catatan singkat. Jangan menebak.
7. Duplikat dari sumber lain: tidak dianotasi ulang jika sudah dipilih sebagai representatif. Gunakan satu baris per `article_id`.
8. Kemiripan kata tidak cukup: harus ada indikasi kejadian atau pembahasan substantif jenis bencana.

## Alur anotasi

1. Baca judul dan isi bersih; untuk kasus tidak jelas, buka tautan asli.
2. Isi kolom relevansi, semua boolean jenis bencana, konteks, dan catatan.
3. Tandai `ambiguous=true` untuk kasus yang membutuhkan keputusan tim.
4. Jangan mengubah `article_id`, `source`, `query_group`, atau kolom split.
5. Simpan satu kali setelah satu batch, jangan menimpa versi anotasi sebelumnya.
6. Jangan melihat atau mengubah baris dengan `split=test` sampai fase evaluasi model.

## Contoh baris

| relevance | gempabumi | tanah_longsor | context | ambiguous | contoh |
|---|---|---|---|---|---|
| `actual_event` | `true` | `true` | `impact_report` | `false` | Gempa disertai longsor dan kerusakan rumah |
| `non_event` | `true` | `false` | `expert_analysis` | `false` | Cara mengenali gempa dan mitigasi |
| `irrelevant` | `false` | `false` | `expert_analysis` | `false` | Krisis politik disebut gempa sosial |

## Output evaluasi

Laporkan:

- Distribusi relevansi.
- Persentase artikel `non_event` dan `irrelevant`.
- Distribusi 8 jenis bencana.
- Jumlah artikel multi-label.
- Cohen’s Kappa untuk relevansi dan konteks.
- Cohen’s Kappa per jenis bencana biner.
- Persentase exact match dan disagreement pada multi-label.

## Siapkan data anotasi

Jalankan dari root proyek:

```powershell
python .\src\create_annotation_sample.py
```

Perintah default menghasilkan:

- `400` artikel unik
- `80` artikel test set
- `320` artikel train/pilot pool
- `100` artikel dual annotation
- seed sampling `20261120`

Output tersedia pada `data/interim/annotation/`:

- `annotation_sample.csv`: seluruh sampel dan status split
- `test_set.csv`: daftar test yang harus dikunci
- `dual_annotation.csv`: subset untuk anotator 1 dan 2
- `sampling_summary.json`: ringkasan jumlah sampel

Untuk mengubah jumlah atau seed:

```powershell
python .\src\create_annotation_sample.py --sample-size 400 --test-size 80 --dual-size 100 --seed 20261120
```

Script secara default mengecualikan artikel yang terhubung sebagai exact atau near-duplicate. Gunakan `--include-duplicates` hanya jika tim sengaja ingin mengevaluasi duplikat.

## Tata kerja spreadsheet

1. Salin `annotation_sample.csv` sebagai file kerja; jangan menulis langsung pada file hasil generator.
2. Buat file terpisah untuk setiap anotator pada 100 artikel dual.
3. Gunakan nilai huruf kecil pada kolom label agar mudah dihitung: `true`/`false`, `actual_event`/`non_event`/`irrelevant`.
4. Untuk jenis bencana, isi `true` hanya jika jenis tersebut dibahas sebagai kejadian atau subjek substantif.
5. Pertama annotasi 30–50 artikel pilot. Dua anotator mengerjakan subset pilot yang sama.
6. Setelah pilot, lakukan adjudikasi dan perbaiki pedoman sebelum annotasi 320 artikel training.
7. Jangan buka `test_set.csv` sebagai bahan penyempurnaan pedoman atau pemilihan model.
8. Simpan versi file kerja dan catatan resolusi disagreement.

## Dashboard pemeriksaan

Buat dashboard HTML interaktif dari CSV terbaru:

```powershell
python .\src\create_annotation_dashboard.py
```

Dashboard disimpan sebagai `data/interim/annotation/annotation_review.html`.
Buka file tersebut di browser. Dashboard menyediakan ringkasan distribusi
label, pencarian teks, filter split/kueri/sumber/relevansi/konteks/jenis
bencana, pembacaan isi artikel, dan unduhan CSV hasil filter. Untuk
membangun dari file atau lokasi lain, gunakan `--input` dan `--output`.

Dashboard menampilkan catatan bahwa label AI masih perlu ditinjau dan
anotasi AI tidak dapat dipakai untuk mengukur kesepakatan antar-anotator.
