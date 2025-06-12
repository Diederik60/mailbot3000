import requests
from typing import List, Dict, Any, Optional
from src.auth.microsoft_auth import MicrosoftAuthenticator
from src.config.settings import settings
import time

class EmailActions:
    def __init__(self):
        self.auth = MicrosoftAuthenticator()
        self.base_url = settings.graph_base_url
    
    def delete_email(self, email_id: str, permanent: bool = False) -> bool:
        """
        Delete an email.
        
        Args:
            email_id: ID of the email to delete
            permanent: If True, permanently delete. If False, move to deleted items.
            
        Returns:
            True if successful, False otherwise
        """
        if settings.dry_run:
            print(f"[DRY RUN] Would delete email: {email_id}")
            return True
        
        headers = self.auth.get_auth_headers()
        
        if permanent:
            # Permanently delete
            url = f"{self.base_url}/me/messages/{email_id}"
            method = "DELETE"
        else:
            # Move to deleted items
            url = f"{self.base_url}/me/messages/{email_id}/move"
            method = "POST"
            headers['Content-Type'] = 'application/json'
        
        try:
            if permanent:
                response = requests.delete(url, headers=headers, timeout=10)
            else:
                # Move to deleted items folder
                data = {"destinationId": "deleteditems"}
                response = requests.post(url, headers=headers, json=data, timeout=10)
            
            success = response.status_code in [200, 202, 204]
            if success:
                print(f"Successfully deleted email: {email_id}")
            else:
                print(f"Failed to delete email {email_id}: {response.status_code}")
            
            return success
        
        except requests.exceptions.RequestException as e:
            print(f"Error deleting email {email_id}: {e}")
            return False
    
    def move_email(self, email_id: str, folder_id: str) -> bool:
        """
        Move an email to a specific folder.
        
        Args:
            email_id: ID of the email to move
            folder_id: ID or name of the destination folder
            
        Returns:
            True if successful, False otherwise
        """
        if settings.dry_run:
            print(f"[DRY RUN] Would move email {email_id} to folder: {folder_id}")
            return True
        
        headers = self.auth.get_auth_headers()
        url = f"{self.base_url}/me/messages/{email_id}/move"
        
        data = {"destinationId": folder_id}
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            success = response.status_code in [200, 201, 202]
            
            if success:
                print(f"Successfully moved email {email_id} to {folder_id}")
            else:
                print(f"Failed to move email {email_id}: {response.status_code}")
            
            return success
        
        except requests.exceptions.RequestException as e:
            print(f"Error moving email {email_id}: {e}")
            return False
    
    def create_folder(self, folder_name: str, parent_folder: str = "msgfolderroot") -> Optional[str]:
        """
        Create a new mail folder.
        
        Args:
            folder_name: Name of the folder to create
            parent_folder: Parent folder ID (default: msgfolderroot for top level)
            
        Returns:
            Folder ID if successful, None otherwise
        """
        if settings.dry_run:
            print(f"[DRY RUN] Would create folder: {folder_name}")
            return "dry_run_folder_id"
        
        headers = self.auth.get_auth_headers()
        url = f"{self.base_url}/me/mailfolders/{parent_folder}/childfolders"
        
        data = {
            "displayName": folder_name
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            if response.status_code in [200, 201]:
                folder_data = response.json()
                folder_id = folder_data.get('id')
                print(f"Successfully created folder: {folder_name} (ID: {folder_id})")
                return folder_id
            else:
                print(f"Failed to create folder {folder_name}: {response.status_code}")
                return None
        
        except requests.exceptions.RequestException as e:
            print(f"Error creating folder {folder_name}: {e}")
            return None
    
    def mark_as_read(self, email_id: str, is_read: bool = True) -> bool:
        """
        Mark an email as read or unread.
        
        Args:
            email_id: ID of the email
            is_read: True to mark as read, False for unread
            
        Returns:
            True if successful, False otherwise
        """
        if settings.dry_run:
            status = "read" if is_read else "unread"
            print(f"[DRY RUN] Would mark email {email_id} as {status}")
            return True
        
        headers = self.auth.get_auth_headers()
        url = f"{self.base_url}/me/messages/{email_id}"
        
        data = {"isRead": is_read}
        
        try:
            response = requests.patch(url, headers=headers, json=data, timeout=10)
            success = response.status_code in [200, 202]
            
            if success:
                status = "read" if is_read else "unread"
                print(f"Successfully marked email {email_id} as {status}")
            
            return success
        
        except requests.exceptions.RequestException as e:
            print(f"Error marking email {email_id}: {e}")
            return False
    
    def bulk_delete(self, email_ids: List[str], permanent: bool = False) -> Dict[str, bool]:
        """
        Delete multiple emails in bulk.
        
        Args:
            email_ids: List of email IDs to delete
            permanent: If True, permanently delete
            
        Returns:
            Dictionary mapping email_id to success status
        """
        results = {}
        
        for email_id in email_ids:
            results[email_id] = self.delete_email(email_id, permanent)
            # Small delay to avoid rate limiting
            time.sleep(0.1)
        
        return results
    
    def bulk_move(self, email_ids: List[str], folder_id: str) -> Dict[str, bool]:
        """
        Move multiple emails to a folder.
        
        Args:
            email_ids: List of email IDs to move
            folder_id: Destination folder ID
            
        Returns:
            Dictionary mapping email_id to success status
        """
        results = {}
        
        for email_id in email_ids:
            results[email_id] = self.move_email(email_id, folder_id)
            # Small delay to avoid rate limiting
            time.sleep(0.1)
        
        return results