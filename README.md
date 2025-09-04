# FastAPI AI Agent (Assessment)

## Setup

1. copy `.env.example` → `.env` and set AGENT_SECRET_KEY (and OPENAI_API_KEY if available)
2. create venv & activate
3. pip install -r requirements.txt
4. run: `uvicorn app.main:app --reload --port 8000`

## Endpoints

- POST /analyze

  - Header: Authorization: Bearer <AGENT_SECRET_KEY>
  - Body:
    ```json
    { "url": "https://example.com", "questions": ["What industry?"] }
    ```

- POST /converse
  - Header: Authorization: Bearer <AGENT_SECRET_KEY>
  - Body:
    ```json
    { "url": "https://example.com", "query": "Who is the target audience?" }
    ```

## Example Responses

### `/analyze` Response

```json
{
  "session_id": "7c2ab574-0c69-49a4-a491-d3d33bcba400",
  "url": "https://www.nike.com/in/",
  "analysis_timestamp": "2025-09-04T12:13:42.823568",
  "company_info": {
    "industry": "Technology",
    "company_size": "Medium (50-200 employees)",
    "location": "San Francisco, CA, USA",
    "core_products_services": ["AI Platform", "Chatbot Service"],
    "unique_selling_proposition": "Innovative AI solutions",
    "target_audience": "Small to Medium Businesses (SMBs)",
    "contact_info": {
      "email": "info@example.com",
      "phone": "+1-555-123-4567",
      "social_media": {
        "linkedin": "https://linkedin.com/company/example",
        "twitter": "https://twitter.com/example"
      }
    }
  },
  "extracted_answers": []
}

### `/converse` Response
{
  "url": "https://www.nike.com/in/",
  "user_query": "What are the key features of their products?",
  "agent_response": "This is a mock answer from the AI agent.",
  "context_sources": ["homepage content", "product description"]
}
```
