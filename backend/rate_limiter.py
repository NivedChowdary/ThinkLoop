"""
Rate limiter to prevent API abuse and control Claude API costs
Works as FastAPI dependency, not decorator
"""
from fastapi import Request, HTTPException
from datetime import datetime, timedelta
from collections import defaultdict
import threading

# In-memory storage for rate limits
# Format: {ip_address: {endpoint: [(timestamp1), (timestamp2), ...]}}
rate_limit_store = defaultdict(lambda: defaultdict(list))
store_lock = threading.Lock()

def clean_old_entries():
    """Remove entries older than 1 hour to prevent memory bloat"""
    with store_lock:
        current_time = datetime.now()
        for ip in list(rate_limit_store.keys()):
            for endpoint in list(rate_limit_store[ip].keys()):
                rate_limit_store[ip][endpoint] = [
                    ts for ts in rate_limit_store[ip][endpoint]
                    if current_time - ts < timedelta(hours=1)
                ]
                if not rate_limit_store[ip][endpoint]:
                    del rate_limit_store[ip][endpoint]
            if not rate_limit_store[ip]:
                del rate_limit_store[ip]

class RateLimiter:
    """
    Rate limiter as FastAPI dependency
    
    Usage in endpoint:
        @app.post("/signup")
        def signup(request: Request, limiter: None = Depends(RateLimiter(max_calls=5, window_seconds=3600))):
            ...
    """
    
    def __init__(self, max_calls: int, window_seconds: int):
        self.max_calls = max_calls
        self.window_seconds = window_seconds
    
    def __call__(self, request: Request):
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        endpoint = request.url.path
        
        # Clean old entries periodically
        if len(rate_limit_store) > 100:
            clean_old_entries()
        
        current_time = datetime.now()
        window_start = current_time - timedelta(seconds=self.window_seconds)
        
        with store_lock:
            # Get call history for this IP and endpoint
            call_history = rate_limit_store[client_ip][endpoint]
            
            # Remove calls outside the window
            call_history = [ts for ts in call_history if ts > window_start]
            rate_limit_store[client_ip][endpoint] = call_history
            
            # Check if limit exceeded
            if len(call_history) >= self.max_calls:
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded. Max {self.max_calls} calls per {self.window_seconds} seconds. Try again later."
                )
            
            # Add current call
            rate_limit_store[client_ip][endpoint].append(current_time)
        
        return None

# Pre-configured rate limiters for common use cases
signup_limiter = RateLimiter(max_calls=5, window_seconds=3600)  # 5 per hour
login_limiter = RateLimiter(max_calls=10, window_seconds=300)   # 10 per 5 min
job_limiter = RateLimiter(max_calls=20, window_seconds=3600)    # 20 per hour
candidate_limiter = RateLimiter(max_calls=50, window_seconds=3600)  # 50 per hour