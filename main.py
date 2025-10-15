import os
import random
import asyncio
import httpx
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pytz
import base64

TIMEZONE = pytz.timezone("Asia/Ashgabat")  # Türkmenistan saati

# --- Ayarlar ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")  # örn: @kanal_adin
HF_API_TOKEN = os.getenv("HF_API_TOKEN")


# --- Konular ---
konular = [
    "Python dili", "JavaScript", "HTML we CSS", "Django", "Flask", "FastAPI", "API näme?",
    "Pascal ABC", "C++ dili", "C# dili", "Programmirleme barada faktlar", "Random bir dilde random bir kod",
    "Random bir programirleme dili barada", "Random bir programirleme temasy",
    "Programmistiň bilmeli zatlary", "Programmiste gerek zatlar", "Git we GitHub",
    "Algoritmalar", "Database", "Peýdaly programmirleme barada saýtlar",
    "Programmistyň dünýäsi", "Programmirleme näme üçin gerek", "Programmirleme ugurlary",
    "Web Programmirleme", "SQL başlangıç üçin", "NoSQL bazalar", "Frontend vs Backend",
    "Mobil programmirleme (Flutter, React Native)", "Programmistler üçin maslahatlar",
    "AI we ChatGPT", "Kiber howpsuzlyk", "Code review we hatalary tapmak",
    "IDE we gurallar (VSCode, PyCharm)", "Programirleme Öwrenmek üçin saytlar", "Programirleme bölümleri"
]

# --- Gemini ile post üretimi ---
async def generate_post():
    konu = random.choice(konular)
    prompt = f"""
    Türkmen dilinde, programmirleme barada gyzyklanýanlara {konu} baradaky gysga, gyzykly we öwrediji bir post ýazgy döredip ber.
    Post diňe netije hökmünde bolsun — giriş sözleri bolmasyn.
    - Temanyň ady we esasy ýazgy bar bolsun
    - 4–6 setirlik düşündirişli, gülkünç, gyzykly we bir zad öwrediji mazmun bolsun
    - Gerek bolsa mysallar getirip görkezde mazmuny baýlaşdyr
    - Düşnükli, hat ýalňyşsyz bolsun. Uniwersal sözleri iňlisçe açdyp bilersiň.
    - Emojiler bilen bezelen bolsun
    - Ahyrynda tema degişli 2–3 hashtag (#teknologiya, #python, #web)
    - Iň soňunda "🤖 AI tarapyndan döredildi."
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
            params={"key": GEMINI_API_KEY},
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=30
        )
        data = response.json()
        try:
            text = data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            text = f"Ýalňyşlyk ýüze çykdy: {e}"

    return konu, text

# --- Gemini ile konu İngilizce prompta çevir ---
async def translate_topic_to_prompt(topic):
    prompt = f"Convert this topic into a short, simple English keyword or phrase suitable for image generation: {topic}"
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
            params={"key": GEMINI_API_KEY},
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=20
        )
        data = response.json()
        try:
            english_prompt = data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            english_prompt = topic
    # Tek satır ve çok uzun olmasın diye kısaltıyoruz:
    english_prompt = english_prompt.split("\n")[0].strip()
    if len(english_prompt) > 60:  # 60 karakteri geçmesin
        english_prompt = english_prompt[:60]
    return english_prompt



async def generate_ai_image(prompt):
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
        payload = {"inputs": prompt, "options": {"wait_for_model": True}}
        response = await client.post(
            "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0",
            headers=headers,
            json=payload,
            timeout=60
        )

        if response.status_code == 200:
            # Eğer direkt bytes geldiyse bunu kullan
            content_type = response.headers.get("content-type", "")
            if "application/json" in content_type:
                data = response.json()
                # Eğer JSON içinde "image" alanı varsa base64 decode yap
                image_base64 = data.get("image", None)
                if image_base64:
                    return base64.b64decode(image_base64)
            else:
                # Direct image bytes olarak dönüyorsa
                return response.content
        else:
            print(f"Hugging Face API hatası: {response.status_code}")
        return None


# --- Telegram'a gönderim ---
async def send_to_telegram(text, image_bytes=None):
    async with httpx.AsyncClient() as client:
        if image_bytes:
            # Telegram API'ye file upload için multipart/form-data gerekiyor
            files = {"photo": ("image.png", image_bytes)}
            data = {"chat_id": CHANNEL_USERNAME, "caption": text}
            await client.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto", data=data, files=files)
        else:
            await client.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                              json={"chat_id": CHANNEL_USERNAME, "text": text})

# --- Günlük görev ---
async def daily_post():
    konu, text = await generate_post()
    prompt = await translate_topic_to_prompt(konu)

    # Buraya ekliyoruz:
    print(f"Görsel için kullanılan prompt: {prompt}")

    image_bytes = await generate_ai_image(prompt)
    await send_to_telegram(text, image_bytes)
    print(f"{datetime.now()}: Post gönderildi ✅ | Tema: {konu}")


# --- Zamanlayıcı ---
async def main():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(daily_post, "cron", hour=6, minute=0, timezone=TIMEZONE)
    scheduler.add_job(daily_post, "cron", hour=9, minute=0, timezone=TIMEZONE)
    scheduler.add_job(daily_post, "cron", hour=12, minute=0, timezone=TIMEZONE)
    scheduler.add_job(daily_post, "cron", hour=15, minute=0, timezone=TIMEZONE)
    scheduler.add_job(daily_post, "cron", hour=18, minute=0, timezone=TIMEZONE)
    scheduler.add_job(daily_post, "cron", hour=21, minute=0, timezone=TIMEZONE)

    scheduler.start()
    print("Bot çalışıyor... ⏰")
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
