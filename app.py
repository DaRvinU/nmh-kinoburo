import html
from urllib.parse import urlparse

import streamlit as st

from backend.ai import analyze_project, rank_projects_ai
from backend.db import (
    init_db,
    save_project,
    get_projects,
    save_project_to_favorites,
    save_campaign,
    get_campaigns,
)
from backend.files import extract_text


st.set_page_config(
    page_title="NMH Кинобюро",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# СТИЛИ
# ============================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Playfair+Display:wght@600;700;800&display=swap');

:root {
    --bg: #0E0F12;
    --surface: #16181D;
    --surface-2: #1C1F25;
    --line: #2B2E36;
    --text: #F3EFE8;
    --muted: #A09E9A;
    --gold: #D4A468;
    --gold-hover: #E3B97F;
    --gold-soft: rgba(212, 164, 104, 0.14);
    --good: #86C08A;
    --warn: #D4A468;
    --bad: #D48A78;
    --radius: 14px;
}

html, body, [class*="css"], .stApp {
    font-family: 'Manrope', sans-serif;
}

.stApp {
    background:
        radial-gradient(900px 420px at 85% -10%, rgba(212,164,104,0.10), transparent 60%),
        var(--bg);
    color: var(--text);
}

/* Убираем лишние элементы Streamlit: навигация в верхней панели */
[data-testid="stSidebar"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"],
footer {
    display: none !important;
}

[data-testid="stHeader"] {
    background: transparent;
}

[data-testid="stAppViewContainer"] .main .block-container,
.block-container {
    max-width: 1080px;
    padding: 28px 24px 64px;
}

/* ---------- Типографика ---------- */
h1, h2, h3 {
    font-family: 'Playfair Display', serif !important;
    color: var(--text);
    letter-spacing: -0.01em;
}

h3 { font-size: 22px !important; }

a { color: var(--gold) !important; }

/* ---------- Верхняя панель ---------- */
.brand {
    display: flex;
    align-items: baseline;
    gap: 10px;
    padding-top: 6px;
}

.brand b {
    font-family: 'Playfair Display', serif;
    font-size: 26px;
    letter-spacing: 1px;
    color: var(--text);
}

.brand span {
    font-size: 11px;
    letter-spacing: 4px;
    color: var(--gold);
    font-weight: 700;
}

[data-testid="stRadio"] [role="radiogroup"] {
    gap: 6px;
    flex-wrap: wrap;
    justify-content: flex-end;
}

[data-testid="stRadio"] label {
    margin: 0;
    padding: 8px 16px;
    border: 1px solid transparent;
    border-radius: 999px;
    cursor: pointer;
    transition: background .15s, border-color .15s;
}

[data-testid="stRadio"] label > div:first-child {
    display: none;
}

[data-testid="stRadio"] label p {
    font-size: 14px;
    font-weight: 600;
    color: var(--muted);
    margin: 0;
}

[data-testid="stRadio"] label:hover {
    background: var(--surface-2);
}

[data-testid="stRadio"] label:has(input:checked) {
    background: var(--gold-soft);
    border-color: var(--gold);
}

[data-testid="stRadio"] label:has(input:checked) p {
    color: var(--gold);
}

.nav-divider {
    height: 1px;
    background: var(--line);
    margin: 10px 0 8px;
}

/* ---------- Заголовки страниц ---------- */
.eyebrow {
    color: var(--gold);
    font-size: 12px;
    letter-spacing: 3px;
    text-transform: uppercase;
    font-weight: 700;
}

.hero {
    padding: 56px 0 36px;
}

.hero h1 {
    font-size: clamp(38px, 6vw, 68px);
    line-height: 1.08;
    font-weight: 800;
    margin: 18px 0 20px;
}

.hero h1 em {
    font-style: italic;
    color: var(--gold);
}

.hero p {
    color: var(--muted);
    font-size: 17px;
    max-width: 620px;
    line-height: 1.7;
    margin: 0;
}

.page-head {
    padding: 22px 0 18px;
}

.page-head h2 {
    font-size: clamp(28px, 4vw, 40px);
    margin: 10px 0 8px;
}

.page-head p {
    color: var(--muted);
    max-width: 640px;
    line-height: 1.65;
    margin: 0;
}

/* ---------- Карточки ---------- */
.stat {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: var(--radius);
    padding: 20px 22px;
}

.stat .num {
    font-family: 'Playfair Display', serif;
    font-size: 40px;
    font-weight: 700;
    color: var(--gold);
    line-height: 1;
}

.stat .label {
    color: var(--muted);
    font-size: 13px;
    margin-top: 8px;
}

.role-card {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: var(--radius);
    padding: 22px;
    min-height: 168px;
}

.role-card .idx {
    color: var(--gold);
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 2px;
}

.role-card h4 {
    font-family: 'Playfair Display', serif;
    font-size: 22px;
    margin: 10px 0 8px;
    color: var(--text);
}

.role-card p {
    color: var(--muted);
    font-size: 14px;
    line-height: 1.6;
    margin: 0;
}

.flow {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-top: 8px;
}

.flow div {
    background: var(--surface-2);
    border: 1px solid var(--line);
    border-radius: 12px;
    padding: 16px;
    font-size: 14px;
    color: var(--muted);
    line-height: 1.5;
}

.flow b {
    display: block;
    color: var(--text);
    margin-bottom: 4px;
}

.section-title {
    font-family: 'Playfair Display', serif;
    font-size: 26px;
    font-weight: 700;
    margin: 40px 0 14px;
}

.form-section {
    font-size: 12px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--gold);
    font-weight: 700;
    margin: 18px 0 6px;
}

/* Контейнеры с рамкой и формы */
[class*="st-key-result_"],
[data-testid="stForm"] {
    background: var(--surface);
    border: 1px solid var(--line) !important;
    border-radius: var(--radius);
    padding: 14px 18px;
    margin-bottom: 16px;
}

[data-testid="stForm"] {
    padding: 20px 22px 22px;
}

/* ---------- Чипы и бейджи ---------- */
.chips {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin: 6px 0 10px;
}

.chip {
    background: var(--surface-2);
    border: 1px solid var(--line);
    color: var(--text);
    border-radius: 999px;
    padding: 3px 11px;
    font-size: 12px;
    font-weight: 600;
}

.chip.gold {
    background: var(--gold-soft);
    border-color: rgba(212,164,104,.45);
    color: var(--gold);
}

.badge {
    display: inline-block;
    border-radius: 999px;
    padding: 4px 12px;
    font-size: 12px;
    font-weight: 700;
    border: 1px solid;
}

.badge.ok   { color: var(--good); border-color: rgba(134,192,138,.5); background: rgba(134,192,138,.10); }
.badge.info { color: var(--gold); border-color: rgba(212,164,104,.5); background: var(--gold-soft); }
.badge.err  { color: var(--bad);  border-color: rgba(212,138,120,.5); background: rgba(212,138,120,.10); }

.project-title {
    font-family: 'Playfair Display', serif;
    font-size: 24px;
    font-weight: 700;
    margin: 4px 0 4px;
    color: var(--text);
}

.project-meta {
    color: var(--muted);
    font-size: 13px;
    margin-bottom: 8px;
}

.score { margin: 14px 0 10px; }

.score-top {
    display: flex;
    justify-content: space-between;
    font-size: 13px;
    color: var(--muted);
    margin-bottom: 6px;
}

.score-top b { color: var(--text); font-size: 15px; }

.bar {
    height: 8px;
    border-radius: 999px;
    background: var(--surface-2);
    overflow: hidden;
}

.bar i {
    display: block;
    height: 100%;
    border-radius: 999px;
}

.block-title {
    font-size: 11px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: var(--gold);
    font-weight: 700;
    margin: 14px 0 6px;
}

.block-text, .block-list {
    color: var(--text);
    font-size: 14px;
    line-height: 1.6;
    margin: 0;
}

.block-list { padding-left: 18px; }
.block-list li { margin-bottom: 3px; }
.block-empty { color: var(--muted); font-size: 13px; }

.callout {
    background: var(--surface-2);
    border-left: 3px solid var(--gold);
    border-radius: 8px;
    padding: 12px 16px;
    margin: 12px 0;
    font-size: 14px;
    line-height: 1.6;
}

.callout small { color: var(--muted); display: block; margin-top: 4px; }

/* ---------- Поля, кнопки ---------- */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-baseweb="select"] > div {
    background: var(--surface-2) !important;
    border: 1px solid var(--line) !important;
    border-radius: 10px !important;
    color: var(--text);
}

[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: var(--gold) !important;
    box-shadow: 0 0 0 1px var(--gold) !important;
}

label p { font-weight: 600; font-size: 14px; }

div.stButton > button,
[data-testid="stFormSubmitButton"] button,
[data-testid="stLinkButton"] a {
    border-radius: 10px;
    min-height: 44px;
    font-weight: 700;
    border: 1px solid var(--line);
    background: var(--surface-2);
    color: var(--text) !important;
    transition: all .15s;
}

div.stButton > button:hover,
[data-testid="stLinkButton"] a:hover {
    border-color: var(--gold);
    color: var(--gold) !important;
}

div.stButton > button[kind="primary"],
[data-testid="stFormSubmitButton"] button[kind="primary"],
[data-testid="stFormSubmitButton"] button[kind="primaryFormSubmit"] {
    background: var(--gold);
    color: #17140F !important;
    border: none;
}

div.stButton > button[kind="primary"]:hover,
[data-testid="stFormSubmitButton"] button:hover {
    background: var(--gold-hover);
    color: #17140F !important;
}

[data-testid="stExpander"] {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 12px;
}

[data-baseweb="tab-list"] { gap: 6px; }

hr { border-color: var(--line); }

/* ---------- Мобильная версия ---------- */
@media (max-width: 768px) {
    .block-container { padding: 16px 14px 48px; }
    [data-testid="stRadio"] [role="radiogroup"] { justify-content: flex-start; }
    [data-testid="stRadio"] label { padding: 7px 12px; }
    .hero { padding: 28px 0 24px; }
    .flow { grid-template-columns: 1fr 1fr; }
    .role-card { min-height: 0; }
    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea { font-size: 16px; }
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# ИНИЦИАЛИЗАЦИЯ И ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================

init_db()

NAV_ITEMS = ["Главная", "Авторам", "Продюсерам", "Продвижение", "Команда"]


def go_to(page_name):
    """Переход между разделами (вызывается как on_click-колбэк)."""
    st.session_state["nav"] = page_name


def get_ai_credentials():
    try:
        return st.secrets.get("GIGACHAT_CREDENTIALS", "")
    except Exception:
        return ""


def normalize_genre(value):
    return " ".join(str(value).casefold().strip().split())


def esc(value):
    """Экранирует пользовательский текст перед вставкой в HTML."""
    return html.escape(str(value if value is not None else ""))


def safe_url(url):
    """Возвращает ссылку, только если это http(s)."""
    url = str(url or "").strip()
    parsed = urlparse(url)
    if parsed.scheme in ("http", "https") and parsed.netloc:
        return url
    return ""


def page_header(eyebrow, title, text):
    st.markdown(
        f"""
        <div class="page-head">
            <div class="eyebrow">{esc(eyebrow)}</div>
            <h2>{esc(title)}</h2>
            <p>{esc(text)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def form_section(title):
    st.markdown(
        f'<div class="form-section">{esc(title)}</div>',
        unsafe_allow_html=True,
    )


def chips_html(items, gold=False):
    items = [i for i in items if str(i).strip()]
    if not items:
        return ""
    cls = "chip gold" if gold else "chip"
    inner = "".join(f'<span class="{cls}">{esc(i)}</span>' for i in items)
    return f'<div class="chips">{inner}</div>'


def info_block(title, value, as_chips=False):
    """HTML-блок «заголовок + содержимое» для AI-анализа."""
    if isinstance(value, str):
        value = value.strip()

    if not value:
        body = '<div class="block-empty">Нет данных</div>'
    elif isinstance(value, list):
        if as_chips:
            body = chips_html(value, gold=True)
        else:
            body = (
                '<ul class="block-list">'
                + "".join(f"<li>{esc(i)}</li>" for i in value)
                + "</ul>"
            )
    else:
        body = f'<p class="block-text">{esc(value)}</p>'

    return f'<div class="block-title">{esc(title)}</div>{body}'


def score_color(score):
    if score >= 75:
        return "var(--good)"
    if score >= 50:
        return "var(--warn)"
    return "var(--bad)"


def meta_line(project):
    parts = [
        project.get("director"),
        project.get("genre"),
        project.get("format"),
        project.get("stage"),
    ]
    return " · ".join(esc(p) for p in parts if p)


def stat_card(number, label):
    return (
        f'<div class="stat"><div class="num">{esc(number)}</div>'
        f'<div class="label">{esc(label)}</div></div>'
    )


# ============================================================
# ОТОБРАЖЕНИЕ AI-АНАЛИЗА
# ============================================================

def show_analysis(analysis, author_genre=None):
    analysis = analysis or {}
    status = analysis.get("status", "")

    if status == "success":
        st.markdown(
            '<span class="badge ok">✓ AI-анализ выполнен</span>',
            unsafe_allow_html=True,
        )
    elif status == "unavailable":
        st.markdown(
            '<span class="badge info">AI не подключён — проект '
            'сохранён без анализа</span>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<span class="badge err">AI-анализ не удался — проект '
            'можно сохранить без него</span>',
            unsafe_allow_html=True,
        )

        error_text = str(analysis.get("error", "Причина не передана"))
        credentials = get_ai_credentials()

        if credentials:
            error_text = error_text.replace(credentials, "[ключ скрыт]")

        with st.expander("Техническая причина ошибки"):
            st.code(error_text[:1200])

    if analysis.get("summary"):
        st.markdown(
            f'<div class="callout">{esc(analysis["summary"])}</div>',
            unsafe_allow_html=True,
        )

    if status == "success" and author_genre and author_genre != "Другое":
        ai_genres = analysis.get("genres", [])

        if isinstance(ai_genres, str):
            ai_genres = [ai_genres]

        author_norm = normalize_genre(author_genre)
        ai_norm = [normalize_genre(item) for item in ai_genres]

        if author_norm not in ai_norm:
            st.markdown(
                f"""
                <div class="callout">
                    Жанровые характеристики различаются: вы указали
                    «{esc(author_genre)}», а AI не включил этот жанр
                    в свой список.
                    <small>Это не обязательно ошибка: AI предлагает
                    дополнительную интерпретацию, а выбранный вами жанр
                    остаётся основным.</small>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<span class="badge ok">AI-анализ учитывает выбранный '
                'вами жанр</span>',
                unsafe_allow_html=True,
            )

    left, right = st.columns(2)

    with left:
        st.markdown(
            info_block("Жанры по версии AI", analysis.get("genres", []), True)
            + info_block("Темы", analysis.get("themes", []), True)
            + info_block(
                "Оценка выбранного автором жанра",
                analysis.get("genre_assessment", ""),
            )
            + info_block(
                "Что в тексте указывает на жанр",
                analysis.get("genre_evidence", []),
            )
            + info_block(
                "Дополнительные жанровые трактовки",
                analysis.get("genre_alternatives", []),
            ),
            unsafe_allow_html=True,
        )

    with right:
        st.markdown(
            info_block("Аудитория", analysis.get("audience", ""))
            + info_block("Сильные стороны", analysis.get("strengths", []))
            + info_block("Риски", analysis.get("risks", []))
            + info_block("Рекомендации", analysis.get("recommendations", [])),
            unsafe_allow_html=True,
        )


# ============================================================
# ГЛАВНАЯ СТРАНИЦА
# ============================================================

def page_home():
    projects = get_projects()
    campaigns = get_campaigns()

    st.markdown("""
    <div class="hero">
        <div class="eyebrow">News Media Holding presents</div>
        <h1>Истории, которые<br><em>найдут своих людей.</em></h1>
        <p>
        Кинобюро объединяет независимых режиссёров, продюсеров и
        медиакоманды: AI помогает быстро находить проекты под задачу,
        а NMH — вывести фильм к аудитории.
        </p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    c1.markdown(stat_card(len(projects), "проектов в базе"),
                unsafe_allow_html=True)
    c2.markdown(stat_card(len(campaigns), "заявок на продвижение"),
                unsafe_allow_html=True)
    c3.markdown(stat_card("3", "формата сотрудничества"),
                unsafe_allow_html=True)

    st.markdown('<div class="section-title">С чего начать</div>',
                unsafe_allow_html=True)

    cards = [
        ("01 / Авторам", "Покажите проект",
         "Отправьте синопсис и материалы — AI разберёт жанр, темы, "
         "аудиторию и даст рекомендации.",
         "Подать проект", "Авторам"),
        ("02 / Продюсерам", "Найдите историю",
         "Опишите задачу своими словами — AI ранжирует проекты по "
         "смыслу и объяснит выбор.",
         "Открыть поиск", "Продюсерам"),
        ("03 / Студиям", "Выведите фильм к зрителю",
         "Обсудите продвижение через медиаресурсы холдинга и "
         "пакеты медиаподдержки.",
         "Заявка на продвижение", "Продвижение"),
    ]

    for column, (idx, title, text, button, target) in zip(
        st.columns(3), cards
    ):
        with column:
            st.markdown(
                f"""
                <div class="role-card">
                    <div class="idx">{esc(idx)}</div>
                    <h4>{esc(title)}</h4>
                    <p>{esc(text)}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.button(
                button,
                key=f"home_cta_{target}",
                on_click=go_to,
                args=(target,),
                use_container_width=True,
            )

    st.markdown('<div class="section-title">Как это работает</div>',
                unsafe_allow_html=True)

    st.markdown("""
    <div class="flow">
        <div><b>1. Заявка</b>Автор подаёт проект и материалы</div>
        <div><b>2. AI-анализ</b>Жанр, темы, аудитория, риски</div>
        <div><b>3. Подбор</b>Продюсер получает ранжированный список</div>
        <div><b>4. Продвижение</b>Платная поддержка через медиа NMH</div>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# ЗАЯВКА РЕЖИССЁРА
# ============================================================

def page_director():
    page_header(
        "Авторам",
        "Заявка режиссёра",
        "Расскажите о проекте. Чем подробнее описание, тем полезнее "
        "будет AI-анализ.",
    )

    with st.form("director_form"):
        form_section("О проекте")

        name = st.text_input("Название проекта *")
        director = st.text_input("Имя режиссёра *")

        synopsis = st.text_area(
            "Синопсис и описание проекта *",
            height=180,
            placeholder=(
                "О чём ваша история? Кто герои? "
                "Что делает её особенной?"
            ),
        )

        form_section("Параметры")

        col1, col2 = st.columns(2)

        with col1:
            genre = st.selectbox(
                "Жанр",
                [
                    "Драма",
                    "Комедия",
                    "Триллер",
                    "Фантастика",
                    "Документальное кино",
                    "Анимация",
                    "Другое",
                ],
            )

            project_format = st.selectbox(
                "Формат",
                [
                    "Полный метр",
                    "Короткий метр",
                    "Сериал",
                    "Документальный фильм",
                    "Веб-сериал",
                    "Другое",
                ],
            )

        with col2:
            stage = st.selectbox(
                "Стадия проекта",
                [
                    "Идея",
                    "Сценарий",
                    "Подготовка к съёмкам",
                    "Съёмки",
                    "Постпродакшн",
                    "Готовый фильм",
                ],
            )

            portfolio_url = st.text_input(
                "Ссылка на портфолио или фильм"
            )

        form_section("Контакты и материалы")

        contact = st.text_input("Контакт для связи *")

        uploaded_file = st.file_uploader(
            "Дополнительные материалы",
            type=["pdf", "docx", "txt"],
            help=(
                "До 15 МБ. Можно загрузить презентацию "
                "или описание проекта."
            ),
        )

        submitted = st.form_submit_button(
            "Отправить проект",
            type="primary",
            use_container_width=True,
        )

    if not submitted:
        return

    if (
        not name.strip()
        or not director.strip()
        or not synopsis.strip()
        or not contact.strip()
    ):
        st.error("Заполните все обязательные поля.")
        return

    project_text = synopsis

    if uploaded_file is not None:
        try:
            file_text = extract_text(uploaded_file)
            project_text += (
                "\n\nДополнительные материалы:\n" + file_text
            )
        except Exception as error:
            st.error(f"Не удалось обработать файл: {error}")
            return

    with st.spinner("Анализируем проект с помощью AI..."):
        analysis = analyze_project(
            project_text,
            credentials=get_ai_credentials(),
            author_genre=genre,
        )

    project = {
        "name": name.strip(),
        "director": director.strip(),
        "synopsis": synopsis.strip(),
        "genre": genre,
        "format": project_format,
        "stage": stage,
        "portfolio_url": portfolio_url.strip(),
        "contact": contact.strip(),
        "analysis": analysis,
    }

    try:
        project_id = save_project(project)
    except Exception as error:
        st.error(f"Не удалось сохранить проект: {error}")
        return

    st.success(
        f"Проект «{name}» сохранён. Номер заявки: {project_id}"
    )

    st.markdown(
        '<div class="section-title">Результат AI-анализа</div>',
        unsafe_allow_html=True,
    )
    show_analysis(analysis, author_genre=genre)

    st.markdown(
        '<div class="section-title">Развивать проект вместе с NMH?</div>',
        unsafe_allow_html=True,
    )
    st.write(
        "Команда Кинобюро может рассмотреть информационную поддержку "
        "и продвижение вашего фильма."
    )

    # Данные для предзаполнения сохраняем до перехода
    st.session_state["campaign_prefill"] = {
        "film_name": name.strip(),
        "company": director.strip(),
        "description": synopsis.strip(),
        "audience": str(analysis.get("audience", "")),
        "contact": contact.strip(),
    }

    st.button(
        "Перейти к заявке на продвижение",
        type="primary",
        key="director_campaign_link",
        on_click=go_to,
        args=("Продвижение",),
    )


# ============================================================
# AI-ПОИСК ПРОЕКТОВ ДЛЯ ПРОДЮСЕРА
# ============================================================

def render_result_card(project, current_producer):
    score = int(project.get("score", 0))
    score = max(0, min(100, score))

    with st.container(border=True, key=f"result_{project['id']}"):
        st.markdown(
            f"""
            <div class="project-title">{esc(project.get("name", ""))}</div>
            <div class="project-meta">{meta_line(project)}</div>
            """,
            unsafe_allow_html=True,
        )

        st.write(project.get("synopsis", ""))

        st.markdown(
            f"""
            <div class="score">
                <div class="score-top">
                    <span>Соответствие запросу по оценке AI</span>
                    <b>{score} / 100</b>
                </div>
                <div class="bar"><i style="width:{score}%;
                    background:{score_color(score)}"></i></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if project.get("fit_summary"):
            st.markdown(
                f'<div class="callout">{esc(project["fit_summary"])}</div>',
                unsafe_allow_html=True,
            )

        left, right = st.columns(2)

        with left:
            if project.get("reasons"):
                st.markdown(
                    info_block(
                        "Почему AI рекомендует проект",
                        project["reasons"],
                    ),
                    unsafe_allow_html=True,
                )

        with right:
            if project.get("concerns"):
                st.markdown(
                    info_block(
                        "Что стоит проверить",
                        project["concerns"],
                    ),
                    unsafe_allow_html=True,
                )

        analysis = project.get("analysis", {})

        if (
            isinstance(analysis, dict)
            and analysis.get("status") == "success"
        ):
            with st.expander("Полный AI-анализ проекта"):
                show_analysis(
                    analysis,
                    author_genre=project.get("genre"),
                )

        actions = st.columns([1, 1, 2])

        link = safe_url(project.get("portfolio_url"))

        if link:
            with actions[0]:
                st.link_button("Портфолио", link)

        if current_producer:
            with actions[1]:
                if st.button(
                    "★ В избранное",
                    key=f"save_{project['id']}",
                ):
                    try:
                        save_project_to_favorites(
                            project["id"],
                            current_producer,
                        )
                        st.success("Добавлено в избранное.")
                    except Exception as error:
                        st.error(
                            f"Не удалось сохранить проект: {error}"
                        )


def page_producer():
    page_header(
        "Продюсерам",
        "AI-поиск проектов",
        "Опишите задачу своими словами. GigaChat проанализирует проекты "
        "и объяснит, какие из них лучше соответствуют запросу.",
    )

    projects = get_projects()

    if not projects:
        st.info(
            "Пока в базе нет проектов. Первым можно добавить проект "
            "через раздел «Авторам»."
        )
        return

    with st.form("producer_search"):
        query = st.text_area(
            "Что вы ищете?",
            placeholder=(
                "Например: ищу комедийный проект для молодой аудитории "
                "с потенциалом для онлайн-платформы..."
            ),
            height=120,
        )

        col1, col2 = st.columns(2)

        with col1:
            search_genre = st.text_input(
                "Желаемые жанры",
                placeholder="Комедия, драма",
            )

        with col2:
            search_themes = st.text_input(
                "Темы и мотивы",
                placeholder="Взросление, семья, отношения",
            )

        producer_id = st.text_input(
            "Ваш контакт или рабочий идентификатор",
            placeholder="Например, email — нужен для избранного",
        )

        submitted = st.form_submit_button(
            "Найти проекты с помощью AI",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        if not query.strip():
            st.warning("Введите поисковый запрос.")
            return

        brief = {
            "genres": [
                item.strip()
                for item in search_genre.split(",")
                if item.strip()
            ],
            "themes": [
                item.strip()
                for item in search_themes.split(",")
                if item.strip()
            ],
        }

        with st.spinner(
            "GigaChat анализирует проекты и подбирает подходящие..."
        ):
            ai_response = rank_projects_ai(
                query=query.strip(),
                projects=projects,
                brief=brief,
                credentials=get_ai_credentials(),
            )

        if ai_response.get("status") != "success":
            st.session_state.pop("search_results", None)

            error_text = str(
                ai_response.get("error", "Неизвестная ошибка")
            )

            credentials = get_ai_credentials()

            if credentials:
                error_text = error_text.replace(
                    credentials,
                    "[ключ скрыт]",
                )

            st.error(
                "AI-поиск временно не выполнился. "
                "Попробуйте повторить запрос."
            )

            with st.expander("Техническая причина"):
                st.code(error_text[:1000])
            return

        original_projects = {
            str(project.get("id", "")): project
            for project in projects
        }

        enriched_results = []

        for item in ai_response.get("results", []):
            original = original_projects.get(
                str(item.get("id", "")),
                {},
            )

            enriched_results.append({**original, **item})

        st.session_state["search_results"] = enriched_results
        st.session_state["producer_id"] = producer_id.strip()
        st.session_state["search_query"] = query.strip()

    results = st.session_state.get("search_results", [])

    if results:
        st.markdown(
            '<div class="section-title">Результаты AI-подбора</div>',
            unsafe_allow_html=True,
        )

        st.caption(
            f"Проанализировано проектов: {len(results)}. Рейтинг "
            "сформирован GigaChat-2 по смысловому соответствию запросу."
        )

        current_producer = st.session_state.get("producer_id", "")

        for project in results:
            render_result_card(project, current_producer)

    elif st.session_state.get("search_query"):
        st.info("AI не вернул проекты для отображения.")


# ============================================================
# ЗАЯВКА НА ПРОДВИЖЕНИЕ ФИЛЬМА
# ============================================================

def page_campaign():
    page_header(
        "Студиям",
        "Продвижение фильма",
        "Расскажите о фильме и задачах продвижения. Команда Кинобюро "
        "оценит возможные форматы сотрудничества.",
    )

    prefill = st.session_state.get("campaign_prefill", {})

    with st.form("campaign_form"):
        form_section("Фильм")

        film_name = st.text_input(
            "Название фильма *",
            value=prefill.get("film_name", ""),
        )

        company = st.text_input(
            "Студия или компания / имя автора *",
            value=prefill.get("company", ""),
        )

        col1, col2 = st.columns(2)

        with col1:
            release_date = st.text_input(
                "Планируемая дата релиза",
                placeholder="Например, весна 2027",
            )

        with col2:
            budget = st.text_input(
                "Бюджет продвижения",
                placeholder="Диапазон или «обсуждается»",
            )

        audience = st.text_area(
            "Целевая аудитория",
            value=prefill.get("audience", ""),
            placeholder="Для кого этот фильм?",
        )

        description = st.text_area(
            "Задачи и материалы",
            value=prefill.get("description", ""),
            height=140,
            placeholder=(
                "Какая поддержка нужна? Какие материалы уже готовы?"
            ),
        )

        form_section("Контакты")

        contact = st.text_input(
            "Контактное лицо и способ связи *",
            value=prefill.get("contact", ""),
        )

        submitted = st.form_submit_button(
            "Отправить заявку",
            type="primary",
            use_container_width=True,
        )

    if not submitted:
        return

    if (
        not film_name.strip()
        or not company.strip()
        or not contact.strip()
    ):
        st.error("Заполните обязательные поля.")
        return

    try:
        campaign_id = save_campaign({
            "film_name": film_name.strip(),
            "company": company.strip(),
            "release_date": release_date.strip(),
            "audience": audience.strip(),
            "budget": budget.strip(),
            "description": description.strip(),
            "contact": contact.strip(),
        })

        st.success(f"Заявка принята. Номер заявки: {campaign_id}")
        st.session_state.pop("campaign_prefill", None)

    except Exception as error:
        st.error(f"Не удалось сохранить заявку: {error}")


# ============================================================
# ПАНЕЛЬ КОМАНДЫ NMH
# ============================================================

def page_admin():
    page_header(
        "Команда NMH",
        "Панель Кинобюро",
        "Все проекты авторов и заявки на продвижение в одном месте.",
    )

    projects = get_projects()
    campaigns = get_campaigns()

    c1, c2 = st.columns(2)
    c1.markdown(stat_card(len(projects), "всего проектов"),
                unsafe_allow_html=True)
    c2.markdown(stat_card(len(campaigns), "заявок на продвижение"),
                unsafe_allow_html=True)

    st.write("")

    tab_projects, tab_campaigns = st.tabs([
        f"Проекты ({len(projects)})",
        f"Заявки ({len(campaigns)})",
    ])

    with tab_projects:
        if not projects:
            st.info("Проектов пока нет.")

        for project in projects:
            with st.expander(
                f"{project.get('name', '—')} — "
                f"{project.get('director', '—')}"
            ):
                st.markdown(
                    f'<div class="project-meta">{meta_line(project)}'
                    "</div>",
                    unsafe_allow_html=True,
                )

                st.write(project.get("synopsis", ""))

                st.markdown(
                    info_block("Контакт", project.get("contact", "")),
                    unsafe_allow_html=True,
                )

                link = safe_url(project.get("portfolio_url"))
                if link:
                    st.link_button("Портфолио", link)

                st.markdown("---")

                show_analysis(
                    project.get("analysis", {}),
                    author_genre=project.get("genre"),
                )

    with tab_campaigns:
        if not campaigns:
            st.info("Заявок на продвижение пока нет.")

        for campaign in campaigns:
            with st.expander(
                f"{campaign.get('film_name', '—')} — "
                f"{campaign.get('company', '—')}"
            ):
                st.write(campaign.get("description", ""))

                left, right = st.columns(2)

                with left:
                    st.markdown(
                        info_block("Релиз", campaign.get("release_date", ""))
                        + info_block("Бюджет", campaign.get("budget", "")),
                        unsafe_allow_html=True,
                    )

                with right:
                    st.markdown(
                        info_block("Аудитория", campaign.get("audience", ""))
                        + info_block("Контакт", campaign.get("contact", "")),
                        unsafe_allow_html=True,
                    )


# ============================================================
# НАВИГАЦИЯ
# ============================================================

brand_col, nav_col = st.columns([1.1, 3])

with brand_col:
    st.markdown(
        '<div class="brand"><b>NMH</b><span>КИНОБЮРО</span></div>',
        unsafe_allow_html=True,
    )

with nav_col:
    page = st.radio(
        "Навигация",
        NAV_ITEMS,
        horizontal=True,
        label_visibility="collapsed",
        key="nav",
    )

st.markdown('<div class="nav-divider"></div>', unsafe_allow_html=True)


if page == "Главная":
    page_home()

elif page == "Авторам":
    page_director()

elif page == "Продюсерам":
    page_producer()

elif page == "Продвижение":
    page_campaign()

elif page == "Команда":
    page_admin()
