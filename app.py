
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
    initial_sidebar_state="expanded",
)


# ============================================================
# СТИЛИ
# ============================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Manrope', sans-serif;
}

.stApp {
    background: #101114;
    color: #F1F0ED;
}

[data-testid="stSidebar"] {
    background: #17191E;
    border-right: 1px solid #303239;
}

.hero {
    padding: 42px 0 30px 0;
}

.eyebrow {
    color: #D8A66A;
    font-size: 12px;
    letter-spacing: 3px;
    text-transform: uppercase;
    font-weight: 700;
}

.hero h1 {
    font-size: clamp(38px, 6vw, 66px);
    line-height: 1.08;
    font-weight: 800;
    margin: 18px 0;
    color: #F4F0E9;
}

.hero p {
    color: #A7A6A2;
    font-size: 17px;
    max-width: 650px;
    line-height: 1.7;
}

.section-title {
    font-size: 24px;
    font-weight: 700;
    margin: 28px 0 12px;
}

.project-card {
    background: #191B20;
    border: 1px solid #34363D;
    border-radius: 12px;
    padding: 22px;
    margin: 12px 0;
}

.project-card h3 {
    margin-top: 0;
    color: #F4F0E9;
}

.muted {
    color: #A7A6A2;
    font-size: 14px;
}

div.stButton > button[kind="primary"] {
    background: #C58E55;
    color: #171717;
    border: none;
    font-weight: 700;
}

div.stButton > button[kind="primary"]:hover {
    background: #D9A66E;
    color: #171717;
}

hr {
    border-color: #34363D;
}

/* Мобильная версия */
@media (max-width: 768px) {
    [data-testid="stSidebar"] {
        display: none;
    }

    [data-testid="stAppViewContainer"] .main .block-container {
        padding: 15px 14px 30px 14px;
        max-width: 100%;
    }

    .st-key-mobile_navigation {
        position: relative !important;
        top: auto !important;
        bottom: auto !important;
        left: auto !important;
        width: 100%;
        z-index: 10;
        background: #17191D;
        border: 1px solid #34363D;
        border-radius: 14px;
        padding: 10px;
        margin-bottom: 22px;
    }

    .st-key-mobile_navigation [role="radiogroup"] {
        display: grid !important;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 8px;
        width: 100%;
    }

    .st-key-mobile_navigation [role="radiogroup"] label {
        display: flex;
        align-items: center;
        justify-content: center;
        min-width: 0;
        min-height: 52px;
        margin: 0;
        padding: 8px 4px;
        border: 1px solid #34363D;
        border-radius: 10px;
        background: #202228;
        color: #D0D0D0;
        text-align: center;
        font-size: 12px !important;
        font-weight: 600;
        line-height: 1.25;
    }

    .st-key-mobile_navigation [role="radiogroup"] label:has(input:checked) {
        background: #303321;
        border-color: #D8F078;
        color: #D8F078;
    }

    .st-key-mobile_navigation [role="radiogroup"] label p {
        font-size: 12px !important;
        margin: 0;
        white-space: normal;
    }

    .st-key-mobile_navigation > div > label {
        display: none;
    }

    footer {
        display: none !important;
    }

    .hero {
        padding: 15px 0 20px;
    }

    .hero h1 {
        font-size: 36px;
        line-height: 1.08;
    }

    h1 {
        font-size: 29px !important;
        line-height: 1.15 !important;
    }

    h2 {
        font-size: 23px !important;
    }

    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea,
    [data-testid="stSelectbox"] [data-baseweb="select"] {
        border-radius: 10px;
        font-size: 16px;
    }

    [data-testid="stFormSubmitButton"] button {
        width: 100%;
        min-height: 48px;
        border-radius: 10px;
        font-weight: 700;
    }

    div.stButton > button {
        min-height: 44px;
        border-radius: 10px;
    }

    [data-testid="stExpander"] {
        border: 1px solid #34363D;
        border-radius: 12px;
        overflow: hidden;
    }

    [data-testid="stMetric"] {
        background: #191B20;
        border: 1px solid #34363D;
        border-radius: 10px;
        padding: 12px;
    }

    .stMarkdown,
    [data-testid="stVerticalBlock"] {
        max-width: 100%;
    }
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# ИНИЦИАЛИЗАЦИЯ
# ============================================================

init_db()


def get_ai_credentials():
    try:
        return st.secrets.get("GIGACHAT_CREDENTIALS", "")
    except Exception:
        return ""


def normalize_genre(value):
    return " ".join(str(value).casefold().strip().split())


# ============================================================
# ОТОБРАЖЕНИЕ AI-АНАЛИЗА
# ============================================================

def show_analysis(analysis, author_genre=None):
    status = analysis.get("status", "")

    if status == "success":
        st.success("AI-анализ выполнен")

    elif status == "unavailable":
        st.info(
            "AI пока не подключён. "
            "Проект сохранён без AI-анализа."
        )

    else:
        st.warning(
            "AI-анализ не удался. "
            "Проект можно сохранить без него."
        )

        error_text = str(
            analysis.get("error", "Причина не передана")
        )

        credentials = get_ai_credentials()

        if credentials:
            error_text = error_text.replace(
                credentials,
                "[ключ скрыт]",
            )

        st.caption("Техническая причина ошибки:")
        st.code(error_text[:1200])

    if analysis.get("summary"):
        st.write(analysis["summary"])

    if (
        status == "success"
        and author_genre
        and author_genre != "Другое"
    ):
        ai_genres = analysis.get("genres", [])

        if isinstance(ai_genres, str):
            ai_genres = [ai_genres]

        author_genre_normalized = normalize_genre(
            author_genre
        )

        ai_genres_normalized = [
            normalize_genre(item)
            for item in ai_genres
        ]

        if author_genre_normalized not in ai_genres_normalized:
            st.warning(
                f"Жанровые характеристики различаются: "
                f"вы указали «{author_genre}», "
                f"а AI не включил этот жанр в свой список."
            )

            st.caption(
                "Это не обязательно ошибка. AI предлагает "
                "дополнительную интерпретацию, а выбранный "
                "вами жанр остаётся основным. При необходимости "
                "проверьте описание и жанровую разметку проекта."
            )
        else:
            st.success(
                "AI-анализ учитывает выбранный вами жанр."
            )

    columns = st.columns(2)

    fields = [
        ("Жанры по версии AI", "genres"),
        ("Оценка выбранного автором жанра", "genre_assessment"),
        ("Что в тексте указывает на жанр", "genre_evidence"),
        ("Дополнительные жанровые трактовки", "genre_alternatives"),
        ("Темы", "themes"),
        ("Сильные стороны", "strengths"),
        ("Риски", "risks"),
        ("Аудитория", "audience"),
        ("Рекомендации", "recommendations"),
    ]

    for index, (title, key) in enumerate(fields):
        with columns[index % 2]:
            value = analysis.get(key, [])

            st.markdown(f"**{title}**")

            if isinstance(value, list):
                if value:
                    for item in value:
                        st.write(f"• {item}")
                else:
                    st.caption("Нет данных")
            else:
                st.write(value or "Нет данных")


# ============================================================
# ГЛАВНАЯ СТРАНИЦА
# ============================================================

def page_home():
    projects = get_projects()
    campaigns = get_campaigns()

    st.markdown("""
    <div class="hero">
        <div class="eyebrow">NEWS MEDIA HOLDING PRESENTS</div>
        <h1>Истории, которые<br>найдут своих людей.</h1>
        <p>
        Кинобюро объединяет независимых режиссёров,
        продюсеров и команды, которым нужны новые
        истории и возможности для сотрудничества.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    col1.metric("Проекты в базе", len(projects))
    col2.metric("Заявки на продвижение", len(campaigns))
    col3.metric("Форматы сотрудничества", "3")

    st.markdown("---")
    st.markdown("### Три направления работы")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### 01 / Авторам")
        st.write(
            "Расскажите о своём проекте и покажите портфолио."
        )

    with col2:
        st.markdown("#### 02 / Продюсерам")
        st.write(
            "Ищите режиссёров и проекты с помощью AI."
        )

    with col3:
        st.markdown("#### 03 / Студиям")
        st.write(
            "Обсудите продвижение независимого фильма "
            "с медиахолдингом."
        )


# ============================================================
# ЗАЯВКА РЕЖИССЁРА
# ============================================================

def page_director():
    st.markdown("## Заявка режиссёра")

    st.write(
        "Расскажите о проекте. Чем подробнее описание, "
        "тем полезнее будет AI-анализ."
    )

    with st.form("director_form"):
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

    if submitted:
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
                    "\n\nДополнительные материалы:\n"
                    + file_text
                )
            except Exception as error:
                st.error(
                    f"Не удалось обработать файл: {error}"
                )
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

            st.success(
                f"Проект «{name}» сохранён. "
                f"Номер заявки: {project_id}"
            )

            show_analysis(
                analysis,
                author_genre=genre,
            )

            st.markdown("---")
            st.markdown("### Хотите развивать проект вместе с NMH?")

            st.write(
                "Команда Кинобюро может рассмотреть возможности "
                "информационной поддержки и продвижения вашего фильма."
            )

            if st.button(
                "Перейти к заявке на продвижение",
                type="primary",
                key="director_campaign_link",
            ):
                st.session_state["campaign_prefill"] = {
                    "film_name": name.strip(),
                    "company": director.strip(),
                    "description": synopsis.strip(),
                    "audience": analysis.get("audience", ""),
                    "contact": contact.strip(),
                }

                st.session_state["mobile_navigation"] = (
                    "↗ Продвиж."
                )
                st.rerun()

        except Exception as error:
            st.error(
                f"Не удалось сохранить проект: {error}"
            )


# ============================================================
# AI-ПОИСК ПРОЕКТОВ ДЛЯ ПРОДЮСЕРА
# ============================================================

def page_producer():
    st.markdown("## AI-поиск проектов")

    st.write(
        "Опишите задачу продюсера. GigaChat проанализирует "
        "проекты и объяснит, какие из них лучше соответствуют запросу."
    )

    projects = get_projects()

    if not projects:
        st.info(
            "Пока в базе нет проектов. Первым можно добавить "
            "проект через раздел «Авторам»."
        )
        return

    with st.form("producer_search"):
        query = st.text_area(
            "Что вы ищете?",
            placeholder=(
                "Например: ищу комедийный проект для молодой "
                "аудитории, с потенциалом для онлайн-платформы..."
            ),
            height=120,
        )

        search_genre = st.text_input(
            "Желаемые жанры",
            placeholder="Комедия, драма",
        )

        search_themes = st.text_input(
            "Темы и мотивы",
            placeholder="Взросление, семья, отношения",
        )

        producer_id = st.text_input(
            "Ваш контакт или рабочий идентификатор",
            placeholder="Например, email",
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
                ai_response.get(
                    "error",
                    "Неизвестная ошибка",
                )
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

            st.caption("Техническая причина:")
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

            enriched_results.append({
                **original,
                **item,
            })

        st.session_state["search_results"] = enriched_results
        st.session_state["producer_id"] = producer_id.strip()
        st.session_state["search_query"] = query.strip()

    results = st.session_state.get("search_results", [])

    if results:
        st.markdown("---")
        st.markdown("### Результаты AI-подбора")

        st.caption(
            "Рейтинг сформирован GigaChat-2 на основе "
            "смыслового соответствия запросу и характеристик проектов."
        )

        st.markdown(
            f"**Проанализировано проектов: {len(results)}**"
        )

        for project in results:
            with st.container(border=True):
                st.markdown(f"### {project['name']}")

                st.caption(
                    f"{project.get('director', 'Автор')} · "
                    f"{project.get('genre', 'Жанр не указан')} · "
                    f"{project.get('format', 'Формат не указан')} · "
                    f"{project.get('stage', 'Стадия не указана')}"
                )

                st.write(project.get("synopsis", ""))

                st.markdown(
                    f"**Оценка соответствия по мнению AI: "
                    f"{project['score']} / 100**"
                )

                st.progress(
                    min(project["score"] / 100, 1.0)
                )

                if project.get("fit_summary"):
                    st.write(project["fit_summary"])

                if project.get("reasons"):
                    st.markdown(
                        "**Почему AI рекомендует проект:**"
                    )

                    for reason in project["reasons"]:
                        st.write(f"• {reason}")

                if project.get("concerns"):
                    st.markdown(
                        "**Что стоит дополнительно проверить:**"
                    )

                    for concern in project["concerns"]:
                        st.write(f"• {concern}")

                if project.get("portfolio_url"):
                    st.markdown(
                        f"[Открыть портфолио]"
                        f"({project['portfolio_url']})"
                    )

                analysis = project.get("analysis", {})

                if (
                    isinstance(analysis, dict)
                    and analysis.get("status") == "success"
                ):
                    with st.expander(
                        "Посмотреть полный AI-анализ проекта"
                    ):
                        show_analysis(
                            analysis,
                            author_genre=project.get("genre"),
                        )

                current_producer = st.session_state.get(
                    "producer_id",
                    "",
                )

                if current_producer:
                    if st.button(
                        "Сохранить в избранное",
                        key=f"save_{project['id']}",
                    ):
                        try:
                            save_project_to_favorites(
                                project["id"],
                                current_producer,
                            )

                            st.success(
                                "Проект добавлен в избранное."
                            )

                        except Exception as error:
                            st.error(
                                "Не удалось сохранить проект: "
                                f"{error}"
                            )

    elif st.session_state.get("search_query"):
        st.info(
            "AI не вернул проекты для отображения."
        )


# ============================================================
# ЗАЯВКА НА ПРОДВИЖЕНИЕ ФИЛЬМА
# ============================================================

def page_campaign():
    st.markdown("## Продвижение фильма")

    st.write(
        "Расскажите о фильме и задачах продвижения. "
        "Команда Кинобюро сможет оценить возможные форматы сотрудничества."
    )

    prefill = st.session_state.get(
        "campaign_prefill",
        {},
    )

    with st.form("campaign_form"):
        film_name = st.text_input(
            "Название фильма *",
            value=prefill.get("film_name", ""),
        )

        company = st.text_input(
            "Студия или компания / имя автора *",
            value=prefill.get("company", ""),
        )

        release_date = st.text_input(
            "Планируемая дата релиза",
            placeholder="Например, весна 2027",
        )

        audience = st.text_area(
            "Целевая аудитория",
            value=prefill.get("audience", ""),
            placeholder="Для кого этот фильм?",
        )

        budget = st.text_input(
            "Предполагаемый бюджет продвижения",
            placeholder=(
                "Можно указать диапазон "
                "или написать «обсуждается»"
            ),
        )

        description = st.text_area(
            "Задачи и материалы",
            value=prefill.get("description", ""),
            height=140,
            placeholder=(
                "Какая поддержка нужна? "
                "Какие материалы уже готовы?"
            ),
        )

        contact = st.text_input(
            "Контактное лицо и способ связи *",
            value=prefill.get("contact", ""),
        )

        submitted = st.form_submit_button(
            "Отправить заявку",
            type="primary",
            use_container_width=True,
        )

    if submitted:
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

            st.success(
                f"Заявка принята. Номер заявки: {campaign_id}"
            )

            st.session_state.pop(
                "campaign_prefill",
                None,
            )

        except Exception as error:
            st.error(
                f"Не удалось сохранить заявку: {error}"
            )


# ============================================================
# ОТКРЫТАЯ ПАНЕЛЬ КОМАНДЫ NMH
# ============================================================

def page_admin():
    st.markdown("## Панель команды Кинобюро")

    projects = get_projects()
    campaigns = get_campaigns()

    col1, col2 = st.columns(2)

    col1.metric("Всего проектов", len(projects))
    col2.metric("Заявок на продвижение", len(campaigns))

    st.markdown("### Проекты режиссёров")

    if not projects:
        st.info("Проектов пока нет.")

    else:
        for project in projects:
            with st.expander(
                f"{project['name']} — {project['director']}"
            ):
                st.write(project["synopsis"])

                st.caption(
                    f"{project['genre']} · "
                    f"{project['format']} · "
                    f"{project['stage']}"
                )

                st.write(
                    f"Контакт: {project['contact']}"
                )

                if project.get("portfolio_url"):
                    st.markdown(
                        f"[Портфолио]({project['portfolio_url']})"
                    )

                show_analysis(
                    project.get("analysis", {}),
                    author_genre=project.get("genre"),
                )

    st.markdown("---")
    st.markdown("### Заявки на продвижение")

    if not campaigns:
        st.info(
            "Заявок на продвижение пока нет."
        )

    else:
        for campaign in campaigns:
            with st.expander(
                f"{campaign['film_name']} — {campaign['company']}"
            ):
                st.write(
                    campaign.get("description", "")
                )

                st.write(
                    f"Релиз: {campaign.get('release_date', '')}"
                )

                st.write(
                    f"Аудитория: {campaign.get('audience', '')}"
                )

                st.write(
                    f"Бюджет: {campaign.get('budget', '')}"
                )

                st.write(
                    f"Контакт: {campaign.get('contact', '')}"
                )


# ============================================================
# НАВИГАЦИЯ
# ============================================================

with st.sidebar:
    st.markdown("## NMH")
    st.caption("КИНОБЮРО")
    st.markdown("---")
    st.caption(
        "Платформа поиска и развития независимого кино"
    )


navigation = {
    "⌂ Главная": "Главная",
    "＋ Авторам": "Авторам",
    "⌕ Поиск": "Продюсерам",
    "↗ Продвиж.": "Продвижение фильма",
    "◯ Команда": "Команда NMH",
}


selected_navigation = st.radio(
    "Навигация",
    list(navigation.keys()),
    horizontal=True,
    label_visibility="collapsed",
    key="mobile_navigation",
)


page = navigation[selected_navigation]


if page == "Главная":
    page_home()

elif page == "Авторам":
    page_director()

elif page == "Продюсерам":
    page_producer()

elif page == "Продвижение фильма":
    page_campaign()

elif page == "Команда NMH":
    page_admin()
