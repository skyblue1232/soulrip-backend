from fastapi import APIRouter, Depends, HTTPException, status
import httpx
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.ai_insight import TodayInsightResponse
from app.services.ai_insight_service import ai_insight_service


router = APIRouter(
    prefix="/ai-insights",
    tags=["AI Insights"],
)


@router.post(
    "/today",
    response_model=TodayInsightResponse,
    status_code=status.HTTP_200_OK,
)
async def create_today_insight(
    db: Session = Depends(get_db),
) -> TodayInsightResponse:
    try:
        return await ai_insight_service.create_today_insight(db)

    except httpx.RequestError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Gemini 서버에 연결할 수 없습니다.",
        ) from error

    except httpx.HTTPStatusError as error:
        response_status = error.response.status_code
        raise HTTPException(
            status_code=(status.HTTP_429_TOO_MANY_REQUESTS if response_status == 429 else status.HTTP_502_BAD_GATEWAY),
            detail=(
                "Gemini API 요청 중 오류가 발생했습니다. "
                f"status={response_status}"
            ),
        ) from error

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    except Exception as error:
        print("AI insight error:", repr(error))

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI 인사이트 생성 중 오류가 발생했습니다.",
        ) from error
