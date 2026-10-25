"""Test analysis detection rules, scoring, contextual nuance, and response schemas."""

import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.schemas import RiskLevel


@pytest.fixture
def client():
    return TestClient(app)


def test_normal_legitimate_internship_message(client):
    """Test 5: Normal legitimate internship message produces low risk score and positive signals."""
    legitimate_text = (
        "Dear Alex,\n\n"
        "Thank you for submitting your application for the Summer 2026 Software Engineering Internship "
        "at Acorn Systems. We have reviewed your resume and would like to invite you to complete a "
        "technical coding assessment through our portal at https://careers.acorn.edu/internships. "
        "Our team will review applications over the next two weeks. We do not charge any fee for applications or onboarding."
    )
    response = client.post("/api/analyze", json={"text": legitimate_text, "input_type": "job_offer"})
    assert response.status_code == 200
    data = response.json()
    assert data["risk_score"] < 20
    assert data["risk_level"] == RiskLevel.LOW.value
    assert len(data["positive_signals"]) > 0
    assert any("fee" in sig.lower() for sig in data["positive_signals"])


def test_message_requesting_upfront_fee(client):
    """Test 6: Message demanding upfront registration fee triggers critical risk."""
    scam_text = (
        "Congratulations! You have been selected for the Data Analyst Internship at Tech Global. "
        "To confirm your laptop dispatch and secure your placement, you are required to pay a registration fee of $150 "
        "refundable deposit before Monday."
    )
    response = client.post("/api/analyze", json={"text": scam_text, "input_type": "job_offer"})
    assert response.status_code == 200
    data = response.json()
    assert data["risk_score"] >= 70
    assert data["risk_level"] == RiskLevel.CRITICAL.value
    rule_ids = [f["rule_id"] for f in data["findings"]]
    assert "FIN-01" in rule_ids
    assert any("registration fee" in ev.lower() or "deposit" in ev.lower() for f in data["findings"] for ev in f["matched_evidence"])


def test_scholarship_message_requesting_otp(client):
    """Test 7: Scholarship message requesting an OTP triggers critical credential-harvesting warning."""
    otp_text = (
        "National Merit Scholarship Notification: Your grant of $3,500 is ready for transfer. "
        "Please provide the 6-digit code received on your phone to verify your bank account and release the funds."
    )
    response = client.post("/api/analyze", json={"text": otp_text, "input_type": "scholarship"})
    assert response.status_code == 200
    data = response.json()
    assert data["risk_score"] >= 70
    assert data["risk_level"] == RiskLevel.CRITICAL.value
    rule_ids = [f["rule_id"] for f in data["findings"]]
    assert "SENS-01" in rule_ids


def test_artificial_urgency_and_financial_pressure(client):
    """Test 8: Message combining tight deadline threats and wire transfer."""
    urgency_text = (
        "URGENT: Your student internship stipend has been issued. Immediate response required within 2 hours or the offer "
        "will be revoked! Purchase Apple gift card of $100 and send the code to verify your account."
    )
    response = client.post("/api/analyze", json={"text": urgency_text, "input_type": "message"})
    assert response.status_code == 200
    data = response.json()
    assert data["risk_score"] >= 70
    assert data["risk_level"] == RiskLevel.CRITICAL.value
    rule_ids = [f["rule_id"] for f in data["findings"]]
    assert "URG-01" in rule_ids
    assert "FIN-02" in rule_ids


def test_suspicious_url_indicators(client):
    """Test 9: Suspicious URL indicators like shorteners, IP addresses, and brand lookalikes."""
    url_text = (
        "Click here to claim your guaranteed research fellowship: http://bit.ly/fellowship2026 "
        "or visit http://192.168.1.100/login to submit your bank credentials."
    )
    response = client.post("/api/analyze", json={"text": url_text, "input_type": "url"})
    assert response.status_code == 200
    data = response.json()
    rule_ids = [f["rule_id"] for f in data["findings"]]
    assert "URL-01" in rule_ids or "URL-02" in rule_ids
    assert data["risk_score"] >= 45


def test_safe_educational_discussion_containing_otp_and_payment(client):
    """Test 10: Educational context containing words like OTP and payment is not falsely flagged."""
    edu_text = (
        "In our university cybersecurity class today, we discussed security awareness. "
        "Our professor gave an example of a scam and emphasized: never share your OTP with anyone, "
        "and legitimate companies will not ask for payment or a registration fee."
    )
    response = client.post("/api/analyze", json={"text": edu_text, "input_type": "message"})
    assert response.status_code == 200
    data = response.json()
    # Should not trigger false positive critical findings for OTP or payment because of negation and educational context
    rule_ids = [f["rule_id"] for f in data["findings"]]
    assert "SENS-01" not in rule_ids
    assert "FIN-01" not in rule_ids
    assert data["risk_level"] == RiskLevel.LOW.value


def test_duplicate_evidence_suppression(client):
    """Test 11: Duplicate triggers do not cause runaway inflation of the risk score."""
    dup_text = (
        "Please pay the registration fee today. The registration fee is mandatory. "
        "Pay the registration fee to our manager immediately."
    )
    response = client.post("/api/analyze", json={"text": dup_text, "input_type": "job_offer"})
    assert response.status_code == 200
    data = response.json()
    fin01_findings = [f for f in data["findings"] if f["rule_id"] == "FIN-01"]
    assert len(fin01_findings) == 1  # Deduplicated into a single unified finding
    assert data["risk_score"] <= 100


def test_score_bounded_between_zero_and_hundred(client):
    """Test 12: Extreme accumulation of scam phrases does not exceed 100."""
    extreme_scam = (
        "Congratulations! 100% guaranteed selection without interview! Immediate response required within 2 hours. "
        "Pay registration fee of $500 via Bitcoin or Apple gift card. Share your OTP and bank account login. "
        "Contact HR on Telegram @scam_recruiter and visit http://192.168.1.1/phish. Do not contact company office!"
    )
    response = client.post("/api/analyze", json={"text": extreme_scam, "input_type": "job_offer"})
    assert response.status_code == 200
    data = response.json()
    assert 0 <= data["risk_score"] <= 100
    assert data["risk_score"] >= 85
    assert data["risk_level"] == RiskLevel.CRITICAL.value


def test_risk_level_matches_score_bands(client):
    """Test 13: Risk level strictly conforms to documented scoring bands."""
    bands = [
        ("Acorn University officially announces the campus library schedule for 2026.", RiskLevel.LOW),
        ("Earn $150 per day for simple 1-hour typing task from home.", RiskLevel.MODERATE),
        ("Selected without interview! Contact HR recruiter via Telegram @recruiter_job.", RiskLevel.HIGH),
        ("Urgent: Pay $200 laptop deposit via gift card within 2 hours or offer is revoked.", RiskLevel.CRITICAL),
    ]
    for text_sample, expected_level in bands:
        response = client.post("/api/analyze", json={"text": text_sample, "input_type": "message"})
        assert response.status_code == 200
        data = response.json()
        score = data["risk_score"]
        level = data["risk_level"]

        if score >= 70:
            assert level == RiskLevel.CRITICAL.value
        elif score >= 45:
            assert level == RiskLevel.HIGH.value
        elif score >= 20:
            assert level == RiskLevel.MODERATE.value
        else:
            assert level == RiskLevel.LOW.value


def test_response_schema_contains_required_fields(client):
    """Test 14: Response schema contains all non-negotiable fields."""
    sample_text = "Internship offer: You are selected without interview. Pay $50 registration fee."
    response = client.post("/api/analyze", json={"text": sample_text, "input_type": "job_offer"})
    assert response.status_code == 200
    data = response.json()

    # Core non-negotiable fields
    required_keys = [
        "analysis_id",
        "risk_score",
        "risk_level",
        "verdict_summary",
        "findings",
        "positive_signals",
        "recommended_actions",
        "analyzer_method",
        "disclaimer",
    ]
    for key in required_keys:
        assert key in data, f"Missing required response field: {key}"

    # Finding sub-fields
    if data["findings"]:
        f = data["findings"][0]
        finding_keys = ["rule_id", "title", "severity", "matched_evidence", "explanation", "recommended_action"]
        for fk in finding_keys:
            assert fk in f, f"Missing finding field: {fk}"
