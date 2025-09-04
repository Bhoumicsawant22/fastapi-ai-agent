import httpx
from bs4 import BeautifulSoup
import re
from typing import Tuple, Dict

async def scrape_text(url: str, timeout: int = 15) -> Tuple[str, Dict]:
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; fastapi-ai-agent/1.0; +https://example.com)"
    }
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        r = await client.get(url)
        r.raise_for_status()
        html = r.text

    soup = BeautifulSoup(html, "lxml")
    parts = []
    if soup.title and soup.title.string:
        parts.append(soup.title.string.strip())
    meta = soup.find("meta", attrs={"name":"description"}) or soup.find("meta", attrs={"property":"og:description"})
    if meta and meta.get("content"):
        parts.append(meta.get("content").strip())
    # collect h1/h2/p
    for tag in soup.find_all(["h1","h2","p"]):
        text = tag.get_text(" ", strip=True)
        if text:
            parts.append(text)
    content = "\n".join(parts).strip()
    contacts = extract_contacts(html)
    return content, {"contacts": contacts}

def extract_contacts(text: str) -> Dict:
    emails = set(re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', text))
    phones = set(re.findall(r'\+?\d[\d\-\s\(\)]{7,}\d', text))
    # social links (simple)
    social = []
    for s in ["linkedin.com","facebook.com","twitter.com","instagram.com","t.me","wa.me"]:
        if s in text:
            social.append(s)
    return {"emails": list(emails), "phones": list(phones), "social": social}