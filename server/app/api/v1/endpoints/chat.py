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
    q_lower = req.question.lower()

    if any(w in q_lower for w in ["отношен", "любов", "мужчин", "брак", "партнер", "чувств"]):
        return (
            f"<b>{name}</b>, анализирую сферу чувств через твою карту:<br><br>"
            f"При <b>Солнце в знаке {sun}</b> и <b>Луне в {moon}</b> для тебя в отношениях ключевой ценностью является эмоциональная безопасность, предсказуемость и глубинная честность.<br><br>"
            f"✨ <b>Астрологический фокус:</b> Твой Асцендент в <b>{asc}</b> притягивает ярких личностей, но длительная близость строится на синхронизации ценностей. "
            f"Дай партнеру возможность проявлять заботу в его темпе, не пытаясь держать все процессы под полным контролем."
        )

    if any(w in q_lower for w in ["деньг", "доход", "финанс", "заработ", "богат", "чек"]):
        return (
            f"<b>{name}</b>, разбираем финансовый код твоей натальной карты:<br><br>"
            f"Твой ресурсный дом под управлением <b>Солнца в {sun}</b> дает максимальный доход, когда ты создаешь авторский, качественный продукт и не соглашаешься на демпинг из страха дефицита.<br><br>"
            f"💎 <b>Точка роста:</b> Высокий чек и признание приходят, когда ты продаешь результат и ценность, а не просто затраченные часы."
        )

    if any(w in q_lower for w in ["работ", "карьер", "призван", "бизнес", "найм", "проект"]):
        return (
            f"<b>{name}</b>, профессиональный вектор твоей карты:<br><br>"
            f"С <b>Асцендентом в {asc}</b> и <b>Солнцем в {sun}</b> тебе жизненно необходима творческая или управленческая автономия. В роли простого исполнителя без права голоса твой потенциал гаснет.<br><br>"
            f"🧭 <b>Рекомендация:</b> Развивай личный бренд и авторскую методологию — это твоя главная точка опоры."
        )

    return (
        f"<b>{name}</b>, разбираем твой вопрос: <i>«{req.question}»</i>.<br><br>"
        f"С позиции синтеза <b>Солнца в {sun}</b>, <b>Луны в {moon}</b> и <b>Асцендента в {asc}</b>, "
        f"твоя сила кроется в умении сохранять внутренний стержень и действовать из состояния спокойной уверенности.<br><br>"
        f"🌌 <i>Совет карты:</i> Не торопи события и опирайся на свои истинные ценности, а не на сиюминутные тревоги."
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

    if openai_key:
        try:
            import urllib.request
            system_prompt = (
                f"Ты — LUNA, чуткий, бережный и глубокий персональный астролог и психолог. "
                f"Данные пользователя: Имя: {req.name or 'Гость'}, Солнце: {req.sun_sign or 'не указано'}, "
                f"Луна: {req.moon_sign or 'не указано'}, Асцендент: {req.asc_sign or 'не указано'}. "
                f"Отвечай тепло, психологично, без категоричности, фатализма и клише. Используй HTML теги <b>, <i>, <br> для оформления."
            )
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
            with urllib.request.urlopen(req_post, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                ans = data["choices"][0]["message"]["content"]
                return ChatAskResponse(answer=ans, source="llm")
        except Exception as e:
            logger.warning("LLM API call failed, using fallback engine: %s", e)

    # Fallback to rich astrological engine
    fallback_text = generate_astrological_fallback(req)
    return ChatAskResponse(answer=fallback_text, source="astrology_engine")
