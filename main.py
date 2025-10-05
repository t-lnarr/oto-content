import os
import random
import asyncio
import httpx
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pytz
TIMEZONE = pytz.timezone("Asia/Ashgabat")  # Türkmenistan saati


TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")  # örn: @kanal_adin

# --- Gemini API ile içerik üretimi ---
async def generate_post():
    konular = [
        "Python dili",
        "JavaScript",
        "HTML we CSS",
        "Django",
        "Flask",
        "FastAPI",
        "API näme?",
        "Pascal ABC",
        "C++ dili",
        "C# dili",
        "Programmirleme barada faktlar",
        "Programmistiň bilmeli zatlary",
        "Programmiste gerek zatlar",
        "Git we GitHub",
        "Algoritmalar",
        "Database",
        "Öýde edip boljak proýektlar",
        "Taslama idealar",
        "Çylşyrymly meseleler",
        "Peýdaly programmirleme barada saýtlar",
        "Programmistyň dünýäsi",
        "Programmirleme näme üçin gerek",
        "Programmirleme ugurlary",
        "Web Programmirleme",
        "SQL başlangıç üçin",
        "NoSQL bazalar",
        "Frontend vs Backend",
        "Mobil programmirleme (Flutter, React Native)",
        "Programmistler üçin maslahatlar",
        "AI we ChatGPT",
        "Kod näme ?",
        "Kod redaktorlary",
        "Programmirleme barada 5 täsin fakt",
        "Kiber howpsuzlyk",
        "Code review we hatalary tapmak",
        "IDE we gurallar (VSCode, PyCharm)",
        "Öwrenmek üçin saytlar (w3schools, freecodecamp, Codecademy)"
    ]


    konu = random.choice(konular)
    prompt = f"""
    Türkmen dilinde, {konu} baradaky gysga, gyzykly we bilgilendiriji post ýazgy döredip ber.
    Post diňe netije hökmünde bolsun — giriş sözleri bolmasyn (meselem: "Elbetde", "Ine" ýaly zatlar ýok bolsun).

    Post şu düzgünlere laýyk bolsun:
    - Postyň başynda gaty çekiji, sorag ýa-da tema bilen baglanyşykly bir at bolsun (örn: **Nädip Python öwrenmeli? 🐍**, **Python ýa-da C++ — Haýsyny saýlamaly? ⚡️**)
    - Soňra 4–6 setirlik düşündirişli, gülkünç we öwrediji mazmun bolsun.
    - Mazmun täze başlaýan programmistler üçin peýdaly maglumat we maslahatlar berýän bolsun.
      (meselem: “Python üçin haýsy sahypalary öwrenmeli?”, “Hangi gurallary ulanmaly?”, “Kody synap görmek üçin täze programmistler üçin amallar”)
    - Emojiler bilen bezelen bolsun.
    - Ahyrynda 2–3 hashtag goş (#programmirleme, #öwren, #yazılım, #ai, #telegrambot)
    - Iň soňunda bu ýazgyny "🤖 AI tarapyndan döredildi." diýip tamamla.

    Maksimum 6 setirlik post ýaz.
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
        return text


# --- Telegram'a gönderim ---
async def send_to_telegram(text):
    async with httpx.AsyncClient() as client:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        await client.post(url, json={"chat_id": CHANNEL_USERNAME, "text": text})


# --- Günlük görevler ---
async def daily_post():
    text = await generate_post()
    await send_to_telegram(text)
    print(f"{datetime.now()}: Post ugradyldy ✅")


# --- Zamanlama ---
async def main():
    scheduler = AsyncIOScheduler()

    # Sabah, öğle, akşam zamanlarını ayarlıyoruz:
    scheduler.add_job(daily_post, "cron", hour=8, minute=0, timezone=TIMEZONE)   # Sabah
    scheduler.add_job(daily_post, "cron", hour=12, minute=0, timezone=TIMEZONE)  # Öğle
    scheduler.add_job(daily_post, "cron", hour=16, minute=30, timezone=TIMEZONE)  # Akşam
    scheduler.add_job(daily_post, "cron", hour=19, minute=0, timezone=TIMEZONE)


    scheduler.start()
    print("Bot işleýär... ⏰")
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
