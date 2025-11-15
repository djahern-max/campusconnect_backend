from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token, verify_token
from app.core.rate_limit import limiter, RATE_LIMITS
from app.models.admin_user import AdminUser
from app.models.invitation_code import InvitationCode, InvitationStatus
from app.models.institution import Institution
from app.models.scholarship import Scholarship
from app.schemas.admin import AdminRegister, AdminLogin, AdminResponse, Token
from app.schemas.invitation import (
    InvitationCodeCreate,
    InvitationCodeResponse,
    InvitationValidateRequest,
    InvitationValidateResponse
)
from typing import List

router = APIRouter(prefix="/admin/auth", tags=["admin-auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/admin/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> AdminUser:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = verify_token(token)
    if payload is None:
        raise credentials_exception
    
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception
    
    query = select(AdminUser).where(AdminUser.email == email)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    return user

@router.post("/validate-invitation", response_model=InvitationValidateResponse)
@limiter.limit(RATE_LIMITS["auth"])
async def validate_invitation(
    request: Request,
    invitation_request: InvitationValidateRequest,
    db: AsyncSession = Depends(get_db)
):
    """Validate an invitation code and return entity info"""
    query = select(InvitationCode).where(
        InvitationCode.code == invitation_request.code,
        InvitationCode.status == InvitationStatus.PENDING
    )
    result = await db.execute(query)
    invitation = result.scalar_one_or_none()
    
    if not invitation:
        return InvitationValidateResponse(
            valid=False,
            message="Invalid or already used invitation code"
        )
    
    # Check expiration
    if invitation.expires_at < datetime.utcnow():
        invitation.status = InvitationStatus.EXPIRED
        await db.commit()
        return InvitationValidateResponse(
            valid=False,
            message="This invitation code has expired"
        )
    
    # Get entity name
    entity_name = "Unknown"
    if invitation.entity_type == "institution":
        query = select(Institution).where(Institution.id == invitation.entity_id)
        result = await db.execute(query)
        entity = result.scalar_one_or_none()
        if entity:
            entity_name = entity.name
    else:
        query = select(Scholarship).where(Scholarship.id == invitation.entity_id)
        result = await db.execute(query)
        entity = result.scalar_one_or_none()
        if entity:
            entity_name = entity.title
    
    return InvitationValidateResponse(
        valid=True,
        entity_type=invitation.entity_type,
        entity_id=invitation.entity_id,
        entity_name=entity_name,
        message=f"Valid invitation for: {entity_name}"
    )

@router.post("/register", response_model=AdminResponse)
@limiter.limit(RATE_LIMITS["auth"])
async def register(
    request: Request,
    admin_data: AdminRegister,
    db: AsyncSession = Depends(get_db)
):
    """Register a new admin user with invitation code"""
    # Validate invitation code first
    query = select(InvitationCode).where(
        InvitationCode.code == admin_data.invitation_code,
        InvitationCode.status == InvitationStatus.PENDING
    )
    result = await db.execute(query)
    invitation = result.scalar_one_or_none()
    
    if not invitation:
        raise HTTPException(status_code=400, detail="Invalid invitation code")
    
    if invitation.expires_at < datetime.utcnow():
        invitation.status = InvitationStatus.EXPIRED
        await db.commit()
        raise HTTPException(status_code=400, detail="Invitation code has expired")
    
    # Check if email already exists
    query = select(AdminUser).where(AdminUser.email == admin_data.email)
    result = await db.execute(query)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new admin user with entity from invitation
    hashed_password = get_password_hash(admin_data.password)
    new_admin = AdminUser(
        email=admin_data.email,
        hashed_password=hashed_password,
        entity_type=invitation.entity_type,
        entity_id=invitation.entity_id,
        role='admin'
    )
    
    db.add(new_admin)
    
    # Mark invitation as claimed
    invitation.status = InvitationStatus.CLAIMED
    invitation.claimed_by = new_admin.id
    invitation.claimed_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(new_admin)
    
    return new_admin

@router.post("/login", response_model=Token)
@limiter.limit(RATE_LIMITS["auth"])
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Login and get access token"""
    query = select(AdminUser).where(AdminUser.email == form_data.username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=AdminResponse)
@limiter.limit(RATE_LIMITS["admin"])
async def get_me(request: Request, current_user: AdminUser = Depends(get_current_user)):
    """Get current user info"""
    return current_user

# INVITATION MANAGEMENT (Super Admin Only)
@router.post("/invitations", response_model=InvitationCodeResponse)
@limiter.limit(RATE_LIMITS["admin"])
async def create_invitation(
    request: Request,
    invitation_data: InvitationCodeCreate,
    current_user: AdminUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate a new invitation code (Super Admin only in production)"""
    # In production, check if user is super_admin
    # if current_user.role != 'super_admin':
    #     raise HTTPException(status_code=403, detail="Only super admins can generate invitations")
    
    # Generate unique code
    code = InvitationCode.generate_code()
    
    # Calculate expiration
    expires_at = datetime.utcnow() + timedelta(days=invitation_data.expires_in_days)
    
    # Create invitation
    new_invitation = InvitationCode(
        code=code,
        entity_type=invitation_data.entity_type,
        entity_id=invitation_data.entity_id,
        assigned_email=invitation_data.assigned_email,
        expires_at=expires_at,
        created_by=current_user.email
    )
    
    db.add(new_invitation)
    await db.commit()
    await db.refresh(new_invitation)
    
    return new_invitation

@router.get("/invitations", response_model=List[InvitationCodeResponse])
@limiter.limit(RATE_LIMITS["admin"])
async def list_invitations(
    request: Request,
    status: str = None,
    limit: int = 100,
    current_user: AdminUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all invitation codes"""
    query = select(InvitationCode).order_by(InvitationCode.created_at.desc())
    
    if status:
        query = query.where(InvitationCode.status == status)
    
    query = query.limit(limit)
    
    result = await db.execute(query)
    invitations = result.scalars().all()
    
    return invitations
