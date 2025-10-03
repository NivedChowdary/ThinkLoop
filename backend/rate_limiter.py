"""
Rate limiter to prevent API abuse and control Claude API costs
"""
from fastapi import Request, HTTPException
from functools import wraps
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

def rate_limit(max_calls: int, window_seconds: int):
    """
    Decorator to rate limit API endpoints
    
    Args:
        max_calls: Maximum number of calls allowed
        window_seconds: Time window in seconds
    
    Example:
        @rate_limit(max_calls=10, window_seconds=60)  # 10 calls per minute
        def my_endpoint():
            pass
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get request object from kwargs
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                # If no request found in args, check kwargs
                request = kwargs.get('request')
            
            if not request:
                # No request object, skip rate limiting
                # This happens when endpoint doesn't have Request as parameter
                # We'll get IP from the first argument if it's FastAPI's automatic injection
                return await func(*args, **kwargs) if callable(func) and hasattr(func, '__name__') else func(*args, **kwargs)
            
            # Get client IP
            client_ip = request.client.host if request.client else "unknown"
            endpoint = request.url.path
            
            # Clean old entries periodically
            if len(rate_limit_store) > 100:  # Clean when storage gets large
                clean_old_entries()
            
            current_time = datetime.now()
            window_start = current_time - timedelta(seconds=window_seconds)
            
            with store_lock:
                # Get call history for this IP and endpoint
                call_history = rate_limit_store[client_ip][endpoint]
                
                # Remove calls outside the window
                call_history = [ts for ts in call_history if ts > window_start]
                rate_limit_store[client_ip][endpoint] = call_history
                
                # Check if limit exceeded
                if len(call_history) >= max_calls:
                    raise HTTPException(
                        status_code=429,
                        detail=f"Rate limit exceeded. Max {max_calls} calls per {window_seconds} seconds. Try again later."
                    )
                
                # Add current call
                rate_limit_store[client_ip][endpoint].append(current_time)
            
            # Call the actual function
            return await func(*args, **kwargs) if callable(func) and hasattr(func, '__name__') else func(*args, **kwargs)
        
        return wrapper
    return decorator

# For production: Consider using Redis for distributed rate limiting
# This in-memory solution works for single-server deployments
# For multi-server: Use Redis with the following structure:
"""
import redis
from fastapi import Request, HTTPException
from functools import wraps
from datetime import datetime

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def rate_limit_redis(max_calls: int, window_seconds: int):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = kwargs.get('request')
            if not request:
                return await func(*args, **kwargs)
            
            client_ip = request.client.host
            endpoint = request.url.path
            key = f"rate_limit:{client_ip}:{endpoint}"
            
            # Increment counter
            current = redis_client.incr(key)
            
            # Set expiry on first call
            if current == 1:
                redis_client.expire(key, window_seconds)
            
            if current > max_calls:
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded. Max {max_calls} calls per {window_seconds} seconds."
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator
"""