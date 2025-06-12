from pydantic_settings import BaseSettings
from typing import Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    # Email Provider Selection
    email_provider: str = "gmail"  # gmail or outlook
    
    # Microsoft Graph API (for Outlook)
    microsoft_client_id: Optional[str] = None
    microsoft_client_secret: Optional[str] = None
    microsoft_tenant_id: Optional[str] = None
    
    # Gmail API Configuration
    google_credentials_file: str = "credentials.json"
    gmail_address: Optional[str] = None
    
    # Free LLM Configuration
    groq_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    
    # Premium LLM Configuration (optional)
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # LLM Provider Selection (explicit choice)
    llm_provider: str = "groq"  # groq, gemini, openai, anthropic
    
    # Email Configuration
    target_email: Optional[str] = None
    
    # Processing Configuration
    dry_run: bool = True
    batch_size: int = 50
    max_emails_per_run: int = 500
    
    # Microsoft Graph Scopes
    scopes: list[str] = [
        "https://graph.microsoft.com/Mail.ReadWrite",
        "https://graph.microsoft.com/Mail.Send",
        "https://graph.microsoft.com/User.Read"
    ]
    
    # Gmail API Scopes
    gmail_scopes: list[str] = [
        "https://www.googleapis.com/auth/gmail.modify",
        "https://www.googleapis.com/auth/gmail.readonly"
    ]
    
    # Microsoft Graph URLs
    graph_base_url: str = "https://graph.microsoft.com/v1.0"
    authority: str = "https://login.microsoftonline.com"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @property
    def has_groq(self) -> bool:
        return self.groq_api_key is not None
    
    @property
    def has_google(self) -> bool:
        return self.google_api_key is not None
    
    @property
    def has_openai(self) -> bool:
        return self.openai_api_key is not None
    
    @property
    def has_anthropic(self) -> bool:
        return self.anthropic_api_key is not None
    
    @property
    def has_gmail_credentials(self) -> bool:
        return Path(self.google_credentials_file).exists()
    
    @property
    def has_outlook_credentials(self) -> bool:
        return all([
            self.microsoft_client_id,
            self.microsoft_client_secret, 
            self.microsoft_tenant_id
        ])
    
    @property
    def available_providers(self) -> list[str]:
        """Get list of available LLM providers"""
        providers = []
        if self.has_groq:
            providers.append("groq")
        if self.has_google:
            providers.append("gemini")
        if self.has_openai:
            providers.append("openai")
        if self.has_anthropic:
            providers.append("anthropic")
        return providers
    
    def validate_email_config(self) -> None:
        """Validate email provider configuration"""
        if self.email_provider == "gmail":
            if not self.has_gmail_credentials:
                raise ValueError(
                    f"Gmail credentials file '{self.google_credentials_file}' not found. "
                    "Please download credentials from Google Cloud Console."
                )
            if not self.gmail_address:
                raise ValueError("GMAIL_ADDRESS is required when using Gmail provider")
        
        elif self.email_provider == "outlook":
            if not self.has_outlook_credentials:
                missing = []
                if not self.microsoft_client_id:
                    missing.append("MICROSOFT_CLIENT_ID")
                if not self.microsoft_client_secret:
                    missing.append("MICROSOFT_CLIENT_SECRET")
                if not self.microsoft_tenant_id:
                    missing.append("MICROSOFT_TENANT_ID")
                raise ValueError(f"Missing required Outlook configuration: {', '.join(missing)}")
        
        else:
            raise ValueError(f"Invalid email provider '{self.email_provider}'. Use 'gmail' or 'outlook'")
        
        if not self.target_email:
            raise ValueError("TARGET_EMAIL is required")
    
    def validate_llm_config(self) -> None:
        """Validate LLM configuration"""
        available = self.available_providers
        if not available:
            raise ValueError(
                "No LLM provider available. Please configure at least one of:\n"
                "- Groq (free tier): Get API key from https://console.groq.com\n"
                "- Google Gemini (free tier): Get API key from https://makersuite.google.com\n"
                "- OpenAI (paid): Get API key from https://platform.openai.com\n"
                "- Anthropic (paid): Get API key from https://console.anthropic.com"
            )
        
        if self.llm_provider not in available:
            raise ValueError(
                f"Selected LLM provider '{self.llm_provider}' is not available.\n"
                f"Available providers: {', '.join(available)}\n"
                f"Please set LLM_PROVIDER to one of the available options."
            )

# Create global settings instance
settings = Settings()