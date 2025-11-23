from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import stripe
import json
from app.core.config import settings
from app.core.database import get_db
from app.models.subscription import Subscription
from datetime import datetime

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

stripe.api_key = settings.STRIPE_SECRET_KEY


@router.post("/stripe")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Handle Stripe webhook events"""

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    # Validate signature if webhook secret is configured
    if hasattr(settings, "STRIPE_WEBHOOK_SECRET") and settings.STRIPE_WEBHOOK_SECRET:
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            # Invalid payload
            raise HTTPException(status_code=400, detail="Invalid payload")
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            raise HTTPException(status_code=403, detail="Invalid signature")
    else:
        # For testing without signature validation
        try:
            event = json.loads(payload)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON payload")

    # Validate event structure
    if not event or "type" not in event:
        raise HTTPException(status_code=400, detail="Invalid event structure")

    # Handle the event
    event_type = event.get("type")

    # Check if data exists in event
    if "data" not in event or "object" not in event.get("data", {}):
        # For unknown event types or malformed events, return success to avoid retries
        print(f"⚠️ Event missing data: {event_type}")
        return {"status": "success", "message": "Event received but missing data"}

    data = event["data"]["object"]

    print(f"📥 Received Stripe event: {event_type}")

    # Handle subscription creation (when trial starts)
    if event_type == "customer.subscription.created":
        await handle_subscription_created(data, db)

    # Handle successful payment
    elif event_type == "invoice.payment_succeeded":
        await handle_payment_succeeded(data, db)

    # Handle failed payment
    elif event_type == "invoice.payment_failed":
        await handle_payment_failed(data, db)

    # Handle subscription update (status changes)
    elif event_type == "customer.subscription.updated":
        await handle_subscription_updated(data, db)

    # Handle subscription deletion/cancellation
    elif event_type == "customer.subscription.deleted":
        await handle_subscription_deleted(data, db)

    # For unknown event types, just acknowledge receipt
    else:
        print(f"ℹ️ Unhandled event type: {event_type}")

    return {"status": "success"}


async def handle_subscription_created(data: dict, db: AsyncSession):
    """Handle new subscription creation"""
    subscription_id = data["id"]
    customer_id = data["customer"]
    status = data["status"]

    # Get entity_type from metadata
    entity_id = int(data["metadata"].get("entity_id", 0))
    entity_type = data["metadata"].get("entity_type", "institution")

    trial_end = data.get("trial_end")
    current_period_start = data["current_period_start"]
    current_period_end = data["current_period_end"]

    print(f"✅ Creating subscription for {entity_type} {entity_id}")

    # Check if subscription already exists
    query = select(Subscription).where(
        Subscription.entity_type == entity_type,
        Subscription.entity_id == entity_id,
    )
    result = await db.execute(query)
    existing = result.scalar_one_or_none()

    if existing:
        # Update existing
        existing.stripe_subscription_id = subscription_id
        existing.stripe_customer_id = customer_id
        existing.status = status
        existing.plan_tier = "premium"
        existing.trial_end_date = (
            datetime.fromtimestamp(trial_end) if trial_end else None
        )
        existing.current_period_start = datetime.fromtimestamp(current_period_start)
        existing.current_period_end = datetime.fromtimestamp(current_period_end)
        existing.updated_at = datetime.utcnow()
    else:
        # Create new subscription
        new_subscription = Subscription(
            entity_type=entity_type,
            entity_id=entity_id,
            stripe_subscription_id=subscription_id,
            stripe_customer_id=customer_id,
            plan_tier="premium",
            status=status,
            trial_end_date=datetime.fromtimestamp(trial_end) if trial_end else None,
            current_period_start=datetime.fromtimestamp(current_period_start),
            current_period_end=datetime.fromtimestamp(current_period_end),
            cancel_at_period_end=False,
        )
        db.add(new_subscription)

    await db.commit()
    print(f"💾 Subscription saved to database for {entity_type} {entity_id}")


async def handle_payment_succeeded(data: dict, db: AsyncSession):
    """Handle successful payment"""
    subscription_id = data.get("subscription")

    if not subscription_id:
        return

    print(f"💰 Payment succeeded for subscription {subscription_id}")

    # Find subscription in database
    query = select(Subscription).where(
        Subscription.stripe_subscription_id == subscription_id
    )
    result = await db.execute(query)
    subscription = result.scalar_one_or_none()

    if subscription:
        subscription.status = "active"
        subscription.updated_at = datetime.utcnow()
        await db.commit()
        print(f"✅ Subscription marked as active")


async def handle_payment_failed(data: dict, db: AsyncSession):
    """Handle failed payment"""
    subscription_id = data.get("subscription")

    if not subscription_id:
        return

    print(f"❌ Payment failed for subscription {subscription_id}")

    # Find subscription in database
    query = select(Subscription).where(
        Subscription.stripe_subscription_id == subscription_id
    )
    result = await db.execute(query)
    subscription = result.scalar_one_or_none()

    if subscription:
        subscription.status = "past_due"
        subscription.updated_at = datetime.utcnow()
        await db.commit()
        print(f"⚠️ Subscription marked as past_due")


async def handle_subscription_updated(data: dict, db: AsyncSession):
    """Handle subscription updates (status changes, etc.)"""
    subscription_id = data["id"]
    status = data["status"]

    print(f"🔄 Subscription updated: {subscription_id} -> {status}")

    # Find subscription in database
    query = select(Subscription).where(
        Subscription.stripe_subscription_id == subscription_id
    )
    result = await db.execute(query)
    subscription = result.scalar_one_or_none()

    if subscription:
        subscription.status = status
        subscription.cancel_at_period_end = data.get("cancel_at_period_end", False)
        subscription.updated_at = datetime.utcnow()
        await db.commit()
        print(f"✅ Subscription updated in database")


async def handle_subscription_deleted(data: dict, db: AsyncSession):
    """Handle subscription deletion/cancellation"""
    subscription_id = data["id"]

    print(f"🗑️ Subscription deleted: {subscription_id}")

    # Find subscription in database
    query = select(Subscription).where(
        Subscription.stripe_subscription_id == subscription_id
    )
    result = await db.execute(query)
    subscription = result.scalar_one_or_none()

    if subscription:
        subscription.status = "canceled"
        subscription.updated_at = datetime.utcnow()
        await db.commit()
        print(f"✅ Subscription marked as canceled")
