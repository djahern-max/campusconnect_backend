# app/services/stripe_service.py
import stripe
from app.core.config import settings
from fastapi import HTTPException
from typing import Optional

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:
    """Service for handling Stripe operations"""

    # Pricing in cents
    INSTITUTION_PRICE = 3999  # $39.99/month
    SCHOLARSHIP_PRICE = 1999  # $19.99/month
    TRIAL_DAYS = 30

    def create_checkout_session(
        self,
        customer_email: str,
        entity_id: int,
        entity_name: str,
        entity_type: str,  # ✅ NEW: Added entity_type parameter
        success_url: str,
        cancel_url: str,
    ) -> dict:
        """
        Create a Stripe checkout session for premium subscription

        Args:
            customer_email: Admin's email
            entity_id: Entity ID (institution or scholarship)
            entity_name: Entity name for description
            entity_type: Type of entity ('institution' or 'scholarship')
            success_url: URL to redirect after successful payment
            cancel_url: URL to redirect if user cancels

        Returns:
            dict with checkout session info
        """
        try:
            # Determine price based on entity type
            price = (
                self.SCHOLARSHIP_PRICE
                if entity_type == "scholarship"
                else self.INSTITUTION_PRICE
            )
            entity_type_display = entity_type.capitalize()

            # Create checkout session
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": "usd",
                            "product_data": {
                                "name": f"CampusConnect Premium - {entity_name}",
                                "description": f"Premium directory listing with admin dashboard for {entity_type_display}",
                            },
                            "unit_amount": price,
                            "recurring": {
                                "interval": "month",
                            },
                        },
                        "quantity": 1,
                    }
                ],
                mode="subscription",
                success_url=success_url,
                cancel_url=cancel_url,
                customer_email=customer_email,
                subscription_data={
                    "trial_period_days": self.TRIAL_DAYS,
                    "metadata": {
                        "entity_id": str(entity_id),  # ✅ Changed from institution_id
                        "entity_name": entity_name,  # ✅ Changed from institution_name
                        "entity_type": entity_type,  # ✅ NEW: Added entity_type
                    },
                },
                metadata={
                    "entity_id": str(entity_id),  # ✅ Changed from institution_id
                    "entity_type": entity_type,  # ✅ NEW: Added entity_type
                },
            )

            return {
                "session_id": session.id,
                "url": session.url,
                "status": session.status,
            }

        except stripe.error.StripeError as e:
            raise HTTPException(status_code=400, detail=f"Stripe error: {str(e)}")

    def create_customer_portal_session(self, customer_id: str, return_url: str) -> dict:
        """
        Create a customer portal session for managing subscription

        Args:
            customer_id: Stripe customer ID
            return_url: URL to return to after portal session

        Returns:
            dict with portal session URL
        """
        try:
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url,
            )

            return {"url": session.url}

        except stripe.error.StripeError as e:
            raise HTTPException(status_code=400, detail=f"Stripe error: {str(e)}")

    def cancel_subscription(self, subscription_id: str) -> dict:
        """
        Cancel a subscription at period end

        Args:
            subscription_id: Stripe subscription ID

        Returns:
            dict with updated subscription info
        """
        try:
            subscription = stripe.Subscription.modify(
                subscription_id, cancel_at_period_end=True
            )

            return {
                "id": subscription.id,
                "status": subscription.status,
                "cancel_at_period_end": subscription.cancel_at_period_end,
                "current_period_end": subscription.current_period_end,
            }

        except stripe.error.StripeError as e:
            raise HTTPException(status_code=400, detail=f"Stripe error: {str(e)}")

    def get_subscription(self, subscription_id: str) -> dict:
        """
        Get subscription details

        Args:
            subscription_id: Stripe subscription ID

        Returns:
            dict with subscription info
        """
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)

            return {
                "id": subscription.id,
                "status": subscription.status,
                "current_period_start": subscription.current_period_start,
                "current_period_end": subscription.current_period_end,
                "cancel_at_period_end": subscription.cancel_at_period_end,
                "trial_end": (
                    subscription.trial_end
                    if hasattr(subscription, "trial_end")
                    else None
                ),
            }

        except stripe.error.StripeError as e:
            raise HTTPException(status_code=400, detail=f"Stripe error: {str(e)}")


# Singleton instance
stripe_service = StripeService()
