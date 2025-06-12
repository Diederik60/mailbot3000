"""
Email actions module for performing operations on emails
"""

from .outlook_actions import EmailActions
from .gmail_actions import GmailActions

__all__ = ["EmailActions", "GmailActions"]