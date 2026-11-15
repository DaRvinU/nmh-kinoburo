
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timezone


DB_PATH = Path("kinoburo.db")


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                director TEXT NOT NULL,
                synopsis TEXT NOT NULL,
                genre TEXT DEFAULT '',
                format TEXT DEFAULT '',
                stage TEXT DEFAULT '',
                portfolio_url TEXT DEFAULT '',
                contact TEXT DEFAULT '',
                analysis TEXT DEFAULT '{}',
                created_at TEXT NOT NULL
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS saved_projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                producer_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                UNIQUE(project_id, producer_id)
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                film_name TEXT NOT NULL,
                company TEXT NOT NULL,
                release_date TEXT DEFAULT '',
                audience TEXT DEFAULT '',
                budget TEXT DEFAULT '',
                description TEXT DEFAULT '',
                contact TEXT DEFAULT '',
                created_at TEXT NOT NULL
            )
        """)


def save_project(project):
    now = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:
        cursor = connection.execute("""
            INSERT INTO projects (
                name, director, synopsis, genre, format,
                stage, portfolio_url, contact, analysis, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            project["name"],
            project["director"],
            project["synopsis"],
            project.get("genre", ""),
            project.get("format", ""),
            project.get("stage", ""),
            project.get("portfolio_url", ""),
            project.get("contact", ""),
            json.dumps(project.get("analysis", {}), ensure_ascii=False),
            now,
        ))

        return cursor.lastrowid


def get_projects():
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM projects ORDER BY created_at DESC"
        ).fetchall()

    projects = []

    for row in rows:
        project = dict(row)
        project["analysis"] = json.loads(project["analysis"] or "{}")
        projects.append(project)

    return projects


def save_project_to_favorites(project_id, producer_id):
    now = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:
        connection.execute("""
            INSERT OR IGNORE INTO saved_projects (
                project_id, producer_id, created_at
            )
            VALUES (?, ?, ?)
        """, (project_id, producer_id, now))


def save_campaign(campaign):
    now = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:
        cursor = connection.execute("""
            INSERT INTO campaigns (
                film_name, company, release_date, audience,
                budget, description, contact, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            campaign["film_name"],
            campaign["company"],
            campaign.get("release_date", ""),
            campaign.get("audience", ""),
            campaign.get("budget", ""),
            campaign.get("description", ""),
            campaign.get("contact", ""),
            now,
        ))

        return cursor.lastrowid


def get_campaigns():
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM campaigns ORDER BY created_at DESC"
        ).fetchall()

    return [dict(row) for row in rows]
