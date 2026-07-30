import logging

from sqlalchemy.orm import joinedload

from app.worker.email import send_job_alert_email
from shared.db import SessionLocal
from shared.models import Job, Subscription
from shared.redis_client import get_redis
from shared.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("jobell.notifier")


def subscription_matches(job: Job, sub: Subscription) -> bool:
    if sub.title_keyword and sub.title_keyword.lower() not in job.title.lower():
        return False
    if sub.level and sub.level != job.level:
        return False
    if sub.location and (not job.location or sub.location.lower() not in job.location.lower()):
        return False
    if sub.min_years is not None and job.min_years_experience is not None:
        if job.min_years_experience > sub.min_years:
            return False
    if sub.degree and sub.degree != job.degree_requirement:
        return False
    return True


def notify_for_job(job_id: int) -> None:
    db = SessionLocal()
    try:
        job = db.query(Job).options(joinedload(Job.company)).filter(Job.id == job_id).first()
        if not job:
            logger.warning("Job %s not found, skipping notification", job_id)
            return

        subs = db.query(Subscription).options(joinedload(Subscription.user)).all()
        matched_users: set[str] = set()
        for sub in subs:
            if subscription_matches(job, sub):
                matched_users.add(sub.user.email)

        for email in matched_users:
            try:
                send_job_alert_email(email, job)
            except Exception:
                logger.exception("Failed to send job alert email to %s", email)
    finally:
        db.close()


def run() -> None:
    r = get_redis()
    pubsub = r.pubsub()
    pubsub.subscribe(settings.new_jobs_channel)
    logger.info("Notifier listening on redis channel %r", settings.new_jobs_channel)

    for message in pubsub.listen():
        if message["type"] != "message":
            continue
        try:
            job_id = int(message["data"])
        except (TypeError, ValueError):
            logger.warning("Ignoring malformed message: %r", message["data"])
            continue
        notify_for_job(job_id)


if __name__ == "__main__":
    run()
