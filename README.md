# Outlook AI Manager

An AI-powered email management system for Outlook that helps you automatically classify, organize, and clean up your emails using Large Language Models (LLMs).

## Features

- **Intelligent Email Classification**: Uses free API-based LLMs (Groq, Google Gemini) to categorize emails as JUNK, PROMOTIONAL, IMPORTANT, or UNKNOWN
- **Explicit Provider Control**: Choose exactly which LLM provider to use - no automatic selection
- **Free LLM Options**: Support for Groq (fast) and Google Gemini (high quality) with generous free tiers
- **Bulk Email Management**: Process hundreds of emails efficiently with batch classification
- **Microsoft Graph Integration**: Secure connection to Outlook/Office 365 accounts
- **Dry Run Mode**: Test classifications without making actual changes
- **Sender Analysis**: Identify patterns in email senders to create automated rules
- **Rich CLI Interface**: Beautiful command-line interface with progress bars and tables

## Installation

### Prerequisites

- Python 3.10 or higher
- [UV package manager](https://github.com/astral-sh/uv) (recommended) or pip
- Microsoft Azure App Registration (for Outlook access)
- One free LLM provider API key:
  - **Groq** (free tier, very fast)
  - **Google Gemini** (free tier, high quality)

### Quick Start

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd outlook-ai-manager
   ```

2. **Install dependencies**:
   ```bash
   # With UV (recommended)
   uv sync
   
   # Or with pip
   pip install -e .
   ```

3. **Set up free LLM**:
   ```bash
   # Interactive setup (recommended)
   uv run python scripts/install_free_llms.py
   
   # Or get help manually
   uv run outlook-ai llm-setup
   ```

4. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

5. **Test the setup**:
   ```bash
   uv run outlook-ai setup
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

| Provider | Cost | Speed | Quality | Batch Support |
|----------|------|-------|---------|---------------|
| Groq | Free tier | Very Fast | Good | Individual only |
| Gemini | Free tier | Fast | Very Good | Full batch support |
| OpenAI | Paid | Fast | Excellent | Full batch support |
| Anthropic | Paid | Medium | Excellent | Full batch support |

**Recommendation**: Use **Groq** for speed or **Gemini** for quality and batch processing.

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
uv run outlook-ai setup

# Show email statistics
uv run outlook-ai stats

# Analyze emails without making changes
uv run outlook-ai analyze --limit 100 --folder inbox

# Clean up emails with automatic junk deletion
uv run outlook-ai clean --limit 200 --auto-delete --confidence-threshold 0.9

# Analyze sender patterns
uv run outlook-ai sender-analysis --sender "example@domain.com"
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

#### 1. Initial Cleanup of Junk Account
```bash
# First, analyze what you have
uv run outlook-ai stats

# Analyze recent emails to see classification quality
uv run outlook-ai analyze --limit 50 --save-results

# Clean up with high confidence threshold (safe)
uv run outlook-ai clean --limit 500 --auto-delete --confidence-threshold 0.9

# Review results and adjust threshold as needed
uv run outlook-ai clean --limit 200 --auto-delete --confidence-threshold 0.8
```

#### 2. Ongoing Maintenance
```bash
# Daily cleanup of new emails
uv run outlook-ai clean --days 1 --auto-delete --confidence-threshold 0.85

# Weekly cleanup of promotional emails
uv run outlook-ai clean --days 7 --folder inbox --auto-delete
```

## Project Structure

```
outlook-ai-manager/
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