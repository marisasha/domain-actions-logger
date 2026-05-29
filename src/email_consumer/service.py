import asyncio
from src.logger import logger
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import ssl

from faststream.rabbit import RabbitBroker
from src.email_consumer.config import settings

RABBITMQ_URL = settings.rabbit.get_rabbitmq_url()
broker = RabbitBroker(RABBITMQ_URL)


@broker.subscriber("email_verification")
async def send_accept_token(data: dict):
    """Отправка email с подтверждением регистрации"""
    try:

        message = MIMEMultipart("alternative")
        message["From"] = settings.email.user
        message["To"] = data["email"]
        message["Subject"] = "Подтверждение регистрации"

        verification_url = f"http://127.0.0.1:8000/api/user/verify-code?id={data['id']}&code={data['token']}&is_email_verification=true"

        html_content = f"""
        <html>
        <body>
            <h2>Добро пожаловать!</h2>
            <p>Для подтверждения регистрации перейдите по ссылке:</p>
            <a href="{verification_url}">{verification_url}</a>
            <p>Спасибо за регистрацию!</p>
        </body>
        </html>
        """

        message.attach(MIMEText(html_content, "html"))

        def send():
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(
                settings.email.host, settings.email.port, context=context
            ) as server:
                if settings.email.user:
                    server.login(settings.email.user, settings.email.password)
                server.send_message(message)

        await asyncio.to_thread(send)

        logger.info(f"Email sent to {data['email']}")

    except Exception as e:
        logger.error(f"Failed to send email: {e}")


@broker.subscriber("move_accept")
async def send_accept_code(data: dict):
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
                <p>Хорошего дня!</p>
            </body>
        </html>
        """
        message.attach(MIMEText(html_content, "html"))

        def send():
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(
                settings.email.host, settings.email.port, context=context
            ) as server:
                if settings.email.user:
                    server.login(settings.email.user, settings.email.password)
                server.send_message(message)

        await asyncio.to_thread(send)

    except Exception as e:
        logger.error(f"Failed to send email: {e}")


async def main() -> None:
    async with broker:
        await broker.start()
        logger.info(RABBITMQ_URL)
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
