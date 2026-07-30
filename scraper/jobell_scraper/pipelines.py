import logging

from shared.db import SessionLocal
from shared.models import Company, Job
from shared.redis_client import get_redis
from shared.settings import settings

logger = logging.getLogger(__name__)


class JobPersistencePipeline:
    """Upserts scraped jobs into Postgres and publishes a redis event for
    every job that is genuinely new (not just re-seen on this crawl), so the
    notifier worker only emails subscribers about actual new postings.
    """

    def open_spider(self, spider):
        self.db = SessionLocal()
        self.redis = get_redis()

    def close_spider(self, spider):
        self.db.close()

    def process_item(self, item, spider):
        company = self._get_or_create_company(item)
        self._upsert_job(item, company)
        return item

    def _get_or_create_company(self, item) -> Company:
        company = self.db.query(Company).filter(Company.slug == item["company_slug"]).first()
        if company:
            return company

        company = Company(
            name=item["company_name"],
            slug=item["company_slug"],
            ats_type=item["ats_type"],
            careers_url=item.get("company_careers_url"),
        )
        self.db.add(company)
        self.db.commit()
        self.db.refresh(company)
        return company

    def _upsert_job(self, item, company: Company) -> None:
        job = (
            self.db.query(Job)
            .filter(Job.company_id == company.id, Job.external_id == item["external_id"])
            .first()
        )

        if job:
            job.title = item["title"]
            job.location = item.get("location")
            job.department = item.get("department")
            job.level = item["level"]
            job.min_years_experience = item.get("min_years_experience")
            job.degree_requirement = item["degree_requirement"]
            job.url = item["url"]
            job.posted_at = item.get("posted_at")
            self.db.commit()
            return

        job = Job(
            company_id=company.id,
            external_id=item["external_id"],
            title=item["title"],
            location=item.get("location"),
            department=item.get("department"),
            level=item["level"],
            min_years_experience=item.get("min_years_experience"),
            degree_requirement=item["degree_requirement"],
            url=item["url"],
            posted_at=item.get("posted_at"),
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)

        logger.info("New job found: %s @ %s (id=%s)", job.title, company.name, job.id)
        self.redis.publish(settings.new_jobs_channel, str(job.id))
