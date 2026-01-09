"""
ParadigmStore Universal Fraud Detection SDK
"""

import requests
import asyncio
import aiohttp
from typing import Dict, Any, Optional

class FraudDetection:
    """Universal Fraud Detection SDK"""
    
    def __init__(self):
        self.api_key: Optional[str] = None
        self.base_url = "http://localhost:9001"  # Will be https://api.paradigmstore.com in production
    
    def initialize(self, api_key: str) -> None:
        """Initialize fraud detection with API key"""
        if not api_key:
            raise ValueError("API key is required")
        self.api_key = api_key
    
    def analyze(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze transaction for fraud risk (synchronous)"""
        if not self.api_key:
            raise RuntimeError("FraudDetection not initialized. Call initialize() first.")
        
        try:
            response = requests.post(
                f"{self.base_url}/api/sdk/analyze",
                json={
                    "transaction": transaction,
                    "api_key": self.api_key
                },
                headers={
                    "Content-Type": "application/json",
                    "X-API-Key": self.api_key
                },
                timeout=10
            )
            
            return response.json()
        except (requests.RequestException) as e:
            return {
                "success": False,
                "error": str(e),
                "risk_score": 0.5,
                "recommendation": "REVIEW"
            }
    
    async def analyze_async(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze transaction for fraud risk (asynchronous)"""
        if not self.api_key:
            raise RuntimeError("FraudDetection not initialized. Call initialize() first.")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/sdk/analyze",
                    json={
                        "transaction": transaction,
                        "api_key": self.api_key
                    },
                    headers={
                        "Content-Type": "application/json",
                        "X-API-Key": self.api_key
                    }
                ) as response:
                    return await response.json()
        except (ValueError, TypeError, AttributeError) as e:
            return {
                "success": False,
                "error": str(e),
                "risk_score": 0.5,
                "recommendation": "REVIEW"
            }

# Global instance
fraud_detection = FraudDetection()

# Convenience functions
def initialize(api_key: str) -> None:
    """Initialize fraud detection with API key"""
    fraud_detection.initialize(api_key)

def analyze(transaction: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze transaction for fraud risk"""
    return fraud_detection.analyze(transaction)

async def analyze_async(transaction: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze transaction for fraud risk (async)"""
    return await fraud_detection.analyze_async(transaction)
