#!/usr/bin/env python3
"""
Debug script to see what emails are actually being fetched
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def debug_email_fetching():
    """Debug what emails are being fetched"""
    from email.email_interface import EmailInterface
    from config.settings import settings
    
    print("🔍 Email Fetching Debug")
    print("=" * 50)
    
    email_interface = EmailInterface()
    
    # Show current configuration
    print(f"Email Provider: {settings.email_provider}")
    print(f"Target Email: {settings.target_email}")
    print(f"Gmail Address: {getattr(settings, 'gmail_address', 'Not set')}")
    
    # Get email stats
    print("\n📊 Email Statistics:")
    stats = email_interface.get_email_stats()
    for folder, data in stats.items():
        print(f"  {folder}: {data['total_count']} total, {data['unread_count']} unread")
    
    # Fetch a few emails from inbox
    print("\n📧 Sample Emails from INBOX:")
    emails = email_interface.fetch_emails(folder="INBOX", limit=3)
    
    for i, email in enumerate(emails, 1):
        print(f"\nEmail {i}:")
        print(f"  ID: {email.get('id', 'No ID')[:20]}...")
        print(f"  Subject: {email.get('subject', 'No Subject')[:60]}...")
        print(f"  From: {email.get('from', {}).get('emailAddress', {}).get('address', 'Unknown')}")
        print(f"  Date: {email.get('receivedDateTime', 'Unknown')}")
        print(f"  Preview: {email.get('bodyPreview', '')[:100]}...")
    
    # Check if we're getting the right emails
    print(f"\n✅ Fetched {len(emails)} emails from INBOX")
    
    if len(emails) == 0:
        print("❌ No emails found! This might be the issue.")
        print("\nTroubleshooting:")
        print("1. Check if you're looking at the right Gmail account")
        print("2. Try different folder names (SPAM, SENT, etc.)")
        print("3. Check Gmail API permissions")
    
    # Try other common folders
    print("\n🔍 Trying other folders...")
    for folder in ["SPAM", "SENT", "TRASH", "PROMOTIONS", "SOCIAL", "UPDATES"]:
        try:
            folder_emails = email_interface.fetch_emails(folder=folder, limit=1)
            print(f"  {folder}: {len(folder_emails)} emails found")
        except Exception as e:
            print(f"  {folder}: Error - {e}")

if __name__ == "__main__":
    debug_email_fetching()