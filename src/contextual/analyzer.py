"""
Contextual Intelligence Analyzer
Analyzes messages using multi-dimensional context, NOT just keywords or blacklists.
This is the "NOMADA Edge" - semantic understanding of scam patterns.
"""

import re
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ContextSignals:
    behavioral: Dict
    social: Dict
    temporal: Dict
    linguistic: Dict


class ContextualAnalyzer:
    """
    Analyzes messages using contextual intelligence.
    Detects scams based on behavior patterns, not just blacklists.
    """
    
    def __init__(self):
        self.urgency_keywords = [
            'urgent', 'immediately', 'now', 'today', 'asap', 'hurry',
            'limited time', 'expires', 'act now', 'don\'t miss',
            'last chance', 'ending soon', 'quick', 'fast'
        ]
        
        self.money_keywords = [
            'money', 'cash', 'payment', 'bank', 'account', 'wire',
            'transfer', 'deposit', 'credit card', 'ssn', 'social security',
            'bitcoin', 'crypto', 'investment', 'profit', 'earn', 'income',
            'salary', 'pay', 'fee', 'charge', 'refund', 'prize', 'lottery',
            'million', 'thousand', 'dollars', '$', '€', '£'
        ]
        
        self.credential_keywords = [
            'password', 'login', 'verify', 'confirm', 'account',
            'username', 'credentials', 'security', 'suspended',
            'locked', 'verify identity', 'click here', 'sign in'
        ]
        
        self.dangerous_file_extensions = [
            'exe', 'bat', 'cmd', 'com', 'scr', 'vbs', 'js',
            'jar', 'msi', 'app', 'dmg', 'pkg'
        ]
        
        self.safe_file_extensions = [
            'pdf', 'doc', 'docx', 'txt', 'jpg', 'png', 'gif'
        ]
    
    def analyze(self, message: str, metadata: Dict) -> Dict:
        """
        Main analysis method - returns comprehensive risk assessment.
        """
        context = self._extract_context(message, metadata)
        risk_score = self._calculate_contextual_risk(context)
        risk_level = self._get_risk_level(risk_score)
        explanation = self._generate_explanation(context, risk_score)
        
        return {
            'risk_score': risk_score,
            'risk_level': risk_level,
            'context_signals': {
                'behavioral': context.behavioral,
                'social': context.social,
                'temporal': context.temporal,
                'linguistic': context.linguistic
            },
            'explanation': explanation,
            'recommended_action': self._get_action(risk_score),
            'patterns_matched': self._get_matched_patterns(context)
        }
    
    def _extract_context(self, message: str, metadata: Dict) -> ContextSignals:
        """Extract all contextual signals from message and metadata."""
        return ContextSignals(
            behavioral=self._analyze_behavior(message, metadata),
            social=self._analyze_social_signals(metadata),
            temporal=self._analyze_timing(metadata),
            linguistic=self._analyze_language(message)
        )
    
    def _analyze_behavior(self, message: str, metadata: Dict) -> Dict:
        """Analyze behavioral patterns in the message."""
        message_lower = message.lower()
        
        action_requested = self._detect_action(message_lower)
        file_type = metadata.get('file_type')
        
        return {
            'platform': metadata.get('platform', 'unknown'),
            'action_requested': action_requested,
            'file_type': file_type,
            'file_risk': self._get_file_risk(file_type),
            'link_count': len(re.findall(r'https?://', message)),
            'suspicious_links': self._detect_suspicious_links(message),
            'urgency_level': self._calculate_urgency(message_lower),
            'requests_credentials': self._requests_credentials(message_lower),
            'requests_money': self._requests_money(message_lower)
        }
    
    def _analyze_social_signals(self, metadata: Dict) -> Dict:
        """Analyze social context signals."""
        account_age = metadata.get('sender_account_age_days', 0)
        connection_degree = metadata.get('connection_degree', 3)
        
        return {
            'account_age_days': account_age,
            'account_age_risk': self._get_account_age_risk(account_age),
            'connection_degree': connection_degree,
            'connection_risk': self._get_connection_risk(connection_degree),
            'claimed_role': metadata.get('claimed_role', 'unknown'),
            'previous_interactions': metadata.get('previous_interactions', 0),
            'trust_score': self._calculate_trust_score(metadata)
        }
    
    def _analyze_timing(self, metadata: Dict) -> Dict:
        """Analyze temporal patterns."""
        return {
            'first_contact': metadata.get('previous_interactions', 0) == 0,
            'rapid_response_expected': metadata.get('urgency_detected', False)
        }
    
    def _analyze_language(self, message: str) -> Dict:
        """Analyze linguistic patterns."""
        message_lower = message.lower()
        
        return {
            'message_length': len(message),
            'urgency_keywords_count': self._count_keywords(message_lower, self.urgency_keywords),
            'money_keywords_count': self._count_keywords(message_lower, self.money_keywords),
            'credential_keywords_count': self._count_keywords(message_lower, self.credential_keywords),
            'excessive_punctuation': self._has_excessive_punctuation(message),
            'all_caps_ratio': self._calculate_caps_ratio(message),
            'grammar_quality': self._assess_grammar(message)
        }
    
    def _calculate_contextual_risk(self, context: ContextSignals) -> int:
        """
        Calculate risk score based on contextual signals.
        This is where the magic happens - contextual intelligence.
        """
        risk = 0
        
        # Behavioral risk factors
        behavioral = context.behavioral
        if behavioral['file_risk'] > 0.8:
            risk += 30
        elif behavioral['file_risk'] > 0.5:
            risk += 15
        
        if behavioral['action_requested'] in ['download', 'transfer_money', 'provide_credentials']:
            risk += 25
        
        if behavioral['urgency_level'] > 0.7:
            risk += 20
        elif behavioral['urgency_level'] > 0.4:
            risk += 10
        
        if behavioral['requests_credentials']:
            risk += 25
        
        if behavioral['requests_money']:
            risk += 20
        
        if behavioral['suspicious_links']:
            risk += 15
        
        # Social risk factors
        social = context.social
        if social['account_age_risk'] > 0.8:
            risk += 20
        elif social['account_age_risk'] > 0.5:
            risk += 10
        
        if social['connection_risk'] > 0.7:
            risk += 15
        
        if social['previous_interactions'] == 0:
            risk += 10
        
        if social['trust_score'] < 0.3:
            risk += 15
        
        # Linguistic risk factors
        linguistic = context.linguistic
        if linguistic['urgency_keywords_count'] > 3:
            risk += 15
        elif linguistic['urgency_keywords_count'] > 1:
            risk += 8
        
        if linguistic['money_keywords_count'] > 2:
            risk += 12
        
        if linguistic['credential_keywords_count'] > 2:
            risk += 15
        
        if linguistic['excessive_punctuation']:
            risk += 10
        
        if linguistic['all_caps_ratio'] > 0.3:
            risk += 10
        
        # Contextual combinations (this is the intelligence part)
        if (behavioral['action_requested'] == 'download' and 
            behavioral['file_risk'] > 0.8 and 
            social['account_age_days'] < 7):
            risk += 20  # New account + dangerous file = high risk
        
        if (behavioral['requests_credentials'] and 
            behavioral['urgency_level'] > 0.6 and 
            social['previous_interactions'] == 0):
            risk += 25  # Urgent credential request from stranger = phishing
        
        if (behavioral['requests_money'] and 
            social['connection_degree'] > 2 and 
            context.temporal['first_contact']):
            risk += 20  # Money request from distant connection on first contact
        
        return min(risk, 100)
    
    def _get_risk_level(self, score: int) -> str:
        """Convert score to risk level."""
        if score < 30:
            return 'safe'
        elif score < 70:
            return 'caution'
        else:
            return 'critical'
    
    def _generate_explanation(self, context: ContextSignals, risk_score: int) -> str:
        """Generate human-readable explanation."""
        reasons = []
        
        behavioral = context.behavioral
        social = context.social
        linguistic = context.linguistic
        
        if behavioral['file_risk'] > 0.8:
            reasons.append(f"Dangerous file type detected ({behavioral['file_type']})")
        
        if behavioral['urgency_level'] > 0.7:
            reasons.append("High urgency language detected")
        
        if social['account_age_days'] < 7:
            reasons.append(f"Very new account ({social['account_age_days']} days old)")
        elif social['account_age_days'] < 30:
            reasons.append(f"New account ({social['account_age_days']} days old)")
        
        if social['connection_degree'] > 2:
            reasons.append("No direct connection to sender")
        
        if behavioral['requests_credentials']:
            reasons.append("Requests login credentials or personal information")
        
        if behavioral['requests_money']:
            reasons.append("Requests money transfer or payment")
        
        if social['previous_interactions'] == 0:
            reasons.append("First time contact from this sender")
        
        if linguistic['excessive_punctuation']:
            reasons.append("Excessive punctuation (spam indicator)")
        
        if behavioral['suspicious_links']:
            reasons.append("Contains suspicious or shortened links")
        
        if not reasons:
            return "No significant risk factors detected."
        
        return " • ".join(reasons)
    
    def _get_action(self, risk_score: int) -> str:
        """Get recommended action based on risk score."""
        if risk_score >= 70:
            return "DO NOT ENGAGE - Report as scam"
        elif risk_score >= 30:
            return "PROCEED WITH CAUTION - Verify sender identity"
        else:
            return "Safe to proceed"
    
    def _get_matched_patterns(self, context: ContextSignals) -> List[str]:
        """Get list of matched scam patterns."""
        patterns = []
        
        behavioral = context.behavioral
        social = context.social
        
        if behavioral['file_type'] in self.dangerous_file_extensions:
            patterns.append('malware_delivery')
        
        if behavioral['requests_credentials']:
            patterns.append('credential_phishing')
        
        if behavioral['requests_money'] and social['account_age_days'] < 30:
            patterns.append('advance_fee_fraud')
        
        if behavioral['urgency_level'] > 0.7 and behavioral['requests_credentials']:
            patterns.append('urgent_phishing')
        
        if 'lottery' in behavioral.get('action_requested', '').lower():
            patterns.append('lottery_scam')
        
        return patterns
    
    # Helper methods
    
    def _detect_action(self, message: str) -> str:
        """Detect what action is being requested."""
        if any(word in message for word in ['download', 'install', 'run', 'execute']):
            return 'download'
        if any(word in message for word in ['send money', 'wire', 'transfer', 'pay', 'deposit']):
            return 'transfer_money'
        if any(word in message for word in ['password', 'login', 'verify', 'confirm identity']):
            return 'provide_credentials'
        if any(word in message for word in ['click', 'visit', 'go to']):
            return 'click_link'
        return 'none'
    
    def _get_file_risk(self, file_type: Optional[str]) -> float:
        """Calculate risk level of file type."""
        if not file_type:
            return 0.0
        
        file_type_lower = file_type.lower()
        
        if file_type_lower in self.dangerous_file_extensions:
            return 1.0
        elif file_type_lower in self.safe_file_extensions:
            return 0.1
        else:
            return 0.5
    
    def _detect_suspicious_links(self, message: str) -> bool:
        """Detect suspicious URL patterns."""
        urls = re.findall(r'https?://[^\s]+', message)
        
        for url in urls:
            url_lower = url.lower()
            if any(indicator in url_lower for indicator in [
                'bit.ly', 'tinyurl', 'goo.gl',  # URL shorteners
                'verify', 'secure', 'account', 'login',  # Phishing indicators
                '.tk', '.ml', '.ga', '.cf',  # Suspicious TLDs
                'click', 'urgent', 'suspended'
            ]):
                return True
        
        return False
    
    def _calculate_urgency(self, message: str) -> float:
        """Calculate urgency level (0-1)."""
        urgency_count = self._count_keywords(message, self.urgency_keywords)
        return min(urgency_count / 5.0, 1.0)
    
    def _requests_credentials(self, message: str) -> bool:
        """Check if message requests credentials."""
        return self._count_keywords(message, self.credential_keywords) >= 2
    
    def _requests_money(self, message: str) -> bool:
        """Check if message requests money."""
        money_count = self._count_keywords(message, self.money_keywords)
        transfer_words = any(word in message for word in ['send', 'transfer', 'wire', 'pay', 'deposit'])
        return money_count >= 2 and transfer_words
    
    def _get_account_age_risk(self, age_days: int) -> float:
        """Calculate risk based on account age."""
        if age_days < 7:
            return 1.0
        elif age_days < 30:
            return 0.7
        elif age_days < 90:
            return 0.4
        else:
            return 0.1
    
    def _get_connection_risk(self, degree: int) -> float:
        """Calculate risk based on connection degree."""
        if degree >= 3:
            return 0.8
        elif degree == 2:
            return 0.4
        else:
            return 0.1
    
    def _calculate_trust_score(self, metadata: Dict) -> float:
        """Calculate overall trust score."""
        score = 0.5
        
        account_age = metadata.get('sender_account_age_days', 0)
        if account_age > 365:
            score += 0.3
        elif account_age > 90:
            score += 0.1
        
        interactions = metadata.get('previous_interactions', 0)
        if interactions > 10:
            score += 0.2
        elif interactions > 0:
            score += 0.1
        
        connection = metadata.get('connection_degree', 3)
        if connection == 1:
            score += 0.2
        
        return min(score, 1.0)
    
    def _count_keywords(self, text: str, keywords: List[str]) -> int:
        """Count occurrences of keywords in text."""
        count = 0
        for keyword in keywords:
            if keyword in text:
                count += 1
        return count
    
    def _has_excessive_punctuation(self, message: str) -> bool:
        """Check for excessive punctuation (spam indicator)."""
        punctuation_count = len(re.findall(r'[!?]{2,}', message))
        return punctuation_count > 2
    
    def _calculate_caps_ratio(self, message: str) -> float:
        """Calculate ratio of uppercase letters."""
        if not message:
            return 0.0
        
        letters = [c for c in message if c.isalpha()]
        if not letters:
            return 0.0
        
        caps = [c for c in letters if c.isupper()]
        return len(caps) / len(letters)
    
    def _assess_grammar(self, message: str) -> str:
        """Basic grammar quality assessment."""
        if len(message) < 10:
            return 'unknown'
        
        sentences = message.split('.')
        if len(sentences) > 1:
            capitalized = sum(1 for s in sentences if s.strip() and s.strip()[0].isupper())
            if capitalized / len(sentences) > 0.8:
                return 'good'
        
        return 'poor'
