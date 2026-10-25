"""Configuration settings for TrustLens AI."""

from typing import List
import os

APP_NAME: str = "TrustLens AI"
APP_VERSION: str = "1.0.0"
TAGLINE: str = "See the warning signs before you trust the message."

# Input constraints
MIN_TEXT_LENGTH: int = 3
MAX_TEXT_LENGTH: int = 10000

# CORS Allowed Origins
DEFAULT_CORS_ORIGINS: List[str] = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:8081",
    "http://127.0.0.1:8081",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

ALLOWED_ORIGINS: List[str] = [
    origin.strip()
    for origin in os.getenv("TRUSTLENS_CORS_ORIGINS", "").split(",")
    if origin.strip()
] or DEFAULT_CORS_ORIGINS
