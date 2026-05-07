# FastAPI AI Agent for Website Intelligence

A FastAPI-based AI agent that analyzes website homepages, extracts structured company insights, and answers follow-up questions using an LLM.

## Overview

This project is a backend API built with FastAPI to scrape homepage content from a given website, process it using an LLM, and return structured business intelligence in JSON format.

It is designed to answer practical questions such as:

- What industry does this company belong to?
- What products or services does it offer?
- What is its unique selling proposition?
- Who is its target audience?
- What contact information is visible on the homepage?

The project also includes a follow-up conversational endpoint so users can ask additional natural-language questions based on the scraped website content.

## Features

- Homepage-only website scraping using `requests` and `BeautifulSoup`
- Structured API design using FastAPI
- Request and response validation using Pydantic
- AI-powered insight extraction using an LLM
- Follow-up question answering endpoint
- Bearer token authentication
- JSON-based output suitable for frontend or automation workflows
- Swagger UI support via FastAPI docs
- Error handling for scraping and inference failures

## Tech Stack

- **Backend Framework:** FastAPI
- **Language:** Python
- **Web Scraping:** requests, BeautifulSoup
- **Validation:** Pydantic
- **AI Inference:** Cerebras SDK / LLM API
- **API Docs:** Swagger UI (FastAPI `/docs`)

## API Endpoints

### 1. `POST /analyze`

Analyzes a website homepage and returns structured business information.

#### Request Body

```json
{
  "url": "https://example.com",
  "questions": [
    "What industry is this company in?",
    "What products or services does it offer?"
  ]
}
```

#### Example Response

```json
{
  "url": "https://example.com",
  "analysisTimestamp": "2026-05-07T10:00:00Z",
  "companyInfo": {
    "industry": "Software",
    "companySize": "Small to Medium",
    "location": "Not explicitly mentioned",
    "coreProductsServices": ["SaaS platform", "Automation tools"],
    "uniqueSellingProposition": "Fast AI-powered workflow automation",
    "targetAudience": "Businesses and startups",
    "contactInfo": {
      "email": "info@example.com",
      "phone": null,
      "social_media": null
    }
  },
  "extractedAnswers": [
    {
      "question": "What industry is this company in?",
      "answer": "Software"
    }
  ]
}
```

### 2. `POST /generate`

Accepts a website URL and a natural-language query, then returns an AI-generated follow-up response.

#### Request Body

```json
{
  "url": "https://example.com",
  "user_query": "What does this company mainly do?"
}
```

#### Example Response

```json
{
  "url": "https://example.com",
  "user_query": "What does this company mainly do?",
  "agent_response": "The company appears to provide software tools focused on automation and workflow efficiency.",
  "context_sources": ["homepage hero section", "product description section"]
}
```

## Project Structure

```bash
fastapi-ai-agent/
├── scraper_inference/
│   └── main.py
├── .env
├── .gitignore
├── README.md
```

## How It Works

1. The user sends a website URL to the API.
2. The backend scrapes the homepage text content.
3. Script and style tags are removed from the HTML.
4. The cleaned text is passed to the LLM with a structured prompt.
5. The model returns structured output in JSON format.
6. The response is validated using Pydantic before being returned.

## Authentication

The API uses Bearer token authentication.

Add the following in your request headers:

```http
Authorization: Bearer YOUR_SECRET_KEY
```

Set the same value in the `.env` file:

```env
SECRET_KEY=your_secret_key_here
```

## Environment Variables

Create a `.env` file in the root directory and add:

```env
CEREBRAS_API_KEY=your_cerebras_api_key_here
SECRET_KEY=your_secret_key_here
```

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/fastapi-ai-agent.git
cd fastapi-ai-agent
```

### 2. Create and activate virtual environment

#### Windows (PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\activate
```

#### Git Bash

```bash
python -m venv .venv
source .venv/Scripts/activate
```

### 3. Install dependencies

```bash
pip install fastapi uvicorn requests beautifulsoup4 python-dotenv pydantic cerebras-cloud-sdk
```

### 4. Run the server

```bash
uvicorn scraper_inference.main:app --reload
```

### 5. Open API docs

```bash
http://127.0.0.1:8000/docs
```

## Design Decisions

- **FastAPI** was chosen for its speed, clean developer experience, and automatic Swagger documentation.
- **Pydantic** was used to enforce strict request and response schemas.
- **Homepage-only scraping** keeps the scope focused and improves speed and predictability.
- **LLM-based extraction** enables semantic inference for industry, USP, and audience instead of relying only on keyword matching.
- **Bearer authentication** was added to protect access to the endpoints.

## Improvements Planned

- Add rate limiting
- Add async scraping for better performance
- Improve context source extraction in the `/generate` endpoint
- Add test cases using `pytest`
- Add deployment on Render or Railway
- Add caching for repeated website analysis

## Demo

After running the server locally, test the API through Swagger UI:

- `/docs` for interactive testing
- `/openapi.json` for OpenAPI schema output

## Notes

- This project currently focuses on homepage analysis only.
- Some websites may block scraping or return incomplete content.
- LLM output quality depends on the selected model and API access.

## Author

**Bhoumic**  
Aspiring Software Developer | Python | FastAPI | React | AI Projects
