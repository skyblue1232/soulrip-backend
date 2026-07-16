from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Location
from app.schemas.insight import InsightItem, InsightResponse

router = APIRouter(prefix="/insights", tags=["insights"])


@router.get("/today", response_model=InsightResponse)
def today_insights(db: Session = Depends(get_db)) -> InsightResponse:
    place = db.scalar(
        select(Location)
        .where(
            Location.content_type_id.in_([12, 14, 28]),
            Location.first_image != "",
        )
        .order_by(func.random())
        .limit(1)
    )

    items = [
        InsightItem(
            id="weather",
            category="오늘의 날씨",
            title="날씨 API 연동 전",
            description="현재 화면에서는 임시 데이터로 표시하고 있어요.",
            icon="☀️",
            tone="weather",
            image_url="",
            is_mock=True,
        ),
        InsightItem(
            id="time",
            category="AI 추천 시간대",
            title="오후 4시 - 7시",
            description="도보 이동과 야경을 함께 즐기기 좋은 시간대예요.",
            icon="◷",
            tone="time",
            image_url="",
            is_mock=True,
        ),
    ]
    if place:
        items.append(
            InsightItem(
                id="place",
                category="혼자 가기 좋은 오늘의 장소",
                title=place.title,
                description=place.addr1 or "서울의 추천 장소를 확인해 보세요.",
                icon="☕",
                tone="place",
                image_url=place.first_image,
                content_id=place.content_id,
            )
        )
    items.append(
        InsightItem(
            id="tip",
            category="오늘의 혼행 팁",
            title="대중교통 + 도보 코스를 추천해요.",
            description="한 지역을 중심으로 묶으면 이동 시간을 줄일 수 있어요.",
            icon="♡",
            tone="tip",
            image_url="",
            is_mock=True,
        )
    )
    return InsightResponse(date=date.today().isoformat(), items=items)
