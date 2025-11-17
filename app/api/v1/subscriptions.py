# app/api/v1/subscriptions.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.api.v1.admin_auth import get_current_user
from app.models.admin_user import AdminUser
from app.models.institution import Institution
from app.models.subscription import Subscription
from app.services.stripe_service import stripe_service
from app.core.config import settings

router = APIRouter(prefix="/admin/subscriptions", tags=["subscriptions"])


@router.post("/create-checkout")
async def create_checkout_session(
    current_user: AdminUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a Stripe checkout session for premium subscription"""

    # Get entity name based on type
    if current_user.entity_type == "institution":
        query = select(Institution).where(Institution.id == current_user.entity_id)
        result = await db.execute(query)
        entity = result.scalar_one_or_none()
        entity_name = entity.name if entity else "Institution"
    elif current_user.entity_type == "scholarship":
        # Import Scholarship model if not already imported
        from app.models.scholarship import Scholarship

        query = select(Scholarship).where(Scholarship.id == current_user.entity_id)
        result = await db.execute(query)
        entity = result.scalar_one_or_none()
        entity_name = entity.title if entity else "Scholarship"
    else:
        entity_name = "Organization"

    # Create checkout session with entity_type
    session = stripe_service.create_checkout_session(
        customer_email=current_user.email,
        entity_id=current_user.entity_id,
        entity_name=entity_name,
        entity_type=current_user.entity_type,  # ✅ NEW: Pass entity_type
        success_url=f"{settings.FRONTEND_URL}/admin/subscription/success",
        cancel_url=f"{settings.FRONTEND_URL}/admin/subscription/cancel",
    )

    return {"checkout_url": session["url"], "session_id": session["session_id"]}


@router.get("/pricing")
async def get_pricing_info(current_user: AdminUser = Depends(get_current_user)):
    """Get pricing information for current user's entity type"""

    # Determine price based on entity type
    if current_user.entity_type == "scholarship":
        price_cents = 1999  # $19.99 for scholarships
        price_monthly = "$19.99"
    else:
        price_cents = 3999  # $39.99 for institutions
        price_monthly = "$39.99"

    return {
        "entity_type": current_user.entity_type,
        "price_cents": price_cents,
        "price_monthly": price_monthly,
        "trial_days": 30,
    }


@router.get("/current")
async def get_current_subscription(
    current_user: AdminUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current subscription status"""

    query = select(Subscription).where(
        Subscription.entity_type == current_user.entity_type,
        Subscription.entity_id == current_user.entity_id,
    )
    result = await db.execute(query)
    subscription = result.scalar_one_or_none()

    if not subscription:
        return {
            "status": "none",
            "plan_tier": "free",
            "message": "No active subscription",
        }

    # TEMPORARILY DISABLED FOR TESTING - Using database values only
    # Uncomment this section to use Stripe as the source of truth
    # if subscription.stripe_subscription_id:
    #     try:
    #         stripe_sub = stripe_service.get_subscription(
    #             subscription.stripe_subscription_id
    #         )
    #         return {
    #             "status": subscription.status,
    #             "plan_tier": subscription.plan_tier,
    #             "current_period_start": stripe_sub.get("current_period_start"),
    #             "current_period_end": stripe_sub.get("current_period_end"),
    #             "cancel_at_period_end": stripe_sub.get("cancel_at_period_end"),
    #             "trial_end": stripe_sub.get("trial_end"),
    #         }
    #     except Exception as e:
    #         print(f"Warning: Could not fetch from Stripe: {e}")
    #         # Fall through to use database values

    # Return database values (convert to Unix timestamps)
    return {
        "status": subscription.status,
        "plan_tier": subscription.plan_tier,
        "current_period_start": (
            int(subscription.current_period_start.timestamp())
            if subscription.current_period_start
            else None
        ),
        "current_period_end": (
            int(subscription.current_period_end.timestamp())
            if subscription.current_period_end
            else None
        ),
        "cancel_at_period_end": subscription.cancel_at_period_end,
        "trial_end": (
            int(subscription.trial_end_date.timestamp())
            if subscription.trial_end_date
            else None
        ),
    }


@router.post("/cancel")
async def cancel_subscription(
    current_user: AdminUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Cancel subscription at end of period"""

    query = select(Subscription).where(
        Subscription.entity_type == current_user.entity_type,
        Subscription.entity_id == current_user.entity_id,
    )
    result = await db.execute(query)
    subscription = result.scalar_one_or_none()

    if not subscription or not subscription.stripe_subscription_id:
        raise HTTPException(status_code=404, detail="No active subscription found")

    # Cancel in Stripe
    result = stripe_service.cancel_subscription(subscription.stripe_subscription_id)

    # Update local database
    subscription.cancel_at_period_end = True
    await db.commit()

    return {
        "message": "Subscription will be canceled at end of period",
        "current_period_end": result["current_period_end"],
    }


@router.get("/portal")
async def get_customer_portal(
    current_user: AdminUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get Stripe customer portal URL"""

    query = select(Subscription).where(
        Subscription.entity_type == current_user.entity_type,
        Subscription.entity_id == current_user.entity_id,
    )
    result = await db.execute(query)
    subscription = result.scalar_one_or_none()

    if not subscription or not subscription.stripe_customer_id:
        raise HTTPException(
            status_code=404, detail="No subscription found. Please subscribe first."
        )

    # Create portal session
    portal = stripe_service.create_customer_portal_session(
        customer_id=subscription.stripe_customer_id,
        return_url=f"{settings.FRONTEND_URL}/admin/dashboard",
    )

    return {"portal_url": portal["url"]}


@router.post("/cancel")
async def cancel_subscription(
    current_user: AdminUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Cancel subscription at end of period"""

    query = select(Subscription).where(
        Subscription.entity_type == current_user.entity_type,
        Subscription.entity_id == current_user.entity_id,
    )
    result = await db.execute(query)
    subscription = result.scalar_one_or_none()

    if not subscription or not subscription.stripe_subscription_id:
        raise HTTPException(status_code=404, detail="No active subscription found")

    # Cancel in Stripe
    result = stripe_service.cancel_subscription(subscription.stripe_subscription_id)

    # Update local database
    subscription.cancel_at_period_end = True
    await db.commit()

    return {
        "message": "Subscription will be canceled at end of period",
        "current_period_end": result["current_period_end"],
    }


@router.get("/portal")
async def get_customer_portal(
    current_user: AdminUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get Stripe customer portal URL"""

    query = select(Subscription).where(
        Subscription.entity_type == current_user.entity_type,
        Subscription.entity_id == current_user.entity_id,
    )
    result = await db.execute(query)
    subscription = result.scalar_one_or_none()

    if not subscription or not subscription.stripe_customer_id:
        raise HTTPException(
            status_code=404, detail="No subscription found. Please subscribe first."
        )

    # Create portal session
    portal = stripe_service.create_customer_portal_session(
        customer_id=subscription.stripe_customer_id,
        return_url=f"{settings.FRONTEND_URL}/admin/dashboard",
    )

    return {"portal_url": portal["url"]}
