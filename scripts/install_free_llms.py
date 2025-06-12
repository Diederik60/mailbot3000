#!/usr/bin/env python3
"""
Script to help install and configure free LLM providers
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def setup_groq():
    """Help set up Groq API"""
    print("\n🔍 Setting up Groq...")
    
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file) as f:
            content = f.read()
            if "GROQ_API_KEY=" in content and "your_groq_api_key_here" not in content:
                print("✅ Groq API key already configured")
                return True
    
    print("📋 Groq Setup Steps:")
    print("1. Visit: https://console.groq.com")
    print("2. Create an account (free)")
    print("3. Go to API Keys section")
    print("4. Create a new API key")
    
    api_key = input("\n🔑 Enter your Groq API key (or press Enter to skip): ").strip()
    
    if api_key:
        # Update .env file
        if env_file.exists():
            with open(env_file, 'r') as f:
                lines = f.readlines()
            
            # Update existing line or add new one
            updated_groq = False
            updated_provider = False
            
            for i, line in enumerate(lines):
                if line.startswith('GROQ_API_KEY='):
                    lines[i] = f'GROQ_API_KEY={api_key}\n'
                    updated_groq = True
                elif line.startswith('LLM_PROVIDER='):
                    lines[i] = 'LLM_PROVIDER=groq\n'
                    updated_provider = True
            
            if not updated_groq:
                lines.append(f'GROQ_API_KEY={api_key}\n')
            if not updated_provider:
                lines.append('LLM_PROVIDER=groq\n')
            
            with open(env_file, 'w') as f:
                f.writelines(lines)
        else:
            with open(env_file, 'w') as f:
                f.write(f'GROQ_API_KEY={api_key}\n')
                f.write('LLM_PROVIDER=groq\n')
        
        print("✅ Groq API key saved to .env")
        print("✅ LLM_PROVIDER set to groq")
        return True
    
    return False

def setup_gemini():
    """Help set up Google Gemini API"""
    print("\n🔍 Setting up Google Gemini...")
    
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file) as f:
            content = f.read()
            if "GOOGLE_API_KEY=" in content and "your_google_api_key_here" not in content:
                print("✅ Google API key already configured")
                return True
    
    print("📋 Google Gemini Setup Steps:")
    print("1. Visit: https://makersuite.google.com/app/apikey")
    print("2. Sign in with Google account")
    print("3. Click 'Create API Key'")
    print("4. Copy the generated key")
    
    api_key = input("\n🔑 Enter your Google API key (or press Enter to skip): ").strip()
    
    if api_key:
        # Update .env file
        if env_file.exists():
            with open(env_file, 'r') as f:
                lines = f.readlines()
            
            # Update existing line or add new one
            updated_google = False
            updated_provider = False
            
            for i, line in enumerate(lines):
                if line.startswith('GOOGLE_API_KEY='):
                    lines[i] = f'GOOGLE_API_KEY={api_key}\n'
                    updated_google = True
                elif line.startswith('LLM_PROVIDER='):
                    lines[i] = 'LLM_PROVIDER=gemini\n'
                    updated_provider = True
            
            if not updated_google:
                lines.append(f'GOOGLE_API_KEY={api_key}\n')
            if not updated_provider:
                lines.append('LLM_PROVIDER=gemini\n')
            
            with open(env_file, 'w') as f:
                f.writelines(lines)
        else:
            with open(env_file, 'w') as f:
                f.write(f'GOOGLE_API_KEY={api_key}\n')
                f.write('LLM_PROVIDER=gemini\n')
        
        print("✅ Google API key saved to .env")
        print("✅ LLM_PROVIDER set to gemini")
        return True
    
    return False

def install_dependencies():
    """Install optional dependencies for free LLMs"""
    print("\n📦 Installing LLM dependencies...")
    
    # Check if UV is available
    try:
        subprocess.run(['uv', '--version'], capture_output=True)
        package_manager = ['uv', 'add']
    except FileNotFoundError:
        package_manager = ['pip', 'install']
    
    dependencies = ['groq', 'google-generativeai']
    
    for dep in dependencies:
        print(f"Installing {dep}...")
        try:
            result = subprocess.run(package_manager + [dep], capture_output=True)
            if result.returncode == 0:
                print(f"✅ {dep} installed")
            else:
                print(f"❌ Failed to install {dep}")
        except Exception as e:
            print(f"❌ Error installing {dep}: {e}")

def show_provider_comparison():
    """Show comparison of available providers"""
    print("\n🔄 Provider Comparison:")
    print("┌─────────────┬─────────────┬─────────────┬─────────────────┐")
    print("│ Provider    │ Cost        │ Speed       │ Quality         │")
    print("├─────────────┼─────────────┼─────────────┼─────────────────┤")
    print("│ Groq        │ Free tier   │ Very Fast   │ Good            │")
    print("│ Gemini      │ Free tier   │ Fast        │ Very Good       │")
    print("│ OpenAI      │ Paid        │ Fast        │ Excellent       │")
    print("│ Anthropic   │ Paid        │ Medium      │ Excellent       │")
    print("└─────────────┴─────────────┴─────────────┴─────────────────┘")
    
    print("\n💡 Recommendations:")
    print("   🚀 For speed: Choose Groq")
    print("   🎯 For quality: Choose Gemini")
    print("   📊 For batch processing: Choose Gemini")

def main():
    """Run setup assistant"""
    print("🚀 Free LLM Setup Assistant")
    print("=" * 40)
    
    show_provider_comparison()
    
    # Install dependencies first
    install_dependencies()
    
    providers_setup = []
    
    print("\n" + "=" * 40)
    print("🔧 Provider Setup")
    
    # Ask user which provider they prefer
    print("\nWhich provider would you like to set up?")
    print("1. Groq (fastest)")
    print("2. Google Gemini (best quality)")
    print("3. Both")
    print("4. Skip setup")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice in ["1", "3"]:
        if setup_groq():
            providers_setup.append("Groq")
    
    if choice in ["2", "3"]:
        if setup_gemini():
            providers_setup.append("Gemini")
    
    print("\n" + "=" * 40)
    print("🎉 Setup Complete!")
    
    if providers_setup:
        print(f"✅ Configured providers: {', '.join(providers_setup)}")
        print("\nNext steps:")
        print("1. Run: uv run outlook-ai setup")
        print("2. Test with: uv run outlook-ai providers")
        print("3. Start classifying: uv run outlook-ai analyze --limit 10")
    else:
        print("❌ No providers were configured")
        print("You can manually add API keys to your .env file:")
        print("- GROQ_API_KEY=your_key")
        print("- GOOGLE_API_KEY=your_key")
        print("- LLM_PROVIDER=groq  # or gemini")

if __name__ == "__main__":
    main()