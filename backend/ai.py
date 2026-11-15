
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


def analyze_project(project_text, credentials=None):
    credentials = credentials or get_credentials()

    if not credentials:
        return {
            "status": "unavailable",
            "summary": "AI-анализ пока недоступен. Добавьте ключ GigaChat.",
            "genres": [],
            "themes": [],
            "strengths": [],
            "risks": [],
            "audience": "",
            "recommendations": [],
        }

    prompt = f"""
Ты — эксперт по кинопроизводству и развитию независимого кино.

Проанализируй описание кинопроекта.
Не выдумывай факты, которых нет в описании.
Отделяй факты от предположений.

Верни результат строго в формате JSON со следующими полями:
{{
    "summary": "Краткое описание проекта",
    "genres": ["Жанры"],
    "themes": ["Основные темы"],
    "strengths": ["Сильные стороны проекта"],
    "risks": ["Возможные проблемы и риски"],
    "audience": "Предполагаемая аудитория",
    "recommendations": ["Рекомендации по развитию проекта"]
}}

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

        if not isinstance(result, dict):
            raise ValueError("Не удалось прочитать ответ AI")

        required_fields = [
            "summary",
            "genres",
            "themes",
            "strengths",
            "risks",
            "audience",
            "recommendations",
        ]

        for field in required_fields:
            result.setdefault(field, [] if field != "summary" and field != "audience" else "")

        result["status"] = "success"
        return result

    except Exception as error:
        return {
            "status": "error",
            "summary": "Не удалось выполнить AI-анализ.",
            "genres": [],
            "themes": [],
            "strengths": [],
            "risks": [],
            "audience": "",
            "recommendations": [],
            "error": str(error),
        }
