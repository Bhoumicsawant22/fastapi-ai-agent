import os
import json
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict

from fastapi import FastAPI, HTTPException
from cerebras.cloud.sdk import Cerebras
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Initialize the FastAPI app
app = FastAPI(
    title="Website Intelligence API",
    description="An API to analyze website content and generate text.",
)

# --- Initialize Cerebras Client (ONCE) ---
try:
    client = Cerebras(
        api_key=os.environ.get("CEREBRAS_API_KEY"),
    )
except Exception as e:
    raise RuntimeError(f"Failed to initialize Cerebras client: {e}") from e


# --- Pydantic Models for All Endpoints ---

# For the /generate endpoint
class PromptRequest(BaseModel):
    content: str

# For the /analyze endpoint
class AnalysisRequest(BaseModel):
    url: HttpUrl
    questions: List[str]

class ContactInfo(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    social_media: Optional[Dict[str, HttpUrl]] = None

class CompanyInfo(BaseModel):
    industry: Optional[str] = None
    company_size: Optional[str] = Field(None, alias="companySize")
    location: Optional[str] = None
    core_products_services: Optional[List[str]] = Field(None, alias="coreProductsServices")
    unique_selling_proposition: Optional[str] = Field(None, alias="uniqueSellingProposition")
    target_audience: Optional[str] = Field(None, alias="targetAudience")
    contact_info: Optional[ContactInfo] = Field(None, alias="contactInfo")

class ExtractedAnswer(BaseModel):
    question: str
    answer: Optional[str] = None

class AnalysisOutput(BaseModel):
    url: HttpUrl
    analysis_timestamp: datetime = Field(alias="analysisTimestamp")
    company_info: CompanyInfo = Field(alias="companyInfo")
    extracted_answers: List[ExtractedAnswer] = Field(alias="extractedAnswers")


# --- Helper & Logic Functions ---

def scrape_homepage_text(url: str) -> str:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()
        return soup.body.get_text(separator=" ", strip=True)
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Failed to scrape URL {url}: {e}")

def analyze_website(url: str, questions: List[str]) -> dict:
    print(f"▶️ Starting analysis for: {url}")
    content = scrape_homepage_text(url)
    print("✅ Scraping complete.")
    
    json_schema = json.dumps(AnalysisOutput.model_json_schema(), indent=2)

    prompt = f"""
    You are an expert business analyst AI. Analyze the website content below to extract information and answer the questions.
    Your response MUST be ONLY the valid JSON object that adheres to the schema. Do not include markdown formatting like ```json.
    
    JSON Schema to use:
    ```json
    {json_schema}
    ```
    
    User's Questions to Answer:
    - {" ".join(questions)}
    
    Website Content:
    ---
    {content[:15000]}
    ---
    """
    
    print("🧠 Contacting Cerebras model for analysis...")
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3.1-8b",
            temperature=0.1,
        )
        raw_response = chat_completion.choices[0].message.content
        
        cleaned_response = raw_response.strip()
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response.removeprefix("```json").strip()
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response.removesuffix("```").strip()
        
        try:
            response_json = json.loads(cleaned_response)

            if "extractedAnswers" in response_json:
                for ans in response_json["extractedAnswers"]:
                    if isinstance(ans.get("answer"), list):
                        ans["answer"] = ", ".join(ans["answer"])

        except json.JSONDecodeError:
            error_detail = f"AI model returned a non-JSON response even after cleaning. Raw response: '{raw_response}'"
            raise HTTPException(status_code=500, detail=error_detail)

        
        response_json["url"] = url
        response_json["analysisTimestamp"] = datetime.now(timezone.utc).isoformat()
        validated_output = AnalysisOutput(**response_json)
        print("✅ Analysis complete.")
        return validated_output.model_dump(by_alias=True)
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


# --- API Endpoints ---

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

app = FastAPI()

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != SECRET_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True

@app.post("/analyze", response_model=AnalysisOutput)
async def analyze_endpoint(request: AnalysisRequest, authorized: bool = Depends(verify_token)):
    try:
        result = analyze_website(request.url, request.questions)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class GenerateRequest(BaseModel):
    url: HttpUrl
    user_query: str

class GenerateResponse(BaseModel):
    url: HttpUrl
    user_query: str
    agent_response: str
    context_sources: List[str]

@app.post("/generate", response_model=GenerateResponse)
async def generate_endpoint(request: GenerateRequest, authorized: bool = Depends(verify_token)):
    try:
        # Scrape website content
        content = scrape_homepage_text(request.url)

        # Build prompt for Cerebras
        prompt = f"""
        You are an AI assistant. The user asked: "{request.user_query}"
        Based on the website content below, answer clearly.
        Also list the 1-3 most relevant context snippets you used.

        Website Content:
        ---
        {content[:15000]}
        ---
        """

        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3.1-8b",
            temperature=0.3,
        )

        agent_response = chat_completion.choices[0].message.content.strip()

        return GenerateResponse(
            url=request.url,
            user_query=request.user_query,
            agent_response=agent_response,
            context_sources=["snippet 1", "snippet 2"]  # <- you can extract real ones later
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


