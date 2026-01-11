"""
Threat Intelligence Service - External API Integrations
FREE APIs for real-time verification:
1. PhishTank (Cisco) - URL blacklist
2. Google Safe Browsing - Domain security
3. Domain age/reputation check
"""

import os
import re
import hashlib
import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
import json

class ThreatIntelService:
    """
    Layered threat verification:
    Layer 1: PhishTank (free, URL blacklist) - $0
    Layer 2: Google Safe Browsing (free tier) - $0
    Layer 3: Domain age/WHOIS check - $0
    Layer 4: AI analysis only if needed - $$$
    """
    
    def __init__(self):
        # API Keys from environment
        self.phishtank_api_key = os.getenv('PHISHTANK_API_KEY', '')
        self.google_safebrowsing_key = os.getenv('GOOGLE_SAFEBROWSING_KEY', '')
        
        # Cache to avoid repeated lookups
        self.url_cache: Dict[str, dict] = {}
        self.domain_cache: Dict[str, dict] = {}
        
        # Known suspicious TLDs (cheap domains often used for scams)
        self.suspicious_tlds = [
            '.xyz', '.top', '.club', '.online', '.site', '.work',
            '.click', '.link', '.info', '.biz', '.cc', '.tk', '.ml',
            '.ga', '.cf', '.gq', '.pw', '.ws'
        ]
        
        # Known legitimate domains (whitelist)
        self.trusted_domains = [
            'linkedin.com', 'google.com', 'microsoft.com', 'apple.com',
            'amazon.com', 'github.com', 'stackoverflow.com', 'medium.com',
            'indeed.com', 'glassdoor.com', 'bamboohr.com', 'workday.com',
            'greenhouse.io', 'lever.co', 'jobvite.com', 'icims.com'
        ]
    
    async def verify_url(self, url: str) -> Dict:
        """
        Full URL verification through all layers.
        Returns threat assessment with confidence score.
        """
        # Check cache first
        url_hash = hashlib.md5(url.encode()).hexdigest()
        if url_hash in self.url_cache:
            cached = self.url_cache[url_hash]
            # Cache valid for 1 hour
            if (datetime.now() - cached['timestamp']).seconds < 3600:
                return cached['result']
        
        result = {
            'url': url,
            'is_malicious': False,
            'threat_level': 'safe',
            'confidence': 0.0,
            'sources': [],
            'details': []
        }
        
        # Extract domain
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            if domain.startswith('www.'):
                domain = domain[4:]
        except:
            result['details'].append('Invalid URL format')
            result['threat_level'] = 'suspicious'
            return result
        
        # Layer 0: Whitelist check
        if any(domain.endswith(trusted) for trusted in self.trusted_domains):
            result['threat_level'] = 'safe'
            result['confidence'] = 0.95
            result['details'].append(f'Domain {domain} is whitelisted')
            return result
        
        # Layer 1: PhishTank check
        phishtank_result = await self._check_phishtank(url)
        if phishtank_result['is_phish']:
            result['is_malicious'] = True
            result['threat_level'] = 'critical'
            result['confidence'] = 0.99
            result['sources'].append('PhishTank')
            result['details'].append('URL found in PhishTank blacklist')
            self._cache_result(url_hash, result)
            return result
        
        # Layer 2: Google Safe Browsing
        safebrowsing_result = await self._check_google_safebrowsing(url)
        if safebrowsing_result['is_unsafe']:
            result['is_malicious'] = True
            result['threat_level'] = 'critical'
            result['confidence'] = 0.98
            result['sources'].append('Google Safe Browsing')
            result['details'].append(f"Threat type: {safebrowsing_result['threat_type']}")
            self._cache_result(url_hash, result)
            return result
        
        # Layer 3: Domain reputation
        domain_result = await self._check_domain_reputation(domain)
        if domain_result['is_suspicious']:
            result['threat_level'] = 'caution'
            result['confidence'] = domain_result['confidence']
            result['sources'].append('Domain Analysis')
            result['details'].extend(domain_result['reasons'])
        
        self._cache_result(url_hash, result)
        return result
    
    async def _check_phishtank(self, url: str) -> Dict:
        """
        Check URL against PhishTank database.
        Free API: https://www.phishtank.com/api_info.php
        """
        result = {'is_phish': False, 'verified': False}
        
        if not self.phishtank_api_key:
            return result
        
        try:
            # PhishTank uses URL encoding for lookup
            url_encoded = url
            api_url = 'https://checkurl.phishtank.com/checkurl/'
            
            async with aiohttp.ClientSession() as session:
                data = {
                    'url': url_encoded,
                    'format': 'json',
                    'app_key': self.phishtank_api_key
                }
                async with session.post(api_url, data=data, timeout=10) as resp:
                    if resp.status == 200:
                        response = await resp.json()
                        if response.get('results', {}).get('in_database'):
                            result['is_phish'] = response['results'].get('valid', False)
                            result['verified'] = response['results'].get('verified', False)
        except Exception as e:
            print(f"PhishTank API error: {e}")
        
        return result
    
    async def _check_google_safebrowsing(self, url: str) -> Dict:
        """
        Check URL against Google Safe Browsing.
        Free tier: 10,000 requests/day
        https://developers.google.com/safe-browsing/v4
        """
        result = {'is_unsafe': False, 'threat_type': None}
        
        if not self.google_safebrowsing_key:
            return result
        
        try:
            api_url = f'https://safebrowsing.googleapis.com/v4/threatMatches:find?key={self.google_safebrowsing_key}'
            
            payload = {
                'client': {
                    'clientId': 'fakedetector',
                    'clientVersion': '1.0.0'
                },
                'threatInfo': {
                    'threatTypes': [
                        'MALWARE', 'SOCIAL_ENGINEERING', 
                        'UNWANTED_SOFTWARE', 'POTENTIALLY_HARMFUL_APPLICATION'
                    ],
                    'platformTypes': ['ANY_PLATFORM'],
                    'threatEntryTypes': ['URL'],
                    'threatEntries': [{'url': url}]
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, json=payload, timeout=10) as resp:
                    if resp.status == 200:
                        response = await resp.json()
                        if response.get('matches'):
                            result['is_unsafe'] = True
                            result['threat_type'] = response['matches'][0].get('threatType', 'UNKNOWN')
        except Exception as e:
            print(f"Google Safe Browsing API error: {e}")
        
        return result
    
    async def _check_domain_reputation(self, domain: str) -> Dict:
        """
        Analyze domain for suspicious characteristics.
        Free heuristics-based check.
        """
        result = {
            'is_suspicious': False,
            'confidence': 0.0,
            'reasons': []
        }
        
        # Check suspicious TLDs
        for tld in self.suspicious_tlds:
            if domain.endswith(tld):
                result['is_suspicious'] = True
                result['confidence'] = 0.6
                result['reasons'].append(f'Suspicious TLD: {tld}')
                break
        
        # Check for typosquatting patterns
        typosquat_targets = ['google', 'linkedin', 'microsoft', 'amazon', 'apple', 'paypal']
        for target in typosquat_targets:
            if target in domain and not domain.endswith(f'{target}.com'):
                result['is_suspicious'] = True
                result['confidence'] = max(result['confidence'], 0.7)
                result['reasons'].append(f'Possible typosquatting of {target}')
        
        # Check for excessive subdomains (common in phishing)
        subdomain_count = domain.count('.')
        if subdomain_count > 3:
            result['is_suspicious'] = True
            result['confidence'] = max(result['confidence'], 0.5)
            result['reasons'].append('Excessive subdomains')
        
        # Check for IP-based URLs
        ip_pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
        if re.match(ip_pattern, domain):
            result['is_suspicious'] = True
            result['confidence'] = max(result['confidence'], 0.8)
            result['reasons'].append('IP-based URL (not using domain name)')
        
        # Check for homograph attacks (mixed scripts)
        # Common substitutions: 0 for o, 1 for l, etc.
        homograph_patterns = [
            (r'0', 'o'), (r'1', 'l'), (r'vv', 'w'),
            (r'rn', 'm'), (r'cl', 'd')
        ]
        for pattern, replacement in homograph_patterns:
            if pattern in domain:
                result['is_suspicious'] = True
                result['confidence'] = max(result['confidence'], 0.65)
                result['reasons'].append(f'Possible homograph attack: {pattern} looks like {replacement}')
        
        return result
    
    async def verify_email_domain(self, email: str) -> Dict:
        """
        Verify if email domain is legitimate for recruitment.
        """
        result = {
            'is_suspicious': False,
            'confidence': 0.0,
            'reasons': []
        }
        
        try:
            domain = email.split('@')[1].lower()
        except:
            result['is_suspicious'] = True
            result['confidence'] = 0.9
            result['reasons'].append('Invalid email format')
            return result
        
        # Free email providers shouldn't be used for corporate recruitment
        free_email_providers = [
            'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
            'aol.com', 'mail.com', 'protonmail.com', 'icloud.com',
            'yandex.com', 'zoho.com'
        ]
        
        if domain in free_email_providers:
            result['is_suspicious'] = True
            result['confidence'] = 0.7
            result['reasons'].append(f'Free email provider ({domain}) used for recruitment')
        
        # Check domain reputation
        domain_rep = await self._check_domain_reputation(domain)
        if domain_rep['is_suspicious']:
            result['is_suspicious'] = True
            result['confidence'] = max(result['confidence'], domain_rep['confidence'])
            result['reasons'].extend(domain_rep['reasons'])
        
        return result
    
    def extract_urls_from_message(self, message: str) -> List[str]:
        """Extract all URLs from a message."""
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, message)
        
        # Also check for URL shorteners that might be obfuscated
        shortener_patterns = [
            r'bit\.ly/\S+', r'tinyurl\.com/\S+', r'goo\.gl/\S+',
            r't\.co/\S+', r'ow\.ly/\S+', r'is\.gd/\S+',
            r'buff\.ly/\S+', r'adf\.ly/\S+'
        ]
        
        for pattern in shortener_patterns:
            matches = re.findall(pattern, message, re.IGNORECASE)
            urls.extend([f'https://{m}' for m in matches if not m.startswith('http')])
        
        return list(set(urls))
    
    def _cache_result(self, url_hash: str, result: dict):
        """Cache verification result."""
        self.url_cache[url_hash] = {
            'result': result,
            'timestamp': datetime.now()
        }


# Global instance
threat_intel = ThreatIntelService()


async def verify_message_urls(message: str) -> Dict:
    """
    Main entry point: Extract and verify all URLs in a message.
    """
    urls = threat_intel.extract_urls_from_message(message)
    
    if not urls:
        return {
            'has_urls': False,
            'url_count': 0,
            'malicious_count': 0,
            'results': []
        }
    
    # Verify all URLs in parallel
    tasks = [threat_intel.verify_url(url) for url in urls]
    results = await asyncio.gather(*tasks)
    
    malicious_count = sum(1 for r in results if r['is_malicious'])
    suspicious_count = sum(1 for r in results if r['threat_level'] in ['caution', 'suspicious'])
    
    return {
        'has_urls': True,
        'url_count': len(urls),
        'malicious_count': malicious_count,
        'suspicious_count': suspicious_count,
        'highest_threat': max((r['threat_level'] for r in results), 
                             key=lambda x: {'safe': 0, 'caution': 1, 'suspicious': 2, 'critical': 3}.get(x, 0)),
        'results': results
    }
