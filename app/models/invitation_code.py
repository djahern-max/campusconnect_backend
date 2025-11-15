from sqlalchemy import Column, Integer, String, TIMESTAMP, Enum as SQLEnum
from sqlalchemy.sql import func
from app.core.database import Base
import enum
import secrets
import string


class InvitationStatus(str, enum.Enum):
    PENDING = "pending"
    CLAIMED = "claimed"
    EXPIRED = "expired"
    REVOKED = "revoked"


class InvitationCode(Base):
    __tablename__ = "invitation_codes"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(Integer, nullable=False, index=True)
    assigned_email = Column(String(255))
    status = Column(
        SQLEnum(InvitationStatus), nullable=False, default=InvitationStatus.PENDING
    )
    claimed_by = Column(Integer)
    expires_at = Column(TIMESTAMP, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    claimed_at = Column(TIMESTAMP)
    created_by = Column(String(100))

    @staticmethod
    def generate_code() -> str:
        """Generate a secure, readable invitation code (ABC-DEF-GHI-JKL format)"""
        chars = string.ascii_uppercase + string.digits
        chars = (
            chars.replace("O", "").replace("0", "").replace("I", "").replace("1", "")
        )

        parts = []
        for _ in range(4):
            part = "".join(secrets.choice(chars) for _ in range(3))
            parts.append(part)

        return "-".join(parts)
