from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid
import httpx
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

load_dotenv()
SECRET_KEY = os.getenv("AGENT_SECRET_KEY", "supersecretkey123")

app = FastAPI(title="FastAPI AI Agent")
security = HTTPBearer()

# -------------------------------
# Auth dependency
# -------------------------------
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != SECRET_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True

# -------------------------------
# Pydantic models
# -------------------------------
class AnalyzeRequest(BaseModel):
    url: str
    questions: Optional[List[str]] = []

class ExtractedAnswer(BaseModel):
    question: str
    answer: str

class CompanyInfo(BaseModel):
    industry: str
    company_size: str
    location: str
    core_products_services: List[str]
    unique_selling_proposition: str
    target_audience: str
    contact_info: dict

class AnalyzeResponse(BaseModel):
    session_id: str
    url: str
    analysis_timestamp: datetime
    company_info: CompanyInfo
    extracted_answers: List[ExtractedAnswer]

class ConverseRequest(BaseModel):
    url: str
    query: str
    conversation_history: Optional[List[dict]] = []

class ConverseResponse(BaseModel):
    url: str
    user_query: str
    agent_response: str
    context_sources: List[str]

# -------------------------------
# In-memory store for scraped content
# -------------------------------
SCRAPED_CONTENT = {}

# -------------------------------
# /analyze endpoint
# -------------------------------
@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest, auth: bool = Depends(verify_token)):
    session_id = str(uuid.uuid4())

    # Fetch homepage
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(request.url)
            html_content = response.text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {e}")

    # Parse homepage
    soup = BeautifulSoup(html_content, "lxml")
    text_content = soup.get_text(separator=" ", strip=True)

    # Store content in memory with session_id
    SCRAPED_CONTENT[session_id] = {
        "url": request.url,
        "text": text_content
    }

    # Simple mock extraction
    company_info = CompanyInfo(
        industry="Technology",
        company_size="Medium (50-200 employees)",
        location="San Francisco, CA, USA",
        core_products_services=["AI Platform", "Chatbot Service"],
        unique_selling_proposition="Innovative AI solutions",
        target_audience="Small to Medium Businesses (SMBs)",
        contact_info={
            "email": "info@example.com",
            "phone": "+1-555-123-4567",
            "social_media": {
                "linkedin": "https://linkedin.com/company/example",
                "twitter": "https://twitter.com/example"
            }
        }
    )

    extracted_answers = [
        ExtractedAnswer(question=q, answer="AI-generated answer") for q in request.questions
    ]

    return AnalyzeResponse(
        session_id=session_id,
        url=request.url,
        analysis_timestamp=datetime.utcnow(),
        company_info=company_info,
        extracted_answers=extracted_answers
    )

# -------------------------------
# /converse endpoint
# -------------------------------
@app.post("/converse", response_model=ConverseResponse)
async def converse(request: ConverseRequest, auth: bool = Depends(verify_token)):
    # Find the content by URL in memory
    session_data = None
    for sid, data in SCRAPED_CONTENT.items():
        if data["url"] == request.url:
            session_data = data
            break

    if not session_data:
        raise HTTPException(status_code=404, detail="No analysis found for this URL. Please call /analyze first.")

    # Mock AI response using homepage content
    agent_response = f"Based on the homepage, the AI says: (mock answer to '{request.query}')"

    return ConverseResponse(
        url=request.url,
        user_query=request.query,
        agent_response=agent_response,
        context_sources=["homepage content"]
    )
