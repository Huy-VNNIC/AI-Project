"""
Logging middleware for structured JSON logs
"""
import time
import json
import logging
from datetime import datetime
from pathlib import Path
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import os

# Setup logging
LOG_DIR = Path(os.getenv('LOG_DIR', 'logs'))
LOG_DIR.mkdir(parents=True, exist_ok=True)

log_file = LOG_DIR / f"api_{datetime.now().strftime('%Y%m%d')}.log"

# JSON formatter
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
        }
        
        # Add extra fields if present
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
        if hasattr(record, 'method'):
            log_data['method'] = record.method
        if hasattr(record, 'path'):
            log_data['path'] = record.path
        if hasattr(record, 'status_code'):
            log_data['status_code'] = record.status_code
        if hasattr(record, 'duration_ms'):
            log_data['duration_ms'] = record.duration_ms
        if hasattr(record, 'user_agent'):
            log_data['user_agent'] = record.user_agent
        
        return json.dumps(log_data)


# Configure logger
logger = logging.getLogger('api')
logger.setLevel(logging.INFO)

# File handler
file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(JSONFormatter())
logger.addHandler(file_handler)

# Console handler (for development)
console_handler = logging.StreamHandler()
console_handler.setFormatter(JSONFormatter())
logger.addHandler(console_handler)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Structured logging middleware
    
    Logs:
    - Request method, path, headers
    - Response status code
    - Request duration
    - Errors
    """
    
    async def dispatch(self, request: Request, call_next):
        # Generate request ID
        request_id = f"{int(time.time() * 1000)}"
        
        # Start timer
        start_time = time.time()
        
        # Log request
        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={
                'request_id': request_id,
                'method': request.method,
                'path': request.url.path,
                'user_agent': request.headers.get('user-agent', 'unknown')
            }
        )
        
        # Add request ID to request state
        request.state.request_id = request_id
        
        try:
            # Process request
            response: Response = await call_next(request)
            
            # Calculate duration
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Log response
            logger.info(
                f"Request completed: {request.method} {request.url.path} - {response.status_code}",
                extra={
                    'request_id': request_id,
                    'method': request.method,
                    'path': request.url.path,
                    'status_code': response.status_code,
                    'duration_ms': duration_ms,
                    'user_agent': request.headers.get('user-agent', 'unknown')
                }
            )
            
            # Add request ID to response headers
            response.headers['X-Request-ID'] = request_id
            
            return response
        
        except Exception as e:
            # Calculate duration
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Log error
            logger.error(
                f"Request failed: {request.method} {request.url.path} - {str(e)}",
                extra={
                    'request_id': request_id,
                    'method': request.method,
                    'path': request.url.path,
                    'duration_ms': duration_ms,
                    'user_agent': request.headers.get('user-agent', 'unknown')
                },
                exc_info=True
            )
            
            raise


def log_generation_event(
    request_id: str,
    mode: str,
    num_sentences: int,
    num_requirements: int,
    num_tasks: int,
    latency_ms: int,
    avg_confidence: float,
    quality_gates: dict
):
    """
    Log task generation event with metrics
    """
    logger.info(
        "Task generation completed",
        extra={
            'request_id': request_id,
            'mode': mode,
            'num_sentences': num_sentences,
            'num_requirements': num_requirements,
            'num_tasks': num_tasks,
            'latency_ms': latency_ms,
            'avg_confidence': round(avg_confidence, 4),
            'quality_gates': quality_gates
        }
    )


def log_feedback_event(
    request_id: str,
    task_id: str,
    rating: int = None,
    has_edits: bool = False
):
    """
    Log feedback submission event
    """
    logger.info(
        "Feedback received",
        extra={
            'request_id': request_id,
            'task_id': task_id,
            'rating': rating,
            'has_edits': has_edits
        }
    )
