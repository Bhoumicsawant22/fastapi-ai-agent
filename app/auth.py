from fastapi import Header, HTTPException
import os
from dotenv import load_dotenv

load_dotenv()  # Load .env

SECRET_KEY = os.getenv("AGENT_SECRET_KEY")

def verify_token(authorization: str = Header(...)):
    """
    Verifies the Authorization header.
    Expected format: "Bearer <SECRET_KEY>"
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization")
    
    if authorization != f"Bearer {SECRET_KEY}":
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    return True
