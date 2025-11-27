"""
Telegram Kanal Botu - Günlük İçerik Paylaşımı
Özellikler:
- Günde 4 post (09:00, 13:00, 13:30, 19:00)
- Günlük test/anket (21:00)
- Gemini API ile içerik üretimi
- Türkmence postlar
"""

import asyncio
import os
import re
from datetime import datetime, time
from telegram import Bot, Poll
from telegram.constants import ParseMode
import google.generativeai as genai

# ==================== YAPILANDIRMA ====================

# API Anahtarları (ortam değişkenlerinden alınacak)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CHANNEL_ID = os.getenv("CHANNEL_ID")

# Gemini API'yi yapılandır
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

# ==================== KONU LİSTELERİ ====================

PYTHON_KONULAR = [
    "Python Näme we Näme üçin öwrenmeli?",
    "Ilkinji Python programmamyz we Print funksiýasy",
    "Üýtgeýänler we maglumat görnüşleri",
    "Matematiki amallar we operatorlar",
    "Setir (String) amallary",
    "Sanaw (List) maglumat gurluşy",
    "Şertli aňlatmalar (if-elif-else)",
    "Aýlanmalar: For aýlanmasy",
    "Aýlanmalar: While aýlanmasy",
    "Funksiýalar - Esasy düşünjeler",
    "Funksiýalar - Parametrler we gaýtaryş bahalary",
    "Sözlük (Dictionary) maglumat gurluşy",
    "Tuple we Set maglumat gurluşlary",
    "Faýl amallary - Okamak",
    "Faýl amallary - Ýazmak",
    "Ýalňyşlyk dolandyryşy (Try-Except)",
    "Modullar we Import",
    "Sanaw düşünjeleri (List Comprehension)",
    "Lambda funksiýalary",
    "Obýekt ugrukdyrlan programmirlemek - Synplar",
    "Obýekt ugrukdyrlan programmirlemek - Miras",
    "Kitaphanalar: requests bilen Web haýyşlary",
    "Kitaphanalar: datetime bilen Sene/Wagt",
    "JSON maglumatlary bilen işlemek",
    "API ulanylyşy we integrasiýa",
]

TEST_KONULAR = [
    "Python Esaslary",
    "Üýtgeýänler we Maglumat Görnüşleri",
    "Matematiki Amallar",
    "Setir Amallary",
    "Sanaw Amallary",
    "Şertli Aňlatmalar",
    "Aýlanmalar",
    "Funksiýalar",
    "Sözlükler",
    "Faýl Amallary",
]

# Güncel konu indeksleri
current_python_index = 0
current_test_index = 0

# ==================== YARDIMCI FONKSİYONLAR ====================

def get_next_python_topic():
    """Sıradaki Python konusunu döndürür"""
    global current_python_index
    topic = PYTHON_KONULAR[current_python_index % len(PYTHON_KONULAR)]
    bolum_no = (current_python_index % len(PYTHON_KONULAR)) + 1
    current_python_index += 1
    return topic, bolum_no

def get_next_test_topic():
    """Sıradaki test konusunu döndürür"""
    global current_test_index
    topic = TEST_KONULAR[current_test_index % len(TEST_KONULAR)]
    current_test_index += 1
    return topic

async def generate_content(prompt):
    """Gemini API ile içerik üretir"""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Gemini API hatası: {e}")
        return None

# ==================== İÇERİK OLUŞTURMA FONKSİYONLARI ====================

async def create_fun_fact():
    """09:00 - Günün Eğlenceli Bilgisi"""
    prompt = """
    Türkmence dilinde gysgaça we düşnükli bir gyzykly maglumat ýaz (5-10 setir).
    Tehnologiýa, ylym, taryh ýa-da gündelik durmuş bilen baglanyşykly gyzykly maglumat bolsun.
    Emoji ulan, ýöne köp bolmasyn (2-3 emoji ýeterlik).
    Ahyrynda temanyň laýyk 2-3 hashtag goş.

    Format:
    🌟 [Başlyk]

    [Mazmun]

    #hashtag1 #hashtag2
    """
    content = await generate_content(prompt)
    return content if content else "🌟 Bu gün ajaýyp gün! Gyzykly maglumatlar ýakyn wagtda... #GyzyklyMaglumat #Öwrenýärin"

async def create_python_lesson():
    """13:00 - Python Dersi"""
    topic, bolum_no = get_next_python_topic()
    prompt = f"""
    Türkmence dilinde "Python Noldan Öwrenýärin" seriýasy üçin ders ýaz.
    Tema: {topic}
    Bölüm Belgisi: {bolum_no}

    Format:
    📚 Python Noldan Öwrenýärin - Bölüm {bolum_no}
    🎯 Tema: {topic}

    [5-10 setir gysgaça, düşnükli we gyzykly düşündiriş]
    [Zerur bolsa gysgaça kod mysaly]

    💡 Maslahat: [1 setir peýdaly maslahat]

    #Python #Programmirlemek #Öwrenýärin

    Örän uzyn bolmasyn, düşnükli we gyzykly bolsun. Emoji ulan, ýöne köp bolmasyn.
    Kod mysallaryny ```python ``` bloklarynda ýaz.
    """
    content = await generate_content(prompt)
    return content if content else f"📚 Python Noldan Öwrenýärin - Bölüm {bolum_no}\n🎯 Tema: {topic}\n\nMazmun taýýarlanýar... #Python #Programmirlemek"

async def create_python_task():
    """13:30 - Python Mini Görev"""
    topic, _ = get_next_python_topic()
    current_python_index -= 1  # Aynı konuyu kullanmak için geri al

    prompt = f"""
    Türkmence dilinde "{topic}" temasyna laýyk mini Python meşgulyny ýaz.

    Format:
    💪 Şu Günüň Meşguly

    [Meşgulyň düşündirişi - 2-3 setir]

    ```python
    # Mysal kod ýa-da çözgüt ýol görkezijisi
    ```

    [Ruhlandyryjy gysgaça söz]

    #PythonMeşguly #Tejribe #Kodlaşdyrmak

    Gysgaça, düşnükli we ruhlandyryjy bolsun. Emoji ulan.
    """
    content = await generate_content(prompt)
    return content if content else f"💪 Şu Günüň Meşguly\n\n{topic} temasyny tejribe edeliň!\n\n#PythonMeşguly #Tejribe"

async def create_daily_tip():
    """19:00 - Günün Tüyosu"""
    prompt = """
    Türkmence dilinde programmirlemek, tehnologiýa ýa-da şahsy ösüş bilen baglanyşykly:
    - Günüň maslahaty
    - Mini taslama pikiri
    - Ruhlandyryjy hekaýa

    Şulardan birini saýla we ýaz (5-10 setir).
    Bilim beriji, ylham beriji we gysgaça bolsun.
    Emoji we hashtag ulan.

    Format:
    💡 [Başlyk]

    [Mazmun]

    #hashtag1 #hashtag2
    """
    content = await generate_content(prompt)
    return content if content else "💡 Günüň Maslahaty\n\nHer gün birneme öňe gidýäris! #Ruhlandyryş #Ösüş"

async def create_quiz():
    """21:00 - Günlük Test/Anket"""
    topic = get_next_test_topic()

    # Daha basit ve net prompt
    prompt = f"""
Türkmence dilinde "{topic}" barada test soragyny döret.

DÜZGÜNLER:
1. Sorag GYSGAJYK bolmaly (1 setir)
2. Kod mysallary BAR BOLSA, diňe düz tekst (markdown ýok, ``` ýok)
3. Her wariant 1 setirde bolmaly
4. 4 wariant bolmaly (A, B, C, D)
5. Dogry jogaby görkezmeli

FORMAT (ÜÝTGETME):
Sorag: [gysgajyk sorag]
A) [wariant 1]
B) [wariant 2]
C) [wariant 3]
D) [wariant 4]
Dogry: [A ýa-da B ýa-da C ýa-da D]

MYSAL 1:
Sorag: Python-da üýtgeýäni nädip yglan edýäris?
A) let x = 10
B) x = 10
C) var x = 10
D) int x = 10
Dogry: B

MYSAL 2:
Sorag: print() funksiýasy näme iş edýär?
A) Faýl açýar
B) Maglumat çap edýär
C) Hasaplaýar
D) Programmany ýapýar
Dogry: B

MYSAL 3:
Sorag: 5 + 3 * 2 netije näçe?
A) 16
B) 11
C) 13
D) 10
Dogry: B

Indi "{topic}" barada şuňa meňzeş test döret. ÝÖNEKEÝ WE GYSGAJYK!
"""

    content = await generate_content(prompt)

    if not content:
        return _get_fallback_quiz(topic)

    # Çok daha basit parse
    try:
        print(f"\n📋 Quiz mazmun:\n{content}\n")

        # Tüm satırları temizle
        lines = content.strip().split('\n')

        question = ""
        options = []
        correct = ""

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Soruyu bul
            if line.startswith("Sorag:"):
                question = line.replace("Sorag:", "").strip()

            # Seçenekleri bul (A), B), C), D) ile başlayanlar)
            elif re.match(r'^[A-D]\)', line):
                option = line[2:].strip()  # "A) " sonrasını al
                # Kod bloklarını temizle
                option = option.replace('```python', '').replace('```', '').strip()
                if option:
                    options.append(option)

            # Doğru cevabı bul
            elif line.startswith("Dogry"):
                # "Dogry:", "Dogry jogap:", vb hepsini yakala
                correct_part = line.split(':', 1)[-1].strip().upper()
                if correct_part and correct_part[0] in 'ABCD':
                    correct = correct_part[0]

        # Kontrol
        if not question or len(options) != 4 or not correct:
            raise ValueError(f"Parse edilmedi: sorag={bool(question)}, wariant={len(options)}, dogry={bool(correct)}")

        correct_index = ord(correct) - ord('A')

        print(f"✅ Parse başarılı:")
        print(f"   Sorag: {question[:50]}...")
        print(f"   Wariantlar: {len(options)}")
        print(f"   Dogry: {correct} (indeks: {correct_index})")

        return {
            "question": f"📝 {topic} Testi\n\n{question}",
            "options": options,
            "correct": correct_index
        }

    except Exception as e:
        print(f"❌ Parse hatasy: {e}")
        print(f"   Mazmun: {content[:300]}")
        return _get_fallback_quiz(topic)


def _get_fallback_quiz(topic):
    """Yedek test soruları"""
    fallback_quizzes = {
        "Python Esaslary": {
            "question": f"📝 {topic} Testi\n\nPython näme görnüşli programmirlemek dili?",
            "options": [
                "Kompilýasiýa edilen dil",
                "Interpretasiýa edilen dil",
                "Assemblý dili",
                "Maşyn dili"
            ],
            "correct": 1
        },
        "Üýtgeýänler we Maglumat Görnüşleri": {
            "question": f"📝 {topic} Testi\n\nHaýsy dürs Python-da üýtgeýän yglan edýär?",
            "options": [
                "let saýla = 10",
                "var saýla = 10",
                "saýla = 10",
                "int saýla = 10"
            ],
            "correct": 2
        },
        "Matematiki Amallar": {
            "question": f"📝 {topic} Testi\n\n10 % 3 amalynyň netijesi näçe?",
            "options": [
                "3",
                "1",
                "0",
                "3.33"
            ],
            "correct": 1
        },
        "Setir Amallary": {
            "question": f"📝 {topic} Testi\n\nHello Dünýä setiriniň uzynlygy näçe?",
            "options": [
                "11",
                "10",
                "12",
                "13"
            ],
            "correct": 0
        },
        "Sanaw Amallary": {
            "question": f"📝 {topic} Testi\n\nSanawa element goşmak üçin haýsy usul ulanylýar?",
            "options": [
                "add()",
                "append()",
                "insert()",
                "push()"
            ],
            "correct": 1
        },
    }

    # Eğer konuya özel yedek varsa onu kullan
    if topic in fallback_quizzes:
        return fallback_quizzes[topic]

    # Yoksa genel yedek
    return {
        "question": f"📝 {topic} Testi\n\nPython öwrenmek näme üçin möhüm?",
        "options": [
            "Ýönekeý we güýçli dil",
            "Diňe oýunlar üçin",
            "Köne tehnologiýa",
            "Diňe professionallar üçin"
        ],
        "correct": 0
    }

# ==================== GÖNDERİM FONKSİYONLARI ====================

async def send_post(bot, content):
    """Kanala post gönderir"""
    try:
        await bot.send_message(
            chat_id=CHANNEL_ID,
            text=content,
            parse_mode=ParseMode.MARKDOWN
        )
        print(f"✅ Post gönderildi: {datetime.now()}")
    except Exception as e:
        print(f"❌ Post gönderme hatası: {e}")

async def send_poll(bot, quiz_data):
    """Kanala anket gönderir"""
    try:
        await bot.send_poll(
            chat_id=CHANNEL_ID,
            question=quiz_data["question"],
            options=quiz_data["options"],
            type=Poll.QUIZ,
            correct_option_id=quiz_data["correct"],
            is_anonymous=True
        )
        print(f"✅ Anket gönderildi: {datetime.now()}")
    except Exception as e:
        print(f"❌ Anket gönderme hatası: {e}")

# ==================== ZAMANLAMA ====================

async def scheduled_post(bot, hour, minute, post_type):
    """Belirtilen saatte post gönderir"""
    while True:
        now = datetime.now()
        target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

        if now >= target:
            # Bugün için geçti, yarına planla
            from datetime import timedelta
            target = target + timedelta(days=1)

        wait_seconds = (target - now).total_seconds()
        print(f"⏰ {post_type} için bekleniyor: {wait_seconds/3600:.1f} saat")

        await asyncio.sleep(wait_seconds)

        # İçerik oluştur ve gönder
        if post_type == "fun_fact":
            content = await create_fun_fact()
            await send_post(bot, content)
        elif post_type == "python_lesson":
            content = await create_python_lesson()
            await send_post(bot, content)
        elif post_type == "python_task":
            content = await create_python_task()
            await send_post(bot, content)
        elif post_type == "daily_tip":
            content = await create_daily_tip()
            await send_post(bot, content)
        elif post_type == "quiz":
            quiz_data = await create_quiz()
            await send_poll(bot, quiz_data)

        # 24 saat bekle
        await asyncio.sleep(86400)

# ==================== ANA FONKSİYON ====================

async def main():
    """Ana bot fonksiyonu"""
    print("🤖 Telegram Kanal Botu başlatılıyor...")
    print(f"📢 Kanal: {CHANNEL_ID}")

    # Bot'u oluştur
    bot = Bot(token=TELEGRAM_BOT_TOKEN)

    # Bot bilgilerini kontrol et
    try:
        bot_info = await bot.get_me()
        print(f"✅ Bot bağlandı: @{bot_info.username}")
    except Exception as e:
        print(f"❌ Bot bağlantı hatası: {e}")
        return

    # Tüm zamanlanmış görevleri başlat
    tasks = [
        scheduled_post(bot, 18, 0, "fun_fact"),      # 09:00
        scheduled_post(bot, 22, 0, "python_lesson"), # 13:00
        scheduled_post(bot, 22, 30, "python_task"),  # 13:30
        scheduled_post(bot, 1, 0, "daily_tip"),     # 19:00
        scheduled_post(bot, 6, 0, "quiz"),          # 21:00
    ]

    print("✅ Tüm zamanlamalar aktif!")
    print("🚀 Bot çalışıyor... (Durdurmak için Ctrl+C)")

    # Tüm görevleri paralel çalıştır
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot durduruldu.")
    except Exception as e:
        print(f"❌ Beklenmeyen hata: {e}")
