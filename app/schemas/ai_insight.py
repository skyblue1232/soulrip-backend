from pydantic import BaseModel, ConfigDict


class TodayInsightItem(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )

    label: str
    headline: str
    description: str
    image_url: str


class TodayInsightResponse(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )

    today: TodayInsightItem
    time: TodayInsightItem
    place: TodayInsightItem
    tip: TodayInsightItem