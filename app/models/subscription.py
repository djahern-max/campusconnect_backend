from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP
from sqlalchemy.sql import func
from app.core.database import Base

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(50), nullable=False)  # 'institution' or 'scholarship'
    entity_id = Column(Integer, nullable=False)
    stripe_customer_id = Column(String(255))
    stripe_subscription_id = Column(String(255))
    plan_tier = Column(String(50))  # 'free', 'premium'
    status = Column(String(50))  # 'trialing', 'active', 'past_due', 'canceled'
    trial_end_date = Column(TIMESTAMP)
    current_period_start = Column(TIMESTAMP)
    current_period_end = Column(TIMESTAMP)
    cancel_at_period_end = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
