from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Location, Post

router = APIRouter(prefix="/meta", tags=["meta"])


@router.get("/categories")
def categories(db: Session = Depends(get_db)):
    rows = db.execute(
        select(Location.content_type_id, Location.content_type, func.count(Location.id))
        .group_by(Location.content_type_id, Location.content_type)
        .order_by(Location.content_type_id.asc())
    ).all()
    return {
        "items": [
            {"contentTypeId": content_type_id, "name": content_type, "count": count}
            for content_type_id, content_type, count in rows
        ]
    }


@router.get("/districts")
def districts(db: Session = Depends(get_db)):
    rows = db.execute(
        select(Location.district, func.count(Location.id))
        .where(Location.district.is_not(None))
        .group_by(Location.district)
        .order_by(Location.district.asc())
    ).all()
    return {"items": [{"district": district, "count": count} for district, count in rows]}


@router.get("/stats")
def stats(db: Session = Depends(get_db)):
    return {
        "places": db.scalar(select(func.count()).select_from(Location).where(Location.content_type_id.not_in([15, 25]))) or 0,
        "festivals": db.scalar(select(func.count()).select_from(Location).where(Location.content_type_id == 15)) or 0,
        "courses": db.scalar(select(func.count()).select_from(Location).where(Location.content_type_id == 25)) or 0,
        "posts": db.scalar(select(func.count()).select_from(Post)) or 0,
    }
