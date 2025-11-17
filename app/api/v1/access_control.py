# app/api/v1/access_control.py
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from app.core.database import get_db
from app.api.v1.admin_auth import get_current_user
from app.models.admin_user import AdminUser
from app.models.subscription import Subscription


class AccessLevel:
    """Access levels for different features"""

    FREE = "free"
    TRIAL = "trial"
    PREMIUM = "premium"


async def check_subscription_access(
    current_user: AdminUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Check if user has active subscription or valid trial

    Returns:
        dict with access info:
        {
            "has_access": bool,
            "access_level": "free" | "trial" | "premium",
            "days_remaining": int | None,
            "trial_expired": bool,
            "needs_payment": bool
        }
    """

    # Check for subscription
    query = select(Subscription).where(
        Subscription.entity_type == current_user.entity_type,
        Subscription.entity_id == current_user.entity_id,
    )
    result = await db.execute(query)
    subscription = result.scalar_one_or_none()

    # No subscription at all
    if not subscription:
        return {
            "has_access": False,
            "access_level": AccessLevel.FREE,
            "days_remaining": None,
            "trial_expired": False,
            "needs_payment": True,
            "message": "Please subscribe to access premium features",
        }

    # Has active paid subscription
    if subscription.status == "active" and subscription.plan_tier == "premium":
        return {
            "has_access": True,
            "access_level": AccessLevel.PREMIUM,
            "days_remaining": None,
            "trial_expired": False,
            "needs_payment": False,
            "message": "Premium subscription active",
        }

    # On trial
    if subscription.status == "trialing" and subscription.trial_end_date:
        now = datetime.utcnow()
        trial_end = subscription.trial_end_date

        # Trial still active
        if trial_end > now:
            days_remaining = (trial_end - now).days
            return {
                "has_access": True,
                "access_level": AccessLevel.TRIAL,
                "days_remaining": days_remaining,
                "trial_expired": False,
                "needs_payment": False,
                "message": f"Trial active - {days_remaining} days remaining",
            }

        # Trial expired
        else:
            return {
                "has_access": False,
                "access_level": AccessLevel.FREE,
                "days_remaining": 0,
                "trial_expired": True,
                "needs_payment": True,
                "message": "Trial expired - please subscribe to continue",
            }

    # Subscription in bad state (past_due, canceled, etc)
    if subscription.status in ["past_due", "canceled", "unpaid"]:
        return {
            "has_access": False,
            "access_level": AccessLevel.FREE,
            "days_remaining": None,
            "trial_expired": True,
            "needs_payment": True,
            "message": "Subscription issue - please update payment",
        }

    # Default: no access
    return {
        "has_access": False,
        "access_level": AccessLevel.FREE,
        "days_remaining": None,
        "trial_expired": False,
        "needs_payment": True,
        "message": "Please subscribe to access premium features",
    }


async def require_premium_access(
    access_info: dict = Depends(check_subscription_access),
):
    """
    Dependency to require premium or trial access
    Raises 403 if user doesn't have access
    """
    if not access_info["has_access"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "Premium subscription required",
                "message": access_info["message"],
                "trial_expired": access_info["trial_expired"],
                "needs_payment": access_info["needs_payment"],
            },
        )
    return access_info


async def require_active_subscription(
    access_info: dict = Depends(check_subscription_access),
):
    """
    Dependency to require active paid subscription (no trial)
    Raises 403 if user is on trial or has no subscription
    """
    if access_info["access_level"] != AccessLevel.PREMIUM:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "Active subscription required",
                "message": "This feature requires an active paid subscription",
                "on_trial": access_info["access_level"] == AccessLevel.TRIAL,
            },
        )
    return access_info
