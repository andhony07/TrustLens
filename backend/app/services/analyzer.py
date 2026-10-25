"""Core analysis pipeline coordinating detectors, scoring, and explanations."""

import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any

from app.schemas import AnalyzeRequest, AnalyzeResponse, Finding, RiskLevel, SeverityLevel
from app.services.detectors import (
    detect_financial_manipulation,
    detect_urgency_and_pressure,
    detect_sensitive_information_requests,
    detect_suspicious_urls_and_comms,
    detect_employment_and_scholarship_red_flags,
    detect_positive_signals,
)
from app.services.scoring import calculate_risk_score
from app.services.explanations import generate_verdict_summary, generate_recommended_actions


def analyze_text(request: AnalyzeRequest) -> AnalyzeResponse:
    """Execute complete deterministic heuristic analysis on the input text."""
    raw_text = request.text
    input_type = request.input_type.value

    # Normalize metrics
    char_count = len(raw_text)
    word_count = len(raw_text.split())

    # Run detectors
    raw_findings: List[Dict[str, Any]] = []
    raw_findings.extend(detect_financial_manipulation(raw_text))
    raw_findings.extend(detect_urgency_and_pressure(raw_text))
    raw_findings.extend(detect_sensitive_information_requests(raw_text))
    raw_findings.extend(detect_suspicious_urls_and_comms(raw_text))
    raw_findings.extend(detect_employment_and_scholarship_red_flags(raw_text, input_type))

    # Detect positive signals
    positive_signals = detect_positive_signals(raw_text)

    # Calculate bounded risk score and qualitative level
    risk_score, risk_level = calculate_risk_score(raw_findings, positive_signals)

    # Generate explanations & actions
    verdict_summary = generate_verdict_summary(risk_score, risk_level, raw_findings, positive_signals)
    recommended_actions = generate_recommended_actions(raw_findings, input_type)

    # Convert raw findings into Pydantic Finding objects
    typed_findings: List[Finding] = []
    for rf in raw_findings:
        typed_findings.append(Finding(
            rule_id=rf["rule_id"],
            title=rf["title"],
            category=rf.get("category", "General Indicator"),
            severity=SeverityLevel(rf.get("severity", "medium")),
            matched_evidence=rf.get("matched_evidence", []),
            explanation=rf["explanation"],
            recommended_action=rf["recommended_action"],
        ))

    return AnalyzeResponse(
        analysis_id=str(uuid.uuid4()),
        timestamp=datetime.now(timezone.utc).isoformat(),
        input_type=input_type,
        character_count=char_count,
        word_count=word_count,
        risk_score=risk_score,
        risk_level=risk_level,
        verdict_summary=verdict_summary,
        findings=typed_findings,
        positive_signals=positive_signals,
        recommended_actions=recommended_actions,
        analyzer_method="heuristic_rule_engine",
        disclaimer=(
            "Heuristic assessment based on pattern detection — not a definitive determination of fraud or authenticity. "
            "Never rely solely on automated analysis; verify directly through official institutional channels."
        ),
    )
