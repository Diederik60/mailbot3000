import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from src.auth.microsoft_auth import MicrosoftAuthenticator
from src.config.settings import settings
import time

class EmailFetcher:
    def __init__(self):
        self.auth = MicrosoftAuthenticator()
        self.base_url = settings.graph_base_url
    
    def fetch_emails(self, 
                    folder: str = "inbox",
                    limit: int = 50,
                    days_back: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Fetch emails from specified folder.
        
        Args:
            folder: Folder name (inbox, junk, sent, etc.)
            limit: Maximum number of emails to fetch
            days_back: Only fetch emails from last N days (None for all)
        """
        headers = self.auth.get_auth_headers()
        
        # Build URL
        url = f"{self.base_url}/me/mailfolders/{folder}/messages"
        
        # Build query parameters
        params = {
            '$top': min(limit, 1000),  # Graph API max is 1000
            '$orderby': 'receivedDateTime desc',
            '$select': 'id,subject,from,receivedDateTime,bodyPreview,body,hasAttachments,importance,isRead,sender,toRecipients,ccRecipients'
        }
        
        # Add date filter if specified
        if days_back:
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)
            cutoff_str = cutoff_date.strftime('%Y-%m-%dT%H:%M:%SZ')
            params['$filter'] = f"receivedDateTime ge {cutoff_str}"
        
        all_emails = []
        
        try:
            while len(all_emails) < limit and url:
                response = requests.get(url, headers=headers, params=params, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                emails = data.get('value', [])
                all_emails.extend(emails)
                
                # Get next page URL
                url = data.get('@odata.nextLink')
                params = {}  # Clear params for next page (they're in the nextLink URL)
                
                print(f"Fetched {len(emails)} emails, total: {len(all_emails)}")
                
                # Rate limiting
                time.sleep(0.1)
                
                if len(all_emails) >= limit:
                    break
        
        except requests.exceptions.RequestException as e:
            print(f"Error fetching emails: {e}")
            return []
        
        return all_emails[:limit]
    
    def get_folders(self) -> List[Dict[str, Any]]:
        """Get all mail folders."""
        headers = self.auth.get_auth_headers()
        url = f"{self.base_url}/me/mailfolders"
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json().get('value', [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching folders: {e}")
            return []
    
    def get_email_stats(self) -> Dict[str, int]:
        """Get basic email statistics."""
        folders = ['inbox', 'junkemail', 'deleteditems', 'sentitems']
        stats = {}
        
        headers = self.auth.get_auth_headers()
        
        for folder in folders:
            try:
                url = f"{self.base_url}/me/mailfolders/{folder}"
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    stats[folder] = {
                        'total_count': data.get('totalItemCount', 0),
                        'unread_count': data.get('unreadItemCount', 0)
                    }
                else:
                    stats[folder] = {'total_count': 0, 'unread_count': 0}
            except Exception as e:
                print(f"Error getting stats for {folder}: {e}")
                stats[folder] = {'total_count': 0, 'unread_count': 0}
        
        return stats
    
    def search_emails(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search emails with a query string."""
        headers = self.auth.get_auth_headers()
        
        url = f"{self.base_url}/me/messages"
        params = {
            '$search': f'"{query}"',
            '$top': min(limit, 1000),
            '$orderby': 'receivedDateTime desc',
            '$select': 'id,subject,from,receivedDateTime,bodyPreview,body,hasAttachments,importance,isRead'
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            return response.json().get('value', [])
        except requests.exceptions.RequestException as e:
            print(f"Error searching emails: {e}")
            return []