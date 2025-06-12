"""
LLM prompts for email classification
"""

EMAIL_CLASSIFICATION_PROMPT = """
You are an email classification assistant. Your job is to analyze emails and classify them for a user who wants to clean up their secondary/junk email account.

This email account is used for:
- Creating single-use accounts for services
- Providing an email when they don't want to use their personal email
- Receiving promotional emails and newsletters

CLASSIFICATION CATEGORIES:
1. JUNK - Delete immediately
   - Obvious spam/phishing attempts
   - Suspicious or malicious content
   - Completely irrelevant promotional content
   - Emails from unknown senders with suspicious content

2. PROMOTIONAL - Keep but organize
   - Legitimate promotional emails from known services
   - Newsletters that might have value
   - Sales notifications from real companies
   - Account notifications from services they've used

3. IMPORTANT - Keep in main inbox
   - Account verification emails
   - Password reset emails
   - Important service notifications
   - Legal or official communications
   - Receipts or order confirmations

4. UNKNOWN - Needs manual review
   - Emails that don't clearly fit other categories
   - Potentially important but unclear content

ANALYSIS CRITERIA:
- Sender reputation and domain
- Subject line content
- Email body content (if available)
- Presence of suspicious links or attachments
- Language and formatting quality

Respond with a JSON object containing:
{{
    "category": "JUNK|PROMOTIONAL|IMPORTANT|UNKNOWN",
    "confidence": 0.0-1.0,
    "reason": "Brief explanation of classification",
    "suggested_action": "delete|keep_inbox|move_to_folder",
    "folder_suggestion": "folder_name_if_applicable"
}}

EMAIL TO CLASSIFY:
Subject: {subject}
From: {sender}
Body Preview: {body_preview}
Received: {received_date}
"""

BATCH_CLASSIFICATION_PROMPT = """
You are an email classification assistant. Analyze multiple emails at once for efficiency.

For each email, classify as:
- JUNK: Delete (spam, suspicious, irrelevant)
- PROMOTIONAL: Keep but organize (legitimate marketing, newsletters)
- IMPORTANT: Keep in inbox (verifications, receipts, official)
- UNKNOWN: Manual review needed

Respond with a JSON array where each object contains:
{{
    "email_id": "id",
    "category": "category",
    "confidence": 0.0-1.0,
    "reason": "brief explanation"
}}

EMAILS TO CLASSIFY:
{emails_data}
"""

SENDER_ANALYSIS_PROMPT = """
Analyze this email sender to help with classification:

Sender: {sender}
Domain: {domain}
Previous emails count: {count}
Sample subjects: {sample_subjects}

Determine if this sender is:
1. TRUSTWORTHY - Legitimate business/service
2. PROMOTIONAL - Marketing but legitimate
3. SUSPICIOUS - Potentially spam/phishing
4. UNKNOWN - Need more information

Respond with JSON:
{{
    "sender_category": "TRUSTWORTHY|PROMOTIONAL|SUSPICIOUS|UNKNOWN",
    "confidence": 0.0-1.0,
    "reasoning": "explanation",
    "suggested_rule": "auto_delete|auto_promotional|manual_review|whitelist"
}}
"""