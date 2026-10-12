
import logging
import time

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy import text
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.customers import router as customer_router
from app.api.predictions import router as prediction_router
from app.api.analytics import router as analytics_router
from app.api.recommendations import router as recommendation_router
from app.api.reports import router as report_router
from app.api.audit import router as audit_router

from app.core.exceptions import AppException
from app.core.logging_config import setup_logging
from app.db.session import SessionLocal


# --------------------------------------------------
# Logging
# --------------------------------------------------

setup_logging()

logger = logging.getLogger(__name__)


# --------------------------------------------------
# FastAPI Application
# --------------------------------------------------

app = FastAPI(
    title="Churn Intelligence Platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# Request Logging Middleware
# --------------------------------------------------

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time

    logger.info(
        "%s %s → %s | %.4fs",
        request.method,
        request.url.path,
        response.status_code,
        process_time
    )

    return response


# --------------------------------------------------
# Startup Event
# --------------------------------------------------

@app.on_event("startup")
async def startup_event():
    logger.info(
        "Churn Intelligence API started successfully"
    )


# --------------------------------------------------
# Application Exception Handler
# --------------------------------------------------

@app.exception_handler(AppException)
async def app_exception_handler(
    request: Request,
    exc: AppException
):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message
            }
        }
    )


# --------------------------------------------------
# HTTP Exception Handler
# --------------------------------------------------

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException
):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": str(exc.detail)
            }
        }
    )


# --------------------------------------------------
# Validation Exception Handler
# --------------------------------------------------

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid request data",
                "details": jsonable_encoder(
                    exc.errors()
                )
            }
        }
    )


# --------------------------------------------------
# General Exception Handler
# --------------------------------------------------

@app.exception_handler(Exception)
async def general_exception_handler(
    request: Request,
    exc: Exception
):
    logger.exception(
        "Unhandled exception occurred"
    )

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred"
            }
        }
    )


# --------------------------------------------------
# Routers
# --------------------------------------------------

app.include_router(auth_router)
app.include_router(customer_router)
app.include_router(prediction_router)
app.include_router(analytics_router)
app.include_router(recommendation_router)
app.include_router(report_router)
app.include_router(audit_router)


# --------------------------------------------------
# Root Endpoint
# --------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "Churn Intelligence API is running 🚀"
    }


# --------------------------------------------------
# Health Check
# --------------------------------------------------

@app.get("/health")
def health_check():

    db_status = "healthy"

    db = None

    try:
        db = SessionLocal()

        db.execute(
            text("SELECT 1")
        )

    except Exception:
        db_status = "unhealthy"

        logger.exception(
            "Database health check failed"
        )

    finally:
        if db:
            db.close()

    overall_status = (
        "healthy"
        if db_status == "healthy"
        else "degraded"
    )

    return {
        "status": overall_status,
        "service": "churn-intelligence-api",
        "version": "1.0.0",
        "database": db_status
    }
