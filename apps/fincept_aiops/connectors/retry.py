"""Retry + circuit-breaker decorator for external connector calls."""
import logging
from functools import wraps
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)


def with_retry(stop_attempts: int = 3, wait_min: float = 1.0, wait_max: float = 10.0):
    """Decorator: retry up to stop_attempts times with exponential backoff."""
    def decorator(fn):
        @retry(
            stop=stop_after_attempt(stop_attempts),
            wait=wait_exponential(multiplier=1, min=wait_min, max=wait_max),
            retry=retry_if_exception_type(Exception),
            reraise=True,
        )
        @wraps(fn)
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)
        return wrapper
    return decorator
