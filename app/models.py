from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict
from datetime import datetime

# --- Request Models ---
class AnalyzeRequest(BaseModel):
    url: HttpUrl
    questions: Optional[List[str]] = []

class ConverseRequest(BaseModel):
    session_id: str
    query: str
    conversation_history: Optional[List[Dict[str, str]]] = []

# --- Response Models ---
class SocialMedia(BaseModel):
    linkedin: Optional[HttpUrl] = None
    twitter: Optional[HttpUrl] = None

class ContactInfo(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    social_media: Optional[SocialMedia] = None

class CompanyInfo(BaseModel):
    industry: Optional[str] = None
    company_size: Optional[str] = None
    location: Optional[str] = None
    core_products_services: Optional[List[str]] = None
    unique_selling_proposition: Optional[str] = None
    target_audience: Optional[str] = None
    contact_info: Optional[ContactInfo] = None

class ExtractedAnswer(BaseModel):
    question: str
    answer: str

class AnalyzeResponse(BaseModel):
    session_id: str
    url: HttpUrl
    analysis_timestamp: datetime
    company_info: CompanyInfo
    extracted_answers: Optional[List[ExtractedAnswer]] = []

class ConverseResponse(BaseModel):
    url: HttpUrl
    user_query: str
    agent_response: str
    context_sources: Optional[List[str]] = []
