"""
Gmail API authentication handler
"""

import os
import pickle
from pathlib import Path
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src.config.settings import settings

class GmailAuthenticator:
    def __init__(self):
        self.scopes = settings.gmail_scopes
        self.credentials_file = settings.google_credentials_file
        self.token_file = "token.pickle"
        self.service = None
    
    def authenticate(self) -> bool:
        """Authenticate and build Gmail service"""
        creds = self._get_credentials()
        if not creds:
            return False
        
        try:
            self.service = build('gmail', 'v1', credentials=creds)
            return True
        except Exception as e:
            print(f"Error building Gmail service: {e}")
            return False
    
    def _get_credentials(self) -> Optional[Credentials]:
        """Get valid credentials for Gmail API"""
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        
        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Error refreshing credentials: {e}")
                    creds = None
            
            if not creds:
                creds = self._get_new_credentials()
            
            # Save credentials for next run
            if creds:
                with open(self.token_file, 'wb') as token:
                    pickle.dump(creds, token)
        
        return creds
    
    def _get_new_credentials(self) -> Optional[Credentials]:
        """Get new credentials via OAuth flow"""
        if not Path(self.credentials_file).exists():
            print(f"Credentials file '{self.credentials_file}' not found.")
            print("Please download it from Google Cloud Console.")
            return None
        
        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                self.credentials_file, self.scopes
            )
            # Run local server for OAuth
            creds = flow.run_local_server(port=0)
            return creds
        except Exception as e:
            print(f"Error in OAuth flow: {e}")
            return None
    
    def test_connection(self) -> bool:
        """Test Gmail API connection"""
        if not self.service:
            if not self.authenticate():
                return False
        
        try:
            # Try to get user profile
            profile = self.service.users().getProfile(userId='me').execute()
            print(f"Connected to Gmail: {profile.get('emailAddress')}")
            return True
        except HttpError as e:
            print(f"Gmail API error: {e}")
            return False
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False
    
    def get_service(self):
        """Get authenticated Gmail service"""
        if not self.service:
            if not self.authenticate():
                raise Exception("Failed to authenticate with Gmail")
        return self.service