# YouTube Anti-JUDOL

**⚠️ PERINGATAN: PROYEK INI BELUM DIUJI SECARA MENYELURUH ⚠️**

Anti-JUDOL adalah alat untuk memantau dan mengklasifikasikan komentar YouTube, khususnya yang berpotensi mempromosikan judi online. Proyek ini masih dalam tahap pengembangan awal dan belum diuji secara menyeluruh.

## Deskripsi

Proyek ini dikembangkan untuk membantu memantau komentar YouTube secara otomatis dengan kemampuan:

- Mengekstrak komentar dari video YouTube
- Mengklasifikasikan komentar menggunakan model machine learning
- ~~Menyimpan hasil dalam format CSV untuk analisis lebih lanjut~~

## Fitur

- Pengambilan komentar YouTube menggunakan SeleniumBase
- Klasifikasi komentar dengan model machine learning (opsional)
- Pengurutan komentar berdasarkan "terbaru" atau "teratas"
- Normalisasi teks untuk bahasa Indonesia menggunakan nlp-id
- Penanganan interupsi yang baik (Ctrl+C) dengan penyimpanan otomatis

## Persyaratan

- Python 3.11 atau lebih tinggi
- Sistem operasi 64-bit (Windows atau Linux)
- Dependensi Python (lihat `pyproject.toml` atau `requirements.txt`)

Catatan: Aplikasi akan secara otomatis mengunduh dan menyiapkan browser Chromium saat pertama kali dijalankan.

## Instalasi

### Setup Otomatis (Direkomendasikan)

Proyek ini menyertakan skrip setup untuk Windows dan Linux yang secara otomatis akan:
- Memeriksa apakah kamu menggunakan sistem 64-bit (wajib)
- Mengunduh dan menginstal uv (pengelola paket Python)
- Membuat virtual environment dengan Python 3.11
- Menginstal semua dependensi
- Mengaktifkan virtual environment

#### Windows

```powershell
# Jalankan skrip PowerShell setup
.\setup.ps1

# Untuk setup pengembangan dengan alat tambahan
.\setup.ps1 --dev
```

#### Linux

```bash
# Buat skrip dapat dieksekusi
chmod +x setup.sh

# Jalankan skrip setup
./setup.sh

# Untuk setup pengembangan dengan alat tambahan
./setup.sh --dev
```

### Instalasi Manual

Jika kamu lebih suka melakukan setup secara manual:

```bash
# Clone repositori
git clone https://github.com/username/anti-judol.git
cd anti-judol

# Buat dan aktifkan virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# atau
.venv\Scripts\activate  # Windows

# Instal dependensi
pip install -e .
```

## Penggunaan

### Menjalankan Anti-JUDOL

Setelah menyiapkan lingkungan, kamu dapat menjalankan aplikasi utama:

```bash
# Aktifkan virtual environment jika belum diaktifkan
source .venv/bin/activate  # Linux/Mac
# atau
.venv\Scripts\activate  # Windows

# Jalankan aplikasi utama
python anti_judol.py --help
```

### Autentikasi

Sebelum menggunakan fitur penghapusan komentar, kamu perlu login ke akun YouTube kamu:

```bash
python anti_judol.py --login
```

Ini akan membuka jendela browser di mana kamu dapat login ke akun YouTube kamu. Sesi login akan disimpan untuk penggunaan di masa mendatang.

### Menghapus Komentar

Kamu dapat menghapus komentar dari video tertentu:

```bash
# Hapus komentar dari URL tertentu
python anti_judol.py --remove_urls "https://www.youtube.com/watch?v=VIDEO_ID1" "https://www.youtube.com/watch?v=VIDEO_ID2"

# Hapus komentar dari URL yang tercantum dalam file teks
python anti_judol.py --remove_txt "urls.txt"
```

### Memeriksa Status Login

```bash
python anti_judol.py --status
```

### Mengambil Komentar YouTube

Kamu juga dapat menggunakan pengambil komentar YouTube secara langsung:

```bash
python youtube_scraper.py --url "https://www.youtube.com/watch?v=VIDEO_ID" --output "output/comments.csv" --sort_by "top"
```

#### Parameter Pengambil Komentar

- `--url`: URL video YouTube (wajib)
- `--output`: Path untuk menyimpan file hasil CSV (default: "temp/comments.csv")
- `--sort_by`: Urutan komentar ("newest" atau "top", default: "top")
- `--model`: Path ke file model untuk klasifikasi (opsional)

## Proses Pengunduhan Browser

Ketika kamu menjalankan `anti_judol.py` untuk pertama kalinya, aplikasi akan secara otomatis:

1. Memeriksa apakah browser Chrome/Chromium sudah terpasang di direktori `bin/chrome`
2. Jika tidak ditemukan, aplikasi akan:
   - Membuat direktori `bin` jika belum ada
   - Mengunduh versi Chromium yang sesuai untuk sistem operasi kamu (Windows atau Linux)
   - Mengekstrak browser ke direktori `bin/chrome`
   - Membuat direktori `bin/User Data` untuk menyimpan data profil browser
3. Browser akan digunakan untuk autentikasi YouTube dan penghapusan komentar

Proses ini memastikan bahwa kamu tidak perlu menginstal browser secara manual, dan aplikasi akan menggunakan versi browser yang konsisten di berbagai lingkungan.

## Struktur Proyek

```
anti-judol/
├── anti_judol/
│   ├── actions/
│   │   ├── auth.py             # Autentikasi YouTube
│   │   └── remover.py          # Fungsionalitas penghapusan komentar
│   ├── download.py             # Pengunduh browser
│   ├── model.py                # Pemuatan model dan inferensi
│   └── normalizer.py           # Normalisasi teks
├── bin/                        # Direktori untuk browser dan data pengguna
│   ├── chrome/                 # File browser yang diunduh
│   └── User Data/              # Data profil browser
├── data/
│   └── models/                # Model terlatih
├── anti_judol.py              # Skrip aplikasi utama
├── youtube_scraper.py         # Pengambil komentar YouTube
├── setup.ps1                  # Skrip setup Windows
├── setup.sh                   # Skrip setup Linux
└── pyproject.toml             # Konfigurasi proyek dan dependensi
```

## Status Pengembangan

Proyek ini masih dalam tahap pengembangan awal dan **BELUM DIUJI SECARA MENYELURUH**. Beberapa fitur mungkin tidak berfungsi sebagaimana mestinya. Gunakan dengan risiko kamu sendiri.

## Keamanan dan Pengujian

### Keamanan Data
- Proyek ini dirancang dengan mempertimbangkan keamanan pengguna: semua operasi dijalankan secara lokal di komputer kamu tanpa mengirimkan data kredensial ke server eksternal.
- Saat login ke YouTube, kredensial disimpan hanya di direktori lokal `bin/User Data` dan tidak pernah dikirim ke pengembang atau pihak ketiga lainnya.
- Meskipun demikian, selalu periksa kode sumber sebelum menjalankan aplikasi yang meminta akses ke akun media sosial kamu.

### Status Pengujian
- Saat ini, proyek belum diuji pada video YouTube yang benar-benar mengandung komentar judi online (JUDOL).
- Pengujian baru dilakukan dengan data simulasi dan belum diverifikasi dalam lingkungan produksi nyata.
- Kami berencana melakukan pengujian komprehensif dengan kasus nyata di masa mendatang untuk memastikan efektivitas deteksi dan penghapusan komentar JUDOL.

[English version](README_EN.md)
