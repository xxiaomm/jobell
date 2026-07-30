import logging
import smtplib
from email.message import EmailMessage

from shared.settings import settings

logger = logging.getLogger("jobell.notifier")


def send_job_alert_email(to_email: str, job) -> None:
    message = EmailMessage()
    message["Subject"] = f"[Jobell] New job: {job.title} @ {job.company.name}"
    message["From"] = settings.email_from
    message["To"] = to_email
    message.set_content(
        f"A new job matching your subscription was just posted:\n\n"
        f"{job.title} - {job.company.name}\n"
        f"Location: {job.location or 'n/a'}\n"
        f"Level: {job.level.value}\n\n"
        f"Apply here: {job.url}\n"
    )

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as smtp:
        if settings.smtp_use_tls:
            smtp.starttls()
        if settings.smtp_user:
            smtp.login(settings.smtp_user, settings.smtp_password or "")
        smtp.send_message(message)

    logger.info("Sent job alert email to %s for job %s", to_email, job.id)
