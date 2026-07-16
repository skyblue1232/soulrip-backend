from app.schemas.common import CamelModel


class InsightItem(CamelModel):
    id: str
    category: str
    title: str
    description: str
    icon: str
    tone: str
    image_url: str
    content_id: str | None = None
    is_mock: bool = False


class InsightResponse(CamelModel):
    date: str
    items: list[InsightItem]
