# Complete Command Reference

## 📋 All Available Commands

### 🔧 Setup & Configuration Commands

#### `setup`
**Purpose**: Initial setup and authentication test  
**Safety**: ✅ **Completely Safe** (read-only)  
**Usage**: `uv run mailbot setup`  
**What it does**: Tests Gmail and LLM connections, validates configuration

#### `gmail-setup`
**Purpose**: Set up Gmail API credentials  
**Safety**: ✅ **Completely Safe** (documentation only)  
**Usage**: `uv run mailbot gmail-setup`  
**What it does**: Shows step-by-step Gmail API setup instructions

#### `llm-setup`
**Purpose**: Help set up free LLM providers  
**Safety**: ✅ **Completely Safe** (documentation only)  
**Usage**: `uv run mailbot llm-setup`  
**What it does**: Shows instructions for Groq/Gemini API setup

#### `providers`
**Purpose**: List available LLM providers and their status  
**Safety**: ✅ **Completely Safe** (read-only)  
**Usage**: `uv run mailbot providers`  
**What it does**: Shows which LLM providers are configured and available

---

### 📊 Information & Analysis Commands

#### `stats`
**Purpose**: Show email statistics  
**Safety**: ✅ **Completely Safe** (read-only)  
**Usage**: `uv run mailbot stats`  
**What it does**: Shows folder counts, sizes, and cleanup recommendations

#### `labels`
**Purpose**: List all Gmail labels/folders in your account  
**Safety**: ✅ **Completely Safe** (read-only)  
**Usage**: `uv run mailbot labels`  
**What it does**: Shows all Gmail labels (system, category, custom) with their IDs

#### `verify-counts`
**Purpose**: Verify email counts by actually fetching emails  
**Safety**: ✅ **Completely Safe** (read-only)  
**Usage**: 
```bash
uv run mailbot verify-counts --folder INBOX --limit 50
uv run mailbot verify-counts --folder SPAM --limit 10
```
**Options**:
- `--folder`: Folder to verify (default: INBOX)
- `--limit`: How many emails to fetch and count (default: 50)

**What it does**: Fetches actual emails to verify API count estimates

#### `analyze`
**Purpose**: Analyze emails and classify them  
**Safety**: ✅ **Completely Safe** (read-only classification)  
**Usage**: 
```bash
uv run mailbot analyze --limit 10
uv run mailbot analyze --limit 50 --folder CATEGORY_PROMOTIONS
uv run mailbot analyze --limit 20 --provider gemini --save-results
```
**Options**:
- `--limit`: Number of emails to analyze (default: 50)
- `--folder`: Folder to analyze (default: inbox)
- `--days`: Only analyze emails from last N days
- `--save-results`: Save classification results to JSON file
- `--provider`: Specify LLM provider (groq, gemini, openai, anthropic)

**What it does**: Classifies emails as JUNK/PROMOTIONAL/IMPORTANT/UNKNOWN

#### `sender-analysis`
**Purpose**: Analyze sender patterns to create classification rules  
**Safety**: ✅ **Completely Safe** (read-only)  
**Usage**: 
```bash
uv run mailbot sender-analysis --sender "example@domain.com"
uv run mailbot sender-analysis --sender "no-reply@store.com" --limit 100
```
**Options**:
- `--sender`: Email address to analyze (required)
- `--limit`: Number of emails to analyze for patterns (default: 100)

**What it does**: Analyzes email patterns from specific sender

---

### ⚠️ Action Commands (Can Modify Emails)

#### `clean`
**Purpose**: Clean up emails by classifying and organizing them  
**Safety**: ⚠️ **DEPENDS ON DRY_RUN SETTING**
- `DRY_RUN=true`: ✅ Safe (shows what would be done)
- `DRY_RUN=false`: ⚠️ **DANGEROUS** (actually modifies emails)

**Usage**: 
```bash
# Safe testing (DRY_RUN=true)
uv run mailbot clean --limit 10 --auto-delete
uv run mailbot clean --limit 50 --folder CATEGORY_PROMOTIONS

# Real cleaning (DRY_RUN=false) - BE CAREFUL!
uv run mailbot clean --limit 20 --auto-delete --confidence-threshold 0.95
```

**Options**:
- `--limit`: Number of emails to process (default: 100)
- `--folder`: Folder to clean (default: inbox)
- `--days`: Only process emails from last N days
- `--auto-delete`: Automatically delete emails classified as JUNK
- `--confidence-threshold`: Minimum confidence for auto-actions (default: 0.8)
- `--provider`: Specify LLM provider

**What it does**: Classifies emails and performs actions (delete/move) based on classification

---

## 🛡️ Safety Guidelines

### Always Safe Commands
These commands NEVER modify your emails:
- `setup`, `stats`, `labels`, `gmail-setup`, `llm-setup`, `providers`
- `analyze`, `sender-analysis`, `verify-counts`

### Potentially Dangerous Commands
- `clean` - Only modifies emails when `DRY_RUN=false`

### Safety Checks
```bash
# Verify DRY_RUN is enabled
grep DRY_RUN .env
# Should show: DRY_RUN=true

# Test safely first
uv run mailbot clean --limit 5
# Look for "[DRY RUN]" messages
```

---

## 🎯 Recommended Workflow

### 1. Initial Setup
```bash
uv run mailbot setup                    # Test connections
uv run mailbot stats                    # See your email situation
uv run mailbot labels                   # Understand your folders
```

### 2. Test Classification
```bash
uv run mailbot analyze --limit 10       # Test on small batch
uv run mailbot verify-counts --folder SPAM --limit 5  # Verify what you're seeing
```

### 3. Safe Cleanup Testing
```bash
uv run mailbot clean --limit 5 --auto-delete  # Test cleanup (DRY_RUN=true)
```

### 4. Real Cleanup (When Ready)
```bash
# Edit .env: DRY_RUN=false
uv run mailbot clean --limit 10 --auto-delete --confidence-threshold 0.95
```

---

## 📁 Common Folder Names

### Gmail System Labels
- `INBOX` - Main inbox
- `SPAM` - Spam folder
- `TRASH` - Deleted emails
- `SENT` - Sent emails
- `DRAFT` - Draft emails

### Gmail Categories
- `CATEGORY_PROMOTIONS` - Promotional emails
- `CATEGORY_SOCIAL` - Social media notifications
- `CATEGORY_UPDATES` - Updates and notifications
- `CATEGORY_FORUMS` - Forum and discussion emails
- `CATEGORY_PERSONAL` - Personal emails

Use `uv run mailbot labels` to see your specific labels.

---

## 🚨 Emergency: Stop/Undo

If something goes wrong:
1. **Stop immediately**: Ctrl+C to cancel running command
2. **Check Gmail Trash**: Deleted emails go to Trash, not permanently deleted
3. **Restore from Trash**: In Gmail web interface, select emails in Trash and click "Move to Inbox"
4. **Set DRY_RUN=true**: Prevent further modifications

---

## 💡 Pro Tips

### For Large Mailboxes (1000+ emails)
```bash
# Start small and increase gradually
uv run mailbot clean --limit 20 --confidence-threshold 0.99   # Very conservative
uv run mailbot clean --limit 50 --confidence-threshold 0.95   # Conservative  
uv run mailbot clean --limit 100 --confidence-threshold 0.9   # Normal
```

### For Different Email Types
```bash
# Clean promotional emails (usually safe)
uv run mailbot clean --folder CATEGORY_PROMOTIONS --limit 50

# Clean spam (very safe)
uv run mailbot clean --folder SPAM --limit 20 --auto-delete

# Be careful with inbox (mixed content)
uv run mailbot clean --folder INBOX --limit 10 --confidence-threshold 0.95
```

### Testing Different LLM Providers
```bash
uv run mailbot analyze --provider groq --limit 10     # Fast
uv run mailbot analyze --provider gemini --limit 10   # High quality
```