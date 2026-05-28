import asyncio
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import ssl

from faststream.rabbit import RabbitBroker
from src.email_consumer.config import settings

RABBITMQ_URL = settings.rabbit.get_rabbitmq_url()
broker = RabbitBroker(RABBITMQ_URL)


@broker.subscriber("registration")
async def send_accept_email(data: dict):
    """Отправка email с подтверждением регистрации"""
    try:

        message = MIMEMultipart("alternative")
        message["From"] = settings.email.user
        message["To"] = data["email"]
        message["Subject"] = "Подтверждение регистрации"

        verification_url = (
            f"http://127.0.0.1:8000/api/user/verify-email/{data['token']}"
        )

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
            if settings.email.port == 465:
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(
                    settings.email.host, settings.email.port, context=context
                ) as server:
                    if settings.email.user:
                        server.login(settings.email.user, settings.email.password)
                    server.send_message(message)

        await asyncio.to_thread(send)

        print(f"Email sent to {data['email']}")

    except Exception as e:
        print(f"Failed to send email: {e}")


async def main() -> None:
    async with broker:
        await broker.start()
        print("Брокер стартовал")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
