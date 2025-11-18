from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.core.database import get_db
from app.schemas.contact import ContactInquiryCreate, ContactInquiryResponse
from app.models.contact_inquiry import ContactInquiry

router = APIRouter(tags=["Contact Inquiries"])


@router.post("/submit", response_model=ContactInquiryResponse, status_code=201)
async def submit_contact_inquiry(
    inquiry: ContactInquiryCreate, db: AsyncSession = Depends(get_db)
):
    """Submit a contact inquiry form (public endpoint)"""
    try:
        db_inquiry = ContactInquiry(
            name=inquiry.name,
            email=inquiry.email,
            institution_name=inquiry.institution_name,
            phone_number=inquiry.phone_number,
            inquiry_type=inquiry.inquiry_type,
            message=inquiry.message,
        )

        db.add(db_inquiry)
        await db.commit()
        await db.refresh(db_inquiry)

        return db_inquiry

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Failed to submit inquiry: {str(e)}"
        )


@router.get("/inquiries", response_model=List[ContactInquiryResponse])
async def get_all_inquiries(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    """Get all contact inquiries (admin only - add auth later if needed)"""
    result = await db.execute(
        select(ContactInquiry)
        .order_by(ContactInquiry.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    inquiries = result.scalars().all()

    return inquiries


@router.get("/inquiries/{inquiry_id}", response_model=ContactInquiryResponse)
async def get_inquiry(inquiry_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific inquiry by ID (admin only - add auth later if needed)"""
    result = await db.execute(
        select(ContactInquiry).filter(ContactInquiry.id == inquiry_id)
    )
    inquiry = result.scalars().first()

    if not inquiry:
        raise HTTPException(status_code=404, detail="Inquiry not found")

    return inquiry
