from pydantic_settings import BaseSettings
from typing import Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    # Microsoft Graph API
    microsoft_client_id: Optional[str] = None
    microsoft_client_secret: Optional[str] = None
    microsoft_tenant_id: Optional[str] = None
    
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
    
    def validate_microsoft_config(self) -> None:
        """Validate Microsoft Graph configuration"""
        missing = []
        if not self.microsoft_client_id:
            missing.append("MICROSOFT_CLIENT_ID")
        if not self.microsoft_client_secret:
            missing.append("MICROSOFT_CLIENT_SECRET")
        if not self.microsoft_tenant_id:
            missing.append("MICROSOFT_TENANT_ID")
        if not self.target_email:
            missing.append("TARGET_EMAIL")
        
        if missing:
            raise ValueError(f"Missing required Microsoft Graph configuration: {', '.join(missing)}")
    
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