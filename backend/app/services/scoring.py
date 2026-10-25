"""Transparent heuristic scoring engine for TrustLens AI."""

from typing import List, Dict, Any, Tuple
from app.schemas import RiskLevel, SeverityLevel

SEVERITY_WEIGHTS = {
    SeverityLevel.CRITICAL: 35,
    SeverityLevel.HIGH: 24,
    SeverityLevel.MEDIUM: 14,
    SeverityLevel.LOW: 8,
}

# Specific high-risk rule weight overrides
RULE_WEIGHTS = {
    "FIN-01": 38,   # Upfront payment demand
    "FIN-02": 36,   # Crypto/gift cards
    "FIN-03": 35,   # Fake check overpayment
    "SENS-01": 38,  # OTP/password harvesting
    "SENS-02": 26,  # Excessive ID/SSN/banking
    "URL-02": 32,   # Direct IP address
    "URL-01": 22,   # Shortened URL
    "URL-03": 25,   # Lookalike brand domain
    "COMM-01": 24,  # Impersonating corporate brand via Gmail
    "COMM-02": 22,  # Off-platform Telegram/WhatsApp
    "EMP-01": 24,   # Guaranteed hire without interview
    "EMP-02": 16,   # $100/hr typing
    "SCHOL-01": 25, # Pay-to-claim scholarship
    "URG-01": 15,   # 2-hour deadline
    "URG-02": 25,   # Secrecy/bypass HR
    "URL-04": 15,   # Free forms for corporate hiring
}


def calculate_risk_score(
    findings: List[Dict[str, Any]],
    positive_signals: List[str]
) -> Tuple[int, RiskLevel]:
    """
    Calculate a bounded heuristic risk score (0-100) and assign an interpretable risk level.
    
    Bands:
      0  - 19: Low
      20 - 44: Moderate
      45 - 69: High
      70 - 100: Critical
    """
    if not findings:
        # No warning signs found
        return (0, RiskLevel.LOW)

    total_points = 0.0
    seen_evidence = set()
    critical_count = 0
    high_count = 0

    # Sort findings by severity descending so most severe rules contribute first
    sorted_findings = sorted(
        findings,
        key=lambda f: SEVERITY_WEIGHTS.get(f["severity"], 10),
        reverse=True
    )

    for idx, f in enumerate(sorted_findings):
        rule_id = f.get("rule_id", "")
        sev = f.get("severity", "medium")
        base_weight = RULE_WEIGHTS.get(rule_id, SEVERITY_WEIGHTS.get(sev, 15))

        if sev == "critical":
            critical_count += 1
        elif sev == "high":
            high_count += 1

        # Check for evidence overlap to suppress double-counting
        ev_tokens = tuple(sorted(f.get("matched_evidence", [])))
        overlap = ev_tokens in seen_evidence
        seen_evidence.add(ev_tokens)

        # Diminishing returns formula for successive findings
        # 1st finding: 100% weight, 2nd: 85%, 3rd: 70%, 4th+: 50%
        factor = 1.0 if idx == 0 else (0.85 if idx == 1 else (0.70 if idx == 2 else 0.50))
        if overlap:
            factor *= 0.5  # Substantial discount for duplicate evidence trigger

        total_points += base_weight * factor

    # Multi-flag synergy escalation (multiple distinct severe categories present)
    if critical_count >= 2:
        total_points += 15
    elif critical_count >= 1 and high_count >= 1:
        total_points += 10
    elif high_count >= 2:
        total_points += 8

    # Positive hygiene mitigation (mild, max -12 points)
    # Important safeguard: positive hygiene cannot sanitize critical scam indicators!
    mitigation = min(len(positive_signals) * 4, 12)
    if critical_count > 0:
        mitigation = min(mitigation, 4)  # Severely restrict mitigation if critical signs exist

    raw_score = total_points - mitigation
    rounded_score = int(round(raw_score))

    # Strict bounding [0, 100]
    bounded_score = max(0, min(100, rounded_score))

    # Ensure critical signs elevate into appropriate bands
    if critical_count >= 1 and bounded_score < 70:
        bounded_score = max(bounded_score, 70)
    elif high_count >= 1 and bounded_score < 45:
        bounded_score = max(bounded_score, 45)

    # Map to standardized category bands
    if bounded_score >= 70:
        level = RiskLevel.CRITICAL
    elif bounded_score >= 45:
        level = RiskLevel.HIGH
    elif bounded_score >= 20:
        level = RiskLevel.MODERATE
    else:
        level = RiskLevel.LOW

    return bounded_score, level
