
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def normalize(value):
    return str(value or "").lower().replace("ё", "е")


def get_tokens(value):
    return set(re.findall(r"[а-яa-z0-9-]{3,}", normalize(value)))


def project_text(project):
    analysis = project.get("analysis", {})

    fields = [
        project.get("name", ""),
        project.get("director", ""),
        project.get("synopsis", ""),
        project.get("genre", ""),
        project.get("stage", ""),
        project.get("format", ""),
        " ".join(analysis.get("genres", [])),
        " ".join(analysis.get("themes", [])),
        analysis.get("tone", ""),
        analysis.get("visual_style", ""),
        " ".join(analysis.get("keywords", [])),
        " ".join(analysis.get("strengths", [])),
    ]

    return " ".join(str(value) for value in fields)


def rank_projects(query, projects, brief=None):
    if not projects:
        return []

    brief = brief or {}
    query_tokens = get_tokens(query)
    documents = [project_text(project) for project in projects]

    try:
        vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            sublinear_tf=True
        )
        matrix = vectorizer.fit_transform(documents + [query])
        similarities = cosine_similarity(
            matrix[-1],
            matrix[:-1]
        ).flatten()
    except ValueError:
        similarities = [0.0] * len(projects)

    wanted_genres = get_tokens(" ".join(brief.get("genres", [])))
    wanted_themes = get_tokens(" ".join(brief.get("themes", [])))

    ranked = []

    for index, project in enumerate(projects):
        analysis = project.get("analysis", {})
        candidate_tokens = get_tokens(project_text(project))

        term_score = (
            len(query_tokens & candidate_tokens)
            / max(1, len(query_tokens))
        )

        genres = get_tokens(
            " ".join(analysis.get("genres", []))
            + " "
            + project.get("genre", "")
        )
        themes = get_tokens(
            " ".join(analysis.get("themes", []))
            + " "
            + project.get("synopsis", "")
        )

        genre_score = (
            len(wanted_genres & genres)
            / max(1, len(wanted_genres))
        )
        theme_score = (
            len(wanted_themes & themes)
            / max(1, len(wanted_themes))
        )

        text_score = float(similarities[index])

        score = 100 * (
            0.50 * text_score
            + 0.20 * term_score
            + 0.18 * genre_score
            + 0.12 * theme_score
        )

        reasons = []

        if genre_score:
            reasons.append("Совпадает жанровый профиль")
        if theme_score:
            reasons.append("Есть пересечение по темам")
        if term_score:
            reasons.append("В описании найдены релевантные признаки")
        if not reasons:
            reasons.append("Смежный кандидат: нужна ручная оценка")

        ranked.append({
            **project,
            "score": round(min(score, 99), 1),
            "reasons": reasons,
            "score_breakdown": {
                "text": round(text_score * 100, 1),
                "terms": round(term_score * 100, 1),
                "genre": round(genre_score * 100, 1),
                "themes": round(theme_score * 100, 1),
            },
        })

    return sorted(
        ranked,
        key=lambda project: project["score"],
        reverse=True
    )
