#!/usr/bin/env python3
"""
Development script to check if everything is set up correctly
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def check_environment():
    """Check if .env file exists and has required variables"""
    print("🔍 Checking environment configuration...")
    
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found. Please copy .env.example to .env and fill in values.")
        return False
    
    required_vars = [
        "MICROSOFT_CLIENT_ID",
        "MICROSOFT_CLIENT_SECRET", 
        "MICROSOFT_TENANT_ID",
        "TARGET_EMAIL"
    ]
    
    missing = []
    with open(env_file) as f:
        content = f.read()
        for var in required_vars:
            if f"{var}=" not in content or f"{var}=your_" in content:
                missing.append(var)
    
    if missing:
        print(f"❌ Missing or placeholder values for: {', '.join(missing)}")
        return False
    
    print("✅ Environment configuration looks good")
    return True

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("\n🔍 Checking dependencies...")
    
    required_packages = [
        "msal", "requests", "pydantic", "pydantic_settings", 
        "rich", "click", "python_dateutil", "pytz"
    ]
    
    optional_packages = ["openai", "anthropic"]
    
    missing_required = []
    missing_optional = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_required.append(package)
    
    for package in optional_packages:
        try:
            __import__(package)
        except ImportError:
            missing_optional.append(package)
    
    if missing_required:
        print(f"❌ Missing required packages: {', '.join(missing_required)}")
        print("Run: uv sync")
        return False
    
    if missing_optional:
        print(f"⚠️  Missing optional LLM packages: {', '.join(missing_optional)}")
        print("You need at least one LLM provider. Install with: uv add openai anthropic")
    
    print("✅ All required dependencies are installed")
    return True

def check_project_structure():
    """Check if all required files and directories exist"""
    print("\n🔍 Checking project structure...")
    
    required_files = [
        "src/__init__.py",
        "src/main.py", 
        "src/config/__init__.py",
        "src/config/settings.py",
        "src/auth/__init__.py",
        "src/auth/microsoft_auth.py",
        "src/email/__init__.py", 
        "src/email/fetcher.py",
        "src/email/processor.py",
        "src/llm/__init__.py",
        "src/llm/classifier.py",
        "src/llm/prompts.py",
        "src/actions/__init__.py",
        "src/actions/email_actions.py",
        "pyproject.toml"
    ]
    
    missing = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing.append(file_path)
    
    if missing:
        print(f"❌ Missing files: {', '.join(missing)}")
        return False
    
    print("✅ Project structure is complete")
    return True

def check_imports():
    """Check if all modules can be imported"""
    print("\n🔍 Checking module imports...")
    
    try:
        from config.settings import settings
        print("✅ Settings module imported successfully")
    except Exception as e:
        print(f"❌ Failed to import settings: {e}")
        return False
    
    try:
        from auth.microsoft_auth import MicrosoftAuthenticator
        print("✅ Authentication module imported successfully")
    except Exception as e:
        print(f"❌ Failed to import authentication: {e}")
        return False
    
    try:
        from email.fetcher import EmailFetcher
        print("✅ Email fetcher imported successfully")
    except Exception as e:
        print(f"❌ Failed to import email fetcher: {e}")
        return False
    
    try:
        from llm.classifier import EmailClassifier
        print("✅ LLM classifier imported successfully")
    except Exception as e:
        print(f"❌ Failed to import LLM classifier: {e}")
        return False
    
    return True

def check_llm_configuration():
    """Check LLM API configuration"""
    print("\n🔍 Checking LLM configuration...")
    
    try:
        from config.settings import settings
        
        has_openai = False
        has_anthropic = False
        
        try:
            import openai
            if settings.openai_api_key:
                has_openai = True
                print("✅ OpenAI configuration found")
        except ImportError:
            pass
        
        try:
            import anthropic
            if settings.anthropic_api_key:
                has_anthropic = True
                print("✅ Anthropic configuration found")
        except ImportError:
            pass
        
        if not (has_openai or has_anthropic):
            print("❌ No LLM provider configured. Please set OPENAI_API_KEY or ANTHROPIC_API_KEY")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking LLM configuration: {e}")
        return False

def main():
    """Run all checks"""
    print("🚀 Outlook AI Manager - Setup Check\n")
    
    checks = [
        check_project_structure,
        check_dependencies, 
        check_environment,
        check_imports,
        check_llm_configuration
    ]
    
    results = []
    for check in checks:
        results.append(check())
    
    print("\n" + "="*50)
    
    if all(results):
        print("🎉 All checks passed! Your setup looks good.")
        print("\nNext steps:")
        print("1. Run: uv run outlook-ai setup")
        print("2. Test with: uv run outlook-ai stats")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()