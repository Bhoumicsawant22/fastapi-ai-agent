import os
import json
import asyncio
import re
from typing import List, Dict, Any

OPENAI_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

if OPENAI_KEY:
    import openai
    openai.api_key = OPENAI_KEY

class AIClient:
    async def extract_core_insights(self, text: str, questions: List[str] = None) -> Dict[str, Any]:
        prompt = self._build_extract_prompt(text, questions)
        if OPENAI_KEY:
            resp = await asyncio.to_thread(
                openai.ChatCompletion.create,
                model=OPENAI_MODEL,
                messages=[
                    {"role":"system","content":"You are an expert at extracting business insights from website homepages. Output valid JSON."},
                    {"role":"user","content":prompt}
                ],
                temperature=0.0,
                max_tokens=800
            )
            content = resp["choices"][0]["message"]["content"]
            try:
                return json.loads(content)
            except Exception:
                m = re.search(r"(\{.*\})", content, re.S)
                if m:
                    try:
                        return json.loads(m.group(1))
                    except:
                        pass
                return {"summary": content}
        else:
            return self._mock_extract(text, questions)

    async def answer_followup(self, query: str, context: str, conversation_history: List[Dict[str,str]] = None) -> str:
        prompt = f"Use the context below to answer the question concisely.\n\nContext:\n{context}\n\nQuestion: {query}"
        if OPENAI_KEY:
            messages = [{"role":"system","content":"You are a helpful assistant answering follow-up questions about a website using provided context."}]
            if conversation_history:
                for item in conversation_history:
                    messages.append({"role": "user" if item.get("role")=="user" else "assistant", "content": item.get("text","")})
            messages.append({"role":"user","content":prompt})
            resp = await asyncio.to_thread(
                openai.ChatCompletion.create,
                model=OPENAI_MODEL,
                messages=messages,
                temperature=0.0,
                max_tokens=500
            )
            return resp["choices"][0]["message"]["content"]
        else:
            return self._mock_answer(query, context)

    def _build_extract_prompt(self, text: str, questions: List[str] = None) -> str:
        instruction = (
            "Return ONLY a JSON object with keys: industry, company_size, location, usp, core_products, "
            "target_audience, contacts, sentiment, summary. Keep values short.\n\n"
        )
        tail = ""
        if questions:
            tail = "\nAdditional questions: " + json.dumps(questions)
        snippet = text[:3000]
        return instruction + "Website text:\n" + snippet + tail

    def _mock_extract(self, text: str, questions: List[str] = None) -> Dict[str,Any]:
        industry = "Unknown"
        lt = text.lower()
        if "software" in lt or "app" in lt or "saas" in lt: industry = "Software / SaaS"
        elif "bank" in lt or "finance" in lt: industry = "Finance"
        elif "clinic" in lt or "doctor" in lt: industry = "Healthcare"
        company_size = "Unknown"
        m = re.search(r'(\d{1,5})\s+employees', lt)
        if m: company_size = m.group(1) + " employees"
        location = "Unknown"
        m = re.search(r'headquartered in ([A-Za-z0-9 ,\-]+)', text)
        if m: location = m.group(1).strip()
        contacts = {"emails": re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', text)[:5], "phones": re.findall(r'\+?\d[\d\-\s\(\)]{7,}\d', text)[:5]}
        usp = text.split("\n")[0][:200]
        core_products = (text.split("\n")[1] if "\n" in text else "")[:300]
        target = "Consumers" if "consumer" in lt or "for customers" in lt else "Businesses"
        sentiment = "neutral"
        summary = (text[:400] + "...") if len(text) > 400 else text
        return {
            "industry": industry,
            "company_size": company_size,
            "location": location,
            "usp": usp,
            "core_products": core_products,
            "target_audience": target,
            "contacts": contacts,
            "sentiment": sentiment,
            "summary": summary
        }

    def _mock_answer(self, query: str, context: str) -> str:
        q = query.lower()
        if "industry" in q:
            return self._mock_extract(context).get("industry", "Unknown")
        if "location" in q or "headquart" in q:
            return self._mock_extract(context).get("location", "Unknown")
        return context[:600]