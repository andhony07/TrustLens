"""Main FastAPI entry point for TrustLens AI."""

import logging
from pathlib import Path
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import APP_NAME, APP_VERSION, TAGLINE, ALLOWED_ORIGINS
from app.api.routes import router as api_router

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("trustlens.main")

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=(
        f"**{TAGLINE}**\n\n"
        "TrustLens AI is a deterministic heuristic detection and risk-scoring platform designed to help students "
        "identify scam indicators in suspicious internship offers, scholarship messages, job postings, and URLs."
    ),
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Custom validation exception handler (clean error response, no stack traces)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        loc = " -> ".join(str(l) for l in err.get("loc", []))
        msg = err.get("msg", "Validation error")
        errors.append(f"{loc}: {msg}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "detail": errors[0] if len(errors) == 1 else errors,
            "status_code": 422,
        },
    )

# Include API routes
app.include_router(api_router)

# Mount frontend static directory if present
frontend_path = Path(__file__).resolve().parent.parent.parent / "frontend"
if frontend_path.exists() and frontend_path.is_dir():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")
    logger.info("Mounted frontend static files from %s", frontend_path)
