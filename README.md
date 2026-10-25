TrustLens AI
Think before you trust.

An explainable, privacy-first scam-risk assessment tool that helps students evaluate suspicious internship offers, scholarship messages, job postings, URLs, and forwarded texts.

TrustLens AI is a local-first cybersecurity triage application built with FastAPI, Pydantic, HTML, CSS, and vanilla JavaScript. It uses a deterministic rule-based engine to identify suspicious patterns, explain the evidence, calculate a risk score from 0–100, and recommend practical next steps.
Important: TrustLens provides a heuristic assessment, not a definitive fraud verdict. Always verify offers through official channels.

Contents
- Why TrustLens?
- Features
- How It Works
- Risk Score Guide
- Technology Stack
- Project Structure
- Requirements
- Installation
- Run the Application
- API Reference
- Run Tests
- Privacy and Security
- Limitations
- AI-Assisted Development Disclosure
Why TrustLens?
Students may receive fraudulent internship offers, fake scholarship announcements, job postings, and messages designed to steal money or credentials. Common tactics include upfront fees, artificial deadlines, suspicious links, and requests for one-time passwords (OTPs).

TrustLens helps users spot warning signs before acting. Instead of returning only a label, it explains which indicators were detected and suggests what to do next.
Features
Two connected views
- Product landing page (#home) — introduces the product, threat categories, analysis workflow, explainability, and privacy principles.
- Analyzer workspace (#analyzer) — provides a focused message-analysis interface, risk gauge, evidence breakdown, and recommendations.
- Hash-based navigation — supports direct links, refresh persistence, and browser Back/Forward navigation between views.
Explainable risk analysis
- Deterministic rule-based detection rather than a generative model.
- Risk score from 0 to 100, with four risk bands.
- Weighted scoring with diminishing returns, multi-indicator escalation, and duplicate-evidence suppression.
- Findings include rule identifiers, categories, severity, matched evidence, explanations, and recommended actions.
- Context and negation safeguards help distinguish suspicious wording from educational warnings such as “never share your OTP.”
- Positive hygiene signals can identify reassuring context, but never prove that a message is legitimate.
Privacy-conscious interaction
- Recent analyses are held in JavaScript memory only, with up to five entries.
- History does not retain the original message text; it allows users to revisit structured reports without another API request.
- Recent history disappears when the page is refreshed or the tab is closed.
- The application is designed for local processing and does not require external API keys.
- Findings and history are rendered using safe DOM APIs such as textContent.
Useful workflow features
- Prioritized recommendations for suspicious messages.
- Copyable assessment reports in Markdown format.
- Responsive dark cybersecurity interface.
- Educational “How It Works” content covering detection, scoring, and limitations.
How It Works
1. Submit a message — paste an internship offer, scholarship message, job posting, or other suspicious text into the analyzer.
2. Inspect patterns — deterministic detectors look for known financial, urgency, credential, URL, and employment-related indicators.
3. Calculate risk — the scoring engine combines detected indicators and maps the result to a risk band.
4. Review evidence — inspect matched evidence, explanations, and severity rather than relying only on the score.
5. Choose a safer next step — follow the recommendations and verify the sender through official channels.
Risk score guide
Score	Level	Interpretation
0–19	Low	Few explicit risk indicators were detected. Continue using normal caution.
20–44	Moderate	Some atypical patterns warrant closer inspection.
45–69	High	Multiple or substantial warning signs call for independent verification.
70–100	Critical	Strong warning signs may include upfront payment demands or credential harvesting. Avoid acting until independently verified.


A low score does not mean that a message is safe. It means the current rules did not detect many explicit indicators.
Detector identifiers
The analyzer may return rule identifiers from categories such as:
- FIN — financial manipulation, including upfront fee or deposit demands.
- URG — urgency and pressure tactics.
- SENS — sensitive information or credential requests.
- URL — suspicious URL indicators.
- EMP — employment and scholarship red flags.
Exact findings depend on the implemented rules and the submitted text.
Technology Stack
Layer	Technology
Backend API	Python, FastAPI
Request/response validation	Pydantic
ASGI server	Uvicorn
Detection and scoring	Deterministic rules, regular expressions, contextual safeguards
Frontend	HTML5, CSS, vanilla JavaScript
Automated tests	pytest


No external AI API key is required for the baseline analyzer.
Project Structure
TrustLens/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── schemas.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── routes.py
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── analyzer.py
│   │       ├── detectors.py
│   │       ├── scoring.py
│   │       └── explanations.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_health.py
│   │   ├── test_validation.py
│   │   └── test_analysis.py
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── .gitignore
└── README.md
Requirements
- Python 3.12 or newer, compatible with the installed project dependencies.
- Windows, macOS, or Linux.
- A modern browser such as Chrome, Edge, Firefox, or Safari.
- No external API keys for the baseline local application.
Installation
Windows PowerShell
Run from the project directory:
cd E:\TrustLens
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt
If PowerShell blocks virtual-environment activation, use Command Prompt instead:
.venv\Scripts\activate.bat
macOS or Linux
cd TrustLens
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt
Run the Application
Start the full-stack server from the project root with the virtual environment activated:
uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
Open these local URLs:
Resource	URL
TrustLens interface	http://127.0.0.1:8000/
API health check	http://127.0.0.1:8000/api/health
Interactive API docs	http://127.0.0.1:8000/api/docs


If port 8000 is unavailable, try port 8081:
uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8081 --reload
Then use http://127.0.0.1:8081/ and the corresponding /api/health and /api/docs URLs.
Optional: Run the frontend separately
For decoupled local development, start the API in one terminal:
uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
Start a simple static server in a second terminal:
python -m http.server 3000 --directory frontend
Open http://127.0.0.1:3000/. The frontend's API base URL and CORS configuration must match the local backend address.
API Reference
The interactive Swagger documentation is available at /api/docs while the server is running.
GET /api/health
Checks whether the API is responding.

Example:
curl http://127.0.0.1:8000/api/health
A successful response includes the service status, application name, analyzer version, and timestamp.
POST /api/analyze
Submits text for risk assessment.

Example request:
curl -X POST "http://127.0.0.1:8000/api/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "You have been selected for an internship. Pay a refundable registration deposit today to secure your position.",
    "input_type": "job_offer",
    "language_hint": "en"
  }'
Example response shape (values abbreviated for readability):
{
  "analysis_id": "example-analysis-id",
  "input_type": "job_offer",
  "character_count": 100,
  "word_count": 17,
  "risk_score": 79,
  "risk_level": "Critical",
  "verdict_summary": "Critical scam indicators identified.",
  "findings": [
    {
      "rule_id": "FIN-01",
      "title": "Mandatory Upfront Fee or Deposit Demand",
      "category": "Financial Manipulation",
      "severity": "critical",
      "matched_evidence": ["registration deposit"],
      "explanation": "Upfront payment demands are a serious warning sign.",
      "recommended_action": "Do not transfer money; verify the offer independently."
    }
  ],
  "positive_signals": [],
  "recommended_actions": [
    "Do not send money before independently verifying the offer."
  ],
  "analyzer_method": "heuristic_rule_engine",
  "disclaimer": "Heuristic assessment, not a definitive fraud determination."
}
The response above illustrates the response structure; exact scores, findings, timestamps, and wording depend on the submitted input and current rules.
Run Tests
From the repository root, with the virtual environment activated:
python -m pytest backend/tests -v
The documented test run collected 16 tests, all of which passed:
16 passed, 5 warnings
Coverage includes:
- Health endpoint and API documentation.
- Empty, whitespace-only, oversized, malformed, and unexpected-type inputs.
- Detection of upfront fees, OTP requests, urgency, and suspicious URLs.
- Contextual negation and legitimate-message cases.
- Duplicate-evidence suppression.
- Risk score bounds and risk-band consistency.
- Response schema validation.
Warnings were reported in the recorded run; passing tests do not imply that warnings have been resolved. Re-run the test suite after making changes.
Privacy and Security
TrustLens is designed to analyze message content locally through the application backend. The current implementation is described as in-memory processing: message bodies are not intentionally persisted to a database or forwarded to third-party analysis services. Recent-analysis history is client-side and session-only.

Keep these deployment considerations in mind:
- Do not submit passwords, live OTPs, private keys, or other secrets to any analysis tool.
- Do not expose a development server directly to the public internet without reviewing authentication, rate limiting, logging, CORS, and deployment settings.
- Verify the actual deployment configuration before making privacy guarantees for a hosted instance.
- Safe DOM rendering helps reduce cross-site scripting risk, but it does not replace broader security review.
Limitations
- Heuristic, not forensic: a score is a pattern-based estimate, not legal proof of fraud.
- False positives and false negatives are possible: legitimate messages may contain suspicious wording, and sophisticated scams may evade current rules.
- No baseline external threat-intelligence lookup: the baseline analyzer does not query paid DNS, malware, or reputation feeds.
- No authenticity guarantee: positive signals or a low score do not prove that a sender, domain, or offer is genuine.
- Verification remains necessary: contact the organization through a known official website, verified phone number, or your institution's placement/career office—not through contact details supplied only in the suspicious message.
AI-Assisted Development Disclosure
In line with the stated Glitchathon guidelines, the project disclosure identifies:
- AI coding assistant: Antigravity AI Coding Assistant (Gemini 3.8 Flash High), as recorded by the project author.
- Human guidance and review: implementation was reviewed and debugged against the project's automated tests and local API behavior.
Update this disclosure if the tools or development process change. Follow the event organizers' current requirements for attribution and submission.
Project Status
TrustLens AI has a local FastAPI backend, a browser-based analyzer, deterministic risk scoring, explanatory findings, and an automated test suite. Use the setup and test commands above to run the version in your checkout.

Remember: pause, inspect the evidence, and verify through official channels before trusting a suspicious offer.
