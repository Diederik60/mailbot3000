"""
Gmail email fetcher using Gmail API
"""

import base64
import email
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import time

from googleapiclient.errors import HttpError
from src.auth.gmail_auth import GmailAuthenticator
from src.config.settings import settings

class GmailFetcher:
    def __init__(self):
        self.auth = GmailAuthenticator()
        self.service = None
    
    def _get_service(self):
        """Get authenticated Gmail service"""
        if not self.service:
            self.service = self.auth.get_service()
        return self.service
    
    def fetch_emails(self, 
                    folder: str = "inbox",
                    limit: int = 50,
                    days_back: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Fetch emails from Gmail
        
        Args:
            folder: Gmail label (inbox, spam, trash, etc.)
            limit: Maximum number of emails to fetch
            days_back: Only fetch emails from last N days
        """
        service = self._get_service()
        
        # Build query
        query = f"in:{folder}"
        if days_back:
            cutoff_date = datetime.now() - timedelta(days=days_back)
            date_str = cutoff_date.strftime('%Y/%m/%d')
            query += f" after:{date_str}"
        
        try:
            # Get message IDs
            result = service.users().messages().list(
                userId='me',
                q=query,
                maxResults=limit
            ).execute()
            
            messages = result.get('messages', [])
            if not messages:
                return []
            
            print(f"Found {len(messages)} messages, fetching details...")
            
            # Fetch message details
            emails = []
            for i, message in enumerate(messages):
                try:
                    email_data = self._get_message_details(service, message['id'])
                    if email_data:
                        emails.append(email_data)
                    
                    # Progress and rate limiting
                    if (i + 1) % 10 == 0:
                        print(f"Fetched {i + 1}/{len(messages)} emails")
                    time.sleep(0.1)  # Rate limiting
                    
                except Exception as e:
                    print(f"Error fetching message {message['id']}: {e}")
                    continue
            
            return emails[:limit]
            
        except HttpError as e:
            print(f"Gmail API error: {e}")
            return []
        except Exception as e:
            print(f"Error fetching emails: {e}")
            return []
    
    def _get_message_details(self, service, message_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a message"""
        try:
            message = service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            # Extract headers
            headers = {h['name']: h['value'] for h in message['payload'].get('headers', [])}
            
            # Extract body
            body_preview = ""
            body_content = ""
            
            if 'parts' in message['payload']:
                body_content = self._extract_body_from_parts(message['payload']['parts'])
            else:
                body_content = self._extract_body_from_payload(message['payload'])
            
            body_preview = body_content[:500] if body_content else ""
            
            # Convert to our standard format
            email_data = {
                'id': message['id'],
                'subject': headers.get('Subject', 'No Subject'),
                'from': {
                    'emailAddress': {
                        'address': self._extract_email_address(headers.get('From', '')),
                        'name': self._extract_display_name(headers.get('From', ''))
                    }
                },
                'receivedDateTime': self._parse_date(headers.get('Date', '')),
                'bodyPreview': body_preview,
                'body': {
                    'content': body_content,
                    'contentType': 'text/plain'
                },
                'hasAttachments': len(message['payload'].get('parts', [])) > 1,
                'importance': 'normal',
                'isRead': 'UNREAD' not in message.get('labelIds', []),
                'sender': {
                    'emailAddress': {
                        'address': self._extract_email_address(headers.get('From', '')),
                        'name': self._extract_display_name(headers.get('From', ''))
                    }
                },
                'toRecipients': [{'emailAddress': {'address': headers.get('To', '')}}],
                'ccRecipients': [{'emailAddress': {'address': headers.get('Cc', '')}}] if headers.get('Cc') else []
            }
            
            return email_data
            
        except Exception as e:
            print(f"Error getting message details: {e}")
            return None
    
    def _extract_body_from_parts(self, parts: List[Dict]) -> str:
        """Extract text body from message parts"""
        for part in parts:
            if part['mimeType'] == 'text/plain':
                if 'data' in part['body']:
                    return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
            elif part['mimeType'] == 'multipart/alternative' and 'parts' in part:
                return self._extract_body_from_parts(part['parts'])
        return ""
    
    def _extract_body_from_payload(self, payload: Dict) -> str:
        """Extract text body from payload"""
        if payload['mimeType'] == 'text/plain' and 'data' in payload['body']:
            return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        return ""
    
    def _extract_email_address(self, from_header: str) -> str:
        """Extract email address from From header"""
        if '<' in from_header and '>' in from_header:
            start = from_header.find('<') + 1
            end = from_header.find('>')
            return from_header[start:end]
        elif '@' in from_header:
            return from_header.strip()
        return from_header
    
    def _extract_display_name(self, from_header: str) -> str:
        """Extract display name from From header"""
        if '<' in from_header:
            return from_header[:from_header.find('<')].strip().strip('"')
        return ""
    
    def _parse_date(self, date_str: str) -> str:
        """Parse date string to ISO format"""
        try:
            # Parse RFC 2822 date format
            parsed = email.utils.parsedate_tz(date_str)
            if parsed:
                timestamp = email.utils.mktime_tz(parsed)
                dt = datetime.fromtimestamp(timestamp)
                return dt.isoformat() + 'Z'
        except:
            pass
        return datetime.now().isoformat() + 'Z'
    
    def get_email_stats(self) -> Dict[str, Dict[str, int]]:
        """Get basic email statistics with better handling for large mailboxes"""
        service = self._get_service()
        stats = {}
        
        # First, get all available labels to understand the structure
        try:
            labels_result = service.users().labels().list(userId='me').execute()
            all_labels = labels_result.get('labels', [])
            
            # Focus on main system labels only
            important_labels = []
            for label in all_labels:
                label_id = label['id']
                label_name = label['name']
                
                # Only include key system labels
                if label_id in ['INBOX', 'SPAM', 'TRASH', 'SENT', 'DRAFT']:
                    important_labels.append((label_id, label_name))
                # Include category labels but not UNREAD (it's a modifier)
                elif label_id.startswith('CATEGORY_') and label_id != 'UNREAD':
                    important_labels.append((label_id, label_name))
            
            print(f"📁 Checking main folders and categories...")
            
        except Exception as e:
            print(f"Warning: Could not get labels list: {e}")
            # Fall back to standard labels
            important_labels = [
                ('INBOX', 'Inbox'),
                ('SPAM', 'Spam'), 
                ('TRASH', 'Trash'),
                ('SENT', 'Sent')
            ]
        
        # Get counts with better handling for large mailboxes
        for label_id, label_name in important_labels:
            try:
                # Get API estimate
                result = service.users().messages().list(
                    userId='me',
                    labelIds=[label_id],
                    maxResults=1
                ).execute()
                
                api_estimate = result.get('resultSizeEstimate', 0)
                
                # For unread count
                try:
                    unread_result = service.users().messages().list(
                        userId='me',
                        labelIds=[label_id, 'UNREAD'],
                        maxResults=1
                    ).execute()
                    unread_estimate = unread_result.get('resultSizeEstimate', 0)
                except Exception:
                    unread_estimate = 0
                
                # Format counts for better readability
                def format_count(count):
                    if count == 0:
                        return "0"
                    elif count < 100:
                        return str(count)
                    elif count < 1000:
                        return f"{count}"
                    elif count < 10000:
                        return f"{count//1000}.{(count%1000)//100}k"
                    else:
                        return f"{count//1000}k+"
                
                # Handle Gmail's 201+ estimates for large folders
                if api_estimate >= 200 and label_id in ['INBOX', 'SENT'] or label_id.startswith('CATEGORY_'):
                    # For large folders, show as "200+" to indicate it's a lot
                    total_display = f"{api_estimate}+" if api_estimate < 1000 else format_count(api_estimate)
                else:
                    total_display = format_count(api_estimate)
                
                unread_display = format_count(unread_estimate)
                
                stats[label_name.lower().replace('category_', '')] = {
                    'total_count': total_display,
                    'unread_count': unread_display,
                    'raw_total': api_estimate,  # Keep raw number for processing decisions
                    'raw_unread': unread_estimate
                }
                
            except Exception as e:
                print(f"Error getting stats for {label_name}: {e}")
                stats[label_name.lower().replace('category_', '')] = {
                    'total_count': 'Error', 
                    'unread_count': 'Error',
                    'raw_total': 0,
                    'raw_unread': 0
                }
        
        return stats
    
    def search_emails(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search emails with a query string"""
        service = self._get_service()
        
        try:
            result = service.users().messages().list(
                userId='me',
                q=query,
                maxResults=limit
            ).execute()
            
            messages = result.get('messages', [])
            emails = []
            
            for message in messages:
                email_data = self._get_message_details(service, message['id'])
                if email_data:
                    emails.append(email_data)
            
            return emails
            
        except Exception as e:
            print(f"Error searching emails: {e}")
            return []