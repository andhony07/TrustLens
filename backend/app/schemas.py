"""Data schemas and Pydantic validation models for TrustLens AI."""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from app.config import MIN_TEXT_LENGTH, MAX_TEXT_LENGTH


class InputType(str, Enum):
    JOB_OFFER = "job_offer"
    SCHOLARSHIP = "scholarship"
    MESSAGE = "message"
    URL = "url"


class RiskLevel(str, Enum):
    LOW = "Low"
    MODERATE = "Moderate"
    HIGH = "High"
    CRITICAL = "Critical"


class SeverityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AnalyzeRequest(BaseModel):
    text: str = Field(
        ...,
        description="The message, offer, or URL text to analyze for scam indicators.",
        min_length=MIN_TEXT_LENGTH,
        max_length=MAX_TEXT_LENGTH,
    )
    input_type: InputType = Field(
        default=InputType.MESSAGE,
        description="Category of the input text (job_offer, scholarship, message, url).",
    )
    language_hint: Optional[str] = Field(
        default="en",
        description="Optional ISO language hint (default: 'en').",
    )

    @field_validator("text")
    @classmethod
    def validate_non_whitespace(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Input text cannot be empty or contain only whitespace.")
        if len(trimmed) < MIN_TEXT_LENGTH:
            raise ValueError(f"Input text must contain at least {MIN_TEXT_LENGTH} non-whitespace characters.")
        if len(v) > MAX_TEXT_LENGTH:
            raise ValueError(f"Input text exceeds maximum allowed length of {MAX_TEXT_LENGTH} characters.")
        return v


class Finding(BaseModel):
    rule_id: str = Field(..., description="Unique identifier for the heuristic rule.")
    title: str = Field(..., description="Concise title of the detected warning sign.")
    category: str = Field(..., description="Broad category of the indicator.")
    severity: SeverityLevel = Field(..., description="Severity level: low, medium, high, or critical.")
    matched_evidence: List[str] = Field(
        default_factory=list,
        description="Key phrases, tokens, or indicators extracted from the input text.",
    )
    explanation: str = Field(..., description="Detailed explanation of why this indicator signals potential risk.")
    recommended_action: str = Field(..., description="Practical immediate step the student should take.")


class AnalyzeResponse(BaseModel):
    analysis_id: str = Field(..., description="Unique UUID identifier for this analysis run.")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp of the analysis.")
    input_type: str = Field(..., description="The verified input type assessed.")
    character_count: int = Field(..., description="Total character count of the analyzed input.")
    word_count: int = Field(..., description="Total word count of the analyzed input.")
    risk_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Calculated risk score bounded between 0 (very low risk) and 100 (critical risk).",
    )
    risk_level: RiskLevel = Field(..., description="Categorical risk rating: Low, Moderate, High, or Critical.")
    verdict_summary: str = Field(..., description="Concise, carefully worded assessment summary.")
    findings: List[Finding] = Field(
        default_factory=list,
        description="Identified suspicious indicators and red flags.",
    )
    positive_signals: List[str] = Field(
        default_factory=list,
        description="Positive indicators observed (does not guarantee legitimacy).",
    )
    recommended_actions: List[str] = Field(
        default_factory=list,
        description="Prioritized list of safe next steps for the user.",
    )
    analyzer_method: str = Field(
        default="heuristic_rule_engine",
        description="Methodology used for detection (deterministic rule engine).",
    )
    disclaimer: str = Field(
        default=(
            "Heuristic assessment based on pattern detection — not a definitive determination of fraud or authenticity. "
            "Never rely solely on automated analysis; verify directly through official institutional channels."
        ),
        description="Legal and operational limitations notice.",
    )


class HealthResponse(BaseModel):
    status: str = Field(default="ok")
    application_name: str = Field(default="TrustLens AI")
    analyzer_version: str = Field(default="1.0.0")
    timestamp: str
