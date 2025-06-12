"""
Gmail email actions for deleting, moving, and organizing emails
"""

from typing import List, Dict, Any
import time

from googleapiclient.errors import HttpError
from src.auth.gmail_auth import GmailAuthenticator
from src.config.settings import settings

class GmailActions:
    def __init__(self):
        self.auth = GmailAuthenticator()
        self.service = None
    
    def _get_service(self):
        """Get authenticated Gmail service"""
        if not self.service:
            self.service = self.auth.get_service()
        return self.service
    
    def delete_email(self, email_id: str, permanent: bool = False) -> bool:
        """
        Delete an email
        
        Args:
            email_id: Gmail message ID
            permanent: If True, permanently delete. If False, move to trash.
        
        Returns:
            True if successful, False otherwise
        """
        if settings.dry_run:
            action = "permanently delete" if permanent else "move to trash"
            print(f"[DRY RUN] Would {action} email: {email_id}")
            return True
        
        service = self._get_service()
        
        try:
            if permanent:
                # Permanently delete
                service.users().messages().delete(
                    userId='me',
                    id=email_id
                ).execute()
                print(f"Permanently deleted email: {email_id}")
            else:
                # Move to trash
                service.users().messages().trash(
                    userId='me',
                    id=email_id
                ).execute()
                print(f"Moved email to trash: {email_id}")
            
            return True
            
        except HttpError as e:
            print(f"Gmail API error deleting {email_id}: {e}")
            return False
        except Exception as e:
            print(f"Error deleting email {email_id}: {e}")
            return False
    
    def move_email(self, email_id: str, label_name: str) -> bool:
        """
        Move an email to a specific label/folder
        
        Args:
            email_id: Gmail message ID
            label_name: Target label name
        
        Returns:
            True if successful, False otherwise
        """
        if settings.dry_run:
            print(f"[DRY RUN] Would move email {email_id} to label: {label_name}")
            return True
        
        service = self._get_service()
        
        try:
            # Get label ID
            label_id = self._get_label_id(label_name)
            if not label_id:
                print(f"Label '{label_name}' not found")
                return False
            
            # Add label to message
            service.users().messages().modify(
                userId='me',
                id=email_id,
                body={
                    'addLabelIds': [label_id],
                    'removeLabelIds': ['INBOX']  # Remove from inbox
                }
            ).execute()
            
            print(f"Successfully moved email {email_id} to {label_name}")
            return True
            
        except HttpError as e:
            print(f"Gmail API error moving {email_id}: {e}")
            return False
        except Exception as e:
            print(f"Error moving email {email_id}: {e}")
            return False
    
    def create_label(self, label_name: str) -> bool:
        """
        Create a new Gmail label
        
        Args:
            label_name: Name of the label to create
        
        Returns:
            True if successful, False otherwise
        """
        if settings.dry_run:
            print(f"[DRY RUN] Would create label: {label_name}")
            return True
        
        service = self._get_service()
        
        try:
            label_object = {
                'name': label_name,
                'labelListVisibility': 'labelShow',
                'messageListVisibility': 'show'
            }
            
            result = service.users().labels().create(
                userId='me',
                body=label_object
            ).execute()
            
            print(f"Successfully created label: {label_name}")
            return True
            
        except HttpError as e:
            if e.resp.status == 409:  # Label already exists
                print(f"Label '{label_name}' already exists")
                return True
            print(f"Gmail API error creating label {label_name}: {e}")
            return False
        except Exception as e:
            print(f"Error creating label {label_name}: {e}")
            return False
    
    def mark_as_read(self, email_id: str, is_read: bool = True) -> bool:
        """
        Mark an email as read or unread
        
        Args:
            email_id: Gmail message ID
            is_read: True to mark as read, False for unread
        
        Returns:
            True if successful, False otherwise
        """
        if settings.dry_run:
            status = "read" if is_read else "unread"
            print(f"[DRY RUN] Would mark email {email_id} as {status}")
            return True
        
        service = self._get_service()
        
        try:
            if is_read:
                # Remove UNREAD label
                body = {'removeLabelIds': ['UNREAD']}
            else:
                # Add UNREAD label
                body = {'addLabelIds': ['UNREAD']}
            
            service.users().messages().modify(
                userId='me',
                id=email_id,
                body=body
            ).execute()
            
            status = "read" if is_read else "unread"
            print(f"Successfully marked email {email_id} as {status}")
            return True
            
        except HttpError as e:
            print(f"Gmail API error marking {email_id}: {e}")
            return False
        except Exception as e:
            print(f"Error marking email {email_id}: {e}")
            return False
    
    def bulk_delete(self, email_ids: List[str], permanent: bool = False) -> Dict[str, bool]:
        """
        Delete multiple emails in bulk
        
        Args:
            email_ids: List of Gmail message IDs
            permanent: If True, permanently delete
        
        Returns:
            Dictionary mapping email_id to success status
        """
        results = {}
        
        for email_id in email_ids:
            results[email_id] = self.delete_email(email_id, permanent)
            # Rate limiting
            time.sleep(0.1)
        
        return results
    
    def bulk_move(self, email_ids: List[str], label_name: str) -> Dict[str, bool]:
        """
        Move multiple emails to a label
        
        Args:
            email_ids: List of Gmail message IDs
            label_name: Target label name
        
        Returns:
            Dictionary mapping email_id to success status
        """
        results = {}
        
        for email_id in email_ids:
            results[email_id] = self.move_email(email_id, label_name)
            # Rate limiting
            time.sleep(0.1)
        
        return results
    
    def _get_label_id(self, label_name: str) -> str:
        """Get Gmail label ID by name"""
        service = self._get_service()
        
        try:
            result = service.users().labels().list(userId='me').execute()
            labels = result.get('labels', [])
            
            for label in labels:
                if label['name'].lower() == label_name.lower():
                    return label['id']
            
            return None
            
        except Exception as e:
            print(f"Error getting label ID: {e}")
            return None
    
    def get_labels(self) -> List[Dict[str, str]]:
        """Get all Gmail labels"""
        service = self._get_service()
        
        try:
            result = service.users().labels().list(userId='me').execute()
            return result.get('labels', [])
        except Exception as e:
            print(f"Error getting labels: {e}")
            return []