import asyncio
from datetime import datetime
from sqlalchemy import select

from src.celery_app import celery_app
from src.logger import logger
from src.user.models import UserModel
from src.domain.models import UserDomainModel, MoveModel
from src.tasks.email_sender import send_email
from src.database import (
    get_celery_session,
)
from src.utils.html_content import get_html_content_for_move_report


def get_or_create_loop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop


@celery_app.task(
    bind=True,
    name="send_report",
    queue="report",
    max_retries=3,
    default_retry_delay=60,
)
def send_report(self):
    loop = get_or_create_loop()
    return loop.run_until_complete(run_send_report(self))


async def run_send_report(self):
    """
    Основная асинхронная логика выполнения задачи.
    """
    try:
        async with get_celery_session() as session:

            users_execute = await session.execute(
                select(UserModel).where(UserModel.is_email_verificated == True)
            )
            users = users_execute.scalars().all()

            if not users:
                logger.warning("No verified users found for report")
                return {"status": "no_users", "sent_count": 0}

            current_hour = datetime.now().hour
            sent_count = 0
            failed_count = 0

            for user in users:
                try:
                    move_count = 0
                    move_list = []
                    user_domains_execute = await session.execute(
                        select(UserDomainModel).where(
                            UserDomainModel.user_id == user.id
                        )
                    )
                    user_domains = user_domains_execute.scalars().all()
                    if not user_domains:
                        continue
                    for ud in user_domains:
                        moves_execute = await session.execute(
                            select(MoveModel).where(MoveModel.user_domain_id == ud.id)
                        )
                        moves = moves_execute.scalars().all()
                        if not moves:
                            continue
                        move_count += len(moves)
                        move_list += moves

                    message_data = {
                        "email": user.email,
                        "subject": "Отчет по кол-во действий на домене ",
                        "message": get_html_content_for_move_report(
                            move_count, move_list, user.first_name
                        ),
                    }

                    send_email.delay(message_data)
                    sent_count += 1
                    logger.info(f"report queued for user: {user.email}")

                except Exception as e:
                    failed_count += 1
                    logger.error(f"Failed to queue report for {user.email}: {e}")

            result = {
                "status": "success",
                "sent_count": sent_count,
                "failed_count": failed_count,
                "total_users": len(users),
                "hour": current_hour,
            }

            logger.info(f"Hourly report completed: {result}")
            return result

    except Exception as e:
        logger.error(f"Error in send_report: {e}")
        raise self.retry(exc=e)
