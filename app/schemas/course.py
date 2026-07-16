from pydantic import Field

from app.schemas.common import CamelModel, PaginationMeta
from app.schemas.location import PlaceOut


class CourseOut(CamelModel):
    id: int
    content_id: str
    title: str
    image_url: str
    district: str | None
    longitude: float | None
    latitude: float | None
    description: str
    stops: list[PlaceOut] = []


class CourseListResponse(CamelModel):
    items: list[CourseOut]
    meta: PaginationMeta


class CourseRecommendRequest(CamelModel):
    mood: str | None = None
    duration_hours: int = Field(default=4, ge=1, le=12)
    transport: str = "WALK_TRANSIT"
    content_types: list[str] = []
    district: str | None = None
    start_latitude: float | None = None
    start_longitude: float | None = None
    max_stops: int | None = Field(default=None, ge=2, le=8)


class GeneratedCourseOut(CamelModel):
    title: str
    summary: str
    estimated_hours: float
    transport: str
    stops: list[PlaceOut]
