import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from src.celery_app import celery_app
from src.config import settings
import logging

logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    name="send_authentication_email",
    queue="user_authentication",
    max_retries=5,
    default_retry_delay=60,
    rate_limit="10/m",
)
def send_authentication_email(self, data: dict):
    """
    Отправка кода для подтверждения пользователя
    """
    try:
        message = MIMEMultipart("alternative")
        message["From"] = settings.email.user
        message["To"] = data["email"]
        message["Subject"] = "Подтверждение регистрации"

        html_content = f"""
        <html>
            <body>
                <h2>Добрый день, {data['first_name']}!</h2>
                <p>Для получения доступа введите следующий код:</p>
                <p style="font-size: 20px; text-align: center; font-weight: bold; padding: 10px; background-color: #f0f0f0;">
                    {data['code']}
                </p>
                <p>Код действителен в течение 5 минут.</p>
                <p>Хорошего дня!</p>
            </body>
        </html>
        """
        message.attach(MIMEText(html_content, "html"))

        def send_sync():
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(
                settings.email.host, settings.email.port, context=context
            ) as server:
                if settings.email.user:
                    server.login(settings.email.user, settings.email.password)
                server.send_message(message)
                logger.info(f"Email sent successfully to {data['email']}")

        send_sync()

        return {"status": "success", "email": data["email"], "task_id": self.request.id}

    except smtplib.SMTPException as e:
        logger.error(f"SMTP error for {data['email']}: {e}")
        raise self.retry(
            exc=e,
            countdown=60 * (self.request.retries + 1),
        )
    except Exception as e:
        logger.error(f"Unexpected error for {data['email']}: {e}")
        raise self.retry(exc=e)
