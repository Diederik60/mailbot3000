import json
from typing import Dict, Any, List, Optional
from src.config.settings import settings
from src.llm.prompts import EMAIL_CLASSIFICATION_PROMPT, BATCH_CLASSIFICATION_PROMPT, SENDER_ANALYSIS_PROMPT
import re

# Import handlers for different LLM providers
class LLMProvider:
    """Base class for LLM providers"""
    
    def __init__(self, name: str):
        self.name = name
    
    def is_available(self) -> bool:
        """Check if this provider is available"""
        raise NotImplementedError
    
    def call_llm(self, prompt: str, temperature: float = 0.1) -> str:
        """Make API call to the LLM"""
        raise NotImplementedError

class GroqProvider(LLMProvider):
    """Groq provider (free tier available)"""
    
    def __init__(self):
        super().__init__("groq")
        try:
            import groq
            self.client = groq.Groq(api_key=settings.groq_api_key)
            self._available = True
        except ImportError:
            print("Groq library not installed. Install with: uv add groq")
            self._available = False
        except Exception:
            self._available = False
    
    def is_available(self) -> bool:
        return settings.has_groq and self._available
    
    def call_llm(self, prompt: str, temperature: float = 0.1) -> str:
        try:
            completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-8b-instant",  # Free model
                temperature=temperature,
                max_tokens=1000
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"Groq error: {e}")
            return ""

class GeminiProvider(LLMProvider):
    """Google Gemini provider (free tier available)"""
    
    def __init__(self):
        super().__init__("gemini")
        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.google_api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')  # Free model
            self._available = True
        except ImportError:
            print("Google GenerativeAI library not installed. Install with: uv add google-generativeai")
            self._available = False
        except Exception:
            self._available = False
    
    def is_available(self) -> bool:
        return settings.has_google and self._available
    
    def call_llm(self, prompt: str, temperature: float = 0.1) -> str:
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": 1000,
                }
            )
            return response.text
        except Exception as e:
            print(f"Gemini error: {e}")
            return ""

class OpenAIProvider(LLMProvider):
    """OpenAI provider (paid)"""
    
    def __init__(self):
        super().__init__("openai")
        try:
            import openai
            self.client = openai.OpenAI(api_key=settings.openai_api_key)
            self._available = True
        except ImportError:
            self._available = False
        except Exception:
            self._available = False
    
    def is_available(self) -> bool:
        return settings.has_openai and self._available
    
    def call_llm(self, prompt: str, temperature: float = 0.1) -> str:
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI error: {e}")
            return ""

class AnthropicProvider(LLMProvider):
    """Anthropic provider (paid)"""
    
    def __init__(self):
        super().__init__("anthropic")
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
            self._available = True
        except ImportError:
            self._available = False
        except Exception:
            self._available = False
    
    def is_available(self) -> bool:
        return settings.has_anthropic and self._available
    
    def call_llm(self, prompt: str, temperature: float = 0.1) -> str:
        try:
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            print(f"Anthropic error: {e}")
            return ""

class EmailClassifier:
    def __init__(self, provider: Optional[str] = None):
        """
        Initialize email classifier with explicit provider selection.
        
        Args:
            provider: "groq", "gemini", "openai", "anthropic" or None to use settings
        """
        self.providers = {
            "groq": GroqProvider(),
            "gemini": GeminiProvider(),
            "openai": OpenAIProvider(),
            "anthropic": AnthropicProvider()
        }
        
        # Use provided provider or fall back to settings
        provider_name = provider or settings.llm_provider
        self.provider = self._get_provider(provider_name)
        
        if not self.provider:
            raise ValueError(f"LLM provider '{provider_name}' is not available")
    
    def _get_provider(self, provider_name: str) -> Optional[LLMProvider]:
        """Get a specific provider if available"""
        if provider_name not in self.providers:
            available = list(self.providers.keys())
            raise ValueError(f"Unknown provider '{provider_name}'. Available: {', '.join(available)}")
        
        provider = self.providers[provider_name]
        if provider.is_available():
            return provider
        return None
    
    def classify_email(self, email: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify a single email.
        
        Args:
            email: Email data from Microsoft Graph API or Gmail API
            
        Returns:
            Classification result
        """
        # Extract email data
        subject = email.get('subject', 'No Subject')
        sender = self._extract_sender(email)
        body_preview = email.get('bodyPreview', '')[:500]  # Limit preview length
        received_date = email.get('receivedDateTime', '')
        
        # Create prompt
        prompt = EMAIL_CLASSIFICATION_PROMPT.format(
            subject=subject,
            sender=sender,
            body_preview=body_preview,
            received_date=received_date
        )
        
        # Get classification
        response = self.provider.call_llm(prompt)
        
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                result['email_id'] = email.get('id')
                result['provider_used'] = self.provider.name
                return result
            else:
                # Fallback if JSON parsing fails
                return self._create_fallback_classification(email, "Failed to parse LLM response")
        
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return self._create_fallback_classification(email, "JSON decode error")
    
    def classify_emails_batch(self, emails: List[Dict[str, Any]], batch_size: int = 10) -> List[Dict[str, Any]]:
        """
        Classify multiple emails in batches for efficiency.
        
        Args:
            emails: List of email data
            batch_size: Number of emails per batch
            
        Returns:
            List of classification results
        """
        results = []
        
        for i in range(0, len(emails), batch_size):
            batch = emails[i:i + batch_size]
            
            # For free LLMs, use individual classification for better reliability
            # Batch processing can be unreliable with smaller models
            if self.provider.name in ["groq"]:
                for email in batch:
                    results.append(self.classify_email(email))
            else:
                # Use batch processing for premium models and Gemini
                batch_results = self._classify_batch(batch)
                results.extend(batch_results)
        
        return results
    
    def _classify_batch(self, emails: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Batch classification for supported models"""
        # Prepare batch data
        emails_data = []
        for email in emails:
            email_data = {
                'id': email.get('id'),
                'subject': email.get('subject', 'No Subject')[:100],
                'sender': self._extract_sender(email),
                'body_preview': email.get('bodyPreview', '')[:200],
                'received_date': email.get('receivedDateTime', '')
            }
            emails_data.append(email_data)
        
        # Create batch prompt
        prompt = BATCH_CLASSIFICATION_PROMPT.format(
            emails_data=json.dumps(emails_data, indent=2)
        )
        
        # Get batch classification
        response = self.provider.call_llm(prompt)
        
        try:
            # Extract JSON array from response
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                batch_results = json.loads(json_match.group())
                # Add provider info
                for result in batch_results:
                    result['provider_used'] = self.provider.name
                return batch_results
            else:
                # Fallback to individual classification
                return [self.classify_email(email) for email in emails]
        
        except json.JSONDecodeError:
            # Fallback to individual classification
            return [self.classify_email(email) for email in emails]
    
    def analyze_sender(self, sender: str, sample_subjects: List[str], count: int) -> Dict[str, Any]:
        """
        Analyze a sender to create classification rules.
        
        Args:
            sender: Sender email address
            sample_subjects: Sample subject lines from this sender
            count: Number of emails from this sender
            
        Returns:
            Sender analysis result
        """
        domain = sender.split('@')[-1] if '@' in sender else sender
        
        prompt = SENDER_ANALYSIS_PROMPT.format(
            sender=sender,
            domain=domain,
            count=count,
            sample_subjects=sample_subjects[:5]  # Limit to 5 samples
        )
        
        response = self.provider.call_llm(prompt)
        
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                result['provider_used'] = self.provider.name
                return result
        except json.JSONDecodeError:
            pass
        
        return {
            'sender_category': 'UNKNOWN',
            'confidence': 0.0,
            'reasoning': 'Failed to analyze sender',
            'suggested_rule': 'manual_review',
            'provider_used': self.provider.name
        }
    
    def _extract_sender(self, email: Dict[str, Any]) -> str:
        """Extract sender email address from email data."""
        sender_data = email.get('from', {})
        if isinstance(sender_data, dict):
            email_address = sender_data.get('emailAddress', {})
            return email_address.get('address', 'Unknown Sender')
        return str(sender_data)
    
    def _create_fallback_classification(self, email: Dict[str, Any], reason: str) -> Dict[str, Any]:
        """Create a fallback classification when LLM fails."""
        return {
            'email_id': email.get('id'),
            'category': 'UNKNOWN',
            'confidence': 0.0,
            'reason': reason,
            'suggested_action': 'manual_review',
            'folder_suggestion': None,
            'provider_used': self.provider.name if self.provider else 'none'
        }
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about available providers"""
        available_providers = [name for name, provider in self.providers.items() if provider.is_available()]
        
        return {
            'current_provider': self.provider.name if self.provider else None,
            'selected_provider': settings.llm_provider,
            'available_providers': available_providers,
            'free_providers': [p for p in available_providers if p in ['groq', 'gemini']],
            'premium_providers': [p for p in available_providers if p in ['openai', 'anthropic']]
        }