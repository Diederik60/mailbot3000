import msal
import requests
from typing import Optional, Dict, Any
from src.config.settings import settings
import json
from pathlib import Path

class MicrosoftAuthenticator:
    def __init__(self):
        self.client_id = settings.microsoft_client_id
        self.client_secret = settings.microsoft_client_secret
        self.tenant_id = settings.microsoft_tenant_id
        self.scopes = settings.scopes
        self.authority = f"{settings.authority}/{self.tenant_id}"
        
        # Token cache file
        self.token_cache_file = Path("token_cache.json")
        
        # Create MSAL app
        self.app = msal.ConfidentialClientApplication(
            client_id=self.client_id,
            client_credential=self.client_secret,
            authority=self.authority,
            token_cache=self._load_token_cache()
        )
    
    def _load_token_cache(self) -> msal.SerializableTokenCache:
        """Load token cache from file if it exists."""
        cache = msal.SerializableTokenCache()
        if self.token_cache_file.exists():
            try:
                with open(self.token_cache_file, 'r') as f:
                    cache.deserialize(f.read())
            except Exception as e:
                print(f"Warning: Could not load token cache: {e}")
        return cache
    
    def _save_token_cache(self) -> None:
        """Save token cache to file."""
        if self.app.token_cache.has_state_changed:
            try:
                with open(self.token_cache_file, 'w') as f:
                    f.write(self.app.token_cache.serialize())
            except Exception as e:
                print(f"Warning: Could not save token cache: {e}")
    
    def get_access_token(self) -> Optional[str]:
        """Get access token, using cache if available or requesting new one."""
        # Try to get token from cache first
        accounts = self.app.get_accounts()
        if accounts:
            result = self.app.acquire_token_silent(
                scopes=self.scopes,
                account=accounts[0]
            )
            if result and "access_token" in result:
                return result["access_token"]
        
        # If no cached token, get new one using client credentials flow
        result = self.app.acquire_token_for_client(scopes=self.scopes)
        
        if "access_token" in result:
            self._save_token_cache()
            return result["access_token"]
        else:
            print(f"Error getting token: {result.get('error_description', 'Unknown error')}")
            return None
    
    def test_connection(self) -> bool:
        """Test if we can connect to Microsoft Graph API."""
        token = self.get_access_token()
        if not token:
            return False
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(
                f"{settings.graph_base_url}/me",
                headers=headers,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authorization headers for API requests."""
        token = self.get_access_token()
        if not token:
            raise Exception("Could not obtain access token")
        
        return {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }