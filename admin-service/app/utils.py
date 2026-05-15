from datetime import datetime
from typing import Optional
from fastapi import Request
import json


def serialize_for_audit(obj) -> Optional[str]:
    if obj is None:
        return None
    
    if hasattr(obj, "__dict__"):
        data = {k: v for k, v in obj.__dict__.items() if not k.startswith('_')}
        for k, v in data.items():
            if isinstance(v, datetime):
                data[k] = v.isoformat()
        return json.dumps(data, default=str, ensure_ascii=False)
    
    if isinstance(obj, dict):
        return json.dumps(obj, default=str, ensure_ascii=False)
    
    return str(obj)


def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def get_user_agent(request: Request) -> str:
    return request.headers.get("User-Agent", "")
