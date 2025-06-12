"""
Email operations module for fetching and processing emails
"""

from .outlook_fetcher import EmailFetcher
from .processor import EmailProcessor

__all__ = ["EmailFetcher", "EmailProcessor"]