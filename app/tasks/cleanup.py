# app/tasks/cleanup.py

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timezone
from sqlalchemy import update
from app.core.database import get_db
from app.models.invitation_code import InvitationCode, InvitationStatus
import logging

logger = logging.getLogger(__name__)


async def expire_old_invitations():
    """Run daily to auto-expire old invitations"""
    try:
        async for db in get_db():
            query = (
                update(InvitationCode)
                .where(
                    InvitationCode.status == InvitationStatus.PENDING,
                    InvitationCode.expires_at < datetime.now(timezone.utc),
                )
                .values(status=InvitationStatus.EXPIRED)
            )

            result = await db.execute(query)
            await db.commit()

            logger.info(f"Expired {result.rowcount} old invitations")
    except Exception as e:
        logger.error(f"Error expiring invitations: {e}")


def start_scheduler():
    """Initialize and start the scheduler"""
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        expire_old_invitations, "cron", hour=2, minute=0
    )  # Run at 2 AM daily
    scheduler.start()
    logger.info("Scheduler started - will expire invitations daily at 2 AM")
    return scheduler
