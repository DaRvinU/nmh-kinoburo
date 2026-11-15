
import hashlib
import json
import os
from datetime import datetime, timezone

import firebase_admin
from firebase_admin import credentials, firestore


_firebase_db = None


def _load_firebase_config():
    """Читает Firebase из переменных окружения или старых Streamlit Secrets."""

    raw_config = os.getenv("FIREBASE_CREDENTIALS_JSON", "").strip()

    if raw_config:
        try:
            config = json.loads(raw_config)
        except json.JSONDecodeError as error:
            raise RuntimeError(
                "FIREBASE_CREDENTIALS_JSON содержит некорректный JSON."
            ) from error
    else:
        try:
            import streamlit as st
            config = dict(st.secrets["firebase"])
        except Exception as error:
            raise RuntimeError(
                "Не найдены настройки Firebase. "
                "Добавьте FIREBASE_CREDENTIALS_JSON "
                "в переменные окружения."
            ) from error

    if "private_key" in config:
        config["private_key"] = (
            config["private_key"].replace("\\n", "\n")
        )

    return config


def get_connection():
    """Возвращает подключение к Firebase Firestore."""
    global _firebase_db

    if _firebase_db is not None:
        return _firebase_db

    firebase_config = _load_firebase_config()

    try:
        try:
            firebase_app = firebase_admin.get_app()
        except ValueError:
            certificate = credentials.Certificate(firebase_config)
            firebase_app = firebase_admin.initialize_app(certificate)

        _firebase_db = firestore.client(app=firebase_app)
        return _firebase_db

    except Exception as error:
        raise RuntimeError(
            f"Не удалось подключиться к Firebase: {error}"
        ) from error


def init_db():
    """Проверяет доступность облачной базы."""
    get_connection()


def save_project(project):
    """Сохраняет заявку режиссёра."""
    db = get_connection()
    now = datetime.now(timezone.utc).isoformat()

    data = {
        "name": project["name"],
        "director": project["director"],
        "synopsis": project["synopsis"],
        "genre": project.get("genre", ""),
        "format": project.get("format", ""),
        "stage": project.get("stage", ""),
        "portfolio_url": project.get("portfolio_url", ""),
        "contact": project.get("contact", ""),
        "logline": project.get("logline", ""),
        "analysis": project.get("analysis", {}),
        "created_at": now,
    }

    document = db.collection("projects").document()
    document.set(data)

    return document.id


def get_projects():
    """Загружает все проекты из облачной базы."""
    db = get_connection()
    documents = db.collection("projects").stream()

    projects = []

    for document in documents:
        project = document.to_dict()
        project["id"] = document.id

        if not isinstance(project.get("analysis"), dict):
            project["analysis"] = {}

        projects.append(project)

    projects.sort(
        key=lambda item: item.get("created_at", ""),
        reverse=True,
    )

    return projects


def save_project_to_favorites(project_id, producer_id):
    """Сохраняет проект в избранное продюсера без дубликатов."""
    db = get_connection()
    now = datetime.now(timezone.utc).isoformat()

    unique_key = f"{producer_id}_{project_id}"
    document_id = hashlib.sha256(
        unique_key.encode("utf-8")
    ).hexdigest()

    db.collection("saved_projects").document(document_id).set({
        "project_id": str(project_id),
        "producer_id": str(producer_id),
        "created_at": now,
    })


def save_campaign(campaign):
    """Сохраняет заявку на продвижение фильма."""
    db = get_connection()
    now = datetime.now(timezone.utc).isoformat()

    data = {
        "film_name": campaign["film_name"],
        "company": campaign["company"],
        "release_date": campaign.get("release_date", ""),
        "audience": campaign.get("audience", ""),
        "budget": campaign.get("budget", ""),
        "description": campaign.get("description", ""),
        "contact": campaign.get("contact", ""),
        "created_at": now,
    }

    document = db.collection("campaigns").document()
    document.set(data)

    return document.id


def get_campaigns():
    """Загружает все заявки на продвижение."""
    db = get_connection()
    documents = db.collection("campaigns").stream()

    campaigns = []

    for document in documents:
        campaign = document.to_dict()
        campaign["id"] = document.id
        campaigns.append(campaign)

    campaigns.sort(
        key=lambda item: item.get("created_at", ""),
        reverse=True,
    )

    return campaigns
