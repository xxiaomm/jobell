import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared.db import Base


class AtsType(str, enum.Enum):
    greenhouse = "greenhouse"
    lever = "lever"
    workday = "workday"
    other = "other"


class JobLevel(str, enum.Enum):
    intern = "intern"
    junior = "junior"
    mid = "mid"
    senior = "senior"
    staff = "staff"
    unknown = "unknown"


class DegreeRequirement(str, enum.Enum):
    none = "none"
    bachelor = "bachelor"
    master = "master"
    phd = "phd"


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    ats_type: Mapped[AtsType] = mapped_column(Enum(AtsType, name="ats_type"), default=AtsType.other)
    careers_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    jobs: Mapped[list["Job"]] = relationship(back_populates="company")


class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = (UniqueConstraint("company_id", "external_id", name="uq_job_company_external_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)
    external_id: Mapped[str] = mapped_column(String(255), nullable=False)

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    department: Mapped[str | None] = mapped_column(String(255), nullable=True)
    level: Mapped[JobLevel] = mapped_column(Enum(JobLevel, name="job_level"), default=JobLevel.unknown)
    min_years_experience: Mapped[int | None] = mapped_column(Integer, nullable=True)
    degree_requirement: Mapped[DegreeRequirement] = mapped_column(
        Enum(DegreeRequirement, name="degree_requirement"), default=DegreeRequirement.none
    )
    url: Mapped[str] = mapped_column(String(1024), nullable=False)

    posted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    company: Mapped["Company"] = relationship(back_populates="jobs")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    subscriptions: Mapped[list["Subscription"]] = relationship(back_populates="user")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    title_keyword: Mapped[str | None] = mapped_column(String(255), nullable=True)
    level: Mapped[JobLevel | None] = mapped_column(Enum(JobLevel, name="job_level"), nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    min_years: Mapped[int | None] = mapped_column(Integer, nullable=True)
    degree: Mapped[DegreeRequirement | None] = mapped_column(
        Enum(DegreeRequirement, name="degree_requirement"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="subscriptions")
