"""API endpoint handlers for TrustLens AI."""

from datetime import datetime, timezone
import logging
from fastapi import APIRouter, HTTPException, status
from app.config import APP_NAME, APP_VERSION
from app.schemas import AnalyzeRequest, AnalyzeResponse, HealthResponse
from app.services.analyzer import analyze_text

logger = logging.getLogger("trustlens.api")
router = APIRouter(prefix="/api", tags=["Scam Analysis"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health and Version Check",
    description="Returns service availability status, application name, and analyzer version.",
)
async def get_health() -> HealthResponse:
    """Return operational health status and metadata."""
    return HealthResponse(
        status="ok",
        application_name=APP_NAME,
        analyzer_version=APP_VERSION,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze Message for Scam Indicators",
    description=(
        "Performs a comprehensive, deterministic heuristic risk assessment on the provided message text. "
        "Extracts suspicious evidence, calculates an interpretable score (0-100), and provides actionable steps."
    ),
)
async def analyze_message(payload: AnalyzeRequest) -> AnalyzeResponse:
    """Analyze input text for deceptive patterns and calculate an explainable risk report."""
    try:
        # Note: We intentionally do NOT log the payload.text for user privacy preservation!
        logger.info("Executing scam risk analysis for input_type=%s, length=%d", payload.input_type.value, len(payload.text))
        result = analyze_text(payload)
        logger.info("Analysis complete: analysis_id=%s, risk_score=%d, level=%s", result.analysis_id, result.risk_score, result.risk_level.value)
        return result
    except ValueError as val_err:
        logger.warning("Validation rejection during analysis: %s", str(val_err))
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(val_err),
        )
    except Exception as exc:
        logger.error("Unexpected error during analysis: %s", str(exc), exc_info=False)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while analyzing the provided message. Please try again.",
        )
