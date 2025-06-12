#!/usr/bin/env python3
"""
Gmail API setup script
"""

import sys
from pathlib import Path

def main():
    print("🚀 Gmail API Setup Assistant")
    print("=" * 40)
    
    # Check if running from project root
    if not Path("pyproject.toml").exists():
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Check .env file
    env_file = Path(".env")
    if not env_file.exists():
        print("📝 Creating .env file from template...")
        if Path(".env.example").exists():
            import shutil
            shutil.copy(".env.example", ".env")
            print("✅ Created .env file")
        else:
            print("❌ .env.example not found")
            return
    
    # Update .env for Gmail
    print("\n📧 Configuring Gmail settings...")
    
    gmail_address = input("Enter your Gmail address: ").strip()
    if not gmail_address or "@gmail.com" not in gmail_address:
        print("❌ Please enter a valid Gmail address")
        return
    
    # Update .env file
    with open(env_file, 'r') as f:
        lines = f.readlines()
    
    # Update relevant lines
    updated_provider = False
    updated_gmail = False
    updated_target = False
    
    for i, line in enumerate(lines):
        if line.startswith('EMAIL_PROVIDER='):
            lines[i] = 'EMAIL_PROVIDER=gmail\n'
            updated_provider = True
        elif line.startswith('GMAIL_ADDRESS='):
            lines[i] = f'GMAIL_ADDRESS={gmail_address}\n'
            updated_gmail = True
        elif line.startswith('TARGET_EMAIL='):
            lines[i] = f'TARGET_EMAIL={gmail_address}\n'
            updated_target = True
    
    # Add missing lines
    if not updated_provider:
        lines.append('EMAIL_PROVIDER=gmail\n')
    if not updated_gmail:
        lines.append(f'GMAIL_ADDRESS={gmail_address}\n')
    if not updated_target:
        lines.append(f'TARGET_EMAIL={gmail_address}\n')
    
    with open(env_file, 'w') as f:
        f.writelines(lines)
    
    print("✅ Updated .env file")
    
    # Check for credentials file
    creds_file = Path("credentials.json")
    if creds_file.exists():
        print("✅ credentials.json found")
    else:
        print("\n⚠️  credentials.json not found")
        print("\nTo complete setup:")
        print("1. Go to https://console.cloud.google.com")
        print("2. Create a project and enable Gmail API")
        print("3. Create OAuth 2.0 credentials (Desktop app)")
        print("4. Download and save as 'credentials.json' in project root")
    
    print("\n🎯 Next steps:")
    print("1. Ensure credentials.json is in place")
    print("2. Run: uv run outlook-ai setup")
    print("3. Grant permissions when prompted")
    print("4. Test with: uv run outlook-ai stats")
    
    print("\n🔧 For LLM setup:")
    print("Run: uv run python scripts/install_free_llms.py")

if __name__ == "__main__":
    main()