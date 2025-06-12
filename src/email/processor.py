"""
Email processing utilities for data transformation and analysis
"""

from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter
from datetime import datetime, timedelta
import re
from urllib.parse import urlparse

class EmailProcessor:
    """Process and analyze email data"""
    
    def __init__(self):
        self.sender_stats = defaultdict(list)
        self.domain_stats = defaultdict(int)
        self.subject_patterns = Counter()
    
    def extract_sender_info(self, email: Dict[str, Any]) -> Dict[str, str]:
        """Extract detailed sender information from email"""
        sender_data = email.get('from', {})
        if isinstance(sender_data, dict):
            email_address = sender_data.get('emailAddress', {})
            return {
                'email': email_address.get('address', 'Unknown'),
                'name': email_address.get('name', 'Unknown'),
                'domain': self._extract_domain(email_address.get('address', ''))
            }
        return {'email': 'Unknown', 'name': 'Unknown', 'domain': 'Unknown'}
    
    def _extract_domain(self, email: str) -> str:
        """Extract domain from email address"""
        if '@' in email:
            return email.split('@')[1].lower()
        return 'Unknown'
    
    def analyze_sender_patterns(self, emails: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze patterns in email senders"""
        sender_analysis = defaultdict(lambda: {
            'count': 0,
            'subjects': [],
            'domains': set(),
            'first_seen': None,
            'last_seen': None
        })
        
        for email in emails:
            sender_info = self.extract_sender_info(email)
            sender_email = sender_info['email']
            
            # Update sender stats
            sender_analysis[sender_email]['count'] += 1
            sender_analysis[sender_email]['subjects'].append(
                email.get('subject', 'No Subject')[:100]
            )
            sender_analysis[sender_email]['domains'].add(sender_info['domain'])
            
            # Track dates
            received_date = email.get('receivedDateTime')
            if received_date:
                if isinstance(received_date, str):
                    received_date = datetime.fromisoformat(received_date.replace('Z', '+00:00'))
                
                if sender_analysis[sender_email]['first_seen'] is None:
                    sender_analysis[sender_email]['first_seen'] = received_date
                else:
                    sender_analysis[sender_email]['first_seen'] = min(
                        sender_analysis[sender_email]['first_seen'], received_date
                    )
                
                if sender_analysis[sender_email]['last_seen'] is None:
                    sender_analysis[sender_email]['last_seen'] = received_date
                else:
                    sender_analysis[sender_email]['last_seen'] = max(
                        sender_analysis[sender_email]['last_seen'], received_date
                    )
        
        # Convert sets to lists for JSON serialization
        for sender_data in sender_analysis.values():
            sender_data['domains'] = list(sender_data['domains'])
        
        return dict(sender_analysis)
    
    def detect_promotional_patterns(self, emails: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Detect common promotional email patterns"""
        patterns = {
            'sale_keywords': [],
            'unsubscribe_senders': [],
            'no_reply_senders': [],
            'marketing_domains': []
        }
        
        sale_keywords = [
            'sale', 'discount', 'offer', 'deal', 'promo', 'special',
            'limited time', 'save', '% off', 'free shipping', 'coupon'
        ]
        
        for email in emails:
            subject = email.get('subject', '').lower()
            sender_info = self.extract_sender_info(email)
            sender_email = sender_info['email'].lower()
            body_preview = email.get('bodyPreview', '').lower()
            
            # Check for sale keywords
            for keyword in sale_keywords:
                if keyword in subject or keyword in body_preview:
                    patterns['sale_keywords'].append(sender_email)
                    break
            
            # Check for unsubscribe mentions
            if 'unsubscribe' in body_preview:
                patterns['unsubscribe_senders'].append(sender_email)
            
            # Check for no-reply senders
            if 'noreply' in sender_email or 'no-reply' in sender_email:
                patterns['no_reply_senders'].append(sender_email)
            
            # Check for marketing domains
            domain = sender_info['domain']
            marketing_indicators = ['marketing', 'promo', 'newsletter', 'email']
            if any(indicator in domain for indicator in marketing_indicators):
                patterns['marketing_domains'].append(domain)
        
        # Remove duplicates
        for key in patterns:
            patterns[key] = list(set(patterns[key]))
        
        return patterns
    
    def analyze_email_frequency(self, emails: List[Dict[str, Any]]) -> Dict[str, Dict[str, int]]:
        """Analyze email frequency by sender and time period"""
        frequency_analysis = defaultdict(lambda: defaultdict(int))
        
        for email in emails:
            sender_info = self.extract_sender_info(email)
            sender_email = sender_info['email']
            
            received_date = email.get('receivedDateTime')
            if received_date:
                if isinstance(received_date, str):
                    received_date = datetime.fromisoformat(received_date.replace('Z', '+00:00'))
                
                # Group by time periods
                date_str = received_date.strftime('%Y-%m-%d')
                week_str = received_date.strftime('%Y-W%U')
                month_str = received_date.strftime('%Y-%m')
                
                frequency_analysis[sender_email]['daily'] += 1
                frequency_analysis[sender_email]['weekly'] += 1
                frequency_analysis[sender_email]['monthly'] += 1
        
        return dict(frequency_analysis)
    
    def extract_urls_and_domains(self, emails: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Extract URLs and domains from email bodies"""
        url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        
        all_urls = []
        all_domains = set()
        
        for email in emails:
            # Check body content
            body = email.get('body', {})
            if isinstance(body, dict):
                content = body.get('content', '')
            else:
                content = str(body)
            
            # Also check body preview
            content += ' ' + email.get('bodyPreview', '')
            
            # Find URLs
            urls = url_pattern.findall(content)
            all_urls.extend(urls)
            
            # Extract domains
            for url in urls:
                try:
                    domain = urlparse(url).netloc
                    if domain:
                        all_domains.add(domain.lower())
                except:
                    continue
        
        return {
            'urls': list(set(all_urls)),
            'domains': list(all_domains)
        }
    
    def categorize_by_content(self, emails: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Categorize emails by content type"""
        categories = {
            'newsletters': [],
            'notifications': [],
            'receipts': [],
            'social': [],
            'security': [],
            'promotional': []
        }
        
        category_keywords = {
            'newsletters': ['newsletter', 'weekly update', 'digest', 'roundup'],
            'notifications': ['notification', 'alert', 'reminder', 'update'],
            'receipts': ['receipt', 'invoice', 'payment', 'order', 'purchase'],
            'social': ['facebook', 'twitter', 'instagram', 'linkedin', 'social'],
            'security': ['security', 'password', 'login', 'verify', '2fa', 'verification'],
            'promotional': ['sale', 'discount', 'promo', 'deal', 'offer']
        }
        
        for email in emails:
            subject = email.get('subject', '').lower()
            body_preview = email.get('bodyPreview', '').lower()
            sender_info = self.extract_sender_info(email)
            content = f"{subject} {body_preview} {sender_info['email']}"
            
            email_id = email.get('id', 'unknown')
            categorized = False
            
            for category, keywords in category_keywords.items():
                if any(keyword in content for keyword in keywords):
                    categories[category].append(email_id)
                    categorized = True
                    break
            
            if not categorized:
                # Default to promotional if no other category matches
                categories['promotional'].append(email_id)
        
        return categories
    
    def get_bulk_delete_candidates(self, 
                                 emails: List[Dict[str, Any]], 
                                 days_old: int = 30,
                                 min_sender_count: int = 5) -> Dict[str, List[str]]:
        """Identify emails that are good candidates for bulk deletion"""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        # Group by sender
        sender_groups = defaultdict(list)
        for email in emails:
            received_date = email.get('receivedDateTime')
            if received_date:
                if isinstance(received_date, str):
                    received_date = datetime.fromisoformat(received_date.replace('Z', '+00:00'))
                
                if received_date < cutoff_date:
                    sender_info = self.extract_sender_info(email)
                    sender_groups[sender_info['email']].append(email.get('id'))
        
        # Filter senders with many emails
        bulk_candidates = {}
        for sender, email_ids in sender_groups.items():
            if len(email_ids) >= min_sender_count:
                bulk_candidates[sender] = email_ids
        
        return bulk_candidates
    
    def generate_processing_report(self, emails: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a comprehensive processing report"""
        if not emails:
            return {"error": "No emails to process"}
        
        return {
            "total_emails": len(emails),
            "sender_patterns": self.analyze_sender_patterns(emails),
            "promotional_patterns": self.detect_promotional_patterns(emails),
            "frequency_analysis": self.analyze_email_frequency(emails),
            "content_categories": self.categorize_by_content(emails),
            "url_analysis": self.extract_urls_and_domains(emails),
            "bulk_delete_candidates": self.get_bulk_delete_candidates(emails)
        }