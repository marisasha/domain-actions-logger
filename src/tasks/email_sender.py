import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from src.celery_app import celery_app
from src.config import settings
from src.logger import logger


@celery_app.task(
    bind=True,
    name="send_email",
    queue="email_sender",
    max_retries=5,
    default_retry_delay=60,
    rate_limit="10/m",
)
def send_email(self, data: dict):
    """
    Отправка сообщения на почту с разделением критических и временных ошибок.
    """
    try:
        message = MIMEMultipart("alternative")
        message["From"] = settings.email.user
        message["To"] = data["email"]
        message["Subject"] = data["subject"]
        message.attach(MIMEText(data["message"], "html"))

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(
            settings.email.host, settings.email.port, context=context
        ) as server:
            if settings.email.user:
                server.login(settings.email.user, settings.email.password)
            server.send_message(message)
            logger.info(f"Email sent successfully to {data['email']}")

        return {"status": "success", "email": data["email"], "task_id": self.request.id}

    except smtplib.SMTPDataError as e:
        if e.smtp_code == 550:
            logger.error(
                f"Permanent SMTP error (User not found) for {data['email']}: {e}"
            )
            return {
                "status": "failed_permanent",
                "email": data["email"],
                "error": str(e),
            }

        logger.error(f"SMTP Data error for {data['email']}: {e}")
        raise self.retry(exc=e, countdown=60 * (self.request.retries + 1))

    except smtplib.SMTPException as e:
        logger.error(f"Temporary SMTP error for {data['email']}: {e}")
        raise self.retry(exc=e, countdown=60 * (self.request.retries + 1))

    except Exception as e:
        logger.error(f"Unexpected error for {data['email']}: {e}")
        raise
