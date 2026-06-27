import os
import requests
from bs4 import BeautifulSoup
from yt_dlp import YoutubeDL
from faster_whisper import WhisperModel
import google.generativeai as genai
from dotenv import load_dotenv

# Load API Key dari file .env
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Konfigurasi Gemini API
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("[!] PERINGATAN: GEMINI_API_KEY tidak ditemukan di file .env!")

# ==========================================
# 1. ENGINE SCRAPER TEKS LANDING PAGE
# ==========================================
def scrape_landing_page(url):
    print(f"\n[+] Mencoba scrape URL: {url}")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            paragraphs = soup.find_all(['h1', 'h2', 'h3', 'p'])
            text_content = " ".join([p.get_text().strip() for p in paragraphs])
            return text_content[:1000]
        else:
            return f"Gagal Scrape. Status Code: {response.status_code}"
    except Exception as e:
        return f"Error saat scraping: {str(e)}"

# ==========================================
# 2. ENGINE DOWNLOAD & TRANSKRIP VIDEO
# ==========================================
def process_video_ad(video_url):
    print(f"\n[+] Mencoba memproses video: {video_url}")
    # Gunakan fallback /18/best agar tidak terkena 403 / format unavailable pada video yang terproteksi
    ydl_opts = {
        'format': 'bestaudio[ext=m4a]/bestaudio/18/best',
        'outtmpl': 'temp_audio.%(ext)s',
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web'],
            }
        },
        'quiet': True
    }
    try:
        print("[+] Mendownload audio asli (.m4a) atau fallback video dari video...")
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            ext = info_dict.get('ext', 'm4a')
            filename = f"temp_audio.{ext}"
            
        print(f"[+] Audio berhasil di-download: {filename}")
        
        print("[+] Menjalankan Whisper AI Lokal (Model: tiny)...")
        model = WhisperModel("tiny", device="cpu", compute_type="int8")
        segments, info = model.transcribe(filename, beam_size=5)
        
        script = ""
        for segment in segments:
            script += f"{segment.text} "
            
        if os.path.exists(filename):
            os.remove(filename)
            
        return script.strip()
    except Exception as e:
        return f"Error saat memproses video: {str(e)}"

# ==========================================
# 3. ENGINE AI MARKETING (GEMINI BRAIN)
# ==========================================
def analyze_and_generate_hooks(marketing_text):
    print("\n[+] Menghubungi Otak AI (Gemini) untuk analisis...")
    if not GEMINI_API_KEY:
        return "Gagal: API Key Kosong."
        
    try:
        # Pake model flash yang cepet, enteng, dan free tier-nya luas
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        system_prompt = (
            "Kamu adalah seorang Senior Growth Hacker dan Project Manager AI Marketing yang skeptis, kritis, dan sangat praktis.\n"
            "Tugasmu adalah membedah teks/transkrip iklan kompetitor berikut dan menghasilkan ide konten baru.\n\n"
            "LANGKAH 1: Bedah secara singkat (Target Audience, Utama Pain Point, dan Core Angle).\n"
            "LANGKAH 2: Buat 5 variasi naskah/hook baru untuk video pendek (TikTok/Reels).\n\n"
            "ATURAN KETAT:\n"
            "1. Setiap naskah Voice Over (VO) HARUS pendek dan padat, MAKSIMAL 22 kata atau kurang lebih 145 karakter agar pas dengan ritme video cepat.\n"
            "2. Fokus 100% pada keunggulan produk itu sendiri. JANGAN menghubungkan atau membandingkan dengan produk kompetitor lain.\n"
            "3. Gunakan gaya bahasa yang kasual, persuasif, dan cocok untuk audiens Indonesia."
        )
        
        full_prompt = f"{system_prompt}\n\nBerikut teks kompetitor yang harus dibedah:\n{marketing_text}"
        
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"Error saat menghubungi Gemini: {str(e)}"

# ==========================================
# RUN SYSTEM
# ==========================================
if __name__ == "__main__":
    # Kita langsung tembak test video Rickroll yang kemarin sukses
    target_video = "https://www.youtube.com/shorts/dQw4w9WgXcQ" 
    
    # 1. Jalankan Transkrip Video lokal
    transkrip_hasil = process_video_ad(target_video)
    print(f"\n[+] Hasil Mentah Transkrip:\n{transkrip_hasil}")
    
    # 2. Oper ke Gemini AI untuk dibedah dan dibuatkan Hook baru
    if "Error" not in transkrip_hasil:
        analisis_marketing = analyze_and_generate_hooks(transkrip_hasil)
        print("\n==================================================")
        print("--- HASIL ANALISIS AI MARKETING & HOOK GENERATOR ---")
        print("==================================================")
        print(analisis_marketing)
    else:
        print("[!] Gagal melanjutkan ke AI karena proses transkrip bermasalah.")
