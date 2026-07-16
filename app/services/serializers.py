import json

from app.db.models import Location
from app.schemas.location import PlaceMapOut, PlaceOut

CONTENT_TYPE_LABELS = {
    12: "관광지",
    14: "문화시설",
    15: "축제공연행사",
    25: "여행코스",
    28: "레포츠",
    32: "숙박",
    38: "쇼핑",
    39: "음식점",
}


def parse_tags(value: str | None) -> list[str]:
    if not value:
        return []
    try:
        result = json.loads(value)
        return result if isinstance(result, list) else []
    except json.JSONDecodeError:
        return []


def place_out(location: Location) -> PlaceOut:
    return PlaceOut(
        id=location.id,
        content_id=location.content_id,
        content_type_id=location.content_type_id,
        content_type=location.content_type,
        title=location.title,
        name=location.title,
        address=location.addr1,
        address_detail=location.addr2,
        district=location.district,
        zipcode=location.zipcode,
        phone=location.tel,
        longitude=location.map_x,
        latitude=location.map_y,
        map_level=location.map_level,
        image_url=location.first_image,
        thumbnail_url=location.first_image2 or location.first_image,
        category=CONTENT_TYPE_LABELS.get(location.content_type_id, location.content_type),
        tags=parse_tags(location.tags_json),
        solo_score=location.solo_score,
        is_featured=location.is_featured,
    )


def place_map_out(location: Location) -> PlaceMapOut:
    assert location.map_x is not None and location.map_y is not None
    return PlaceMapOut(
        id=location.id,
        content_id=location.content_id,
        title=location.title,
        category=CONTENT_TYPE_LABELS.get(location.content_type_id, location.content_type),
        longitude=location.map_x,
        latitude=location.map_y,
        image_url=location.first_image,
        district=location.district,
    )
