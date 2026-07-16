# Soulrip FastAPI Backend

서울 지역 JSON 7종을 SQLite에 적재하고 Vue 프론트엔드에 REST API로 제공하는 백엔드입니다.

## 1. 포함 기능

- 관광지·문화시설·레포츠·쇼핑·숙박 통합 검색/상세/지도/주변 검색
- 축제 목록·상세·월별 캘린더·날짜별 조회
- 여행코스 목록·상세·간단 추천
- 익명 커뮤니티 게시글 CRUD, 비밀번호 확인, 댓글, 좋아요
- 브라우저 `clientId` 기반 여행 기록 CRUD
- 제공 데이터와 게시글 검색 기반 챗봇 `POST /api/v1/chat`
- 오늘의 인사이트 임시 API
- Swagger 문서 `/docs`

## 2. 중요한 데이터 제한

업로드된 `서울_축제공연행사.json`에는 `createdtime`, `modifiedtime`만 있고 실제 행사 `startDate`, `endDate`는 없습니다. 두 값은 데이터 생성·수정 시각이므로 축제 일정으로 사용하면 안 됩니다.

달력을 사용하려면 `data/festival_schedules.json`에 축제 `contentId`별 시작일·종료일을 보완한 뒤 다시 시드하세요. 형식은 `data/festival_schedules.example.json`을 참고합니다.

또한 현재 업로드 데이터에는 음식점(contentTypeId 39) 파일이 없습니다. 맛집 기능을 실제 데이터로 제공하려면 `data/서울_음식점.json`을 추가하면 시드 스크립트가 자동 인식합니다.

## 3. 실행

```bash
cd soulrip-backend
python -m venv .venv

# Windows Git Bash
source .venv/Scripts/activate

pip install -r requirements.txt
cp .env.example .env
python -m scripts.seed_data
uvicorn app.main:app --reload
```

- API: `http://127.0.0.1:8000/api/v1`
- Swagger: `http://127.0.0.1:8000/docs`

## 4. 프론트엔드 연결

`.env` 또는 `.env.local`:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
```

기존 프론트 호출은 다음과 연결됩니다.

- `api.getPlaces()` → `GET /places`
- `api.getFestivals(month)` → `GET /festivals?month=7&year=2026`
- `api.getPosts({ limit: 4 })` → `GET /posts?limit=4`

## 5. 주요 API

### 장소

- `GET /api/v1/places`
- `GET /api/v1/places/map`
- `GET /api/v1/places/nearby`
- `GET /api/v1/places/{contentId}`

### 축제

- `GET /api/v1/festivals`
- `GET /api/v1/festivals/calendar?year=2026&month=7`
- `GET /api/v1/festivals/on-date?date=2026-07-14`
- `GET /api/v1/festivals/{contentId}`
- `POST /api/v1/festivals/{contentId}/schedules` (`X-Admin-Key` 필요)

### 코스

- `GET /api/v1/courses`
- `GET /api/v1/courses/{contentId}`
- `POST /api/v1/courses/recommend`

### 커뮤니티

- `GET /api/v1/posts`
- `POST /api/v1/posts`
- `GET /api/v1/posts/{id}`
- `PATCH /api/v1/posts/{id}`
- `DELETE /api/v1/posts/{id}?password=...`
- `POST /api/v1/posts/{id}/verify-password`
- `POST /api/v1/posts/{id}/likes`
- `GET /api/v1/posts/{id}/comments`
- `POST /api/v1/posts/{id}/comments`
- `PATCH /api/v1/posts/comments/{commentId}`
- `DELETE /api/v1/posts/comments/{commentId}?password=...`

### 여행 기록

- `GET /api/v1/travel-records?clientId=...`
- `POST /api/v1/travel-records`
- `GET /api/v1/travel-records/{id}?clientId=...`
- `PATCH /api/v1/travel-records/{id}`
- `DELETE /api/v1/travel-records/{id}?clientId=...`

### 챗봇·기타

- `POST /api/v1/chat`
- `GET /api/v1/insights/today`
- `GET /api/v1/meta/categories`
- `GET /api/v1/meta/districts`
- `GET /api/v1/meta/stats`
- `GET /api/v1/health`

## 6. 커뮤니티 비밀번호

과제 요구사항에 맞춰 현재 코드는 게시글·댓글 수정용 비밀번호를 평문 저장/비교합니다. 실제 운영 서비스에서는 반드시 해시 저장으로 변경해야 합니다.
