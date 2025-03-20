import time
import random
import functools
from typing import Callable, Any, TypeVar, cast
import logging

T = TypeVar('T')

logger = logging.getLogger(__name__)

def retry_with_exponential_backoff(
    max_retries: int = 5,
    initial_delay: float = 1.0,
    exponential_base: float = 2,
    jitter: bool = True,
    max_delay: float = 60.0
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Retry a function with exponential backoff.
    
    Args:
        max_retries: Maximum number of retries
        initial_delay: Initial delay in seconds
        exponential_base: Base for exponential calculation
        jitter: Add random jitter to delay
        max_delay: Maximum delay in seconds
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            # Initialize variables
            num_retries = 0
            delay = initial_delay
            
            # Loop until max retries reached
            while True:
                try:
                    return func(*args, **kwargs)
                
                except Exception as e:
                    # Check if we've hit the max retries
                    num_retries += 1
                    if num_retries > max_retries:
                        logger.error(f"Max retries ({max_retries}) exceeded with exception: {str(e)}")
                        raise
                    
                    # Calculate next delay with exponential backoff
                    delay = min(delay * exponential_base, max_delay)
                    
                    # Add jitter if requested
                    if jitter:
                        delay = delay * (0.5 + random.random())
                    
                    logger.warning(f"Retrying in {delay:.2f} seconds after error: {str(e)}")
                    time.sleep(delay)
        
        return cast(Callable[..., T], wrapper)
    
    return decorator
