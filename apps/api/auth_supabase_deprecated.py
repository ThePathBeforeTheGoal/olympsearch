# apps/api/auth.py
import os
import requests
from functools import lru_cache
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
ADMIN_EMAILS = os.getenv("ADMIN_EMAILS", "")

if not SUPABASE_URL:
    raise RuntimeError("SUPABASE_URL env is required")
if not SUPABASE_SERVICE_ROLE_KEY:
    # В деве можно временно работать без, но в проде должна быть.
    # raise RuntimeError("SUPABASE_SERVICE_ROLE_KEY env is required")
    pass

@lru_cache(maxsize=1)
def _supabase_user_endpoint():
    return f"{SUPABASE_URL.rstrip('/')}/auth/v1/user"

def _get_user_from_supabase_token(access_token: str):
    """Call Supabase admin endpoint to validate token and return user object."""
    if not SUPABASE_SERVICE_ROLE_KEY:
        return None
    url = _supabase_user_endpoint()
    headers = {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {access_token}",
    }
    try:
        r = requests.get(url, headers=headers, timeout=5)
    except requests.RequestException:
        return None
    if r.status_code == 200:
        return r.json()
    return None

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    # 1) validate via Supabase admin endpoint
    user = _get_user_from_supabase_token(token)
    if user:
        # expected fields: id (sub), email, aud, role, etc.
        return {
            "id": user.get("id") or user.get("sub"),
            "email": user.get("email"),
            "role": user.get("role", "authenticated"),
            "raw": user,
        }

    # 2) demo fallback (local testing)
    if token == "demo-user":
        return {"id": "demo-user", "email": "demo@example.com", "role": "demo"}

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

async def get_admin_user(user = Depends(get_current_user)):
    admin_emails = [e.strip() for e in ADMIN_EMAILS.split(",") if e.strip()]
    if user.get("email") in admin_emails:
        return user
    # можете дополнительно разрешить по списку UUID:
    # if user.get("id") in ADMIN_IDS: ...
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
