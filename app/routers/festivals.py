import calendar
import math
from datetime import date, datetime, time, timedelta

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.database import get_db
from app.db.models import FestivalSchedule, Location
from app.schemas.common import MessageResponse, PaginationMeta
from app.schemas.festival import (
    CalendarEventOut,
    FestivalCalendarResponse,
    FestivalListResponse,
    FestivalOut,
    FestivalScheduleCreate,
)

router = APIRouter(prefix="/festivals", tags=["festivals"])
settings = get_settings()


def _festival_out(location: Location, schedule: FestivalSchedule | None) -> FestivalOut:
    fallback_date = location.source_modified_at.date() if location.source_modified_at else None
    return FestivalOut(
        id=location.id,
        content_id=location.content_id,
        name=location.title,
        title=location.title,
        start_date=schedule.start_date if schedule else fallback_date,
        end_date=schedule.end_date if schedule else fallback_date,
        location=location.addr1,
        address_detail=location.addr2,
        district=location.district,
        category=(schedule.category if schedule and schedule.category else location.content_type),
        description=(schedule.description if schedule and schedule.description else location.description or ""),
        image_url=location.first_image,
        thumbnail_url=location.first_image2 or location.first_image,
        longitude=location.map_x,
        latitude=location.map_y,
        phone=location.tel,
        date_available=schedule is not None or fallback_date is not None,
    )


def _month_range(year: int, month: int) -> tuple[date, date]:
    last_day = calendar.monthrange(year, month)[1]
    return date(year, month, 1), date(year, month, last_day)


@router.get("", response_model=FestivalListResponse)
def list_festivals(
    month: int | None = Query(default=None, ge=1, le=12),
    year: int = Query(default=date.today().year, ge=2000, le=2100),
    q: str | None = None,
    district: str | None = None,
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> FestivalListResponse:
    filters = [Location.content_type_id == 15]
    if q:
        like = f"%{q.strip()}%"
        filters.append(or_(Location.title.ilike(like), Location.addr1.ilike(like)))
    if district:
        filters.append(Location.district == district)

    stmt = select(Location).where(*filters)
    count_stmt = select(func.count(func.distinct(Location.id))).select_from(Location).where(*filters)

    if month is not None:
        start, end = _month_range(year, month)
        schedule_in_month = (
            select(FestivalSchedule.id)
            .where(
                FestivalSchedule.location_id == Location.id,
                FestivalSchedule.start_date <= end,
                FestivalSchedule.end_date >= start,
            )
            .exists()
        )
        has_schedule = select(FestivalSchedule.id).where(
            FestivalSchedule.location_id == Location.id
        ).exists()
        modified_start = datetime.combine(start, time.min)
        modified_end = datetime.combine(end + timedelta(days=1), time.min)
        fallback_in_month = (
            ~has_schedule
            & (Location.source_modified_at >= modified_start)
            & (Location.source_modified_at < modified_end)
        )
        month_filter = or_(schedule_in_month, fallback_in_month)
        stmt = stmt.where(month_filter)
        count_stmt = count_stmt.where(month_filter)

    total = db.scalar(count_stmt) or 0
    locations = db.scalars(
        stmt.order_by(Location.source_modified_at.desc().nullslast()).offset((page - 1) * size).limit(size)
    ).all()

    location_ids = [item.id for item in locations]
    schedules = db.scalars(
        select(FestivalSchedule)
        .where(FestivalSchedule.location_id.in_(location_ids))
        .order_by(FestivalSchedule.start_date.asc())
    ).all() if location_ids else []
    schedule_map: dict[int, FestivalSchedule] = {}
    for schedule in schedules:
        schedule_map.setdefault(schedule.location_id, schedule)

    return FestivalListResponse(
        items=[_festival_out(item, schedule_map.get(item.id)) for item in locations],
        meta=PaginationMeta(total=total, page=page, size=size, pages=max(1, math.ceil(total / size))),
    )


@router.get("/calendar", response_model=FestivalCalendarResponse)
def festival_calendar(
    year: int = Query(ge=2000, le=2100),
    month: int = Query(ge=1, le=12),
    db: Session = Depends(get_db),
) -> FestivalCalendarResponse:
    start, end = _month_range(year, month)
    rows = db.execute(
        select(FestivalSchedule, Location)
        .join(Location, FestivalSchedule.location_id == Location.id)
        .where(FestivalSchedule.start_date <= end, FestivalSchedule.end_date >= start)
        .order_by(FestivalSchedule.start_date.asc(), Location.title.asc())
    ).all()
    scheduled_location_ids = {location.id for schedule, location in rows}
    fallback_locations = db.scalars(
        select(Location).where(
            Location.content_type_id == 15,
            Location.source_modified_at >= datetime.combine(start, time.min),
            Location.source_modified_at < datetime.combine(end + timedelta(days=1), time.min),
            ~select(FestivalSchedule.id).where(
                FestivalSchedule.location_id == Location.id
            ).exists(),
        )
    ).all()
    items = [
        CalendarEventOut(
            id=schedule.id,
            festival_id=location.id,
            content_id=location.content_id,
            title=location.title,
            start_date=schedule.start_date,
            end_date=schedule.end_date,
            district=location.district,
            location=location.addr1,
            image_url=location.first_image,
        )
        for schedule, location in rows
    ]
    items.extend(
        CalendarEventOut(
            id=-location.id,
            festival_id=location.id,
            content_id=location.content_id,
            title=location.title,
            start_date=location.source_modified_at.date(),
            end_date=location.source_modified_at.date(),
            district=location.district,
            location=location.addr1,
            image_url=location.first_image,
        )
        for location in fallback_locations
        if location.id not in scheduled_location_ids and location.source_modified_at
    )
    return FestivalCalendarResponse(
        year=year,
        month=month,
        items=items,
    )


@router.get("/on-date", response_model=list[FestivalOut])
def festivals_on_date(
    target_date: date = Query(alias="date"),
    db: Session = Depends(get_db),
) -> list[FestivalOut]:
    rows = db.execute(
        select(FestivalSchedule, Location)
        .join(Location, FestivalSchedule.location_id == Location.id)
        .where(
            FestivalSchedule.start_date <= target_date,
            FestivalSchedule.end_date >= target_date,
        )
        .order_by(Location.title.asc())
    ).all()
    return [_festival_out(location, schedule) for schedule, location in rows]


@router.post("/{content_id}/schedules", response_model=FestivalOut, status_code=201)
def create_schedule(
    content_id: str,
    payload: FestivalScheduleCreate,
    x_admin_key: str | None = Header(default=None, alias="X-Admin-Key"),
    db: Session = Depends(get_db),
) -> FestivalOut:
    if not settings.admin_key or x_admin_key != settings.admin_key:
        raise HTTPException(status_code=403, detail="관리자 키가 올바르지 않습니다.")
    if payload.end_date < payload.start_date:
        raise HTTPException(status_code=400, detail="종료일은 시작일보다 빠를 수 없습니다.")

    location = db.scalar(
        select(Location).where(Location.content_id == content_id, Location.content_type_id == 15)
    )
    if location is None:
        raise HTTPException(status_code=404, detail="축제를 찾을 수 없습니다.")

    schedule = FestivalSchedule(
        location_id=location.id,
        start_date=payload.start_date,
        end_date=payload.end_date,
        category=payload.category,
        description=payload.description,
        source=payload.source,
    )
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return _festival_out(location, schedule)


@router.delete("/schedules/{schedule_id}", response_model=MessageResponse)
def delete_schedule(
    schedule_id: int,
    x_admin_key: str | None = Header(default=None, alias="X-Admin-Key"),
    db: Session = Depends(get_db),
) -> MessageResponse:
    if not settings.admin_key or x_admin_key != settings.admin_key:
        raise HTTPException(status_code=403, detail="관리자 키가 올바르지 않습니다.")
    schedule = db.get(FestivalSchedule, schedule_id)
    if schedule is None:
        raise HTTPException(status_code=404, detail="축제 일정을 찾을 수 없습니다.")
    db.delete(schedule)
    db.commit()
    return MessageResponse(message="축제 일정이 삭제되었습니다.")


@router.get("/{content_id}", response_model=FestivalOut)
def get_festival(content_id: str, db: Session = Depends(get_db)) -> FestivalOut:
    location = db.scalar(
        select(Location).where(Location.content_id == content_id, Location.content_type_id == 15)
    )
    if location is None:
        raise HTTPException(status_code=404, detail="축제를 찾을 수 없습니다.")
    schedule = db.scalar(
        select(FestivalSchedule)
        .where(FestivalSchedule.location_id == location.id)
        .order_by(FestivalSchedule.start_date.asc())
    )
    return _festival_out(location, schedule)
