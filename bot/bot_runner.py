#!/usr/bin/env python3
"""
LUNA Astrologer — Standalone Telegram Bot Long-Polling Runner
Zero third-party dependencies (uses Python standard library).
"""

import os
import sys
import json
import time
import socket
import urllib.request
import urllib.error

# Force IPv4
orig_getaddrinfo = socket.getaddrinfo
def getaddrinfo_v4(host, port, family=0, type=0, proto=0, flags=0):
    return orig_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
socket.getaddrinfo = getaddrinfo_v4

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "7968512345:AAExampleTokenPlaceholderForLocalDev")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://nadinnchik.github.io/luna-app/")


def telegram_api(method: str, data: dict = None) -> dict:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    headers = {"Content-Type": "application/json"}
    body = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=body, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def send_welcome_message(chat_id: int, user_first_name: str = "Гость"):
    welcome_text = (
        f"✨ <b>Здравствуй, {user_first_name}!</b>\n\n"
        f"Я <b>LUNA</b> — твой персональный проводник в мир натальной астрологии и психологического самопознания.\n\n"
        f"🌙 <b>Что ждет тебя внутри Mini App:</b>\n"
        f"• ☀️ <b>Большая Тройка:</b> Солнце, Луна и Асцендент\n"
        f"• 🔮 <b>AI-Астролог:</b> Чат с картой на любые темы\n"
        f"• 🪐 <b>Лунный календарь</b> и персональная энергия дня\n"
        f"• 📚 <b>7 PRO-разборов:</b> Любовь, Деньги, Карьера, Дети, Соляр\n\n"
        f"Нажми кнопку ниже, чтобы открыть приложение 👇"
    )

    reply_markup = {
        "inline_keyboard": [
            [
                {
                    "text": "🌙 Открыть LUNA Mini App",
                    "web_app": {"url": WEBAPP_URL}
                }
            ],
            [
                {
                    "text": "✨ Рассчитать мою карту",
                    "web_app": {"url": WEBAPP_URL}
                }
            ]
        ]
    }

    telegram_api("sendMessage", {
        "chat_id": chat_id,
        "text": welcome_text,
        "parse_mode": "HTML",
        "reply_markup": reply_markup
    })


def send_chat_answer(chat_id: int, question: str, user_first_name: str = "Гость"):
    ans = generate_bot_response(question, user_first_name)
    reply_markup = {
        "inline_keyboard": [
            [
                {
                    "text": "🌙 Открыть LUNA Mini App",
                    "web_app": {"url": WEBAPP_URL}
                }
            ]
        ]
    }
    telegram_api("sendMessage", {
        "chat_id": chat_id,
        "text": ans,
        "parse_mode": "HTML",
        "reply_markup": reply_markup
    })
    name = user_first_name or "душа"
    q_raw = question.strip()
    q_lower = q_raw.lower()
    clean_q = "".join(c for c in q_lower if c.isalnum() or c.isspace()).strip()
    words = clean_q.split()

    # 1. GREETINGS
    greeting_words = {"привет", "приветик", "здравствуй", "здравствуйте", "хай", "салют", "ку", "йоу", "hello", "hi", "hey"}
    is_greeting = False
    if clean_q in ["привет", "здравствуй", "здравствуйте", "добрый день", "доброе утро", "добрый вечер", "хай", "салют", "ку", "йоу", "hello", "hi", "доброго времени"]:
        is_greeting = True
    elif len(words) <= 3 and any(w in greeting_words for w in words):
        is_greeting = True

    if is_greeting:
        return (
            f"✨ <b>Здравствуй, {name}!</b> Рада встрече.\n\n"
            f"Я <b>LUNA</b> — твой персональный астролог и проводник по натальной карте.\n\n"
            f"О чем бы тебе хотелось узнать прямо сейчас?\n"
            f"• 💖 <b>Отношения:</b> совместимость, гармония, повторяющиеся сценарии\n"
            f"• 💎 <b>Деньги и работа:</b> финансовый код, проявленность, выбор дела\n"
            f"• 🪐 <b>Твоя карта:</b> Большая Тройка, таланты и точки роста\n"
            f"• 🌿 <b>Энергия:</b> как восстановить ресурс и выйти из напряжения\n\n"
            f"Напиши свой вопрос или открой приложение кнопкой ниже 👇"
        )

    # 2. GRATITUDE
    gratitude_words = {"спасибо", "благодарю", "от души", "спасибки", "сяп", "пасиб", "спасибочки", "ты супер", "thanks", "thank you"}
    if clean_q in gratitude_words or (len(words) <= 3 and any(w in gratitude_words for w in words)):
        return (
            f"✨ <b>Во благо, {name}!</b>\n\n"
            f"Пусть подсказки натальной карты служат тебе надежной опорой и компасом. "
            f"Если возникнет новый вопрос по отношениям, карьере или самочувствию — я всегда рядом. О чем еще хотелось бы узнать?"
        )

    # 3. LLM API (OpenAI / Gemini)
    openai_key = os.getenv("OPENAI_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")
    sys_prompt = (
        f"Ты — LUNA, чуткий, бережный и глубокий персональный астролог и психолог. "
        f"Имя пользователя: {name}. "
        f"Отвечай тепло, психологично, без фатализма и клише, опираясь на астрологический синтез. "
        f"Используй HTML теги <b>, <i> для форматирования. Текст до 150 слов."
    )

    if openai_key:
        try:
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": question}
                ],
                "temperature": 0.7,
                "max_tokens": 500
            }
            req_post = urllib.request.Request(
                "https://api.openai.com/v1/chat/completions",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Authorization": f"Bearer {openai_key}", "Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req_post, timeout=12) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"OpenAI error in bot: {e}")

    if gemini_key:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
            gemini_payload = {
                "system_instruction": {"parts": [{"text": sys_prompt}]},
                "contents": [{"role": "user", "parts": [{"text": question}]}],
                "generationConfig": {"temperature": 0.7, "maxOutputTokens": 500}
            }
            req_post = urllib.request.Request(url, data=json.dumps(gemini_payload).encode("utf-8"), headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req_post, timeout=12) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
                if parts and "text" in parts[0]:
                    return parts[0]["text"]
        except Exception as e:
            print(f"Gemini error in bot: {e}")

    # 4. ASTROLOGICAL RULE-BASED SYNTHESIS
    if any(w in q_lower for w in ["отношен", "любов", "мужчин", "брак", "партнер", "чувств", "парен", "девушк", "одинок", "развод", "расстава"]):
        return (
            f"<b>{name}</b>, анализирую сферу чувств через твою натальную карту:\n\n"
            f"В отношениях твоей ключевой потребностью является эмоциональная безопасность, глубинная честность и взаимное принятие.\n\n"
            f"✨ <b>Астрологический фокус:</b> Не пытайся решать эмоциональное напряжение через гиперконтроль. "
            f"Проговори свои истинные чувства через мягкое «мне важна твоя поддержка», давая партнеру проявить заботу в его темпе.\n\n"
            f"<i>Подробный анализ совместимости и языка любви доступен внутри приложения 👇</i>"
        )

    if any(w in q_lower for w in ["деньг", "доход", "финанс", "заработ", "богат", "чек", "кредит", "долг", "потолок", "стоимост"]):
        return (
            f"<b>{name}</b>, разбираем финансовый код твоей натальной карты:\n\n"
            f"Твой денежный потенциал раскрывается на максимум, когда ты создаешь авторский, качественный продукт и не соглашаешься на демпинг из страха дефицита.\n\n"
            f"💎 <b>Точка роста:</b> Высокий чек и признание приходят, когда ты продаешь ценность и трансформацию, а не просто затраченные часы.\n\n"
            f"<i>Полный аудит твоих денежных каналов ждет тебя в приложении 👇</i>"
        )

    if any(w in q_lower for w in ["работ", "карьер", "призван", "бизнес", "найм", "проект", "професси", "свое дело", "реализац"]):
        return (
            f"<b>{name}</b>, профессиональный вектор твоей карты:\n\n"
            f"Тебе жизненно необходима автономия в решениях и возможность создавать смыслы. В жестких рамках механического найма без права голоса твой потенциал быстро угасает.\n\n"
            f"🧭 <b>Рекомендация:</b> Развивай личный бренд, экспертный авторитет и авторскую методологию.\n\n"
            f"<i>Подробный разбор карьеры и предназначения открой в приложении 👇</i>"
        )

    if any(w in q_lower for w in ["энерг", "устал", "выгоран", "сил нет", "сон", "ресурс", "тревог", "тело", "отдых", "апати"]):
        return (
            f"<b>{name}</b>, энергетический баланс твоей натальной карты:\n\n"
            f"Твоя нервная система требует качественного заземления и регулярных пауз в тишине. Периоды отдачи должны сменяться фазами полного покоя.\n\n"
            f"🌿 <b>Совет от Луны:</b> Отдых — это не награда за подвиг, а базовое условие твоей продуктивности.\n\n"
            f"<i>Смотри персональную энергию дня и календарь в приложении 👇</i>"
        )

    if any(w in q_lower for w in ["сценар", "повторя", "по кругу", "грабли", "тупик", "ошибк", "почему я", "блоки", "страх"]):
        return (
            f"<b>{name}</b>, разбор повторяющегося сценария по твоей карте:\n\n"
            f"Подсознательно может включаться привычка чувствовать безопасность через гиперконтроль («если не я, всё разрушится»). Это создает замкнутый круг спасательства.\n\n"
            f"⚡ <b>Как разомкнуть круг:</b> В момент, когда хочется взвалить всё на себя — сделай паузу и дай пространству проявиться. Твой масштаб — в спокойной уверенности."
        )

    # General fallback
    return (
        f"<b>{name}</b>, смотрю на твой вопрос через призму твоей натальной карты:\n\n"
        f"В этой теме карта советует опираться на зрелую силу духа и глубокую внутреннюю интуицию. "
        f"Не торопи события из состояния спешки или тревоги — первое спокойное решение, идущее из чувства достоинства, будет самым точным.\n\n"
        f"<i>Чтобы рассчитать точные координаты карты и задать персонализированный вопрос — открой Mini App 👇</i>"
    )


def poll_updates():
    print("🌙 Starting LUNA Astrologer Telegram Bot...")
    print(f"🔗 Connected WebApp: {WEBAPP_URL}")

    # Set Menu Button
    try:
        telegram_api("setChatMenuButton", {
            "menu_button": {
                "type": "web_app",
                "text": "🌙 Открыть LUNA",
                "web_app": {"url": WEBAPP_URL}
            }
        })
        print("✅ WebApp Menu Button configured.")
    except Exception as e:
        print(f"⚠️ Could not set menu button: {e}")

    offset = 0
    while True:
        try:
            updates = telegram_api("getUpdates", {
                "offset": offset,
                "timeout": 20,
                "allowed_updates": ["message", "callback_query"]
            })

            if updates.get("ok"):
                for u in updates.get("result", []):
                    offset = u["update_id"] + 1
                    msg = u.get("message")
                    if not msg:
                        continue

                    chat_id = msg["chat"]["id"]
                    text = msg.get("text", "")
                    user_fn = msg.get("from", {}).get("first_name", "друг")

                    if text.startswith("/start") or text.startswith("/app") or text.startswith("/natal"):
                        send_welcome_message(chat_id, user_fn)
                    elif text.startswith("/help"):
                        help_text = (
                            "🌙 <b>LUNA Astrologer Help</b>\n\n"
                            "Чтобы открыть приложение и рассчитать натальную карту, нажмите кнопку <b>«🌙 Открыть LUNA»</b> в левом нижнем углу меню или воспользуйтесь кнопкой под приветствием.\n\n"
                            "Вы также можете задать любой вопрос прямо здесь в чате!"
                        )
                        telegram_api("sendMessage", {
                            "chat_id": chat_id,
                            "text": help_text,
                            "parse_mode": "HTML"
                        })
                    else:
                        send_chat_answer(chat_id, text, user_fn)

        except KeyboardInterrupt:
            print("\n🛑 Bot stopped.")
            break
        except Exception as e:
            time.sleep(2)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        BOT_TOKEN = sys.argv[1]

    if "Placeholder" in BOT_TOKEN:
        print("ℹ️ Set TELEGRAM_BOT_TOKEN environment variable or pass token as argument:")
        print("   python3 bot_runner.py <YOUR_BOT_TOKEN>")
        sys.exit(1)

    poll_updates()
