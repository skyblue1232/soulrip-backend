from datetime import date, datetime

from pydantic import Field

from app.schemas.common import CamelModel
from app.schemas.location import PlaceOut


class TravelRecordItemInput(CamelModel):
    content_id: str
    note: str = ""


class TravelRecordCreate(CamelModel):
    client_id: str = Field(min_length=1, max_length=100)
    title: str = Field(min_length=1, max_length=200)
    memo: str = ""
    visited_at: date
    is_public: bool = False
    items: list[TravelRecordItemInput] = []


class TravelRecordUpdate(CamelModel):
    client_id: str
    title: str | None = Field(default=None, min_length=1, max_length=200)
    memo: str | None = None
    visited_at: date | None = None
    is_public: bool | None = None
    items: list[TravelRecordItemInput] | None = None


class TravelRecordItemOut(CamelModel):
    id: int
    stop_order: int
    note: str
    place: PlaceOut


class TravelRecordOut(CamelModel):
    id: int
    client_id: str
    title: str
    memo: str
    visited_at: date
    is_public: bool
    items: list[TravelRecordItemOut]
    created_at: datetime
    updated_at: datetime


class TravelRecordListResponse(CamelModel):
    items: list[TravelRecordOut]
    total: int
