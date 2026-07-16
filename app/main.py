from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.db.database import Base, engine
from app.routers import (
    ai_insights,
    chat,
    courses,
    festivals,
    health,
    insights,
    meta,
    places,
    posts,
    travel_records,
)

settings = get_settings()

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="서울 혼행 정보, 축제, 코스, 여행 기록, 익명 커뮤니티, 챗봇 API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix=settings.api_prefix)
app.include_router(meta.router, prefix=settings.api_prefix)
app.include_router(places.router, prefix=settings.api_prefix)
app.include_router(festivals.router, prefix=settings.api_prefix)
app.include_router(courses.router, prefix=settings.api_prefix)
app.include_router(posts.router, prefix=settings.api_prefix)
app.include_router(travel_records.router, prefix=settings.api_prefix)
app.include_router(insights.router, prefix=settings.api_prefix)
app.include_router(ai_insights.router, prefix=settings.api_prefix)
app.include_router(chat.router, prefix=settings.api_prefix)


@app.get("/")
def root():
    return {
        "name": settings.app_name,
        "docs": "/docs",
        "health": f"{settings.api_prefix}/health",
    }