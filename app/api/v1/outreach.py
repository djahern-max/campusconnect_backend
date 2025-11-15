from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, or_
from typing import List, Optional
from datetime import datetime, timedelta
from app.core.database import get_db
from app.api.v1.admin_auth import get_current_user
from app.models.admin_user import AdminUser
from app.models.outreach_tracking import OutreachTracking, ContactStatus, ContactMethod
from app.models.message_templates import MessageTemplate, OutreachActivity
from app.models.institution import Institution
from app.models.scholarship import Scholarship
from app.models.invitation_code import InvitationCode
from app.schemas.outreach import (
    OutreachCreate,
    OutreachUpdate,
    OutreachResponse,
    OutreachListResponse,
    MessageTemplateCreate,
    MessageTemplateUpdate,
    MessageTemplateResponse,
    SendMessageRequest,
    OutreachStatsResponse,
    BulkContactRequest
)

router = APIRouter(prefix="/admin/outreach", tags=["outreach-crm"])


@router.get("/stats", response_model=OutreachStatsResponse)
async def get_outreach_stats(
    current_user: AdminUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get overall outreach statistics"""
    
    # Total entities
    total_institutions = await db.execute(select(func.count(Institution.id)))
    total_scholarships = await db.execute(select(func.count(Scholarship.id)))
    
    total_entities = total_institutions.scalar() + total_scholarships.scalar()
    
    # Contact status counts
    status_counts = {}
    for status in ContactStatus:
        query = select(func.count(OutreachTracking.id)).where(
            OutreachTracking.status == status
        )
        result = await db.execute(query)
        status_counts[status.value] = result.scalar()
    
    # Calculate not contacted
    contacted_count = await db.execute(select(func.count(OutreachTracking.id)))
    not_contacted = total_entities - contacted_count.scalar()
    
    # Conversion rate
    registered = status_counts.get('registered', 0)
    contacted = sum(status_counts.values())
    conversion_rate = (registered / contacted * 100) if contacted > 0 else 0
    
    # Pending follow-ups
    pending_followups = await db.execute(
        select(func.count(OutreachTracking.id)).where(
            OutreachTracking.next_follow_up_date <= datetime.utcnow(),
            OutreachTracking.status.in_([ContactStatus.CONTACTED, ContactStatus.FOLLOW_UP_SENT])
        )
    )
    
    return {
        "total_entities": total_entities,
        "not_contacted": not_contacted,
        "contacted": contacted,
        "registered": registered,
        "declined": status_counts.get('declined', 0),
        "no_response": status_counts.get('no_response', 0),
        "conversion_rate": round(conversion_rate, 2),
        "pending_followups": pending_followups.scalar(),
        "status_breakdown": status_counts
    }


@router.get("", response_model=List[OutreachListResponse])
async def list_outreach(
    status: Optional[ContactStatus] = None,
    entity_type: Optional[str] = None,
    needs_followup: bool = False,
    search: Optional[str] = None,
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0),
    current_user: AdminUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all outreach records with filtering"""
    
    query = select(OutreachTracking)
    
    # Filters
    if status:
        query = query.where(OutreachTracking.status == status)
    
    if entity_type:
        query = query.where(OutreachTracking.entity_type == entity_type)
    
    if needs_followup:
        query = query.where(
            OutreachTracking.next_follow_up_date <= datetime.utcnow(),
            OutreachTracking.status.in_([ContactStatus.CONTACTED, ContactStatus.FOLLOW_UP_SENT])
        )
    
    if search:
        query = query.where(
            or_(
                OutreachTracking.contact_name.ilike(f"%{search}%"),
                OutreachTracking.contact_email.ilike(f"%{search}%"),
                OutreachTracking.notes.ilike(f"%{search}%")
            )
        )
    
    query = query.order_by(OutreachTracking.priority.desc(), OutreachTracking.updated_at.desc())
    query = query.limit(limit).offset(offset)
    
    result = await db.execute(query)
    outreach_records = result.scalars().all()
    
    # Enrich with entity names
    response = []
    for record in outreach_records:
        entity_name = await get_entity_name(db, record.entity_type, record.entity_id)
        response.append({
            **record.__dict__,
            "entity_name": entity_name
        })
    
    return response


@router.post("", response_model=OutreachResponse)
async def create_outreach(
    outreach_data: OutreachCreate,
    current_user: AdminUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create outreach record for an entity"""
    
    # Check if already exists
    query = select(OutreachTracking).where(
        OutreachTracking.entity_type == outreach_data.entity_type,
        OutreachTracking.entity_id == outreach_data.entity_id
    )
    result = await db.execute(query)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Outreach record already exists for this entity")
    
    # Create record
    new_outreach = OutreachTracking(
        entity_type=outreach_data.entity_type,
        entity_id=outreach_data.entity_id,
        contact_name=outreach_data.contact_name,
        contact_title=outreach_data.contact_title,
        contact_email=outreach_data.contact_email,
        contact_phone=outreach_data.contact_phone,
        linkedin_url=outreach_data.linkedin_url,
        priority=outreach_data.priority or 'normal',
        notes=outreach_data.notes,
        created_by=current_user.email
    )
    
    db.add(new_outreach)
    await db.commit()
    await db.refresh(new_outreach)
    
    return new_outreach


@router.put("/{outreach_id}", response_model=OutreachResponse)
async def update_outreach(
    outreach_id: int,
    updates: OutreachUpdate,
    current_user: AdminUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update outreach record"""
    
    query = select(OutreachTracking).where(OutreachTracking.id == outreach_id)
    result = await db.execute(query)
    outreach = result.scalar_one_or_none()
    
    if not outreach:
        raise HTTPException(status_code=404, detail="Outreach record not found")
    
    # Update fields
    for field, value in updates.dict(exclude_unset=True).items():
        setattr(outreach, field, value)
    
    await db.commit()
    await db.refresh(outreach)
    
    return outreach


# Helper functions
async def get_entity_name(db: AsyncSession, entity_type: str, entity_id: int) -> str:
    """Get entity name for display"""
    if entity_type == "institution":
        query = select(Institution).where(Institution.id == entity_id)
        result = await db.execute(query)
        entity = result.scalar_one_or_none()
        return entity.name if entity else "Unknown Institution"
    else:
        query = select(Scholarship).where(Scholarship.id == entity_id)
        result = await db.execute(query)
        entity = result.scalar_one_or_none()
        return entity.title if entity else "Unknown Scholarship"


async def get_or_create_invitation(
    db: AsyncSession,
    entity_type: str,
    entity_id: int,
    email: Optional[str],
    created_by: str
) -> InvitationCode:
    """Get existing invitation or create new one"""
    
    # Check for existing unused invitation
    query = select(InvitationCode).where(
        InvitationCode.entity_type == entity_type,
        InvitationCode.entity_id == entity_id,
        InvitationCode.status == 'pending'
    )
    result = await db.execute(query)
    existing = result.scalar_one_or_none()
    
    if existing:
        return existing
    
    # Create new invitation
    code = InvitationCode.generate_code()
    expires_at = datetime.utcnow() + timedelta(days=30)
    
    new_invitation = InvitationCode(
        code=code,
        entity_type=entity_type,
        entity_id=entity_id,
        assigned_email=email,
        expires_at=expires_at,
        created_by=created_by
    )
    
    db.add(new_invitation)
    await db.flush()
    
    return new_invitation


def personalize_message(
    template: str,
    entity_name: str,
    contact_name: Optional[str],
    invitation_code: Optional[str],
    city: Optional[str],
    state: Optional[str]
) -> str:
    """Replace tokens with actual values"""
    
    replacements = {
        '{entity_name}': entity_name or '',
        '{institution_name}': entity_name or '',
        '{scholarship_name}': entity_name or '',
        '{contact_name}': contact_name or 'there',
        '{invitation_code}': invitation_code or '[CODE WILL BE GENERATED]',
        '{city}': city or '',
        '{state}': state or ''
    }
    
    result = template
    for token, value in replacements.items():
        result = result.replace(token, value)
    
    return result


# MESSAGE TEMPLATES
@router.get("/templates", response_model=List[MessageTemplateResponse])
async def list_templates(
    current_user: AdminUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all message templates"""
    query = select(MessageTemplate).where(MessageTemplate.is_active == True)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/templates", response_model=MessageTemplateResponse)
async def create_template(
    template_data: MessageTemplateCreate,
    current_user: AdminUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create new message template"""
    new_template = MessageTemplate(
        name=template_data.name,
        template_type=template_data.template_type,
        subject=template_data.subject,
        body=template_data.body,
        created_by=current_user.email
    )
    
    db.add(new_template)
    await db.commit()
    await db.refresh(new_template)
    
    return new_template
