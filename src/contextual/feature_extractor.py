"""
Privacy-First Feature Extractor
Extracts ONLY anonymized numerical features from messages.
NO message content, NO PII ever leaves the browser/server.
"""

import re
from typing import Dict, Optional


class PrivacyFirstFeatureExtractor:
    """
    Extracts ONLY anonymized numerical features.
    Privacy guarantee: Features cannot be used to reconstruct original message.
    """
    
    def __init__(self):
        self.urgency_keywords = [
            'urgent', 'immediately', 'now', 'today', 'asap', 'hurry',
            'limited time', 'expires', 'act now', 'don\'t miss'
        ]
        
        self.money_keywords = [
            'money', 'cash', 'payment', 'bank', 'account', 'wire',
            'transfer', 'deposit', 'bitcoin', 'crypto', 'investment',
            'profit', 'earn', 'income', 'fee', 'prize', 'lottery'
        ]
        
        self.credential_keywords = [
            'password', 'login', 'verify', 'confirm', 'account',
            'username', 'credentials', 'security', 'suspended'
        ]
        
        # Rachel Good scam pattern keywords
        self.recruiter_keywords = [
            'recruiter', 'recruitment', 'hiring', 'hr', 'talent acquisition',
            'principal', 'talent partner', 'hiring manager'
        ]
        
        self.location_inquiry_keywords = [
            'where are you located', 'what is your location', 'current location',
            'where do you live', 'city', 'state you reside'
        ]
        
        self.experience_inquiry_keywords = [
            'years of experience', 'how long have you', 'experience in',
            'background in', 'worked with'
        ]
        
        # CV SCAM indicators (offers to improve CV for fee)
        self.cv_scam_keywords = [
            'improve your cv', 'improve your resume', 'review your cv', 'review your resume',
            'optimize your cv', 'optimize your resume', 'enhance your profile',
            'help with your cv', 'rewrite your resume', 'cv services', 'resume services',
            'career coaching fee', 'cv writing fee'
        ]
        
        # LEGITIMATE job offer indicators
        self.legitimate_job_keywords = [
            'job description', 'job opening', 'position available', 'we are hiring',
            'job requirements', 'qualifications', 'responsibilities', 'years experience',
            'send your cv', 'send your resume', 'submit your cv', 'apply for',
            'job posting', 'vacancy', 'employment opportunity'
        ]
        
        # Technical skills (indicates real job, not scam)
        self.technical_skills_keywords = [
            'java', 'python', 'javascript', 'react', 'angular', 'node', 'sql',
            'aws', 'azure', 'docker', 'kubernetes', 'agile', 'scrum',
            'developer', 'engineer', 'architect', 'analyst', 'manager',
            'adobe', 'sap', 'hybris', 'aem', 'salesforce', 'oracle'
        ]
        
        # Financial phishing keywords (Destiny Mastercard, etc.)
        self.financial_phishing_keywords = [
            'destiny', 'mastercard', 'credit card', 'credit limit',
            'credit invitation', 'security deposit', 'pre-approved',
            'congratulations you qualify', 'claim your card'
        ]
    
    def extract_features(self, message: str, metadata: Dict) -> Dict:
        """
        Extract anonymized features from message.
        Returns ONLY numerical/categorical features - NEVER raw text or PII.
        """
        message_lower = message.lower()
        
        return {
            # Message structure features
            'message_length': len(message),
            'word_count': len(message.split()),
            'sentence_count': len(re.split(r'[.!?]+', message)),
            'avg_word_length': self._calculate_avg_word_length(message),
            
            # Keyword density features
            'urgency_keywords_count': self._count_keywords(message_lower, self.urgency_keywords),
            'money_keywords_count': self._count_keywords(message_lower, self.money_keywords),
            'credential_keywords_count': self._count_keywords(message_lower, self.credential_keywords),
            
            # Link and attachment features
            'link_count': len(re.findall(r'https?://', message)),
            'has_shortened_url': int(self._has_shortened_url(message)),
            'file_attachment': int(bool(metadata.get('has_attachment'))),
            'file_extension_risk': self._get_extension_risk(metadata.get('file_type')),
            
            # Linguistic features
            'exclamation_count': message.count('!'),
            'question_count': message.count('?'),
            'caps_ratio': self._calculate_caps_ratio(message),
            'number_count': len(re.findall(r'\d+', message)),
            'currency_symbol_count': sum(message.count(c) for c in ['$', '€', '£']),
            
            # Social context features (anonymized)
            'sender_account_age_days': metadata.get('sender_account_age_days', 0),
            'connection_degree': metadata.get('connection_degree', 3),
            'previous_interactions': min(metadata.get('previous_interactions', 0), 100),
            
            # Platform and context (categorical IDs, not strings)
            'platform_id': self._platform_to_id(metadata.get('platform')),
            'context_type_id': self._context_to_id(metadata.get('claimed_role')),
            
            # Behavioral flags (binary)
            'requests_download': int(self._requests_download(message_lower)),
            'requests_payment': int(self._requests_payment(message_lower)),
            'requests_credentials': int(self._requests_credentials(message_lower)),
            'has_urgency': int(self._count_keywords(message_lower, self.urgency_keywords) > 0),
            
            # Rachel Good scam pattern features
            'recruiter_keywords_count': self._count_keywords(message_lower, self.recruiter_keywords),
            'location_inquiry': int(self._count_keywords(message_lower, self.location_inquiry_keywords) > 0),
            'experience_inquiry': int(self._count_keywords(message_lower, self.experience_inquiry_keywords) > 0),
            'gmail_recruiter_combo': int(self._detect_gmail_recruiter_combo(metadata)),
            'vague_address_pattern': int(self._detect_vague_address(message_lower)),
            
            # Financial phishing features (Destiny Mastercard, etc.)
            'financial_phishing_keywords_count': self._count_keywords(message_lower, self.financial_phishing_keywords),
            'credit_card_mention': int('credit card' in message_lower or 'mastercard' in message_lower),
            'credit_limit_mention': int('credit limit' in message_lower or 'credit line' in message_lower),
            'security_deposit_mention': int('security deposit' in message_lower or 'deposit required' in message_lower),
            
            # CV scam vs legitimate job detection
            'cv_scam_keywords_count': self._count_keywords(message_lower, self.cv_scam_keywords),
            'legitimate_job_keywords_count': self._count_keywords(message_lower, self.legitimate_job_keywords),
            'technical_skills_count': self._count_keywords(message_lower, self.technical_skills_keywords),
            'has_corporate_email': int(self._has_corporate_email(metadata)),
            'has_specific_job_title': int(self._has_job_title(message_lower))
        }
    
    def _calculate_avg_word_length(self, message: str) -> float:
        """Calculate average word length."""
        words = message.split()
        if not words:
            return 0.0
        return sum(len(word) for word in words) / len(words)
    
    def _count_keywords(self, text: str, keywords: list) -> int:
        """Count keyword occurrences."""
        count = 0
        for keyword in keywords:
            if keyword in text:
                count += 1
        return count
    
    def _has_shortened_url(self, message: str) -> bool:
        """Check for URL shorteners."""
        shorteners = ['bit.ly', 'tinyurl', 'goo.gl', 't.co', 'ow.ly']
        return any(shortener in message.lower() for shortener in shorteners)
    
    def _get_extension_risk(self, file_type: Optional[str]) -> float:
        """Get file extension risk score (0-1)."""
        if not file_type:
            return 0.0
        
        dangerous = ['exe', 'bat', 'cmd', 'scr', 'vbs', 'js', 'jar', 'msi']
        safe = ['pdf', 'doc', 'docx', 'txt', 'jpg', 'png']
        
        file_type_lower = file_type.lower()
        
        if file_type_lower in dangerous:
            return 1.0
        elif file_type_lower in safe:
            return 0.1
        else:
            return 0.5
    
    def _calculate_caps_ratio(self, message: str) -> float:
        """Calculate uppercase letter ratio."""
        if not message:
            return 0.0
        
        letters = [c for c in message if c.isalpha()]
        if not letters:
            return 0.0
        
        caps = [c for c in letters if c.isupper()]
        return len(caps) / len(letters)
    
    def _platform_to_id(self, platform: Optional[str]) -> int:
        """Convert platform to numerical ID."""
        platform_map = {
            'linkedin': 1,
            'gmail': 2,
            'outlook': 3,
            'unknown': 0
        }
        return platform_map.get(platform, 0)
    
    def _context_to_id(self, context: Optional[str]) -> int:
        """Convert context type to numerical ID."""
        context_map = {
            'recruiter': 1,
            'investor': 2,
            'friend': 3,
            'coworker': 4,
            'support': 5,
            'delivery_service': 6,
            'professional': 7,
            'unknown': 0
        }
        return context_map.get(context, 0)
    
    def _requests_download(self, message: str) -> bool:
        """Check if message requests download."""
        download_words = ['download', 'install', 'run', 'execute', 'open file']
        return any(word in message for word in download_words)
    
    def _requests_payment(self, message: str) -> bool:
        """Check if message requests payment."""
        payment_words = ['send money', 'wire', 'transfer', 'pay', 'deposit', 'bank details']
        return any(word in message for word in payment_words)
    
    def _requests_credentials(self, message: str) -> bool:
        """Check if message requests credentials."""
        cred_count = self._count_keywords(message, self.credential_keywords)
        return cred_count >= 2
    
    def _detect_gmail_recruiter_combo(self, metadata: Dict) -> bool:
        """Detect Rachel Good pattern: Gmail + Recruiter title combo."""
        # Check if sender uses Gmail AND claims to be recruiter
        sender_email = metadata.get('sender_email', '').lower()
        claimed_role = metadata.get('claimed_role', '').lower()
        
        is_gmail = '@gmail.com' in sender_email
        is_recruiter = claimed_role in ['recruiter', 'recruitment', 'hiring', 'hr']
        
        return is_gmail and is_recruiter
    
    def _detect_vague_address(self, message: str) -> bool:
        """Detect vague address patterns like 'I reside in California'."""
        vague_patterns = [
            r'i reside in',
            r'i am located in',
            r'i live in',
            r'based in'
        ]
        return any(re.search(pattern, message) for pattern in vague_patterns)
    
    def _has_corporate_email(self, metadata: Dict) -> bool:
        """Check if sender uses corporate email (not gmail/yahoo/hotmail)."""
        sender_email = metadata.get('sender_email', '').lower()
        if not sender_email:
            return False
        
        free_email_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 
                              'aol.com', 'mail.com', 'protonmail.com', 'icloud.com']
        
        for domain in free_email_domains:
            if domain in sender_email:
                return False
        
        # Has @ symbol and not a free email = corporate
        return '@' in sender_email
    
    def _has_job_title(self, message: str) -> bool:
        """Check if message mentions specific job titles."""
        job_titles = [
            'developer', 'engineer', 'architect', 'analyst', 'manager',
            'director', 'specialist', 'consultant', 'administrator',
            'coordinator', 'lead', 'senior', 'junior', 'intern'
        ]
        return any(title in message for title in job_titles)
