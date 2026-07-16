from app.schemas.common import CamelModel, PaginationMeta


class PlaceOut(CamelModel):
    id: int
    content_id: str
    content_type_id: int
    content_type: str
    title: str
    name: str
    address: str
    address_detail: str
    district: str | None
    zipcode: str
    phone: str
    longitude: float | None
    latitude: float | None
    map_level: int | None
    image_url: str
    thumbnail_url: str
    category: str
    tags: list[str]
    solo_score: int | None
    is_featured: bool


class PlaceListResponse(CamelModel):
    items: list[PlaceOut]
    meta: PaginationMeta


class PlaceMapOut(CamelModel):
    id: int
    content_id: str
    title: str
    category: str
    longitude: float
    latitude: float
    image_url: str
    district: str | None


class PlaceMapResponse(CamelModel):
    items: list[PlaceMapOut]
    total: int


class NearbyPlaceOut(PlaceOut):
    distance_km: float


class NearbyPlaceResponse(CamelModel):
    items: list[NearbyPlaceOut]
    total: int
