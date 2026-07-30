from datetime import datetime

from pydantic import BaseModel, ConfigDict

from shared.models import DegreeRequirement, JobLevel


class SubscriptionCreate(BaseModel):
    title_keyword: str | None = None
    level: JobLevel | None = None
    location: str | None = None
    min_years: int | None = None
    degree: DegreeRequirement | None = None


class SubscriptionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title_keyword: str | None = None
    level: JobLevel | None = None
    location: str | None = None
    min_years: int | None = None
    degree: DegreeRequirement | None = None
    created_at: datetime
