from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict
from datetime import datetime

# Outreach Tracking Schemas
class OutreachCreate(BaseModel):
    entity_type: str
    entity_id: int
    contact_name: Optional[str] = None
    contact_title: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    priority: Optional[str] = 'normal'
    notes: Optional[str] = None

class OutreachUpdate(BaseModel):
    contact_name: Optional[str] = None
    contact_title: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    notes: Optional[str] = None
    response_feedback: Optional[str] = None
    next_follow_up_date: Optional[datetime] = None

class OutreachResponse(BaseModel):
    id: int
    entity_type: str
    entity_id: int
    contact_name: Optional[str]
    contact_title: Optional[str]
    contact_email: Optional[str]
    contact_phone: Optional[str]
    linkedin_url: Optional[str]
    status: str
    last_contact_date: Optional[datetime]
    last_contact_method: Optional[str]
    contact_attempt_count: int
    invitation_code_id: Optional[int]
    invitation_sent_date: Optional[datetime]
    next_follow_up_date: Optional[datetime]
    follow_up_count: int
    notes: Optional[str]
    response_feedback: Optional[str]
    priority: str
    tags: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class OutreachListResponse(OutreachResponse):
    entity_name: str

# Statistics
class OutreachStatsResponse(BaseModel):
    total_entities: int
    not_contacted: int
    contacted: int
    registered: int
    declined: int
    no_response: int
    conversion_rate: float
    pending_followups: int
    status_breakdown: Dict[str, int]

# Message Templates
class MessageTemplateCreate(BaseModel):
    name: str
    template_type: str
    subject: Optional[str] = None
    body: str

class MessageTemplateUpdate(BaseModel):
    name: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None

class MessageTemplateResponse(BaseModel):
    id: int
    name: str
    template_type: str
    subject: Optional[str]
    body: str
    times_used: int
    conversion_count: int
    is_active: bool
    is_default: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Sending Messages
class SendMessageRequest(BaseModel):
    template_id: Optional[int] = None
    contact_method: str
    subject: Optional[str] = None
    message: Optional[str] = None
    include_invitation: bool = True

class BulkContactRequest(BaseModel):
    outreach_ids: List[int]
    template_id: int
    contact_method: str
    include_invitation: bool = True

# Activity Log
class OutreachActivityResponse(BaseModel):
    id: int
    activity_type: str
    contact_method: str
    subject: Optional[str]
    message_sent: str
    response_received: bool
    response_text: Optional[str]
    response_date: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True
