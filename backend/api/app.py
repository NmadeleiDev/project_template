import logging
import time
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from api.exceptions import APIException
from api.routes import auth, user
from core.settings import app_settings


async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title=app_settings.app_name,
    description=app_settings.app_description,
    version="1.0.0",
    root_path="/api",
    lifespan=lifespan,
)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log requests and response times"""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        logger = logging.getLogger(__name__)

        # Get client IP
        client_ip = request.client.host if request.client else "unknown"

        # Log incoming request
        logger.info(
            f"Request: {request.method} {request.url.path} | "
            f"Client IP: {client_ip} | "
            f"Query params: {dict(request.query_params)}"
        )

        # Process request
        response = await call_next(request)

        # Calculate elapsed time
        elapsed_time = time.time() - start_time

        # Log response
        logger.info(
            f"Response: {request.method} {request.url.path} | "
            f"Status: {response.status_code} | "
            f"Time elapsed: {elapsed_time:.4f}s"
        )

        return response


# Add middleware
app.add_middleware(RequestLoggingMiddleware)


# Exception handler for custom API exceptions
@app.exception_handler(APIException)
async def api_exception_handler(request: Request, exc: APIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "internal_code": exc.internal_code,
            "detail": exc.detail,
            "status_code": exc.status_code,
        },
    )


# Health check
@app.get("/", tags=["Health"])
async def read_root():
    return "OK"


@app.get("/health", tags=["Health"])
async def health_check():
    return "OK"


@app.get("/ping", tags=["Health"])
async def ping():
    return "pong"


# Include routers
app.include_router(auth.router)
app.include_router(user.router)
