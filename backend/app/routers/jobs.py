from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.schemas.job import CompanyOut, JobListOut, JobOut
from shared.db import get_db
from shared.models import Company, DegreeRequirement, Job, JobLevel

router = APIRouter(prefix="/api", tags=["jobs"])


@router.get("/jobs", response_model=JobListOut)
def list_jobs(
    title: str | None = Query(None, description="Case-insensitive substring match on job title"),
    level: JobLevel | None = None,
    location: str | None = Query(None, description="Case-insensitive substring match on location"),
    min_years: int | None = Query(None, description="Only jobs requiring at most this many years of experience"),
    degree: DegreeRequirement | None = None,
    posted_after: datetime | None = Query(None, description="Only jobs posted after this timestamp"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> JobListOut:
    stmt = select(Job).options(joinedload(Job.company)).where(Job.is_active.is_(True))

    if title:
        stmt = stmt.where(Job.title.ilike(f"%{title}%"))
    if level:
        stmt = stmt.where(Job.level == level)
    if location:
        stmt = stmt.where(Job.location.ilike(f"%{location}%"))
    if min_years is not None:
        stmt = stmt.where(
            (Job.min_years_experience.is_(None)) | (Job.min_years_experience <= min_years)
        )
    if degree:
        stmt = stmt.where(Job.degree_requirement == degree)
    if posted_after:
        stmt = stmt.where(Job.posted_at >= posted_after)

    total = len(db.execute(stmt).scalars().all())

    stmt = stmt.order_by(Job.posted_at.desc().nullslast()).offset((page - 1) * page_size).limit(page_size)
    items = db.execute(stmt).scalars().all()

    return JobListOut(total=total, page=page, page_size=page_size, items=[JobOut.model_validate(j) for j in items])


@router.get("/jobs/{job_id}", response_model=JobOut)
def get_job(job_id: int, db: Session = Depends(get_db)) -> JobOut:
    job = db.get(Job, job_id, options=[joinedload(Job.company)])
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobOut.model_validate(job)


@router.get("/companies", response_model=list[CompanyOut])
def list_companies(db: Session = Depends(get_db)) -> list[CompanyOut]:
    companies = db.execute(select(Company).order_by(Company.name)).scalars().all()
    return [CompanyOut.model_validate(c) for c in companies]
