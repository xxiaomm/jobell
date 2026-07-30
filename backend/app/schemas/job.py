from datetime import datetime

from pydantic import BaseModel, ConfigDict

from shared.models import DegreeRequirement, JobLevel


class CompanyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    careers_url: str | None = None


class JobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    location: str | None = None
    department: str | None = None
    level: JobLevel
    min_years_experience: int | None = None
    degree_requirement: DegreeRequirement
    url: str
    posted_at: datetime | None = None
    first_seen_at: datetime
    company: CompanyOut


class JobListOut(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[JobOut]
