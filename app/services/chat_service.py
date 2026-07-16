import re
from functools import lru_cache

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models import FestivalSchedule, Location, Post
from app.schemas.chat import ChatResponse, ChatSource

settings = get_settings()

LANGUAGE_NAMES = {
    "ko": "Korean", "en": "English", "ja": "Japanese", "zh": "Simplified Chinese",
    "fr": "French", "es": "Spanish", "de": "German",
}
FALLBACK_MESSAGES = {
    "ko": "저장된 서울 데이터에서 관련 결과를 찾지 못했어요. 장소명, 자치구 또는 여행 유형을 함께 입력해 주세요.",
    "en": "I couldn't find a related result in the saved Seoul data. Try a place name, district, or travel category.",
    "ja": "保存されたソウルのデータに関連する結果がありません。場所名、区、旅行カテゴリーを入力してください。",
    "zh": "在已保存的首尔数据中找不到相关结果。请输入地点名称、行政区或旅行类别。",
    "fr": "Aucun résultat associé n'a été trouvé dans les données de Séoul. Essayez un lieu, un arrondissement ou une catégorie.",
    "es": "No encontré resultados relacionados en los datos de Seúl. Prueba con un lugar, distrito o categoría.",
    "de": "In den gespeicherten Seoul-Daten wurde nichts Passendes gefunden. Versuche einen Ort, Bezirk oder eine Kategorie.",
}
RESULT_MESSAGES = {
    "ko": "저장된 서울 데이터에서 관련 결과를 찾았어요: {titles}. 아래 결과에서 상세 정보를 확인해 보세요.",
    "en": "I found related results in the saved Seoul data: {titles}. Check the results below for details.",
    "ja": "保存されたソウルのデータから関連情報が見つかりました：{titles}。詳細は下の結果をご覧ください。",
    "zh": "在已保存的首尔数据中找到了相关结果：{titles}。请在下方查看详细信息。",
    "fr": "Résultats trouvés dans les données de Séoul : {titles}. Consultez-les ci-dessous pour plus de détails.",
    "es": "Encontré resultados en los datos de Seúl: {titles}. Consulta los detalles abajo.",
    "de": "Passende Ergebnisse in den Seoul-Daten: {titles}. Details findest du unten.",
}

STOP_WORDS = {
    "추천", "추천해줘", "추천해주세요", "알려줘", "알려주세요", "보여줘", "보여주세요", "어디", "어떤", "대해",
    "있는", "좋은", "가볼만한", "서울", "서울시", "장소", "정보", "관련",
}
PARTICLES = ("에서", "으로", "에게", "에는", "이랑", "하고", "의", "을", "를", "은", "는", "이", "가", "에")


def _search_terms(message: str) -> list[str]:
    terms: list[str] = []
    for raw in re.findall(r"[0-9A-Za-z가-힣]+", message):
        term = raw
        for particle in PARTICLES:
            if term.endswith(particle) and len(term) > len(particle) + 1:
                term = term[:-len(particle)]
                break
        if len(term) >= 2 and term not in STOP_WORDS and term not in terms:
            terms.append(term)
    return terms[:8]


def _search_context(db: Session, message: str) -> tuple[list[ChatSource], str]:
    terms = _search_terms(message)
    location_filters = []
    post_filters = []
    for term in terms:
        like = f"%{term}%"
        location_filters.extend((
            Location.title.ilike(like),
            Location.addr1.ilike(like),
            Location.addr2.ilike(like),
            Location.district.ilike(like),
            Location.content_type.ilike(like),
        ))
        post_filters.extend((Post.title.ilike(like), Post.content.ilike(like), Post.tags_json.ilike(like)))

    locations = []
    if location_filters:
        candidates = db.scalars(
            select(Location)
            .where(or_(*location_filters))
            .order_by(Location.is_featured.desc(), Location.solo_score.desc().nullslast(), Location.source_modified_at.desc())
            .limit(100)
        ).all()
        def relevance(item: Location) -> tuple[int, int, int]:
            title = item.title.lower()
            searchable = " ".join((item.title, item.addr1, item.addr2, item.district or "", item.content_type)).lower()
            matched = sum(term.lower() in searchable for term in terms)
            title_matches = sum(term.lower() in title for term in terms)
            return matched, title_matches, item.is_featured

        locations = sorted(candidates, key=relevance, reverse=True)[:8]
    if not locations and any(word in message for word in ("추천", "가볼", "혼자", "갈만한")):
        locations = db.scalars(
            select(Location)
            .where(Location.content_type_id.not_in((15, 25)))
            .order_by(Location.is_featured.desc(), Location.solo_score.desc().nullslast(), Location.source_modified_at.desc())
            .limit(8)
        ).all()

    posts = []
    if post_filters:
        posts = db.scalars(
            select(Post)
            .where(or_(*post_filters))
            .order_by(Post.created_at.desc())
            .limit(3)
        ).all()

    sources: list[ChatSource] = []
    context_lines: list[str] = []

    for item in locations:
        sources.append(
            ChatSource(
                type="LOCATION",
                id=item.content_id,
                title=item.title,
                subtitle=f"{item.content_type} · {item.addr1}",
                image_url=item.first_image,
            )
        )
        modified_date = item.source_modified_at.date() if item.source_modified_at else None
        date_text = f" / 축제일: {modified_date}" if item.content_type_id == 15 and modified_date else ""
        context_lines.append(
            f"장소: {item.title} / 유형: {item.content_type} / 주소: {item.addr1} {item.addr2} "
            f"/ 전화: {item.tel or '없음'} / 위도: {item.map_y or '없음'} / 경도: {item.map_x or '없음'}{date_text}"
        )

    for post in posts:
        sources.append(
            ChatSource(
                type="POST",
                id=str(post.id),
                title=post.title,
                subtitle=f"{post.nickname} · {post.type}",
            )
        )
        context_lines.append(f"커뮤니티 글: {post.title} / 내용: {post.content[:300]}")

    if ("축제" in message or "행사" in message) and not any(item.content_type_id == 15 for item in locations):
        schedules = db.execute(
            select(FestivalSchedule, Location)
            .join(Location, FestivalSchedule.location_id == Location.id)
            .order_by(FestivalSchedule.start_date.asc())
            .limit(5)
        ).all()
        for schedule, location in schedules:
            if not any(source.id == location.content_id for source in sources):
                sources.append(
                    ChatSource(
                        type="FESTIVAL",
                        id=location.content_id,
                        title=location.title,
                        subtitle=f"{schedule.start_date} ~ {schedule.end_date}",
                        image_url=location.first_image,
                    )
                )
            context_lines.append(
                f"축제: {location.title} / 일정: {schedule.start_date}~{schedule.end_date} / 장소: {location.addr1}"
            )

    search_note = f"JSON 데이터 검색어: {', '.join(terms) if terms else '없음'}"
    return sources[:8], "\n".join([search_note, *context_lines])


def _fallback_answer(message: str, sources: list[ChatSource], language: str = "ko") -> str:
    if not sources:
        return FALLBACK_MESSAGES.get(language, FALLBACK_MESSAGES["ko"])

    titles = ", ".join(source.title for source in sources[:4])
    template = RESULT_MESSAGES.get(language, RESULT_MESSAGES["ko"])
    return template.format(titles=titles)


def _gemini_text(prompt: str) -> str:
    import httpx

    response = httpx.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{settings.gemini_model}:generateContent",
        headers={"Content-Type": "application/json", "x-goog-api-key": settings.gemini_api_key},
        json={"contents": [{"role": "user", "parts": [{"text": prompt}]}]},
        timeout=30.0,
    )
    response.raise_for_status()
    payload = response.json()
    return "".join(
        part.get("text", "")
        for part in payload.get("candidates", [{}])[0].get("content", {}).get("parts", [])
    ).strip()


@lru_cache(maxsize=256)
def _korean_search_query(message: str, language: str) -> str:
    if language == "ko" or not settings.gemini_api_key:
        return message
    try:
        return _gemini_text(
            "Translate the following Seoul travel search query into Korean. "
            "Return only concise Korean search keywords with no explanation:\n" + message
        ) or message
    except Exception:
        return message


def answer_chat(db: Session, message: str, history: list[dict], language: str = "ko") -> ChatResponse:
    search_query = _korean_search_query(message, language)
    sources, context = _search_context(db, search_query)
    fallback = _fallback_answer(message, sources, language)

    if not settings.gemini_api_key:
        return ChatResponse(
            answer=fallback,
            sources=sources,
            suggestions=["혼자 걷기 좋은 곳", "이번 달 축제", "종로구 문화시설"],
            used_ai=False,
        )

    try:
        import httpx

        contents = [
            {
                "role": "model" if item.get("role") == "assistant" else "user",
                "parts": [{"text": str(item.get("content") or "")}],
            }
            for item in history[-10:]
            if item.get("content")
        ]
        contents.append({
            "role": "user",
            "parts": [{"text": f"질문: {message}\n\n검색된 데이터:\n{context or '검색 결과 없음'}"}],
        })
        response = httpx.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{settings.gemini_model}:generateContent",
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": settings.gemini_api_key,
            },
            json={
                "systemInstruction": {
                    "parts": [{
                        "text": (
                            "너는 Soulrip 서울 여행 도우미다. 반드시 제공된 데이터 문맥만 근거로 답하고, "
                            "문맥에 없는 영업시간·가격·축제 날짜를 추측하지 않는다. 검색 결과가 없으면 모른다고 답한다. "
                            "답변에 사용한 장소명은 제공된 표기를 그대로 쓴다. "
                            f"Answer concisely in {LANGUAGE_NAMES.get(language, 'Korean')}."
                        )
                    }]
                },
                "contents": contents,
            },
            timeout=30.0,
        )
        response.raise_for_status()
        payload = response.json()
        answer = "".join(
            part.get("text", "")
            for part in payload.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [])
        ).strip() or fallback
        used_ai = True
    except Exception:
        answer = fallback
        used_ai = False

    return ChatResponse(
        answer=answer,
        sources=sources,
        suggestions=["혼자 걷기 좋은 곳", "이번 달 축제", "종로구 문화시설"],
        used_ai=used_ai,
    )
