import os
import random
import asyncio
import httpx
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pytz
from flask import Flask
from threading import Thread

# --- Flask Keep Alive ---
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Bot is running and alive!"

def run():
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()


# --- Zaman Dilimi ---
TIMEZONE = pytz.timezone("Asia/Ashgabat")

# --- Çevre Değişkenleri ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")  # örn: @kanal_adin

# --- Gemini API ile içerik üretimi ---
async def generate_post():
    konular = [
        "Python dili", "JavaScript", "HTML we CSS", "Django", "Flask",
        "FastAPI", "API näme?", "Pascal ABC", "C++ dili", "C# dili",
        "Programmirleme barada faktlar", "Programmistiň bilmeli zatlary",
        "Programmiste gerek zatlar", "Git we GitHub", "Algoritmalar",
        "Database", "Öýde edip boljak proýektlar", "Taslama idealar",
        "Çylşyrymly meseleler", "Peýdaly programmirleme barada saýtlar",
        "Programmistyň dünýäsi", "Programmirleme näme üçin gerek",
        "Programmirleme ugurlary", "Web Programmirleme",
        "SQL başlangıç üçin", "NoSQL bazalar", "Frontend vs Backend",
        "Mobil programmirleme (Flutter, React Native)",
        "Programmistler üçin maslahatlar", "AI we ChatGPT", "Kod näme ?",
        "Kod redaktorlary", "Programmirleme barada 5 täsin fakt",
        "Kiber howpsuzlyk", "Code review we hatalary tapmak",
        "IDE we gurallar (VSCode, PyCharm)",
        "Öwrenmek üçin saytlar (w3schools, freecodecamp, Codecademy)"
    ]

    konu = random.choice(konular)
    prompt = f"""
    Türkmen dilinde, {konu} baradaky gysga, gyzykly we bilgilendiriji post ýazgy döredip ber.
    Post diňe netije hökmünde bolsun — giriş sözleri bolmasyn.

    Düzgünler:
    - Başynda soragly ýa-da tema bilen baglanyşykly çekiji başlyk bolsun.
    - Soňra 4–6 setirlik düşündiriş bolsun.
    - Emojiler bolsun.
    - Ahyrynda 2–3 hashtag we "🤖 AI tarapyndan döredildi." bolsun.
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
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            return f"Ýalňyşlyk ýüze çykdy: {e}"


# --- Telegram’a gönderim ---
async def send_to_telegram(text):
    async with httpx.AsyncClient() as client:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        await client.post(url, json={"chat_id": CHANNEL_USERNAME, "text": text})


# --- Günlük post görevi ---
async def daily_post():
    text = await generate_post()
    await send_to_telegram(text)
    print(f"{datetime.now()}: Post ugradyldy ✅")


# --- Ana fonksiyon ---
async def main():
    keep_alive()

    scheduler = AsyncIOScheduler()

    # Sabah, öğle, akşam zamanlarını ayarlıyoruz:
    scheduler.add_job(daily_post, "cron", hour=8, minute=0, timezone=TIMEZONE)
    scheduler.add_job(daily_post, "cron", hour=12, minute=0, timezone=TIMEZONE)
    scheduler.add_job(daily_post, "cron", hour=16, minute=0, timezone=TIMEZONE)
    scheduler.add_job(daily_post, "cron", hour=20, minute=0, timezone=TIMEZONE)

    scheduler.start()
    print("Bot işleýär... ⏰")
    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main())
