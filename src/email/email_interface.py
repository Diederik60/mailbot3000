"""
Unified email interface that works with both Gmail and Outlook
"""

from typing import List, Dict, Any, Optional
from src.config.settings import settings

class EmailInterface:
    """Unified interface for email operations"""
    
    def __init__(self):
        self.provider = settings.email_provider
        self._fetcher = None
        self._actions = None
        self._setup_provider()
    
    def _setup_provider(self):
        """Setup the appropriate email provider"""
        if self.provider == "gmail":
            from src.email.gmail_fetcher import GmailFetcher
            from src.actions.gmail_actions import GmailActions
            self._fetcher = GmailFetcher()
            self._actions = GmailActions()
        
        elif self.provider == "outlook":
            from src.email.outlook_fetcher import EmailFetcher
            from src.actions.outlook_actions import EmailActions
            self._fetcher = EmailFetcher()
            self._actions = EmailActions()
        
        else:
            raise ValueError(f"Unknown email provider: {self.provider}")
    
    def test_connection(self) -> bool:
        """Test email provider connection"""
        if self.provider == "gmail":
            return self._fetcher.auth.test_connection()
        elif self.provider == "outlook":
            return self._fetcher.auth.test_connection()
        return False
    
    def fetch_emails(self, 
                    folder: str = "inbox",
                    limit: int = 50,
                    days_back: Optional[int] = None) -> List[Dict[str, Any]]:
        """Fetch emails from specified folder/label"""
        return self._fetcher.fetch_emails(folder, limit, days_back)
    
    def get_email_stats(self) -> Dict[str, Dict[str, int]]:
        """Get email statistics"""
        return self._fetcher.get_email_stats()
    
    def search_emails(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search emails"""
        return self._fetcher.search_emails(query, limit)
    
    def delete_email(self, email_id: str, permanent: bool = False) -> bool:
        """Delete an email"""
        return self._actions.delete_email(email_id, permanent)
    
    def move_email(self, email_id: str, folder: str) -> bool:
        """Move email to folder/label"""
        return self._actions.move_email(email_id, folder)
    
    def mark_as_read(self, email_id: str, is_read: bool = True) -> bool:
        """Mark email as read/unread"""
        return self._actions.mark_as_read(email_id, is_read)
    
    def bulk_delete(self, email_ids: List[str], permanent: bool = False) -> Dict[str, bool]:
        """Delete multiple emails"""
        return self._actions.bulk_delete(email_ids, permanent)
    
    def bulk_move(self, email_ids: List[str], folder: str) -> Dict[str, bool]:
        """Move multiple emails"""
        return self._actions.bulk_move(email_ids, folder)
    
    def create_folder(self, folder_name: str) -> bool:
        """Create folder/label"""
        if self.provider == "gmail":
            return self._actions.create_label(folder_name)
        elif self.provider == "outlook":
            return self._actions.create_folder(folder_name)
        return False
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about current email provider"""
        return {
            'provider': self.provider,
            'target_email': settings.target_email,
            'has_credentials': self._check_credentials()
        }
    
    def _check_credentials(self) -> bool:
        """Check if credentials are available"""
        if self.provider == "gmail":
            return settings.has_gmail_credentials
        elif self.provider == "outlook":
            return settings.has_outlook_credentials
        return False