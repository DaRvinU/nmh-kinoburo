
from backend.matching import rank_projects


def test_empty_projects_return_empty_list():
    assert rank_projects("драма о семье", []) == []


def test_matching_ranks_relevant_project_higher():
    projects = [
        {
            "id": 1,
            "name": "Последний космос",
            "director": "Иван",
            "synopsis": "Фантастическая история о космическом путешествии",
            "genre": "Фантастика",
            "analysis": {
                "genres": ["Фантастика"],
                "themes": ["Космос", "Путешествие"],
            },
        },
        {
            "id": 2,
            "name": "Тихий берег",
            "director": "Мария",
            "synopsis": "Семейная драма о жизни в маленьком городе",
            "genre": "Драма",
            "analysis": {
                "genres": ["Драма"],
                "themes": ["Семья", "Отношения"],
            },
        },
    ]

    result = rank_projects(
        "фантастика космос путешествие",
        projects,
        brief={"genres": ["Фантастика"], "themes": ["Космос"]},
    )

    assert len(result) == 2
    assert result[0]["id"] == 1
    assert result[0]["score"] > result[1]["score"]


def test_matching_returns_score_and_reasons():
    projects = [
        {
            "id": 1,
            "name": "История",
            "director": "Анна",
            "synopsis": "История о взрослении и поиске себя",
            "genre": "Драма",
            "analysis": {
                "genres": ["Драма"],
                "themes": ["Взросление"],
            },
        }
    ]

    result = rank_projects("драма взросление", projects)

    assert len(result) == 1
    assert "score" in result[0]
    assert "reasons" in result[0]
    assert isinstance(result[0]["reasons"], list)
