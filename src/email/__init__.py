"""
Email operations module for fetching and processing emails
"""

from .fetcher import EmailFetcher
from .processor import EmailProcessor

__all__ = ["EmailFetcher", "EmailProcessor"]