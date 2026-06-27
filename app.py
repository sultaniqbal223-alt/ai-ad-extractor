import os
import requests
from bs4 import BeautifulSoup
from yt_dlp import YoutubeDL
from faster_whisper import WhisperModel
import google.generativeai as genai
from dotenv import load_dotenv

from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Load env & config Gemini
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

app = FastAPI(title="AI Marketing Ad-Extractor")

# Izinkan CORS biar frontend bisa komunikasi lancar
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Core Engines (Scraper, Whisper, Gemini)
def scrape_landing_page(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            paragraphs = soup.find_all(['h1', 'h2', 'h3', 'p'])
            return " ".join([p.get_text().strip() for p in paragraphs])[:1500]
        return f"Gagal akses website. Status Code: {response.status_code}"
    except Exception as e:
        return f"Error scraping: {str(e)}"

def process_video_ad(video_url):
    # Menggunakan fallback /18/best agar tidak diblokir 403 oleh YouTube
    ydl_opts = {
        'format': 'bestaudio[ext=m4a]/bestaudio/18/best',
        'outtmpl': 'temp_audio.%(ext)s',
        'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
        'quiet': True
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            filename = f"temp_audio.{info_dict.get('ext', 'm4a')}"
        
        model = WhisperModel("tiny", device="cpu", compute_type="int8")
        segments, _ = model.transcribe(filename, beam_size=5)
        script = " ".join([segment.text for segment in segments])
        
        if os.path.exists(filename):
            os.remove(filename)
        return script.strip()
    except Exception as e:
        return f"Error proses video: {str(e)}"

def analyze_marketing(text):
    if not GEMINI_API_KEY:
        return "API Key Gemini belum diset di file .env!"
    try:
        # Pake gemini-2.5-flash agar kompatibel dengan model termutakhir
        model = genai.GenerativeModel("gemini-2.5-flash")
        system_prompt = (
            "Kamu adalah seorang Senior Growth Hacker dan Project Manager AI Marketing yang kritis.\n"
            "Tugasmu adalah membedah teks/transkrip iklan kompetitor dan menghasilkan ide konten baru.\n\n"
            "Format Output harus rapi menggunakan Markdown:\n"
            "### 🎯 Hasil Analisis Kompetitor\n"
            "* **Target Audience:** (isi)\n"
            "* **Pain Point Utama:** (isi)\n"
            "* **Core Angle:** (isi)\n\n"
            "### 🎬 5 Variasi Naskah/Hook Baru (TikTok/Reels)\n"
            "1. **[Hook 1]** VO: (isi)\n"
            "2. **[Hook 2]** VO: (isi)\n"
            "3. **[Hook 3]** VO: (isi)\n"
            "4. **[Hook 4]** VO: (isi)\n"
            "5. **[Hook 5]** VO: (isi)\n\n"
            "ATURAN KETAT:\n"
            "- Setiap Voice Over (VO) wajib pendek dan padat, MAKSIMAL 22 kata atau 145 karakter.\n"
            "- Fokus penuh pada keunggulan produk itu sendiri. JANGAN bandingkan dengan brand lain.\n"
            "- Gunakan gaya bahasa kasual Indonesia."
        )
        response = model.generate_content(f"{system_prompt}\n\nTeks kompetitor:\n{text}")
        return response.text
    except Exception as e:
        return f"Error Gemini: {str(e)}"

# Routing API
@app.get("/")
def read_root():
    return FileResponse("index.html")

@app.post("/analyze")
async def handle_analyze(input_type: str = Form(...), input_value: str = Form(...)):
    if not input_value.strip():
        raise HTTPException(status_code=400, detail="Input tidak boleh kosong")
    
    # 1. Ambil data mentah berdasarkan tipe input
    if input_type == "url_lp":
        raw_text = scrape_landing_page(input_value)
    elif input_type == "url_video":
        raw_text = process_video_ad(input_value)
    else:
        raw_text = input_value # Jika user pilih copy-paste manual
        
    if "Error" in raw_text or "Gagal" in raw_text:
        return JSONResponse(status_code=400, content={"detail": raw_text})
        
    # 2. Olah ke Gemini
    ai_result = analyze_marketing(raw_text)
    return {"raw_text": raw_text, "analysis": ai_result}
