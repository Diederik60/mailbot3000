### Prerequisites

- Python 3.10 or higher
- [UV package manager](https://github.com/astral-sh/uv) (recommended) or pip
- **Gmail API credentials** OR Microsoft Azure App Registration
- One free LLM provider API key:
  - **Groq** (free tier, very fast)
  - **Google Gemini** (free tier, high quality)

### Quick Start with Gmail (Recommended - No Paywalls!)

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd mailbot-manager
   ```

2. **Install dependencies**:
   ```bash
   uv sync
   ```

3. **Set up Gmail API (5 minutes, completely free)**:
   ```bash
   # Interactive Gmail setup
   uv run python scripts/setup_gmail.py
   
   # Or get detailed instructions
   uv run mailbot gmail-setup
   ```

4. **Set up free LLM**:
   ```bash
   uv run python scripts/install_free_llms.py
   ```

5. **Test the setup**:
   ```bash
   uv run mailbot setup
   # Mailbot Manager

An AI-powered email management system for Outlook that helps you automatically classify, organize, and clean up your emails using Large Language Models (LLMs).

## Features

- **Intelligent Email Classification**: Uses free API-based LLMs to categorize emails as JUNK, PROMOTIONAL, IMPORTANT, or UNKNOWN
- **Dual Email Support**: Works with both Gmail and Outlook
- **Explicit Provider Control**: Choose which LLM provider to use 
- **Bulk Email Management**: Process emails efficiently with batch classification
- **Dry Run Mode**: Test classifications without making actual changes
- **Sender Analysis**: Identify patterns in email senders to create automated rules
- **Rich CLI Interface**: Command-line interface with progress bars and tables

## Installation

   ```

### Alternative: Outlook Setup (Requires Azure)

If you prefer Outlook or already have Azure setup:

1. **Follow steps 1-2 above**
2. **Set up Microsoft Graph API**:
   ```bash
   # Set email provider to outlook in .env
   EMAIL_PROVIDER=outlook
   ```
3. **Create Azure App Registration** (see Azure setup section below)
4. **Continue with steps 4-5 above**

## Email Provider Setup

### Gmail API Setup (Free & Easy)

#### Step 1: Google Cloud Console
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing one
3. Enable the Gmail API

#### Step 2: Create Credentials
1. Go to "Credentials" in the left sidebar
2. Click "+ CREATE CREDENTIALS" → "OAuth client ID"
3. Choose "Desktop application"
4. Download the JSON credentials file

#### Step 3: Configure Project
```bash
# Save credentials file as 'credentials.json' in project root
# Update .env:
EMAIL_PROVIDER=gmail
GMAIL_ADDRESS=your_gmail@gmail.com
TARGET_EMAIL=your_gmail@gmail.com
```

### Microsoft Graph API Setup (Azure Required)

Only follow this if you want to use Outlook instead of Gmail:

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to "App registrations" → "New registration"
3. Register your app with these permissions:
   - `Mail.ReadWrite`
   - `Mail.Send`
   - `User.Read`
4. Add credentials to `.env`:
   ```env
   EMAIL_PROVIDER=outlook
   MICROSOFT_CLIENT_ID=your_client_id
   MICROSOFT_CLIENT_SECRET=your_client_secret
   MICROSOFT_TENANT_ID=your_tenant_id
   TARGET_EMAIL=your_outlook_email@outlook.com
   ```

## Configuration

### Free LLM Setup Options

#### Option 1: Groq (Free Tier, Very Fast)
```bash
# Get API key from https://console.groq.com
# Add to .env:
GROQ_API_KEY=your_groq_api_key_here
LLM_PROVIDER=groq
```

#### Option 2: Google Gemini (Free Tier, High Quality)
```bash
# Get API key from https://makersuite.google.com/app/apikey
# Add to .env:
GOOGLE_API_KEY=your_google_api_key_here
LLM_PROVIDER=gemini
```

### Provider Comparison

| Provider | Cost | Setup Time | API Limits | Complexity |
|----------|------|------------|------------|------------|
| **Gmail** | Free | 5 minutes | Very generous | Easy |
| **Outlook** | Free* | 15+ minutes | Good | Complex |

*Outlook requires Azure account which may have usage limits

| LLM Provider | Cost | Speed | Quality | Batch Support |
|--------------|------|-------|---------|---------------|
| **Groq** | Free tier | Very Fast | Good | Individual only |
| **Gemini** | Free tier | Fast | Very Good | Full batch support |
| OpenAI | Paid | Fast | Excellent | Full batch support |
| Anthropic | Paid | Medium | Excellent | Full batch support |

**💡 Recommended Setup**: Gmail + Groq (both completely free, 10 minutes total setup)

### Environment Variables

Create a `.env` file with:

```env
# Microsoft Graph API Configuration
MICROSOFT_CLIENT_ID=your_application_client_id
MICROSOFT_CLIENT_SECRET=your_client_secret
MICROSOFT_TENANT_ID=your_tenant_id

# LLM API Configuration (choose one or both)
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# Email Configuration
TARGET_EMAIL=your_secondary_email@outlook.com

# Processing Configuration
DRY_RUN=true
BATCH_SIZE=50
MAX_EMAILS_PER_RUN=500
```

## Usage

### Basic Commands

```bash
# Test setup and authentication
uv run mailbot setup

# Show email statistics  
uv run mailbot stats

# Get Gmail setup help
uv run mailbot gmail-setup

# Check available providers
uv run mailbot providers

# Analyze emails without making changes
uv run mailbot analyze --limit 100

# Clean up emails with automatic junk deletion
uv run mailbot clean --limit 200 --auto-delete --confidence-threshold 0.9

# Use specific providers
uv run mailbot analyze --provider gemini --limit 50
```

### Command Options

#### `analyze` command
- `--limit`: Number of emails to analyze (default: 50)
- `--folder`: Folder to analyze - inbox, junkemail, etc. (default: inbox)
- `--days`: Only analyze emails from last N days
- `--save-results`: Save classification results to JSON file

#### `clean` command
- `--limit`: Number of emails to process (default: 100)
- `--folder`: Folder to clean (default: inbox)
- `--days`: Only process emails from last N days
- `--auto-delete`: Automatically delete emails classified as JUNK
- `--confidence-threshold`: Minimum confidence for auto-actions (default: 0.8)

### Example Workflows

#### 1. Initial Cleanup of Junk Account (Gmail)
```bash
# First, check what you have
uv run mailbot stats

# Analyze recent emails to see classification quality  
uv run mailbot analyze --limit 50 --save-results

# Clean up with high confidence threshold (safe)
uv run mailbot clean --limit 500 --auto-delete --confidence-threshold 0.9

# Review results and adjust threshold as needed
uv run mailbot clean --limit 200 --auto-delete --confidence-threshold 0.8
```

#### 2. Switching Between Email Providers
```bash
# Switch to Gmail (edit .env file)
EMAIL_PROVIDER=gmail
GMAIL_ADDRESS=your_email@gmail.com

# Switch to Outlook (edit .env file) 
EMAIL_PROVIDER=outlook
TARGET_EMAIL=your_email@outlook.com

# Test the switch
uv run mailbot setup
```

## Project Structure

```
mailbot-manager/
├── src/
│   ├── auth/           # Microsoft Graph authentication
│   ├── email/          # Email fetching and processing
│   ├── llm/            # AI classification logic
│   ├── actions/        # Email operations (delete, move, etc.)
│   ├── config/         # Application settings
│   └── main.py         # CLI entry point
├── tests/              # Test suite
├── pyproject.toml      # Project configuration
├── .env.example        # Environment template
└── README.md           # This file
```

## Development

### Setting up for Development

```bash
# Install with development dependencies
uv sync --dev

# Run tests
uv run pytest

# Format code
uv run black src/

# Type checking
uv run mypy src/

# Linting
uv run flake8 src/
```

### Adding New Features

1. Create feature branch: `git checkout -b feature/new-feature`
2. Implement changes in appropriate module
3. Add tests in `tests/` directory
4. Update documentation
5. Submit pull request

## Safety Features

- **Dry Run Mode**: All operations can be tested without making actual changes
- **Confidence Thresholds**: Only high-confidence classifications trigger automatic actions
- **Backup Handling**: Deleted emails are moved to Deleted Items folder (not permanently deleted)
- **Rate Limiting**: Built-in delays to respect API limits
- **Error Handling**: Graceful handling of API errors and network issues

## Troubleshooting

### Common Issues

1. **Authentication Errors**:
   - Verify Azure app registration permissions
   - Check client ID, secret, and tenant ID in `.env`
   - Ensure admin consent has been granted

2. **No LLM Response**:
   - Check API key validity
   - Verify API quota/billing
   - Try switching between OpenAI and Anthropic

3. **Rate Limiting**:
   - Reduce `BATCH_SIZE` in `.env`
   - Add delays between operations

### Debug Mode

Set `DRY_RUN=true` in `.env` to see what actions would be taken without executing them.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- Microsoft Graph API for email access
- OpenAI and Anthropic for LLM capabilities
- Rich library for beautiful CLI output
- Click for command-line interface framework