# mailbot3000
mailbot3000

# Project structure
```
outlook-ai-manager/
│
├── src/                             # Main source code (importable package)
│   ├── __init__.py                  # Makes src a Python package
│   ├── auth/                        # Authentication module
│   │   ├── __init__.py              # Makes auth a subpackage
│   │   └── microsoft_auth.py        # Microsoft Graph API authentication
│   ├── email/                       # Email operations module
│   │   ├── __init__.py              
│   │   ├── fetcher.py               # Fetch emails from Outlook
│   │   └── processor.py             # Process and transform email data
│   ├── llm/                         # AI/LLM integration module
│   │   ├── __init__.py              
│   │   ├── classifier.py            # Email classification logic
│   │   └── prompts.py               # LLM prompts and templates
│   ├── actions/                     # Email action module
│   │   ├── __init__.py              
│   │   └── email_actions.py         # Delete, move, organize emails
│   ├── config/                      # Configuration module
│   │   ├── __init__.py              
│   │   └── settings.py              # App settings and environment vars
│   └── main.py                      # CLI entry point
│
├── tests/                           # Test files
│   └── __init__.py                  
│
├── pyproject.toml                   # Project configuration (replaces setup.py)
├── uv.lock                          # Dependency lock file (auto-generated)
├── .env.example                     # Environment variable template
├── .gitignore                       # Git ignore patterns
└── README.md                        # Project documentation
```