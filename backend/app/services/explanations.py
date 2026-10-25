"""Explanation generator and recommendations engine for TrustLens AI."""

from typing import List, Dict, Any
from app.schemas import RiskLevel


def generate_verdict_summary(
    risk_score: int,
    risk_level: RiskLevel,
    findings: List[Dict[str, Any]],
    positive_signals: List[str]
) -> str:
    """Generate a clear, measured, non-alarmist verdict summary."""
    if not findings:
        if positive_signals:
            return (
                "Low heuristic risk detected. Reassuring professional hygiene signals (such as verified domains or standard "
                "application procedures) were observed. Note: The absence of flags does not guarantee authenticity; remain vigilant."
            )
        return (
            "Minimal scam indicators detected based on heuristic analysis. While no immediate red flags were identified, "
            "always verify unsolicited correspondence through the organization's published directories."
        )

    categories = list(dict.fromkeys(f.get("category", "") for f in findings if f.get("category")))
    cat_text = ", ".join(categories[:3])

    if risk_level == RiskLevel.CRITICAL:
        return (
            f"Critical scam indicators identified (Risk Score: {risk_score}/100). The message exhibits acute red flags "
            f"in {cat_text.lower()}, including high-consequence solicitations such as upfront monetary demands or credential harvesting. "
            f"We strongly advise ceasing communication immediately."
        )
    elif risk_level == RiskLevel.HIGH:
        return (
            f"Substantial warning signs detected (Risk Score: {risk_score}/100). Characteristics associated with fraudulent "
            f"solicitations were observed in {cat_text.lower()}. Exercise extreme caution and do not provide funds or credentials."
        )
    elif risk_level == RiskLevel.MODERATE:
        return (
            f"Elevated caution advised (Risk Score: {risk_score}/100). Indicators such as {cat_text.lower()} warrant independent "
            f"verification before proceeding with any application or interview steps."
        )
    else:
        return (
            f"Low-level warning patterns observed (Risk Score: {risk_score}/100). Minor phrasing anomalies detected, "
            f"though without direct high-severity fraud mechanisms. Verify the sender independently."
        )


def generate_recommended_actions(
    findings: List[Dict[str, Any]],
    input_type: str = "message"
) -> List[str]:
    """Generate prioritized, actionable checklist tailored to the student's situation."""
    actions = []
    rule_ids = {f.get("rule_id", "") for f in findings}

    if "FIN-01" in rule_ids or "FIN-02" in rule_ids or "FIN-03" in rule_ids:
        actions.append("Do NOT send money, pay registration fees, purchase gift cards, or deposit unsolicited checks.")

    if "SENS-01" in rule_ids:
        actions.append("NEVER disclose One-Time Passwords (OTPs), 2FA codes, or account passwords to anyone.")

    if "SENS-02" in rule_ids:
        actions.append("Withhold sensitive personal identifiers (SSN, national ID numbers, banking login details).")

    if "URL-01" in rule_ids or "URL-02" in rule_ids or "URL-03" in rule_ids or "URL-04" in rule_ids:
        actions.append("Do not click links provided in the message; navigate directly to the company's verified careers website.")

    if "COMM-01" in rule_ids or "COMM-02" in rule_ids:
        actions.append("Decline off-platform communication on Telegram or WhatsApp; request all correspondence via official corporate email.")

    if "EMP-01" in rule_ids or "SCHOL-01" in rule_ids:
        actions.append("Check whether you previously submitted a formal application for this role or scholarship.")

    # Universal hygiene recommendations
    actions.append("Consult your university career center, placement officer, or trusted advisor before taking action.")
    actions.append("Report suspicious solicitations to your campus IT security desk or national fraud reporting portal.")

    # Deduplicate while preserving order
    deduped = []
    for act in actions:
        if act not in deduped:
            deduped.append(act)

    return deduped
