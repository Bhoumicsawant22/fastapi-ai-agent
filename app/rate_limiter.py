import time
from fastapi import Request, HTTPException
from starlette.status import HTTP_429_TOO_MANY_REQUESTS

class RateLimiterDependency:
    def __init__(self, max_requests: int = 30, period_seconds: int = 60):
        self.max = max_requests
        self.period = period_seconds
        self._store = {}  # { key: [timestamps...] }

    async def __call__(self, request: Request):
        now = time.time()
        ip = request.client.host or "unknown"
        key = f"{ip}:{request.headers.get('authorization','')}"
        arr = self._store.get(key, [])
        # keep timestamps inside window
        arr = [t for t in arr if t > now - self.period]
        if len(arr) >= self.max:
            raise HTTPException(status_code=HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded")
        arr.append(now)
        self._store[key] = arr