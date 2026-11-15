
import json
import os
import re

from gigachat import GigaChat
from gigachat.models import Chat, Messages


def get_credentials():
    return os.getenv("GIGACHAT_CREDENTIALS", "").strip()


def is_ai_available():
    return bool(get_credentials())


def extract_json(text):
    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    return None


def analyze_project(project_text, credentials=None, author_genre=None):
    credentials = credentials or get_credentials()

    if not credentials:
        return {
            "status": "unavailable",
            "summary": "AI-анализ пока недоступен. Добавьте ключ GigaChat.",
            "genres": [],
            "genre_assessment": "",
            "genre_evidence": [],
            "genre_alternatives": [],
            "themes": [],
            "strengths": [],
            "risks": [],
            "audience": "",
            "recommendations": [],
        }

    selected_genre = author_genre or "Не указан"

    prompt = f"""
Ты — эксперт по кинопроизводству и развитию независимого кино.

Проанализируй описание кинопроекта. Не выдумывай факты,
которых нет в тексте. Отделяй наблюдения от предположений.

Автор самостоятельно выбрал жанр: "{selected_genre}".

Важно оценить выбранный жанр независимо:
- Не соглашайся с автором автоматически.
- Не подгоняй анализ под выбранный жанр.
- Не отвергай жанр только из-за отсутствия очевидных клише.
- Укажи конкретные элементы описания, подтверждающие
  или не подтверждающие выбранный жанр.
- Если информации недостаточно, прямо скажи об этом.
- Дополнительные жанры указывай отдельно.
- Близкие жанры не считай автоматически противоречием.

Верни результат строго в формате JSON:
{{
    "summary": "Краткое описание проекта",
    "genres": ["Жанры, которые AI считает подходящими"],
    "genre_assessment": "Оценка выбранного автором жанра: подтверждается, частично подтверждается, не подтверждается или недостаточно данных. Объясни почему",
    "genre_evidence": ["Конкретные элементы описания, которые подтверждают или не подтверждают жанр"],
    "genre_alternatives": ["Дополнительные жанровые трактовки и объяснение"],
    "themes": ["Основные темы"],
    "strengths": ["Сильные стороны проекта"],
    "risks": ["Возможные проблемы и риски"],
    "audience": "Предполагаемая аудитория",
    "recommendations": ["Рекомендации по развитию проекта"]
}}

Выбранный автором жанр: {selected_genre}

Описание проекта:
{project_text}
"""

    try:
        with GigaChat(
            credentials=credentials,
            model="GigaChat-2",
            scope="GIGACHAT_API_PERS",
            verify_ssl_certs=False,
            timeout=60,
        ) as giga:
            response = giga.chat(
                Chat(
                    model="GigaChat-2",
                    messages=[
                        Messages(
                            role="user",
                            content=prompt,
                        )
                    ],
                    temperature=0.2,
                )
            )

        content = response.choices[0].message.content
        result = extract_json(content)

        if not isinstance(result, dict):
            raise ValueError("Не удалось прочитать ответ AI")

        required_fields = [
            "summary",
            "genres",
            "genre_assessment",
            "genre_evidence",
            "genre_alternatives",
            "themes",
            "strengths",
            "risks",
            "audience",
            "recommendations",
        ]

        for field in required_fields:
            default = [] if field in [
                "genres",
                "genre_evidence",
                "genre_alternatives",
                "themes",
                "strengths",
                "risks",
                "recommendations",
            ] else ""
            result.setdefault(field, default)

        result["status"] = "success"
        return result

    except Exception as error:
        return {
            "status": "error",
            "summary": "Не удалось выполнить AI-анализ.",
            "genres": [],
            "genre_assessment": "",
            "genre_evidence": [],
            "genre_alternatives": [],
            "themes": [],
            "strengths": [],
            "risks": [],
            "audience": "",
            "recommendations": [],
            "error": str(error),
        }
