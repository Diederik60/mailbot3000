"""
LLM integration module for email classification
"""

from .classifier import EmailClassifier
from .prompts import (
    EMAIL_CLASSIFICATION_PROMPT,
    BATCH_CLASSIFICATION_PROMPT, 
    SENDER_ANALYSIS_PROMPT
)

__all__ = [
    "EmailClassifier",
    "EMAIL_CLASSIFICATION_PROMPT",
    "BATCH_CLASSIFICATION_PROMPT",
    "SENDER_ANALYSIS_PROMPT"
]