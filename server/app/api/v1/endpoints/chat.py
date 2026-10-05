import os
import json
import logging
from typing import Optional, List, Dict, Any

try:
    from pydantic import BaseModel
except ImportError:
    class BaseModel:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

try:
    from fastapi import APIRouter, Depends, HTTPException
except ImportError:
    class APIRouter:
        def post(self, *args, **kwargs):
            return lambda fn: fn
    def Depends(fn):
        return None
    class HTTPException(Exception):
        def __init__(self, status_code, detail):
            self.status_code = status_code
            self.detail = detail

try:
    from app.models.models import User
except Exception:
    User = None

try:
    from app.core.deps import get_current_user_optional
except Exception:
    get_current_user_optional = None

router = APIRouter()
logger = logging.getLogger(__name__)


class ChatAskRequest(BaseModel):
    question: str
    name: Optional[str] = None
    sun_sign: Optional[str] = None
    moon_sign: Optional[str] = None
    asc_sign: Optional[str] = None
    birth_date: Optional[str] = None
    context: Optional[str] = None


class ChatAskResponse(BaseModel):
    answer: str
    source: str  # 'llm' or 'astrology_engine'


def generate_astrological_fallback(req: ChatAskRequest) -> str:
    name = req.name or "душа"
    sun = req.sun_sign or "Козерог"
    moon = req.moon_sign or "Козерог"
    asc = req.asc_sign or "Стрелец"
    q_raw = req.question.strip()
    q_lower = q_raw.lower()

    # Clean punctuation for exact greeting/gratitude matching
    clean_q = "".join(c for c in q_lower if c.isalnum() or c.isspace()).strip()
    words = clean_q.split()

    # 1. GREETINGS (привет, здравствуйте, добрый день, etc.)
    greeting_words = {"привет", "приветик", "здравствуй", "здравствуйте", "хай", "салют", "ку", "йоу", "хеллоу", "добрый", "утро", "вечер", "hello", "hi", "hey"}
    is_greeting = False
    if clean_q in ["привет", "здравствуй", "здравствуйте", "добрый день", "доброе утро", "добрый вечер", "хай", "салют", "ку", "йоу", "hello", "hi", "доброго времени"]:
        is_greeting = True
    elif len(words) <= 3 and any(w in greeting_words for w in words) and not any(w in q_lower for w in ["почему", "когда", "деньги", "отношения", "работа", "муж"]):
        is_greeting = True

    if is_greeting:
        return (
            f"✨ <b>Здравствуй, {name}!</b> Рада нашей встрече.<br><br>"
            f"Я — <b>LUNA</b>, твой персональный астролог и проводник по натальной карте (☀️ <b>{sun}</b> • 🌙 <b>{moon}</b> • ↑ <b>{asc}</b>).<br><br>"
            f"О чем бы тебе хотелось узнать сегодня?<br>"
            f"• 💖 <b>Отношения и любовь:</b> совместимость, гармония, выбор партнера<br>"
            f"• 💎 <b>Деньги и карьера:</b> финансовый код, проявленность, точки роста<br>"
            f"• 🔄 <b>Повторяющиеся сценарии:</b> как разомкнуть привычный круг<br>"
            f"• 🌿 <b>Энергия и баланс:</b> персональные ключи к ресурсному состоянию<br><br>"
            f"<i>Задай любой вопрос простыми словами, и мы разберем его с опорой на твою карту!</i>"
        )

    # 2. SMALL TALK (как дела, что делаешь, как ты)
    if any(phrase in q_lower for phrase in ["как дела", "как ты", "что делаешь", "чем занята", "как настроение", "как поживаешь", "how are you"]):
        return (
            f"✨ <b>Спасибо, {name}, всё спокойно и гармонично!</b><br><br>"
            f"Я сейчас настраиваюсь на планетарные ритмы твоего гороскопа (☀️ <b>{sun}</b> • 🌙 <b>{moon}</b> • ↑ <b>{asc}</b>). "
            f"Готова помочь тебе прояснить любую волнующую тему — в отношениях, финансах, карьере или внутреннем состоянии.<br><br>"
            f"Как ты себя чувствуешь сегодня? О чем хочется поговорить?"
        )

    # 3. EMOTIONAL STATE & EMPATHY (мне грустно, устала, тревожно, нет сил)
    if any(w in q_lower for w in ["мне грустно", "мне плохо", "я устала", "усталость", "нет сил", "тревожно", "плачу", "одиноко", "тоска", "апатия", "выгораю"]):
        return (
            f"🤍 <b>{name}, я рядом и очень тебя понимаю.</b><br><br>"
            f"С Луной в знаке <b>{moon}</b> твоя эмоциональная система очень тонко чувствует любые перегрузки и внешнее давление. "
            f"Когда накапливается усталость, психика просит не новых подвигов, а бережного замедления и тишины.<br><br>"
            f"🌿 <b>Что сделать прямо сейчас:</b><br>"
            f"1. <i>Сними с себя обязанность быть идеальной:</i> разреши себе сегодня просто отдохнуть.<br>"
            f"2. <i>Заземление тела:</i> теплый травяной чай, мягкий плед и теплая вода помогут снять напряжение.<br>"
            f"3. <i>Не принимай решений в упадке сил:</i> твой ясный фокус вернется, как только отдохнет Луна.<br><br>"
            f"<i>Если хочешь посмотреть на ситуацию через карту глубже — напиши, что именно вызвало это состояние.</i>"
        )

    # 4. GRATITUDE (спасибо, благодарю, etc.)
    gratitude_words = {"спасибо", "благодарю", "от души", "спасибки", "сяп", "пасиб", "спасибочки", "благодарность", "thanks", "thank you"}
    if clean_q in gratitude_words or (len(words) <= 3 and any(w in gratitude_words for w in words)):
        return (
            f"✨ <b>Во благо, {name}!</b><br><br>"
            f"Пусть подсказки твоей натальной карты служат тебе надежным компасом и опорой. "
            f"Если захочешь разобрать еще какой-то вопрос или посмотреть другие сферы — я всегда рядом. О чем бы тебе хотелось спросить?"
        )

    # 5. IDENTITY & CAPABILITIES (кто ты, что ты умеешь, помощь, etc.)
    if any(w in q_lower for w in ["кто ты", "что ты умеешь", "что ты можешь", "как пользоваться", "помощь", "справка", "о чем спросить", "расскажи о себе"]):
        return (
            f"🌙 <b>Я — LUNA</b>, твой чуткий персональный AI-астролог.<br><br>"
            f"Я синтезирую планетарные координаты твоего рождения (☀️ <b>{sun}</b>, 🌙 <b>{moon}</b>, ↑ <b>{asc}</b>) и помогаю находить ответы на глубокие вопросы:<br>"
            f"• <b>Любовь & Отношения:</b> истинные потребности в близости и сценарии выбора<br>"
            f"• <b>Деньги & Бизнес:</b> раскрытие потенциала и финансовая уверенность<br>"
            f"• <b>Предназначение:</b> твоя суперсила и авторская реализация<br>"
            f"• <b>Ресурс:</b> персональные способы отдыха и снятия тревоги<br><br>"
            f"<i>Напиши свой вопрос к карте в поле ввода ниже 👇</i>"
        )

    # 6. RECURRING PATTERNS & SCENARIOS
    if any(w in q_lower for w in ["сценар", "повторя", "по кругу", "грабли", "тупик", "ошибк", "почему я", "блоки", "страх"]):
        return (
            f"<b>{name}</b>, разбор повторяющегося сценария по твоей карте:<br><br>"
            f"<b>1. Что происходит по карте:</b><br>"
            f"В твоей натальной карте ключевой механизм зацикливания связан с взаимодействием <b>Солнца в {sun}</b> и <b>Луны в {moon}</b>.<br><br>"
            f"<b>2. На что обратить внимание:</b><br>"
            f"Подсознательно ты привыкла удерживать контроль и брать избыточную ответственность. Это притягивает ситуации, где приходится доказывать свою ценность.<br><br>"
            f"💡 <b>Что делать / Практический совет:</b><br>"
            f"1. <i>Заметить импульс спасателя:</i> когда хочется взвалить всё на себя — сделай паузу на 24 часа.<br>"
            f"2. <i>Разделяй ответственность:</i> позволь другим людям нести их долю последствий.<br>"
            f"3. <i>Опора на достоинство:</i> твоя сила раскрывается через спокойствие и внутренние границы, а не через постоянную борьбу."
        )

    # 7. RELATIONSHIPS & LOVE
    if any(w in q_lower for w in ["отношен", "любов", "мужчин", "брак", "партнер", "чувств", "парен", "девушк", "одинок", "развод", "расстава", "ревность"]):
        return (
            f"<b>{name}</b>, анализирую сферу чувств через твою карту:<br><br>"
            f"<b>1. Что происходит по карте:</b><br>"
            f"При <b>Солнце в знаке {sun}</b> и <b>Луне в {moon}</b> для тебя в отношениях ключевой ценностью является эмоциональная безопасность, глубинная честность и взаимное уважение.<br><br>"
            f"<b>2. На что обратить внимание:</b><br>"
            f"Твой Асцендент в <b>{asc}</b> создает образ сильной, самодостаточной личности, но внутри есть потребность в мягкости и бережном принятии.<br><br>"
            f"💡 <b>Что делать / Практический совет:</b><br>"
            f"1. <i>Проговаривай потребности прямо:</i> формулируй через «Мне важно почувствовать твою поддержку», без накопления обид.<br>"
            f"2. <i>Дай партнеру проявиться:</i> не пытайся контролировать каждый шаг отношений.<br>"
            f"3. <i>Выдели время для двоих:</i> совместные паузы вне бытовой рутины возвращают тепло."
        )

    # 8. MONEY & FINANCES
    if any(w in q_lower for w in ["деньг", "доход", "финанс", "заработ", "богат", "чек", "кредит", "долг", "потолок", "стоимост"]):
        return (
            f"<b>{name}</b>, разбираем финансовый код твоей натальной карты:<br><br>"
            f"<b>1. Что происходит по карте:</b><br>"
            f"Твой ресурсный сектор под влиянием <b>Солнца в {sun}</b> дает максимальный доход, когда ты создаешь авторский, качественный продукт и ценишь свое мастерство.<br><br>"
            f"<b>2. На что обратить внимание:</b><br>"
            f"С <b>Асцендентом в {asc}</b> высокий чек и признание приходят, когда ты продаешь ценность и трансформацию, а не соглашаешься на демпинг из страха дефицита.<br><br>"
            f"💡 <b>Что делать / Практический совет:</b><br>"
            f"1. <i>Зафиксируй минимальный чек:</i> не бери заказы ниже комфортной планки.<br>"
            f"2. <i>Упаковывай опыт:</i> переходи от разрозненных задач к комплексным решениям.<br>"
            f"3. <i>Резерв спокойствия:</i> откладывай 10% в подушку безопасности для снятия тревоги Луны."
        )

    # 9. CAREER & PURPOSE & WORK
    if any(w in q_lower for w in ["работ", "карьер", "призван", "бизнес", "найм", "проект", "професси", "свое дело", "реализац"]):
        return (
            f"<b>{name}</b>, профессиональный вектор твоей карты:<br><br>"
            f"<b>1. Что происходит по карте:</b><br>"
            f"С <b>Асцендентом в {asc}</b> и <b>Солнцем в {sun}</b> тебе жизненно необходима творческая или управленческая автономия. В роли простого исполнителя без права голоса твой потенциал быстро угасает.<br><br>"
            f"<b>2. На что обратить внимание:</b><br>"
            f"Опасность закопаться в механической рутине вместо развития личного бренда.<br><br>"
            f"💡 <b>Что делать / Практический совет:</b><br>"
            f"1. <i>Делегируй рутину:</i> освободи минимум 30% времени на стратегию.<br>"
            f"2. <i>Заявляй об опыте:</i> делись своими кейсами и авторской методологией.<br>"
            f"3. <i>Фокус на 1 проекте:</i> доведи ключевой замысел до твердого результата."
        )

    # 10. ENERGY & REST & BURNOUT
    if any(w in q_lower for w in ["энерг", "устал", "выгоран", "сил нет", "сон", "ресурс", "тревог", "тело", "отдых", "апати"]):
        return (
            f"<b>{name}</b>, энергетический баланс твоей натальной карты:<br><br>"
            f"<b>1. Что происходит по карте:</b><br>"
            f"Запас твоих жизненных сил регулируется <b>Луной в знаке {moon}</b>. Твоя нервная система требует качественного заземления и регулярных пауз в тишине.<br><br>"
            f"<b>2. На что обратить внимание:</b><br>"
            f"Не кори себя за необходимость восстановиться. Отдых — это фундамент твоей натальной силы.<br><br>"
            f"💡 <b>Что делать / Практический совет:</b><br>"
            f"1. <i>Цифровой детокс:</i> отключи уведомления за 1 час до сна.<br>"
            f"2. <i>Телесный ритуал:</i> ванна с солью, травяной чай и свежий воздух.<br>"
            f"3. <i>Личное пространство:</i> 1 час в день только для себя без домашних задач."
        )

    # 11. GENERAL NATAL SYNTHESIS
    return (
        f"<b>{name}</b>, смотрю на твой вопрос через призму натальной карты (☀️ <b>{sun}</b> • 🌙 <b>{moon}</b> • ↑ <b>{asc}</b>):<br><br>"
        f"<b>1. Что происходит по карте:</b><br>"
        f"В этой теме карта советует опираться на зрелую устойчивость Солнца в знаке {sun} и внутреннюю интуицию Луны в {moon}.<br><br>"
        f"<b>2. На что обратить внимание:</b><br>"
        f"Асцендент в <b>{asc}</b> помогает находить нестандартные решения и видеть ситуацию целиком. Не поддавайся спешке и сомнениям.<br><br>"
        f"💡 <b>Что делать / Практический совет:</b><br>"
        f"1. <i>Доверяй первому спокойному решению:</i> там, где чувствуется достоинство.<br>"
        f"2. <i>Разбей задачу на шаги:</i> начни с 1 понятного действия на сегодня.<br>"
        f"3. <i>Держи свой центр:</i> не позволяй чужой суете сбивать твой ориентир.<br><br>"
        f"<i>Если хочешь углубиться в детали — уточни свой вопрос в чате!</i>"
    )


@router.post("/ask", response_model=ChatAskResponse)
def ask_ai_astrologer(
    req: ChatAskRequest,
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    AI Astrologer chat completion endpoint.
    Uses LLM API if key is available in environment, otherwise returns deep astrological synthesis.
    """
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Вопрос не может быть пустым.")

    # Populate from current_user if authenticated and fields missing
    if current_user:
        if not req.name and current_user.name:
            req.name = current_user.name
        if not req.sun_sign and current_user.sun_sign:
            req.sun_sign = current_user.sun_sign
        if not req.moon_sign and current_user.moon_sign:
            req.moon_sign = current_user.moon_sign
        if not req.asc_sign and current_user.asc_sign:
            req.asc_sign = current_user.asc_sign

    # Check for OpenAI or Gemini key in environment
    openai_key = os.getenv("OPENAI_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")

    system_prompt = (
        f"Ты — LUNA, чуткий, бережный и глубокий персональный астролог и психолог. "
        f"Данные пользователя: Имя: {req.name or 'Гость'}, Солнце: {req.sun_sign or 'не указано'}, "
        f"Луна: {req.moon_sign or 'не указано'}, Асцендент: {req.asc_sign or 'не указано'}. "
        f"ПРАВИЛА ОБЩЕНИЯ:\n"
        f"1. Если пользователь просто здоровается (например: «привет», «здравствуй», «добрый день»), поприветствуй его тепло по имени, напомни, что ты LUNA и поможешь разобрать любые вопросы по карте (любовь, деньги, карьера, сценарии, энергия), и спроси, о чем ему хочется узнать. НЕ делай разбор слова «привет».\n"
        f"2. Если пользователь благодарит — ответь тепло и доброжелательно.\n"
        f"3. На вопросы по отношениям, деньгам, призванию, ситуациям — отвечай глубоко, психологично, с опорой на его натальные координаты, без фатализма и клише.\n"
        f"4. ОБЯЗАТЕЛЬНАЯ СТРУКТУРА ОТВЕТА: каждый содержательный ответ строй по цепочке: «Что происходит по карте» -> «На что обратить внимание» -> «💡 Что делать / Практический совет» (1–3 конкретных шага, что человеку делать прямо сейчас).\n"
        f"5. Используй HTML теги <b>, <i>, <br> для красивого и структурированного оформления."
    )

    if openai_key:
        try:
            import urllib.request
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": req.question}
                ],
                "temperature": 0.7,
                "max_tokens": 600
            }
            req_post = urllib.request.Request(
                "https://api.openai.com/v1/chat/completions",
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {openai_key}",
                    "Content-Type": "application/json"
                }
            )
            with urllib.request.urlopen(req_post, timeout=12) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                ans = data["choices"][0]["message"]["content"]
                return ChatAskResponse(answer=ans, source="llm")
        except Exception as e:
            logger.warning("OpenAI API call failed, trying next provider or fallback: %s", e)

    if gemini_key:
        try:
            import urllib.request
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
            gemini_payload = {
                "system_instruction": {
                    "parts": [{"text": system_prompt}]
                },
                "contents": [
                    {
                        "role": "user",
                        "parts": [{"text": req.question}]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 600
                }
            }
            req_post = urllib.request.Request(
                url,
                data=json.dumps(gemini_payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req_post, timeout=12) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts and "text" in parts[0]:
                        return ChatAskResponse(answer=parts[0]["text"], source="llm")
        except Exception as e:
            logger.warning("Gemini API call failed, using fallback engine: %s", e)

    # Fallback to rich astrological engine
    fallback_text = generate_astrological_fallback(req)
    return ChatAskResponse(answer=fallback_text, source="astrology_engine")
