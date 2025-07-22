"""Python client for the Private Captcha service."""

from .client import Client, GLOBAL_DOMAIN, EU_DOMAIN
from .exceptions import (
    APIKeyError,
    PrivateCaptchaError,
    SolutionError,
    VerificationFailedError,
)
from .models import VerifyOutput

__all__ = [
    "Client",
    "GLOBAL_DOMAIN",
    "EU_DOMAIN",
    "PrivateCaptchaError",
    "APIKeyError",
    "SolutionError",
    "VerifyOutput",
    "VerificationFailedError",
]
