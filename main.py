import os
import random
import asyncio
import httpx
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pytz

TIMEZONE = pytz.timezone("Asia/Ashgabat")

# --- Ayarlar ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")
HF_API_TOKEN = os.getenv("HF_API_TOKEN")

konular = [
    "Python dili", "JavaScript", "HTML we CSS", "Django", "Flask", "FastAPI", 
    "Pascal ABC", "C++ dili", "C# dili", "Algoritmalar", "Database",
    "Web Programmirleme", "AI we ChatGPT", "Kiber howpsuzlyk"
]

# --- Gemini ile post üretimi ---
async def generate_post():
    konu = random.choice(konular)
    prompt = f"""
    Türkmen dilinde, programmirleme barada gyzyklanýanlara {konu} baradaky gysga, 
    gyzykly we öwrediji bir post ýazgy döredip ber.
    Post dişe netije hökümünde bolsun – giriş sözleri bolmasyn.
    - Temanyň ady we esasy ýazgy bar bolsun
    - 4–6 setirlik düşündiriş, gülküñç, gyzykly we bir zat öwrediji mazmun bolsun
    - Emojiler bilen bezelen bolsun
    - Ahyrynda tema degişli 2–3 hashtag (#teknologiya, #python, #web)
    - Işi soňunda "🤖 AI tarapyndan döredildi."
    """
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            response = await client.post(
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
                params={"key": GEMINI_API_KEY},
                json={"contents": [{"parts": [{"text": prompt}]}]},
            )
            data = response.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            print(f"Gemini hatası: {e}")
            text = f"Hata ýüze çykdy: {e}"
    
    return konu, text

# --- Topic'i ingilizceye çevir ---
async def translate_topic_to_prompt(topic):
    prompt = f"Convert this topic into a short, simple English keyword (max 10 words): {topic}"
    async with httpx.AsyncClient(timeout=20) as client:
        try:
            response = await client.post(
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
                params={"key": GEMINI_API_KEY},
                json={"contents": [{"parts": [{"text": prompt}]}]},
            )
            data = response.json()
            english_prompt = data["candidates"][0]["content"]["parts"][0]["text"]
            english_prompt = english_prompt.split("\n")[0].strip()[:60]
            return english_prompt
        except Exception as e:
            print(f"Translation hatası: {e}")
            return topic

# --- AI görsel üretimi (DÜZELTILMIŞ) ---
async def generate_ai_image(prompt):
    """
    Hugging Face API'den görsel üretiyor.
    Direkt bytes döndürüyor, base64 değil!
    """
    print(f"Görsel üretiliyor: {prompt}")
    
    async with httpx.AsyncClient(timeout=120) as client:
        headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
        payload = {"inputs": prompt}
        
        try:
            response = await client.post(
                "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0",
                headers=headers,
                json=payload,
            )
            
            print(f"HF Status Code: {response.status_code}")
            
            # 402 = Quota aşılmış, 503 = Model loading, 200 = Başarı
            if response.status_code == 200:
                # Hugging Face direkt image bytes döndürüyor
                return response.content
            elif response.status_code == 503:
                print("Model yükleniyor, lütfen bekleyin...")
                return None
            elif response.status_code == 402:
                print("⚠️ Hugging Face API Quote AŞILMIŞ veya Ödeme Gerekli!")
                print(f"Response: {response.text}")
                return None
            else:
                print(f"API Hatası: {response.status_code} - {response.text[:200]}")
                return None
                
        except asyncio.TimeoutError:
            print("Timeout: Görsel üretimi çok uzun sürdü")
            return None
        except Exception as e:
            print(f"Görsel üretim hatası: {e}")
            return None

# --- Telegram'a gönderim ---
async def send_to_telegram(text, image_bytes=None):
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            if image_bytes:
                # Görsel varsa photo olarak gönder
                files = {"photo": ("image.png", image_bytes, "image/png")}
                data = {"chat_id": CHANNEL_USERNAME, "caption": text}
                response = await client.post(
                    f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto",
                    data=data,
                    files=files
                )
                print(f"Telegram Photo: {response.status_code}")
            else:
                # Görsel yoksa sadece metin gönder
                response = await client.post(
                    f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                    json={"chat_id": CHANNEL_USERNAME, "text": text}
                )
                print(f"Telegram Message: {response.status_code}")
        except Exception as e:
            print(f"Telegram gönderim hatası: {e}")

# --- Günlük görev ---
async def daily_post():
    try:
        print(f"\n📝 Post üretiliyor... ({datetime.now()})")
        
        konu, text = await generate_post()
        prompt = await translate_topic_to_prompt(konu)
        
        print(f"Konu: {konu}")
        print(f"İngilizce Prompt: {prompt}")
        
        # Görsel üret (hata olsa da devam et)
        image_bytes = await generate_ai_image(prompt)
        
        # Telegram'a gönder
        await send_to_telegram(text, image_bytes)
        
        print(f"✅ Post gönderildi! | Tema: {konu}")
        
    except Exception as e:
        print(f"❌ Daily post hatası: {e}")

# --- Zamanlayıcı ---
async def main():
    scheduler = AsyncIOScheduler()
    
    # 7 kez günde post gönder
    hours = [6, 9, 12, 15, 18, 21, 23]
    for hour in hours:
        scheduler.add_job(daily_post, "cron", hour=hour, minute=0, timezone=TIMEZONE)
    
    scheduler.start()
    print("🤖 Bot çalışıyor...")
    
    try:
        while True:
            await asyncio.sleep(3600)
    except KeyboardInterrupt:
        print("Bot durduruldu")
        scheduler.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
