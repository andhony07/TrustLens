# TrustLens AI 🔍🛡️

> **"See the warning signs before you trust the message."**  
> *A deterministic scam-detection and explainable risk-scoring platform empowering students to assess suspicious internship offers, scholarship messages, job postings, URLs, and forwarded texts.*

---

## 1. Project Purpose

College and university students are increasingly targeted by sophisticated employment scams, predatory scholarship schemes, and credential-harvesting attacks. Fraudulent recruiters exploit urgency, fake corporate branding, and financial pressure, promising high-paying remote roles while demanding "laptop deposits", registration fees, or 2FA verification codes (OTPs).

**TrustLens AI** is an explainable, privacy-first cybersecurity triage tool built for the **Glitchathon Hackathon**. It evaluates untrusted solicitations in real time, extracts concrete evidence, calculates an interpretable **0–100 risk score**, and delivers actionable, student-centric safety recommendations.

---

## 2. Key Features

- **Dual-View Architecture (Home & Analyzer):**
  - **Dedicated Product Landing Page (`#home`):** Hero section featuring *"Think before you trust"*, interactive threat interception simulation card, four detection category breakdowns, a 3-step workflow, explainability feature highlights, and privacy/limitations architecture.
  - **Professional SOC Workspace Dashboard (`#analyzer`):** Full cybersecurity analysis environment with a persistent left sidebar, live recent count, radar-pulse empty state, circular SVG risk gauge, and responsive 2-column evidence breakdown.
- **Client-Side Hash-Based Navigation:** Seamless switching between Home and Analyzer views (`#home` vs `#analyzer`) with full browser Back/Forward history support, instant deep-linking, and refresh persistence.
- **Explainable Heuristic Engine:** Deterministic rule-based detection across 5 core categories—no black-box hallucinations or simulated AI claims.
- **Interpretable Risk Scoring (0–100):** Weighted risk aggregation with diminishing returns, multi-flag synergy escalation, and duplicate-evidence suppression.
- **Categorical Risk Bands:**
  - `0–19`: **Low** (hygiene signals present, standard caution advised)
  - `20–44`: **Moderate** (atypical patterns, elevated diligence required)
  - `45–69`: **High** (substantial red flags detected, independent verification mandatory)
  - `70–100`: **Critical** (severe threats: upfront fee demands, OTP harvesting, fake checks)
- **Session-Only Recent Analyses:** Quick-access history of up to 5 evaluations stored in JavaScript memory only. Revisit past assessments with zero API re-requests; raw user text is never retained in memory, and data disappears on tab closure or refresh. Includes an accessible clear-history confirmation flow.
- **Enhanced 4-Section Educational Modal:** Comprehensive breakdown covering:
  - *Section A:* Deterministic pattern analysis principles.
  - *Section B:* Interpretable score bands and heuristic definitions.
  - *Section C:* Implemented detector signals (`FIN`, `URG`, `SENS`, `URL`, `EMP`, and negation context safeguards).
  - *Section D:* Privacy architecture, volatile memory processing, and deployment caveats.
- **Contextual Nuance & Negation Awareness:** Recognizes educational reminders and negation phrases (e.g., *"never share your OTP"*, *"we do not charge fees"*) to prevent false positives.
- **Positive Hygiene Signals:** Identifies reassuring indicators (accredited `.edu`/`.gov` domains, enterprise ATS portals, explicit no-fee policies, multi-round technical assessments) without treating them as an absolute guarantee of authenticity.
- **Zero Data Retention (Privacy-First):** In-memory processing only. User inputs are never logged, stored in databases, or forwarded to external third parties.
- **XSS-Resistant Safe Rendering:** All findings, summaries, and historical records are rendered through secure DOM construction (`textContent`) to eliminate script injection risks.
- **Actionable Student Next Steps:** Prioritized guidance (refusing off-platform messaging, contacting university career desks, reporting fraud).
- **One-Click Assessment Export:** Copy structured markdown assessment reports directly to the clipboard.
- **Responsive Dark SaaS Interface:** Cybersecurity aesthetic with SVG circular risk gauges, accessible focus states, and sample messages.

---

## 3. Architecture

TrustLens AI maintains a clean separation of concerns between its Python backend and vanilla web frontend:

```
trustlens-ai/
├── backend/
│   ├── app/
│   │   ├── __init__.py           # Application package definition
│   │   ├── main.py               # FastAPI entry point, CORS, static mounting
│   │   ├── config.py             # App settings, origins, limits
│   │   ├── schemas.py            # Pydantic validation models & enums
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── routes.py         # /api/health and /api/analyze endpoints
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── analyzer.py       # Orchestration pipeline
│   │       ├── detectors.py      # Deterministic regex & contextual detectors
│   │       ├── scoring.py        # Non-linear weighted scoring algorithm
│   │       └── explanations.py   # Verdict generation & actionable recommendations
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_health.py        # Health & documentation route tests
│   │   ├── test_validation.py    # Empty, whitespace, oversized input tests
│   │   └── test_analysis.py      # Detection accuracy, negation & band tests
│   └── requirements.txt          # Python dependencies
├── frontend/
│   ├── index.html                # Semantic, accessible HTML5 layout
│   ├── styles.css                # Dark cybersecurity SaaS design tokens
│   └── app.js                    # ES6+ client logic, async fetch, animations
├── .gitignore
└── README.md
```

---

## 4. System Requirements

- **Python:** 3.12+ (or 3.14+)
- **OS:** Windows, macOS, or Linux
- **Browser:** Any modern browser (Chrome, Edge, Firefox, Safari)
- **Zero External API Keys:** Operates 100% offline and locally.

---

## 5. Installation Instructions

Clone the repository and set up a virtual environment:

### Windows (PowerShell / Command Prompt)

```powershell
# Navigate into the project directory
cd E:\TrustLens

# Create virtual environment using uv or standard python venv
python -m venv .venv

# Activate the virtual environment
.venv\Scripts\activate

# Install backend dependencies
pip install -r backend/requirements.txt
```

### macOS / Linux (Bash)

```bash
cd trustlens-ai
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

---

## 6. Startup Commands

### Option A: Unified Full-Stack Server (Recommended)

FastAPI automatically serves the frontend static files at root `/` while exposing API endpoints at `/api`:

```bash
# From workspace root with .venv activated:
uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
```

Open your browser and navigate to:
- **Application UI:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Interactive Swagger API Docs:** [http://127.0.0.1:8000/api/docs](http://127.0.0.1:8000/api/docs)
- **Health Endpoint:** [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)

### Option B: Standalone Frontend Server (Decoupled Dev)

If you prefer running the frontend on a separate port (e.g., port 3000):

```bash
# Terminal 1 — Start Backend:
uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000

# Terminal 2 — Start Frontend Server:
python -m http.server 3000 --directory frontend
```

The frontend automatically connects to the backend at `http://127.0.0.1:8000` via configured CORS headers.

---

## 7. Example API Usage

### Health Check

**Request:**
```http
GET /api/health HTTP/1.1
Host: 127.0.0.1:8000
```

**Response (200 OK):**
```json
{
  "status": "ok",
  "application_name": "TrustLens AI",
  "analyzer_version": "1.0.0",
  "timestamp": "2026-10-25T08:18:52.932071+00:00"
}
```

### Risk Assessment

**Request:**
```http
POST /api/analyze HTTP/1.1
Host: 127.0.0.1:8000
Content-Type: application/json

{
  "text": "Congratulations! You have been selected for the Data Analyst Internship at Tech Global. Your stipend will be $3,500/month working from home. To confirm your laptop dispatch and secure your placement, you are required to pay a registration fee of $150 refundable deposit before Monday via Zelle or wire transfer. Immediate response required within 24 hours or the offer will be revoked!",
  "input_type": "job_offer",
  "language_hint": "en"
}
```

**Response (200 OK):**
```json
{
  "analysis_id": "c1f729b1-0428-406a-a6ea-8a56b26d36e2",
  "timestamp": "2026-10-25T08:20:28.910245+00:00",
  "input_type": "job_offer",
  "character_count": 397,
  "word_count": 59,
  "risk_score": 79,
  "risk_level": "Critical",
  "verdict_summary": "Critical scam indicators identified (Risk Score: 79/100). The message exhibits acute red flags in financial manipulation, urgency and pressure, employment & scholarship red flags, including high-consequence solicitations such as upfront monetary demands or credential harvesting. We strongly advise ceasing communication immediately.",
  "findings": [
    {
      "rule_id": "FIN-01",
      "title": "Mandatory Upfront Fee or Deposit Demand",
      "category": "Financial Manipulation",
      "severity": "critical",
      "matched_evidence": [
        "registration fee",
        "refundable deposit"
      ],
      "explanation": "Legitimate employers and official scholarship foundations never ask candidates or students to pay application fees, training charges, laptop deposits, or onboarding expenses out of pocket.",
      "recommended_action": "Do not transfer any money. Real internships and scholarships do not charge students to participate."
    },
    {
      "rule_id": "URG-01",
      "title": "Artificial Urgency and Manufactured Pressure",
      "category": "Urgency and Pressure",
      "severity": "medium",
      "matched_evidence": [
        "within 24 hours",
        "Immediate response required",
        "offer will be revoked"
      ],
      "explanation": "Scammers create artificial deadlines and urgency to trigger panic, rushing victims into hasty decisions before they have time to consult parents, university advisors, or official company directories.",
      "recommended_action": "Take your time. Legitimate recruiters and universities allow reasonable time to evaluate legitimate offers."
    },
    {
      "rule_id": "EMP-01",
      "title": "Guaranteed Selection Without Formal Evaluation",
      "category": "Employment & Scholarship Red Flags",
      "severity": "high",
      "matched_evidence": [
        "Congratulations! You have been selected"
      ],
      "explanation": "Real companies and research labs screen candidates through interviews, technical challenges, and reference reviews. Offers delivered with zero prior application or evaluation are almost universally fraudulent.",
      "recommended_action": "Verify if you ever applied to this company. Authentic recruiters do not hire blind candidates via unsolicited text."
    }
  ],
  "positive_signals": [],
  "recommended_actions": [
    "Do NOT send money, pay registration fees, purchase gift cards, or deposit unsolicited checks.",
    "Check whether you previously submitted a formal application for this role or scholarship.",
    "Consult your university career center, placement officer, or trusted advisor before taking action.",
    "Report suspicious solicitations to your campus IT security desk or national fraud reporting portal."
  ],
  "analyzer_method": "heuristic_rule_engine",
  "disclaimer": "Heuristic assessment based on pattern detection — not a definitive determination of fraud or authenticity. Never rely solely on automated analysis; verify directly through official institutional channels."
}
```

---

## 8. Detection Limitations & Ethical Disclaimers

1. **Heuristic Guidepost, Not Legal Proof:** TrustLens AI uses transparent pattern matching and structural indicators. A high risk score indicates strong congruence with known scam strategies, but does not constitute a formal forensic verdict.
2. **Absence of Proof is Not Proof of Absence:** A score of `0` indicates that no explicit indicators were triggered; it does not guarantee that a sender is authentic. Attackers may send neutral introductory greetings before escalating to fraudulent demands.
3. **No External Threat Intelligence Lookup in Baseline:** The baseline engine operates strictly offline without calling external paid DNS or malware domain intelligence feeds.
4. **Student Privacy Protection:** Messages are analyzed in volatile memory. No text bodies, IP addresses, or student information are persisted.

---

## 9. Automated Testing

The suite includes 16 test cases covering health checks, OpenAPI specifications, input constraints, empty/whitespace/oversized inputs, detection rules, contextual negation, score bounds, and schema contracts.

Run the tests using `pytest`:

```bash
pytest backend/tests -v
```

**Actual Test Suite Output:**
```
============================= test session starts =============================
platform win32 -- Python 3.14.6, pytest-9.1.1, pluggy-1.7.0
rootdir: E:\TrustLens
collected 16 items

backend/tests/test_analysis.py::test_normal_legitimate_internship_message PASSED [  6%]
backend/tests/test_analysis.py::test_message_requesting_upfront_fee PASSED [ 12%]
backend/tests/test_analysis.py::test_scholarship_message_requesting_otp PASSED [ 18%]
backend/tests/test_analysis.py::test_artificial_urgency_and_financial_pressure PASSED [ 25%]
backend/tests/test_analysis.py::test_suspicious_url_indicators PASSED    [ 31%]
backend/tests/test_analysis.py::test_safe_educational_discussion_containing_otp_and_payment PASSED [ 37%]
backend/tests/test_analysis.py::test_duplicate_evidence_suppression PASSED [ 43%]
backend/tests/test_analysis.py::test_score_bounded_between_zero_and_hundred PASSED [ 50%]
backend/tests/test_analysis.py::test_risk_level_matches_score_bands PASSED [ 56%]
backend/tests/test_analysis.py::test_response_schema_contains_required_fields PASSED [ 62%]
backend/tests/test_health.py::test_health_endpoint_success PASSED        [ 68%]
backend/tests/test_health.py::test_swagger_documentation_accessible PASSED [ 75%]
backend/tests/test_validation.py::test_empty_input_rejection PASSED      [ 81%]
backend/tests/test_validation.py::test_whitespace_only_input_rejection PASSED [ 87%]
backend/tests/test_validation.py::test_oversized_input_rejection PASSED  [ 93%]
backend/tests/test_validation.py::test_unexpected_input_types_and_malformed_requests PASSED [100%]

======================= 16 passed, 5 warnings in 1.73s ========================
```

---

## 10. AI-Assisted Development Disclosure

In accordance with Glitchathon guidelines:
- **Architecture & System Design:** Designed by full-stack engineering principles with clear separation of FastAPI services, Pydantic schemas, and vanilla ES6+ frontend.
- **Assisting AI Model:** Antigravity AI Coding Assistant (Gemini 3.8 Flash High).
- **Human Guidance & Review:** Code was reviewed, verified, and debugged against live test suites, validating contextual negation rules, UI design tokens, and live API endpoints.
