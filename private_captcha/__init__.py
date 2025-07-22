"""Python client for the Private Captcha service."""

from .client import Client
from .exceptions import (
    APIKeyError,
    PrivateCaptchaError,
    SolutionError,
    VerificationFailedError,
)
from .models import VerifyOutput

__all__ = [
    "Client",
    "PrivateCaptchaError",
    "APIKeyError",
    "SolutionError",
    "VerifyOutput",
    "VerificationFailedError",
]
