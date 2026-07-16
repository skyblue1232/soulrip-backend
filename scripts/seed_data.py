from pathlib import Path

from sqlalchemy import func, select

from app.db.database import Base, SessionLocal, engine
from app.db.models import Location, Post
from app.services.importer import import_festival_schedules, import_locations

BASE_DIR = Path(__file__).resolve().parents[1]


def find_data_dir() -> Path:
    """Find the directory containing the downloaded Seoul content datasets."""
    candidates = [
        BASE_DIR / "data",
        BASE_DIR.parents[1] / "data",
    ]
    for candidate in candidates:
        if any(candidate.glob("서울_*.json")):
            return candidate
    return candidates[0]


DATA_DIR = find_data_dir()


def seed_sample_posts(db):
    count = db.scalar(select(func.count()).select_from(Post)) or 0
    if count:
        return
    db.add_all(
        [
            Post(
                type="SOLO_MEAL",
                title="혼밥하기 편한 광장시장 메뉴 추천해요",
                content="바 좌석이나 서서 먹는 메뉴가 많아서 혼자 방문하기 부담이 적었어요.",
                nickname="서울산책러",
                edit_password="1234",
                tags_json='["혼밥", "광장시장", "추천"]',
            ),
            Post(
                type="COMPANION",
                title="주말 전시 같이 보실 분 있나요?",
                content="토요일 오후에 종로구 문화시설을 둘러볼 예정입니다.",
                nickname="익명여행자",
                edit_password="1234",
                tags_json='["전시", "동행", "종로"]',
            ),
        ]
    )
    db.commit()


def main():
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        location_result = import_locations(db, DATA_DIR)
        schedule_result = import_festival_schedules(db, DATA_DIR)
        seed_sample_posts(db)
        total = db.scalar(select(func.count()).select_from(Location)) or 0
        print({
            "locations": location_result,
            "festivalSchedules": schedule_result,
            "totalLocations": total,
        })


if __name__ == "__main__":
    main()
