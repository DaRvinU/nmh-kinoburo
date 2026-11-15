"""Оценка качества ИИ-подбора на тестовых данных.

Запуск из корня репозитория:  python eval/run_eval.py
Нужен ключ GIGACHAT_CREDENTIALS (в .env или в переменных окружения).
Результат: таблица в консоли + файлы eval/results.md и eval/results.json
"""
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

from backend.ai import MIN_SCORE, filter_relevant, rank_projects_ai
from backend.matching import rank_projects

HERE = Path(__file__).resolve().parent
projects = json.loads((HERE / "projects.json").read_text(encoding="utf-8"))
queries = json.loads((HERE / "queries.json").read_text(encoding="utf-8"))

names = {p["id"]: p["name"] for p in projects}


def ai_shown(query):
    """Возвращает (список id в топ-3, ошибка). Показываем только проекты выше порога."""
    for attempt in range(2):
        response = rank_projects_ai(query=query, projects=projects)
        if response["status"] == "success":
            relevant = filter_relevant(response["results"])
            return [item["id"] for item in relevant[:3]], ""
        time.sleep(3)
    return [], response.get("error", "ошибка")


def keyword_shown(query):
    """Обычный поиск по словам (TF-IDF) — для сравнения. Нулевые совпадения не показываем."""
    ranked = rank_projects(query, projects)
    return [item["id"] for item in ranked if item["score"] > 0][:3]


def precision(shown, expected):
    if not shown:
        return 0.0
    return sum(1 for pid in shown if pid in expected) / len(shown)


rows = []
for number, item in enumerate(queries, start=1):
    query, expected = item["query"], item["expected"]
    ai_ids, error = ai_shown(query)
    kw_ids = keyword_shown(query)
    rows.append({
        "n": number, "query": query, "expected": expected,
        "ai": ai_ids, "keyword": kw_ids, "error": error,
    })
    print(f"[{number}/{len(queries)}] {query[:55]:55} AI={ai_ids} слова={kw_ids}")
    time.sleep(1)

positive = [r for r in rows if r["expected"]]
negative = [r for r in rows if not r["expected"]]


def hit_rate(key):
    return sum(1 for r in positive if set(r[key]) & set(r["expected"])) / len(positive)


def mean_precision(key):
    return sum(precision(r[key], r["expected"]) for r in positive) / len(positive)


no_match_ai = sum(1 for r in negative if not r["ai"]) / len(negative)
no_match_kw = sum(1 for r in negative if not r["keyword"]) / len(negative)
errors = [r for r in rows if r["error"]]

summary = {
    "queries_total": len(rows),
    "queries_with_answer": len(positive),
    "queries_without_answer": len(negative),
    "threshold": MIN_SCORE,
    "ai_top3_hit": round(hit_rate("ai"), 2),
    "keyword_top3_hit": round(hit_rate("keyword"), 2),
    "ai_precision_at_3": round(mean_precision("ai"), 2),
    "keyword_precision_at_3": round(mean_precision("keyword"), 2),
    "ai_no_match_correct": round(no_match_ai, 2),
    "keyword_no_match_correct": round(no_match_kw, 2),
    "ai_errors": len(errors),
}

lines = [
    "# Результаты оценки ИИ-подбора",
    "",
    f"Тестовых проектов: {len(projects)}. Запросов: {len(rows)} "
    f"({len(positive)} с ожидаемым ответом, {len(negative)} без подходящих проектов). "
    f"Порог релевантности: {MIN_SCORE}/100.",
    "",
    "| Метрика | ИИ-подбор (GigaChat-2) | Поиск по словам (TF-IDF) |",
    "|---|---|---|",
    f"| Релевантность Топ-3 | {summary['ai_top3_hit']:.0%} | {summary['keyword_top3_hit']:.0%} |",
    f"| Precision@3 (доля подходящих среди показанных) | {summary['ai_precision_at_3']:.0%} | {summary['keyword_precision_at_3']:.0%} |",
    f"| Корректный ответ «ничего не подошло» | {summary['ai_no_match_correct']:.0%} | {summary['keyword_no_match_correct']:.0%} |",
    f"| Ошибки запросов к ИИ | {summary['ai_errors']} | — |",
    "",
    "## Разбор по запросам",
    "",
    "| № | Запрос | Ожидалось | ИИ | Слова |",
    "|---|---|---|---|---|",
]


def label(ids):
    return ", ".join(names[i] for i in ids) if ids else "—"


for r in rows:
    mark = "" if r["ai"] and set(r["ai"]) & set(r["expected"]) or (not r["expected"] and not r["ai"]) else " ❌"
    lines.append(f"| {r['n']} | {r['query']} | {label(r['expected'])} | {label(r['ai'])}{mark} | {label(r['keyword'])} |")

(HERE / "results.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
(HERE / "results.json").write_text(
    json.dumps({"summary": summary, "rows": rows}, ensure_ascii=False, indent=2),
    encoding="utf-8",
)

print("\nИТОГ:", json.dumps(summary, ensure_ascii=False, indent=2))
print("Файлы eval/results.md и eval/results.json созданы.")
