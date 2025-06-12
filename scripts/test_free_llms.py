#!/usr/bin/env python3
"""
Test script for free LLM providers
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_llm_provider(provider_name):
    """Test a specific LLM provider"""
    print(f"\n🧪 Testing {provider_name}...")
    
    try:
        from llm.classifier import EmailClassifier
        
        # Create classifier with specific provider
        classifier = EmailClassifier(provider_name)
        
        # Test email
        test_email = {
            'id': 'test_123',
            'subject': 'URGENT: 50% OFF Sale - Limited Time Only!',
            'from': {
                'emailAddress': {
                    'address': 'sales@marketingcompany.com',
                    'name': 'Marketing Company'
                }
            },
            'bodyPreview': 'Huge sale this weekend only! Click here to shop now and save big. Unsubscribe link at bottom.',
            'receivedDateTime': '2024-01-15T10:30:00Z'
        }
        
        print(f"   Testing classification...")
        result = classifier.classify_email(test_email)
        
        print(f"   ✅ Provider: {result.get('provider_used', 'unknown')}")
        print(f"   ✅ Category: {result.get('category', 'unknown')}")
        print(f"   ✅ Confidence: {result.get('confidence', 0):.2f}")
        print(f"   ✅ Reason: {result.get('reason', 'No reason')[:60]}...")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    """Test all available providers"""
    print("🚀 Testing Free LLM Providers")
    print("=" * 40)
    
    # Import after adding path
    try:
        from config.settings import settings
        from llm.classifier import EmailClassifier
    except Exception as e:
        print(f"❌ Failed to import modules: {e}")
        print("Make sure you're running from the project root directory")
        return
    
    # Check what's available
    print("📋 Checking available providers...")
    available = settings.available_providers
    selected = settings.llm_provider
    
    if not available:
        print("❌ No LLM providers available")
        print("\nTo set up free providers:")
        print("1. Run: python scripts/install_free_llms.py")
        print("2. Or: uv run outlook-ai llm-setup")
        return
    
    print(f"✅ Available providers: {', '.join(available)}")
    print(f"📌 Selected provider: {selected}")
    
    if selected not in available:
        print(f"⚠️  Selected provider '{selected}' is not available!")
        print("Please update LLM_PROVIDER in your .env file")
        return
    
    # Test the selected provider
    print(f"\n🎯 Testing selected provider: {selected}")
    success = test_llm_provider(selected)
    
    # Test other available providers if requested
    other_providers = [p for p in available if p != selected]
    if other_providers and input(f"\nTest other providers {other_providers}? (y/n): ").lower() == 'y':
        for provider in other_providers:
            test_llm_provider(provider)
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 Testing Complete - Your setup is ready!")
        print("✅ You can now classify emails with your configured LLM")
    else:
        print("❌ Testing failed. Check your API keys and configuration.")

if __name__ == "__main__":
    main()