# 🎯 AI Competitor Ad-Angle Extractor & Hook Generator

Aplikasi berbasis AI yang dirancang untuk membantu *Digital Marketer*, *Advertiser*, dan *Affiliate Marketer* membedah strategi konten iklan kompetitor secara otomatis dan menghasilkan 5 variasi naskah iklan baru berdurasi pendek (TikTok/Reels/Shorts) dalam hitungan detik.

## 💡 Masalah yang Diselesaikan (Marketing Pain Points)
* **Brainstorming Fatigue:** Pembuatan ide *angle* iklan baru setiap minggu memakan waktu berjam-jam. Tools ini memotong waktu kerja dari 3 jam menjadi 3 menit.
* **Ad-Fatigue Solution:** Membantu pengiklan membuat variasi konten baru dengan cepat tanpa kehilangan esensi pesan produk yang terbukti laris di pasar.
* **Cost Efficiency:** Menggunakan infrastruktur lokal ($0) untuk transkripsi video dan memanfaatkan *free-tier* API untuk analisis teks.

## 🛠️ Fitur Utama & Arsitektur Sistem
Aplikasi ini dibangun dengan pendekatan murni **Vibe Coding** dengan arsitektur lokal yang hemat biaya:
1. **Multi-Input Scraper & Extractor:** 
   * **URL Landing Page:** Mengekstrak teks penawaran menggunakan `BeautifulSoup4`.
   * **URL Video (TikTok/YouTube):** Mengambil audio mentah bypass proteksi via `yt-dlp`.
2. **Local Audio-to-Text AI:** Memproses transkripsi audio langsung di mesin lokal menggunakan model **OpenAI Whisper (`faster-whisper`)** tanpa biaya API tambahan.
3. **AI Marketing Engine:** Memanfaatkan **Gemini 2.5 Flash API** untuk membedah psikologi konsumen (*Target Audience, Pain Point, Core Angle*) dan menyusun ulang naskah baru.
4. **Interactive Dashboard:** Tampilan web sederhana dan responsif menggunakan **FastAPI** dan **Tailwind CSS**.

## 📏 Aturan Ketat Copywriting AI
Sistem prompt pada engine AI dikonfigurasi secara ketat untuk menghasilkan output siap pakai:
* **Voice Over (VO) Limitation:** Naskah yang dihasilkan dibatasi maksimal **22 kata atau ~145 karakter** per video agar sesuai dengan ritme retensi audiens video pendek.
* **Product-Focused:** AI dipaksa fokus 100% pada keunggulan produk itu sendiri, tanpa menghubungkan atau membandingkan secara negatif dengan kompetitor lain.

## 🚀 Cara Menjalankan di Localhost

### 1. Kloning & Persiapan Environment
```bash
# Masuk ke folder project
cd ad-extractor-ai

# Buat dan aktifkan Virtual Environment
python -m venv venv
source venv/bin/activate  # Untuk Mac/Linux
# .\venv\Scripts\activate  # Untuk Windows
```

### 2. Instalasi Dependensi
```bash
pip install -r requirements.txt
```

### 3. Konfigurasi Environment Variables
Buat file bernama `.env` di folder utama project dan tambahkan API Key Gemini Anda:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 4. Menjalankan Server Lokal
Jalankan server FastAPI menggunakan `uvicorn`:
```bash
uvicorn app:app --reload
```
Setelah itu, buka browser Anda dan akses: [http://127.0.0.1:8000](http://127.0.0.1:8000)
