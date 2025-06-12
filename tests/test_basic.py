"""
Basic tests for Outlook AI Manager
"""

import pytest
from unittest.mock import Mock, patch
from src.config.settings import Settings
from src.email.processor import EmailProcessor
from src.llm.classifier import EmailClassifier

def test_settings_creation():
    """Test that settings can be created with default values"""
    settings = Settings(
        microsoft_client_id="test_id",
        microsoft_client_secret="test_secret", 
        microsoft_tenant_id="test_tenant",
        target_email="test@example.com"
    )
    
    assert settings.microsoft_client_id == "test_id"
    assert settings.dry_run == True  # Default value
    assert settings.batch_size == 50  # Default value

def test_email_processor_sender_extraction():
    """Test email processor sender extraction"""
    processor = EmailProcessor()
    
    # Mock email data
    email = {
        'from': {
            'emailAddress': {
                'address': 'test@example.com',
                'name': 'Test User'
            }
        }
    }
    
    sender_info = processor.extract_sender_info(email)
    
    assert sender_info['email'] == 'test@example.com'
    assert sender_info['name'] == 'Test User'
    assert sender_info['domain'] == 'example.com'

def test_email_processor_domain_extraction():
    """Test domain extraction from email addresses"""
    processor = EmailProcessor()
    
    assert processor._extract_domain('user@gmail.com') == 'gmail.com'
    assert processor._extract_domain('test@subdomain.example.org') == 'subdomain.example.org'
    assert processor._extract_domain('invalid_email') == 'Unknown'

def test_email_processor_promotional_patterns():
    """Test detection of promotional email patterns"""
    processor = EmailProcessor()
    
    emails = [
        {
            'subject': 'Big Sale - 50% off everything!',
            'from': {'emailAddress': {'address': 'sales@store.com', 'name': 'Store'}},
            'bodyPreview': 'Limited time offer. Click to unsubscribe.'
        },
        {
            'subject': 'Your order confirmation',
            'from': {'emailAddress': {'address': 'noreply@shop.com', 'name': 'Shop'}},
            'bodyPreview': 'Thank you for your purchase.'
        }
    ]
    
    patterns = processor.detect_promotional_patterns(emails)
    
    assert 'sales@store.com' in patterns['sale_keywords']
    assert 'sales@store.com' in patterns['unsubscribe_senders']
    assert 'noreply@shop.com' in patterns['no_reply_senders']

def test_email_processor_content_categorization():
    """Test email content categorization"""
    processor = EmailProcessor()
    
    emails = [
        {
            'id': '1',
            'subject': 'Weekly Newsletter',
            'from': {'emailAddress': {'address': 'news@site.com', 'name': 'Site'}},
            'bodyPreview': 'This weeks roundup of news'
        },
        {
            'id': '2', 
            'subject': 'Password Reset Required',
            'from': {'emailAddress': {'address': 'security@bank.com', 'name': 'Bank'}},
            'bodyPreview': 'Please verify your identity'
        },
        {
            'id': '3',
            'subject': 'Receipt for your purchase',
            'from': {'emailAddress': {'address': 'billing@store.com', 'name': 'Store'}},
            'bodyPreview': 'Order #12345 - Total: $99.99'
        }
    ]
    
    categories = processor.categorize_by_content(emails)
    
    assert '1' in categories['newsletters']
    assert '2' in categories['security']
    assert '3' in categories['receipts']

@patch('src.llm.classifier.openai')
def test_email_classifier_fallback(mock_openai):
    """Test email classifier fallback behavior"""
    # Mock OpenAI to raise an exception
    mock_openai.OpenAI.return_value.chat.completions.create.side_effect = Exception("API Error")
    
    # Mock settings to have OpenAI key
    with patch('src.llm.classifier.settings') as mock_settings:
        mock_settings.has_openai = True
        mock_settings.has_anthropic = False
        mock_settings.openai_api_key = "test_key"
        
        classifier = EmailClassifier("openai")
        
        email = {
            'id': 'test_id',
            'subject': 'Test Subject',
            'from': {'emailAddress': {'address': 'test@example.com', 'name': 'Test'}},
            'bodyPreview': 'Test body',
            'receivedDateTime': '2024-01-01T10:00:00Z'
        }
        
        result = classifier.classify_email(email)
        
        # Should return fallback classification
        assert result['email_id'] == 'test_id'
        assert result['category'] == 'UNKNOWN'
        assert result['confidence'] == 0.0

def test_settings_validation():
    """Test settings validation methods"""
    # Test Microsoft config validation
    settings = Settings()
    
    with pytest.raises(ValueError, match="Missing required Microsoft Graph configuration"):
        settings.validate_microsoft_config()
    
    # Test LLM config validation  
    with pytest.raises(ValueError, match="At least one LLM API key must be provided"):
        settings.validate_llm_config()
    
    # Test valid config
    settings.openai_api_key = "test_key"
    settings.validate_llm_config()  # Should not raise

def test_email_processor_bulk_delete_candidates():
    """Test identification of bulk delete candidates"""
    from datetime import datetime, timedelta
    
    processor = EmailProcessor()
    
    # Create emails from 35 days ago
    old_date = (datetime.now() - timedelta(days=35)).isoformat() + 'Z'
    
    emails = []
    # Create 6 emails from same sender (above threshold)
    for i in range(6):
        emails.append({
            'id': f'email_{i}',
            'from': {'emailAddress': {'address': 'spam@example.com', 'name': 'Spam'}},
            'receivedDateTime': old_date
        })
    
    # Create 3 emails from different sender (below threshold)
    for i in range(3):
        emails.append({
            'id': f'other_{i}',
            'from': {'emailAddress': {'address': 'other@example.com', 'name': 'Other'}},
            'receivedDateTime': old_date
        })
    
    candidates = processor.get_bulk_delete_candidates(emails, days_old=30, min_sender_count=5)
    
    # Should only include sender with 6+ emails
    assert 'spam@example.com' in candidates
    assert 'other@example.com' not in candidates
    assert len(candidates['spam@example.com']) == 6

def test_email_processor_empty_input():
    """Test email processor with empty input"""
    processor = EmailProcessor()
    
    report = processor.generate_processing_report([])
    assert "error" in report
    assert report["error"] == "No emails to process"
    
    patterns = processor.detect_promotional_patterns([])
    assert all(len(pattern_list) == 0 for pattern_list in patterns.values())

if __name__ == "__main__":
    pytest.main([__file__])