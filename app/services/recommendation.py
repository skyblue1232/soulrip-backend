from math import asin, cos, radians, sin, sqrt

from app.db.models import Location


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    earth_radius = 6371.0
    d_lat = radians(lat2 - lat1)
    d_lon = radians(lon2 - lon1)
    a = sin(d_lat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(d_lon / 2) ** 2
    return earth_radius * 2 * asin(sqrt(a))


def order_nearest(
    candidates: list[Location],
    start_latitude: float | None,
    start_longitude: float | None,
) -> list[Location]:
    if not candidates:
        return []

    remaining = candidates[:]
    if start_latitude is None or start_longitude is None:
        current = remaining.pop(0)
    else:
        current = min(
            remaining,
            key=lambda item: haversine_km(
                start_latitude,
                start_longitude,
                item.map_y or start_latitude,
                item.map_x or start_longitude,
            ),
        )
        remaining.remove(current)

    ordered = [current]
    while remaining:
        next_item = min(
            remaining,
            key=lambda item: haversine_km(
                current.map_y or 37.5665,
                current.map_x or 126.9780,
                item.map_y or 37.5665,
                item.map_x or 126.9780,
            ),
        )
        ordered.append(next_item)
        remaining.remove(next_item)
        current = next_item

    return ordered
