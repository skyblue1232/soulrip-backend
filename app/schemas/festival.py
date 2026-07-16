from datetime import date

from app.schemas.common import CamelModel, PaginationMeta


class FestivalOut(CamelModel):
    id: int
    content_id: str
    name: str
    title: str
    start_date: date | None
    end_date: date | None
    location: str
    address_detail: str
    district: str | None
    category: str
    description: str
    image_url: str
    thumbnail_url: str
    longitude: float | None
    latitude: float | None
    phone: str
    date_available: bool


class FestivalListResponse(CamelModel):
    items: list[FestivalOut]
    meta: PaginationMeta


class CalendarEventOut(CamelModel):
    id: int
    festival_id: int
    content_id: str
    title: str
    start_date: date
    end_date: date
    district: str | None
    location: str
    image_url: str


class FestivalCalendarResponse(CamelModel):
    year: int
    month: int
    items: list[CalendarEventOut]


class FestivalScheduleCreate(CamelModel):
    start_date: date
    end_date: date
    category: str | None = None
    description: str | None = None
    source: str = "manual"
