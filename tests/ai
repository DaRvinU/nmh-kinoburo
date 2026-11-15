import json

import backend.ai as ai


def test_extract_json_plain():
    assert ai.extract_json('{"a": 1}') == {"a": 1}


def test_extract_json_inside_markdown():
    assert ai.extract_json('Вот ответ:\n```json\n{"a": 1}\n```') == {"a": 1}


def test_extract_json_garbage_returns_none():
    assert ai.extract_json("это вообще не JSON") is None


def test_filter_relevant_drops_low_scores():
    items = [{"id": "a", "score": 90}, {"id": "b", "score": 39}, {"id": "c", "score": 40}]
    assert [item["id"] for item in filter_ids(items)] == ["a", "c"]


def filter_ids(items):
    return ai.filter_relevant(items)


def test_search_without_key_is_unavailable(monkeypatch):
    monkeypatch.delenv("GIGACHAT_CREDENTIALS", raising=False)
    result = ai.rank_projects_ai("драма", [{"id": "1", "name": "X"}])
    assert result["status"] == "unavailable"


def test_analyze_without_key_is_unavailable(monkeypatch):
    monkeypatch.delenv("GIGACHAT_CREDENTIALS", raising=False)
    assert ai.analyze_project("текст")["status"] == "unavailable"


class _FakeGiga:
    """Подмена GigaChat: возвращает заранее заданный ответ."""
    answer = ""

    def __init__(self, *args, **kwargs):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def chat(self, payload):
        message = type("M", (), {"content": _FakeGiga.answer})()
        return type("R", (), {"choices": [type("C", (), {"message": message})()]})()


PROJECTS = [{"id": "1", "name": "A"}, {"id": "2", "name": "B"}]


def test_search_rejects_incomplete_list(monkeypatch):
    monkeypatch.setattr(ai, "GigaChat", _FakeGiga)
    _FakeGiga.answer = json.dumps({"ranked_projects": [{"id": "1", "score": 80}]})
    result = ai.rank_projects_ai("q", PROJECTS, credentials="key")
    assert result["status"] == "error"


def test_search_rejects_invented_project(monkeypatch):
    monkeypatch.setattr(ai, "GigaChat", _FakeGiga)
    _FakeGiga.answer = json.dumps({"ranked_projects": [
        {"id": "1", "score": 80}, {"id": "999", "score": 70}]})
    result = ai.rank_projects_ai("q", PROJECTS, credentials="key")
    assert result["status"] == "error"


def test_search_sorts_and_clamps_scores(monkeypatch):
    monkeypatch.setattr(ai, "GigaChat", _FakeGiga)
    _FakeGiga.answer = json.dumps({"ranked_projects": [
        {"id": "1", "score": 20}, {"id": "2", "score": 250}]})
    result = ai.rank_projects_ai("q", PROJECTS, credentials="key")
    assert result["status"] == "success"
    assert [item["id"] for item in result["results"]] == ["2", "1"]
    assert result["results"][0]["score"] == 100


def test_search_non_json_answer_is_error(monkeypatch):
    monkeypatch.setattr(ai, "GigaChat", _FakeGiga)
    _FakeGiga.answer = "извините, не могу"
    result = ai.rank_projects_ai("q", PROJECTS, credentials="key")
    assert result["status"] == "error"
