"""Deterministic rule detectors for scam indicators and positive signals."""

import re
from typing import List, Dict, Any, Tuple
from urllib.parse import urlparse

# Negation & Educational Markers
NEGATION_PATTERNS = [
    r"\bnever\s+(?:share|send|provide|give|pay|wire)\b",
    r"\bdo\s+not\s+(?:share|send|provide|give|pay|wire|deposit)\b",
    r"\bdon't\s+(?:share|send|provide|give|pay|wire|deposit)\b",
    r"\bwill\s+not\s+(?:ask|charge|request|demand)\b",
    r"\bwon't\s+(?:ask|charge|request|demand)\b",
    r"\bbeware\s+of\b",
    r"\bavoid\s+(?:paying|sharing|clicking)\b",
    r"\bno\s+(?:fee|charges|payment|deposit)\s+(?:required|needed|asked)\b",
    r"\bfree\s+of\s+charge\b",
    r"\bwithout\s+any\s+(?:fee|charges|payment)\b",
    r"\bwarning:\s*never\b",
    r"\bcaution:\s*do\s+not\b",
]

EDUCATIONAL_PATTERNS = [
    r"\bcybersecurity\s+(?:class|training|course|workshop|awareness|club)\b",
    r"\bsecurity\s+awareness\b",
    r"\bhow\s+to\s+(?:spot|detect|identify|avoid)\s+(?:scams|fraud|phishing)\b",
    r"\beducational\s+(?:purpose|reminder|guide|alert)\b",
    r"\bphishing\s+simulation\b",
    r"\btips\s+to\s+stay\s+safe\b",
    r"\blearn\s+to\s+protect\s+yourself\b",
    r"\bexample\s+of\s+a\s+(?:scam|phishing|fraud)\b",
]

# URL Shorteners
SHORTENER_DOMAINS = {
    "bit.ly", "tinyurl.com", "t.co", "is.gd", "buff.ly", "ow.ly",
    "cutt.ly", "rb.gy", "shorturl.at", "tiny.cc", "goo.gl", "rebrand.ly",
    "clck.ru", "s.id", "soo.gd", "v.gd", "bc.vc", "shorte.st"
}

# High-Risk / Commonly Abused Free TLDs in Phishing
RISKY_TLDS = {
    ".xyz", ".top", ".click", ".work", ".loan", ".zip", ".buzz",
    ".gq", ".cf", ".tk", ".ml", ".ga", ".fit", ".rest", ".monster",
    ".cam", ".bar", ".sbs", ".cfd"
}

# Major Brands Often Targeted in Impersonation
TARGETED_BRANDS = [
    "google", "microsoft", "amazon", "apple", "meta", "netflix",
    "unicef", "who", "united nations", "harvard", "stanford", "mit",
    "internshala", "linkedin", "deloitte", "mckinsey", "goldman sachs",
    "tesla", "uber", "spotify", "cisco", "ibm", "oracle"
]

FREE_MAIL_PROVIDERS = {
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com",
    "aol.com", "proton.me", "protonmail.com", "mail.com", "zoho.com",
    "yandex.com", "icloud.com"
}


def is_negated_or_educational_context(text: str, match_start: int, match_end: int) -> bool:
    """Check if the matched segment is preceded by a negation or resides within an educational sentence."""
    lower_text = text.lower()

    # Check whole text for strong educational intent
    for edu_pat in EDUCATIONAL_PATTERNS:
        if re.search(edu_pat, lower_text):
            return True

    # Check sentence or local window (up to 90 chars before match)
    window_start = max(0, match_start - 90)
    preceding_window = lower_text[window_start:match_start]

    for neg_pat in NEGATION_PATTERNS:
        if re.search(neg_pat, preceding_window):
            return True

    # Check sentence containing the match
    sentences = re.split(r"[.!?\n]+", lower_text)
    cum_len = 0
    for sentence in sentences:
        s_start = cum_len
        s_end = cum_len + len(sentence)
        cum_len = s_end + 1
        if s_start <= match_start <= s_end:
            for neg_pat in NEGATION_PATTERNS:
                if re.search(neg_pat, sentence):
                    return True
            for edu_pat in EDUCATIONAL_PATTERNS:
                if re.search(edu_pat, sentence):
                    return True
            break

    return False


def extract_urls(text: str) -> List[str]:
    """Extract raw URLs or domain-like strings from text."""
    url_pattern = r"(?:https?:\/\/|www\.)[^\s<>{}\"\'\(\)]+|[a-zA-Z0-9_\.-]+\.(?:com|org|net|io|xyz|top|click|co|edu|gov|work|loan|zip|online|info)\b[^\s<>{}\"\'\(\)]*"
    matches = re.findall(url_pattern, text, re.IGNORECASE)
    cleaned = []
    for m in matches:
        clean = m.rstrip(".,;!?:)'\"")
        if clean and clean not in cleaned:
            cleaned.append(clean)
    return cleaned


def detect_financial_manipulation(text: str) -> List[Dict[str, Any]]:
    """Detect upfront fee demands, unusual payment methods, and check overpayment schemes."""
    findings = []
    lower = text.lower()

    # Rule FIN-01: Upfront Fee Demands
    fin01_patterns = [
        (r"\b(?:registration|application|processing|training|interview|clearance|security|equipment|laptop)\s+fee\b", "Upfront processing or equipment fee demand"),
        (r"\b(?:refundable\s+deposit|security\s+deposit|laptop\s+deposit)\b", "Security or equipment deposit demand"),
        (r"\bpay\s+(?:\$|usd|rs\.?|inr|eur|€|£)?\s*\d+\s*(?:to\s+(?:secure|start|apply|register|reserve))\b", "Direct monetary payment required to secure offer"),
        (r"\b(?:fee|charge)\s+of\s+(?:\$|usd|rs\.?|inr|eur|€|£)?\s*\d+\b", "Explicit fee required for job/scholarship processing"),
        (r"\bpay\s+upfront\b", "Requirement to pay upfront charges"),
        (r"\bsend\s+money\s+for\s+(?:materials|training|background\s+check|software|id\s+badge)\b", "Demanding money for company onboarding items"),
    ]

    matched_fin01 = []
    for pat, desc in fin01_patterns:
        for m in re.finditer(pat, lower):
            if not is_negated_or_educational_context(text, m.start(), m.end()):
                evidence = text[m.start():m.end()]
                if evidence not in matched_fin01:
                    matched_fin01.append(evidence)

    if matched_fin01:
        findings.append({
            "rule_id": "FIN-01",
            "category": "Financial Manipulation",
            "title": "Mandatory Upfront Fee or Deposit Demand",
            "severity": "critical",
            "matched_evidence": matched_fin01,
            "explanation": (
                "Legitimate employers and official scholarship foundations never ask candidates or students to pay "
                "application fees, training charges, laptop deposits, or onboarding expenses out of pocket."
            ),
            "recommended_action": "Do not transfer any money. Real internships and scholarships do not charge students to participate."
        })

    # Rule FIN-02: Unusual / Irreversible Payment Mechanisms
    fin02_patterns = [
        (r"\b(?:apple|google\s+play|steam|amazon|vanilla|target|razer)\s+(?:gift\s+card|cards?|code)\b", "Payment or reimbursement via retail gift cards"),
        (r"\b(?:western\s+union|moneygram)\b", "Money transfer through wire services"),
        (r"\b(?:bitcoin|btc|usdt|crypto|cryptocurrency|ethereum|binance)\b", "Payment requested via cryptocurrency"),
        (r"\b(?:cash\s*app|zelle|venmo)\s+(?:payment|transfer|deposit|to)\b", "Payment requested through personal peer-to-peer apps"),
    ]

    matched_fin02 = []
    for pat, desc in fin02_patterns:
        for m in re.finditer(pat, lower):
            if not is_negated_or_educational_context(text, m.start(), m.end()):
                evidence = text[m.start():m.end()]
                if evidence not in matched_fin02:
                    matched_fin02.append(evidence)

    if matched_fin02:
        findings.append({
            "rule_id": "FIN-02",
            "category": "Financial Manipulation",
            "title": "Irreversible or Untraceable Payment Mechanism",
            "severity": "critical",
            "matched_evidence": matched_fin02,
            "explanation": (
                "The message solicits payment or transaction through untraceable methods (gift cards, wire transfers, "
                "or cryptocurrency) which cannot be recovered once transferred."
            ),
            "recommended_action": "Never purchase gift cards or send cryptocurrency for a job, scholarship, or internship offer."
        })

    # Rule FIN-03: Cheque Overpayment / Mobile Deposit Fraud
    fin03_patterns = [
        (r"\b(?:send|mail)\s+(?:you\s+a\s+)?(?:check|cheque)\b", "Promising to send a check to candidate"),
        (r"\bmobile\s+deposit\s+(?:the\s+)?(?:check|cheque)\b", "Requesting mobile deposit of check"),
        (r"\bdeposit\s+(?:the\s+)?(?:check|cheque)\s+and\s+(?:send|wire|transfer|buy)\b", "Check deposit paired with return funds transfer"),
        (r"\bkeep\s+(?:\$|usd)?\s*\d+\s+as\s+your\s+(?:commission|pay|cut)\b", "Classic fake check overpayment scheme"),
    ]

    matched_fin03 = []
    for pat, desc in fin03_patterns:
        for m in re.finditer(pat, lower):
            if not is_negated_or_educational_context(text, m.start(), m.end()):
                evidence = text[m.start():m.end()]
                if evidence not in matched_fin03:
                    matched_fin03.append(evidence)

    if matched_fin03:
        findings.append({
            "rule_id": "FIN-03",
            "category": "Financial Manipulation",
            "title": "Suspected Check Overpayment Scheme",
            "severity": "critical",
            "matched_evidence": matched_fin03,
            "explanation": (
                "The message exhibits hallmark characteristics of a fake check scam: issuing a counterfeit check, "
                "instructing you to deposit it, and asking you to wire back remaining funds before the bank bounces it."
            ),
            "recommended_action": "Do not deposit checks from unknown parties. The bank will hold you responsible for bounced amounts."
        })

    return findings


def detect_urgency_and_pressure(text: str) -> List[Dict[str, Any]]:
    """Detect artificial deadlines, psychological pressure, and verification bypass."""
    findings = []
    lower = text.lower()

    # Rule URG-01: Artificial Deadlines & Psychological Urgency
    urg01_patterns = [
        (r"\bwithin\s+(?:1|2|3|4|6|12|24|48)\s+hours?\b", "Extreme short-window deadline"),
        (r"\b(?:expires|valid\s+only)\s+(?:today|tonight|in\s+few\s+hours|immediately)\b", "Immediate expiration threat"),
        (r"\bimmediate\s+response\s+required\b", "Forced immediate action requirement"),
        (r"\bact\s+(?:fast|now|quickly)\s+or\s+(?:lose|miss)\b", "Coercive urgency prompt"),
        (r"\blimited\s+(?:slots|seats|positions|spots)\s+(?:remaining|left|available)\b", "Manufactured scarcity pressure"),
        (r"\blast\s+chance\s+to\s+(?:claim|secure|accept)\b", "Final chance pressure tactic"),
        (r"\boffer\s+will\s+be\s+(?:revoked|canceled|given\s+away)\b", "Revocation threat to prevent verification"),
    ]

    matched_urg01 = []
    for pat, desc in urg01_patterns:
        for m in re.finditer(pat, lower):
            if not is_negated_or_educational_context(text, m.start(), m.end()):
                evidence = text[m.start():m.end()]
                if evidence not in matched_urg01:
                    matched_urg01.append(evidence)

    if matched_urg01:
        findings.append({
            "rule_id": "URG-01",
            "category": "Urgency and Pressure",
            "title": "Artificial Urgency and Manufactured Pressure",
            "severity": "medium",
            "matched_evidence": matched_urg01,
            "explanation": (
                "Scammers create artificial deadlines and urgency to trigger panic, rushing victims into hasty decisions "
                "before they have time to consult parents, university advisors, or official company directories."
            ),
            "recommended_action": "Take your time. Legitimate recruiters and universities allow reasonable time to evaluate legitimate offers."
        })

    # Rule URG-02: Secrecy Demands and Verification Bypass
    urg02_patterns = [
        (r"\bdo\s+not\s+(?:contact|call|email)\s+(?:hr|the\s+office|customer\s+support|headquarters|campus)\b", "Explicit instruction not to contact company office"),
        (r"\bkeep\s+this\s+(?:confidential|secret|between\s+us|private)\b", "Insistence on secrecy"),
        (r"\bbypass\s+(?:the\s+)?(?:portal|application|hr|formal\s+process)\b", "Encouraging bypass of official recruitment portals"),
        (r"\bdo\s+not\s+inform\s+anyone\b", "Isolation tactic from mentors or family"),
    ]

    matched_urg02 = []
    for pat, desc in urg02_patterns:
        for m in re.finditer(pat, lower):
            if not is_negated_or_educational_context(text, m.start(), m.end()):
                evidence = text[m.start():m.end()]
                if evidence not in matched_urg02:
                    matched_urg02.append(evidence)

    if matched_urg02:
        findings.append({
            "rule_id": "URG-02",
            "category": "Urgency and Pressure",
            "title": "Demand for Secrecy or Verification Bypass",
            "severity": "high",
            "matched_evidence": matched_urg02,
            "explanation": (
                "Demands to bypass official HR channels or keep communication secret are serious red flags designed "
                "to isolate candidates from fraud checks and institutional oversight."
            ),
            "recommended_action": "Immediately contact the organization's official career center or HR through their verified website."
        })

    return findings


def detect_sensitive_information_requests(text: str) -> List[Dict[str, Any]]:
    """Detect requests for authentication codes (OTP), banking credentials, and unnecessary identity data."""
    findings = []
    lower = text.lower()

    # Rule SENS-01: Authentication Code (OTP / 2FA / Password) Solicitation
    sens01_patterns = [
        (r"\b(?:share|send|provide|forward|give)\s+(?:your\s+|the\s+)?(?:otp|one-time\s+password|6-digit\s+code|verification\s+code|2fa\s+code)\b", "Direct solicitation of OTP or verification code"),
        (r"\b(?:otp|code)\s+received\s+on\s+your\s+(?:phone|mobile|sms|email)\b", "Requesting SMS or email authentication code"),
        (r"\b(?:share|provide|send)\s+(?:your\s+)?(?:password|pin\s+number|login\s+credentials)\b", "Solicitation of account password or PIN"),
        (r"\botp\s+(?:required|needed)\s+for\s+(?:interview|verification|scholarship|offer)\b", "Claiming OTP is needed to unlock offer"),
    ]

    matched_sens01 = []
    for pat, desc in sens01_patterns:
        for m in re.finditer(pat, lower):
            if not is_negated_or_educational_context(text, m.start(), m.end()):
                evidence = text[m.start():m.end()]
                if evidence not in matched_sens01:
                    matched_sens01.append(evidence)

    if matched_sens01:
        findings.append({
            "rule_id": "SENS-01",
            "category": "Sensitive Information",
            "title": "Solicitation of Security Verification Codes (OTP/2FA/PIN)",
            "severity": "critical",
            "matched_evidence": matched_sens01,
            "explanation": (
                "One-Time Passwords (OTPs) and 2FA codes grant direct access to your personal, bank, or university accounts. "
                "No legitimate employer or scholarship committee ever needs your authentication code."
            ),
            "recommended_action": "Never share OTPs or verification codes under any circumstance. If shared, immediately change account passwords."
        })

    # Rule SENS-02: Excessive Identity & Financial Credentials
    sens02_patterns = [
        (r"\b(?:ssn|social\s+security\s+number)\b", "Request for full Social Security Number"),
        (r"\b(?:cvv|security\s+code|card\s+expiry)\b", "Request for credit or debit card security code"),
        (r"\b(?:net\s*banking|internet\s*banking)\s+(?:password|pin|credentials)\b", "Request for online banking login credentials"),
        (r"\bbank\s+account\s+(?:login|password|pin)\b", "Request for banking account authentication"),
        (r"\b(?:send|upload)\s+(?:scanned\s+copy\s+of\s+)?(?:passport|national\s+id|driving\s+license)\s+(?:immediately|to\s+(?:whatsapp|telegram))\b", "Immediate ID scan solicitation over insecure channels"),
    ]

    matched_sens02 = []
    for pat, desc in sens02_patterns:
        for m in re.finditer(pat, lower):
            if not is_negated_or_educational_context(text, m.start(), m.end()):
                evidence = text[m.start():m.end()]
                if evidence not in matched_sens02:
                    matched_sens02.append(evidence)

    if matched_sens02:
        findings.append({
            "rule_id": "SENS-02",
            "category": "Sensitive Information",
            "title": "Premature or Excessive Personal/Banking Identity Demands",
            "severity": "high",
            "matched_evidence": matched_sens02,
            "explanation": (
                "Demanding sensitive financial details, banking passwords, or full identity cards prior to a formal interview "
                "and signed onboarding contract is a strong signal for identity theft and account draining."
            ),
            "recommended_action": "Do not provide banking credentials or government ID numbers over unverified messaging channels."
        })

    return findings


def detect_suspicious_urls_and_comms(text: str) -> List[Dict[str, Any]]:
    """Detect URL shorteners, brand spoofing, free hosting, and off-platform redirection."""
    findings = []
    lower = text.lower()
    urls = extract_urls(text)

    # Rule URL-01: URL Shorteners
    shortened_urls = []
    for u in urls:
        parsed = urlparse(u if "://" in u else f"http://{u}")
        host = (parsed.netloc or "").lower().split(":")[0]
        if host in SHORTENER_DOMAINS:
            shortened_urls.append(u)

    if shortened_urls:
        findings.append({
            "rule_id": "URL-01",
            "category": "Suspicious URLs",
            "title": "Obfuscated / Shortened Link Detected",
            "severity": "high",
            "matched_evidence": shortened_urls,
            "explanation": (
                "Link shortening services conceal the true destination web address. Scammers frequently use them in SMS "
                "and forwarded recruitment messages to bypass automated security filters."
            ),
            "recommended_action": "Do not click shortened links. If necessary, use a link expansion service without navigating to the site."
        })

    # Rule URL-02: Direct IP Address URLs
    ip_urls = []
    ip_pattern = r"(?:https?:\/\/)?(?:\d{1,3}\.){3}\d{1,3}(?::\d+)?(?:\/[^\s]*)?"
    for m in re.finditer(ip_pattern, text):
        evidence = m.group(0)
        if evidence not in ip_urls:
            ip_urls.append(evidence)

    if ip_urls:
        findings.append({
            "rule_id": "URL-02",
            "category": "Suspicious URLs",
            "title": "Direct IP Address Hostname in Link",
            "severity": "critical",
            "matched_evidence": ip_urls,
            "explanation": (
                "Legitimate institutions host their career portals and scholarship forms on registered domain names, "
                "never on raw IP addresses. Direct IP links are commonly associated with hostile phishing infrastructure."
            ),
            "recommended_action": "Never enter credentials or personal information on links pointing directly to IP addresses."
        })

    # Rule URL-03: Suspicious TLD or Lookalike Brand Domains
    lookalike_matches = []
    for u in urls:
        parsed = urlparse(u if "://" in u else f"http://{u}")
        host = (parsed.netloc or "").lower().split(":")[0]
        # Check risky TLDs
        for tld in RISKY_TLDS:
            if host.endswith(tld):
                lookalike_matches.append(u)
                break
        # Check brand keywords combined with job suffixes
        for brand in ["google", "amazon", "microsoft", "apple", "deloitte", "internshala"]:
            if brand in host and not host.endswith(f"{brand}.com") and not host.endswith(f"{brand}.co.in"):
                if any(suffix in host for suffix in ["career", "job", "portal", "verify", "offer", "hr"]):
                    if u not in lookalike_matches:
                        lookalike_matches.append(u)

    if lookalike_matches:
        findings.append({
            "rule_id": "URL-03",
            "category": "Suspicious URLs",
            "title": "Lookalike Brand Domain or High-Risk TLD",
            "severity": "high",
            "matched_evidence": lookalike_matches,
            "explanation": (
                "The link uses high-risk top-level domains or lookalike naming structures mimicking well-known corporate entities. "
                "Note: Heuristic structural detection, not an external threat database lookup."
            ),
            "recommended_action": "Visit the company's verified primary domain directly by typing it into your browser."
        })

    # Rule URL-04: Free Form / Hosting for Corporate Application
    free_hosting_patterns = [
        (r"(?:docs\.google\.com\/forms|forms\.gle|typeform\.com|formsite\.com)", "Free online form service used as official job portal"),
        (r"(?:weebly\.com|wixsite\.com|blogspot\.com|wordpress\.com|firebaseapp\.com)", "Free webpage hosting used for corporate career portal"),
    ]
    free_host_matches = []
    for pat, desc in free_hosting_patterns:
        for m in re.finditer(pat, lower):
            evidence = text[m.start():m.end()]
            if evidence not in free_host_matches:
                free_host_matches.append(evidence)

    # Check if text claims to be a Fortune 500 company using a free form
    claims_major_brand = any(b in lower for b in TARGETED_BRANDS)
    if free_host_matches and claims_major_brand:
        findings.append({
            "rule_id": "URL-04",
            "category": "Suspicious URLs",
            "title": "Generic Free Form/Hosting for Major Enterprise Recruitment",
            "severity": "medium",
            "matched_evidence": free_host_matches,
            "explanation": (
                "Established corporations and government agencies manage recruitment through enterprise Applicant Tracking Systems "
                "(e.g. Workday, Greenhouse, Lever), not free anonymous forms or subdomains."
            ),
            "recommended_action": "Cross-check the open position directly on the organization's official career dashboard."
        })

    # Rule COMM-01: Free Email Address Impersonating Major Brand
    email_pattern = r"\b[A-Za-z0-9._%+-]+@([A-Za-z0-9.-]+\.[A-Z|a-z]{2,})\b"
    free_email_matches = []
    for m in re.finditer(email_pattern, text):
        domain = m.group(1).lower()
        if domain in FREE_MAIL_PROVIDERS:
            # Check if text references an established organization
            for brand in TARGETED_BRANDS:
                if brand in lower:
                    evidence = f"{m.group(0)} (claiming {brand.title()})"
                    if evidence not in free_email_matches:
                        free_email_matches.append(evidence)

    if free_email_matches:
        findings.append({
            "rule_id": "COMM-01",
            "category": "Communication Red Flags",
            "title": "Corporate Impersonation via Free Mailbox Provider",
            "severity": "high",
            "matched_evidence": free_email_matches,
            "explanation": (
                "The sender uses a free public email provider (e.g. @gmail.com or @yahoo.com) while claiming to officially represent "
                "a major global corporation or university. Authentic corporate recruiters send correspondence from company-owned domain emails."
            ),
            "recommended_action": "Check the sender's full email address. Authentic representatives email from official @company.com domains."
        })

    # Rule COMM-02: Immediate Off-Platform Communication Shift
    off_platform_patterns = [
        (r"\b(?:contact|reach|message|dm|chat\s+with)\s+(?:us|me|hr|manager|recruiter)?\s*(?:on|via)\s+(?:telegram|whatsapp|signal)\b", "Redirection to encrypted messaging apps"),
        (r"\bt\.me\/[a-zA-Z0-9_]+\b", "Direct Telegram handle or channel link"),
        (r"\bwa\.me\/[0-9]+\b", "Direct WhatsApp click-to-chat link"),
        (r"\btelegram\s+(?:username|id|handle|app)\b", "Prompting Telegram handle communication"),
    ]

    matched_comm02 = []
    for pat, desc in off_platform_patterns:
        for m in re.finditer(pat, lower):
            if not is_negated_or_educational_context(text, m.start(), m.end()):
                evidence = text[m.start():m.end()]
                if evidence not in matched_comm02:
                    matched_comm02.append(evidence)

    if matched_comm02:
        findings.append({
            "rule_id": "COMM-02",
            "category": "Communication Red Flags",
            "title": "Immediate Redirection to Informal Messaging Apps",
            "severity": "high",
            "matched_evidence": matched_comm02,
            "explanation": (
                "Directing candidates to Telegram or WhatsApp avoids institutional recordkeeping and corporate security monitoring, "
                "a very frequent tactic in student employment scams."
            ),
            "recommended_action": "Insist on communicating through official corporate email and university career portals."
        })

    return findings


def detect_employment_and_scholarship_red_flags(text: str, input_type: str = "message") -> List[Dict[str, Any]]:
    """Detect guaranteed employment, unrealistic payouts, and bogus scholarships."""
    findings = []
    lower = text.lower()

    # Rule EMP-01: Guaranteed Selection Without Evaluation
    emp01_patterns = [
        (r"\b(?:selected|hired|chosen)\s+without\s+(?:an?\s+)?interview\b", "Guaranteed hiring without an interview"),
        (r"\b100%\s+guaranteed\s+(?:placement|job|internship|selection)\b", "Unconditional placement guarantee"),
        (r"\bcongratulations[,!]\s+(?:you\s+(?:have\s+been|are)\s+selected|your\s+resume\s+has\s+been\s+shortlisted)\b", "Unsolicited selection notification"),
        (r"\bno\s+experience\s+(?:required|needed)[,!]\s*(?:earn|\$|immediate\s+start)\b", "No vetting with immediate high returns"),
        (r"\binstant\s+(?:offer|hire|selection)\b", "Instant hiring without candidate assessment"),
    ]

    matched_emp01 = []
    for pat, desc in emp01_patterns:
        for m in re.finditer(pat, lower):
            if not is_negated_or_educational_context(text, m.start(), m.end()):
                evidence = text[m.start():m.end()]
                if evidence not in matched_emp01:
                    matched_emp01.append(evidence)

    if matched_emp01:
        findings.append({
            "rule_id": "EMP-01",
            "category": "Employment & Scholarship Red Flags",
            "title": "Guaranteed Selection Without Formal Evaluation",
            "severity": "high",
            "matched_evidence": matched_emp01,
            "explanation": (
                "Real companies and research labs screen candidates through interviews, technical challenges, and reference reviews. "
                "Offers delivered with zero prior application or evaluation are almost universally fraudulent."
            ),
            "recommended_action": "Verify if you ever applied to this company. Authentic recruiters do not hire blind candidates via unsolicited text."
        })

    # Rule EMP-02: Unrealistic Compensation vs Simple Tasks
    emp02_patterns = [
        (r"\b(?:\$|usd)\s*(?:[5-9]\d|[1-9]\d{2,})\s*(?:\/|\s*per\s*)(?:hr|hour)\s+for\s+(?:data\s+entry|typing|sms|review|rating)\b", "Extreme hourly rate for basic clerical tasks"),
        (r"\bearn\s+(?:\$|usd|rs\.?|inr|€)\s*\d{3,}\s*(?:daily|per\s+day)\s+working\s+(?:from\s+home|part\s*time|1-2\s+hours)\b", "Exaggerated daily earnings for minimal hours"),
        (r"\b(?:simple|easy)\s+tasks?\s+to\s+earn\s+(?:\$|\d+)\b", "Simple click/task scam formulation"),
    ]

    matched_emp02 = []
    for pat, desc in emp02_patterns:
        for m in re.finditer(pat, lower):
            if not is_negated_or_educational_context(text, m.start(), m.end()):
                evidence = text[m.start():m.end()]
                if evidence not in matched_emp02:
                    matched_emp02.append(evidence)

    if matched_emp02:
        findings.append({
            "rule_id": "EMP-02",
            "category": "Employment & Scholarship Red Flags",
            "title": "Disproportionate Compensation for Low-Effort Tasks",
            "severity": "medium",
            "matched_evidence": matched_emp02,
            "explanation": (
                "Offering thousands of dollars for simple data entry, video rating, or typing tasks is a classic lure "
                "used by task-fraud syndicates to bait students into fee-advancement schemes."
            ),
            "recommended_action": "Compare compensation against industry standards. If the pay sounds too good to be true, it invariably is."
        })

    # Rule SCHOL-01: Bogus Scholarship Claims paired with Fees
    schol01_patterns = [
        (r"\b(?:guaranteed|unclaimed)\s+scholarship\s+(?:award|grant|fund)\b", "Guaranteed or unclaimed grant money claim"),
        (r"\bscholarship\s+(?:winner|awarded)\s+without\s+application\b", "Winning scholarship without having submitted an application"),
        (r"\bclaim\s+your\s+scholarship\s+by\s+paying\b", "Paying to claim a scholarship grant"),
    ]

    matched_schol01 = []
    for pat, desc in schol01_patterns:
        for m in re.finditer(pat, lower):
            if not is_negated_or_educational_context(text, m.start(), m.end()):
                evidence = text[m.start():m.end()]
                if evidence not in matched_schol01:
                    matched_schol01.append(evidence)

    if matched_schol01:
        findings.append({
            "rule_id": "SCHOL-01",
            "category": "Employment & Scholarship Red Flags",
            "title": "Unsolicited or Pay-to-Claim Scholarship Lure",
            "severity": "high",
            "matched_evidence": matched_schol01,
            "explanation": (
                "Authentic scholarship trusts and government agencies award grants based on merit or need, never through unsolicited SMS/WhatsApp "
                "nor requiring payment to release funds."
            ),
            "recommended_action": "Confirm scholarship legitimacy with your university's financial aid office before responding."
        })

    return findings


def detect_positive_signals(text: str) -> List[str]:
    """Identify reassuring hygiene indicators while preserving clarity that they do not guarantee authenticity."""
    signals = []
    lower = text.lower()

    # Domain indicators
    if re.search(r"\bhttps?:\/\/[a-zA-Z0-9.-]+\.(?:edu|gov|ac\.uk|edu\.in)\b", lower):
        signals.append("Uses accredited institutional domain (.edu, .gov, .ac.uk, or .edu.in)")

    # Enterprise ATS / Verified Portals
    ats_match = re.search(r"\b(?:myworkdayjobs\.com|greenhouse\.io|lever\.co|handshake\.com|smartrecruiters\.com|linkedin\.com\/jobs|jobs\.apple\.com|careers\.google\.com)\b", lower)
    if ats_match:
        signals.append(f"References recognized enterprise recruitment portal ({ats_match.group(0)})")

    # Explicit 'no fee' policy statement
    if re.search(r"\b(?:no\s+fee|we\s+do\s+not\s+charge|free\s+of\s+charge|never\s+charges?\s+(?:candidates|students)|without\s+any\s+fee)\b", lower):
        signals.append("Includes clear affirmative statement that application and onboarding are free of charge (no fees required)")

    # Structured multi-round evaluation mentioned
    if re.search(r"\b(?:technical\s+round|coding\s+assessment|panel\s+interview|portfolio\s+review|behavioral\s+interview)\b", lower):
        signals.append("Mentions standard professional evaluation stages (technical round, interview, portfolio)")

    # Standard reasonable review timeline
    if re.search(r"\b(?:review\s+(?:applications|period)|within\s+(?:2-3|two\s+to\s+three)\s+weeks|rolling\s+admissions)\b", lower):
        signals.append("States a realistic professional review timeline rather than artificial urgency")

    # Contact via corporate email domain
    email_matches = re.findall(r"\b[A-Za-z0-9._%+-]+@([A-Za-z0-9.-]+\.[A-Z|a-z]{2,})\b", text)
    corp_emails = [dom for dom in email_matches if dom.lower() not in FREE_MAIL_PROVIDERS and not any(dom.lower().endswith(tld) for tld in RISKY_TLDS)]
    if corp_emails:
        signals.append(f"Provides contact through verified corporate email domain (@{corp_emails[0]})")

    return signals
