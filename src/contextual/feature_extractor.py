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
            'has_urgency': int(self._count_keywords(message_lower, self.urgency_keywords) > 0)
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
