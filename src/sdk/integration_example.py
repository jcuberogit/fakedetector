"""
Universal Fraud Detection SDK Integration Example
Demonstrates how to integrate the SDK with the main fraud detection agent
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any

from sdk import (
    FraudDetectionSdk, FraudDetectionSdkOptions, MobileChatRequest,
    MobileTransactionRequest, MobileCounterfactualRequest, LoginRequest,
    DeviceInfo, LocationInfo, TransactionContext, FraudFeedback,
    FraudHistoryRequest, UserPreferences
)


class FraudDetectionIntegrationExample:
    """Example integration of the Universal SDK with the fraud detection agent"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.logger = logging.getLogger(__name__)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    async def run_comprehensive_example(self):
        """Run a comprehensive example demonstrating all SDK features"""
        logger.info("🛡️ Universal Fraud Detection SDK Integration Example")
        logger.info("=" * 60)
        
        # Initialize SDK
        options = FraudDetectionSdkOptions(
            BaseUrl=self.base_url,
            Environment="development",
            Timeout=30.0
        )
        
        async with FraudDetectionSdk(options) as sdk:
            logger.info("✅ SDK initialized successfully")
            
            # 1. Authentication Flow
            await self._demonstrate_authentication(sdk)
            
            # 2. Chat-based Fraud Analysis
            await self._demonstrate_chat_analysis(sdk)
            
            # 3. Transaction Risk Assessment
            await self._demonstrate_transaction_risk(sdk)
            
            # 4. Counterfactual Analysis
            await self._demonstrate_counterfactual_analysis(sdk)
            
            # 5. HTTP Request Interception
            await self._demonstrate_http_interception(sdk)
            
            # 6. Fraud History and Analytics
            await self._demonstrate_fraud_history(sdk)
            
            # 7. User Preferences Management
            await self._demonstrate_user_preferences(sdk)
            
            # 8. Feedback Submission
            await self._demonstrate_feedback_submission(sdk)
            
            logger.info("\n🎉 All examples completed successfully!")
    
    async def _demonstrate_authentication(self, sdk: FraudDetectionSdk):
        """Demonstrate authentication flow"""
        logger.info("\n🔐 Authentication Flow")
        logger.info("-" * 30)
        
        # Login
        login_request = LoginRequest(
            Username="demo@paradigmstore.com",
            Password="DemoPassword123!",
            DeviceInfo=DeviceInfo(
                DeviceId="demo_device_001",
                DeviceType="Desktop",
                OsVersion="Windows 11",
                AppVersion="1.0.0"
            )
        )
        
        auth_result = await sdk.login_async(login_request)
        if auth_result.is_success:
            logger.info("✅ Login successful")
            logger.info(f"   Token Type: {auth_result.token_response.token_type}")
            logger.info(f"   Expires In: {auth_result.token_response.expires_in} seconds")
        else:
            logger.info(f"❌ Login failed: {auth_result.error_message}")
            return
        
        # Check authentication status
        is_authenticated = await sdk.is_authenticated_async()
        logger.info(f"   Authenticated: {is_authenticated}")
        
        # Get current user
        user = await sdk.get_current_user_async()
        if user:
            logger.info(f"   User: {user.name} ({user.email})")
            logger.info(f"   Roles: {', '.join(user.roles)}")
    
    async def _demonstrate_chat_analysis(self, sdk: FraudDetectionSdk):
        """Demonstrate chat-based fraud analysis"""
        logger.info("\n💬 Chat-based Fraud Analysis")
        logger.info("-" * 35)
        
        # Example 1: General fraud question
        chat_request = MobileChatRequest(
            Message="I'm about to make a $5,000 transfer to someone I met online. Is this safe?",
            ConversationId="conv_001",
            SessionId="session_001",
            Location=LocationInfo(
                Latitude=40.7128,
                Longitude=-74.0060,
                City="New York",
                State="NY",
                Country="USA"
            )
        )
        
        response = await sdk.chat_async(chat_request)
        logger.info(f"🤖 AI Response: {response.message}")
        logger.info(f"   Risk Score: {response.risk_score:.2f}")
        logger.info(f"   Risk Level: {response.risk_level}")
        logger.info(f"   Recommendations: {', '.join(response.recommendations)}")
        
        # Example 2: Transaction-specific question
        chat_request2 = MobileChatRequest(
            Message="Can you analyze this transaction for me?",
            TransactionContext=TransactionContext(
                Amount=2500.0,
                MerchantName="Cryptocurrency Exchange",
                Location="Offshore",
                PaymentMethod="Wire Transfer",
                Currency="USD"
            )
        )
        
        response2 = await sdk.chat_async(chat_request2)
        logger.info(f"\n🤖 Transaction Analysis: {response2.message}")
        logger.info(f"   Risk Score: {response2.risk_score:.2f}")
        if response2.detected_patterns:
            logger.info(f"   Detected Patterns: {', '.join(response2.detected_patterns)}")
    
    async def _demonstrate_transaction_risk(self, sdk: FraudDetectionSdk):
        """Demonstrate transaction risk assessment"""
        logger.info("\n💳 Transaction Risk Assessment")
        logger.info("-" * 35)
        
        # High-risk transaction
        high_risk_txn = MobileTransactionRequest(
            Amount=50000.0,
            MerchantName="Offshore Investment Fund",
            Location="Cayman Islands",
            TransactionTime=datetime.now(),
            PaymentMethod="Wire Transfer",
            DeviceInfo=DeviceInfo(
                DeviceId="device_001",
                DeviceType="Mobile",
                OsVersion="iOS 15.0",
                AppVersion="2.1.0",
                IsJailbroken=False,
                IsEmulator=False
            ),
            MerchantCategory="Investment",
            TransactionType="Transfer",
            Currency="USD",
            IsRecurring=False,
            Metadata={
                "ip_address": "192.168.1.100",
                "user_agent": "MobileApp/2.1.0"
            }
        )
        
        response = await sdk.check_transaction_risk_async(high_risk_txn)
        logger.info(f"🚨 High-Risk Transaction Analysis:")
        logger.info(f"   Risk Score: {response.risk_score:.2f}")
        logger.info(f"   Risk Level: {response.risk_level}")
        logger.info(f"   Recommendations: {', '.join(response.recommendations)}")
        if response.suggested_actions:
            for action in response.suggested_actions:
                logger.info(f"   Suggested Action: {action.action_type} - {action.description}")
        
        # Low-risk transaction
        low_risk_txn = MobileTransactionRequest(
            Amount=25.0,
            MerchantName="Local Coffee Shop",
            Location="New York, NY",
            TransactionTime=datetime.now(),
            PaymentMethod="Credit Card",
            DeviceInfo=DeviceInfo(
                DeviceId="device_001",
                DeviceType="Mobile",
                OsVersion="iOS 15.0",
                AppVersion="2.1.0"
            ),
            MerchantCategory="Food & Beverage",
            TransactionType="Purchase",
            Currency="USD",
            IsRecurring=True
        )
        
        response2 = await sdk.check_transaction_risk_async(low_risk_txn)
        logger.info(f"\n✅ Low-Risk Transaction Analysis:")
        logger.info(f"   Risk Score: {response2.risk_score:.2f}")
        logger.info(f"   Risk Level: {response2.risk_level}")
        logger.info(f"   Recommendations: {', '.join(response2.recommendations)}")
    
    async def _demonstrate_counterfactual_analysis(self, sdk: FraudDetectionSdk):
        """Demonstrate counterfactual analysis"""
        logger.info("\n🔄 Counterfactual Analysis")
        logger.info("-" * 30)
        
        counterfactual_request = MobileCounterfactualRequest(
            TransactionId="txn_high_risk_001",
            TargetRiskThreshold=0.3,
            Factors=["amount", "location", "merchant", "payment_method"],
            MaxRecommendations=5,
            IncludeExplanations=True
        )
        
        response = await sdk.get_counterfactual_analysis_async(counterfactual_request)
        logger.info(f"📊 Counterfactual Analysis Results:")
        logger.info(f"   Original Risk Score: {response.original_risk_score:.2f}")
        logger.info(f"   Target Threshold: {response.target_threshold:.2f}")
        logger.info(f"   Can Achieve Target: {response.can_achieve_target}")
        logger.info(f"   Best Achievable Risk: {response.best_achievable_risk_score:.2f}")
        logger.info(f"   Confidence Level: {response.confidence_level:.2f}")
        logger.info(f"   Detailed Explanation: {response.detailed_explanation}")
        
        if response.margin_to_safe:
            logger.info(f"   Margin to Safe: {response.margin_to_safe:.2f}")
        
        logger.info(f"\n💡 Recommendations:")
        for i, rec in enumerate(response.recommendations, 1):
            logger.info(f"   {i}. {rec.change}")
            logger.info(f"      Expected Risk: {rec.expected_risk_score:.2f}")
            logger.info(f"      Impact: {rec.impact_level}")
            logger.info(f"      Feasibility: {rec.feasibility}")
            logger.info(f"      Explanation: {rec.explanation}")
    
    async def _demonstrate_http_interception(self, sdk: FraudDetectionSdk):
        """Demonstrate HTTP request interception"""
        logger.info("\n🌐 HTTP Request Interception")
        logger.info("-" * 35)
        
        # Simulate various HTTP requests
        test_requests = [
            {
                "method": "GET",
                "url": "https://api.bank.com/account/balance",
                "headers": {"User-Agent": "BankingApp/1.0", "Authorization": "Bearer token123"},
                "body": None,
                "description": "Normal API call"
            },
            {
                "method": "POST",
                "url": "https://api.bank.com/transfer",
                "headers": {"Content-Type": "application/json"},
                "body": '{"amount": 10000, "recipient": "suspicious@example.com"}',
                "description": "High-value transfer"
            },
            {
                "method": "POST",
                "url": "https://api.bank.com/admin/users",
                "headers": {"User-Agent": "AdminTool/1.0"},
                "body": '{"action": "delete_user", "user_id": "12345"}',
                "description": "Admin operation"
            },
            {
                "method": "GET",
                "url": "https://api.bank.com/health",
                "headers": {},
                "body": None,
                "description": "Health check"
            }
        ]
        
        for req in test_requests:
            logger.info(f"\n🔍 Analyzing: {req['description']}")
            logger.info(f"   Method: {req['method']} {req['url']}")
            
            analysis = await sdk.intercept_request_async(
                req["method"],
                req["url"],
                req["headers"],
                req["body"]
            )
            
            logger.info(f"   Risk Score: {analysis['risk_score']:.2f}")
            logger.info(f"   Should Block: {analysis['should_block']}")
            logger.info(f"   Recommended Action: {analysis['recommended_action']}")
            if analysis['reason']:
                logger.info(f"   Reason: {analysis['reason']}")
    
    async def _demonstrate_fraud_history(self, sdk: FraudDetectionSdk):
        """Demonstrate fraud history and analytics"""
        logger.info("\n📊 Fraud History and Analytics")
        logger.info("-" * 35)
        
        # Get fraud history
        history_request = FraudHistoryRequest(
            StartDate=datetime.now() - timedelta(days=30),
            EndDate=datetime.now(),
            MaxItems=20,
            Page=1,
            RiskLevelFilter="High",
            TransactionTypeFilter="Transfer"
        )
        
        history = await sdk.get_fraud_history_async(history_request)
        logger.info(f"📈 Fraud History Summary:")
        logger.info(f"   Total High-Risk Transactions: {history.total_count}")
        logger.info(f"   Page: {history.page} of {(history.total_count // history.page_size) + 1}")
        logger.info(f"   Has More: {history.has_more}")
        
        if history.transactions:
            logger.info(f"\n🚨 Recent High-Risk Transactions:")
            for i, txn in enumerate(history.transactions[:5], 1):
                logger.info(f"   {i}. {txn.transaction_id}")
                logger.info(f"      Amount: ${txn.amount:,.2f}")
                logger.info(f"      Merchant: {txn.merchant_name}")
                logger.info(f"      Risk Score: {txn.risk_score:.2f}")
                logger.info(f"      Status: {txn.status}")
                if txn.fraud_patterns:
                    logger.info(f"      Patterns: {', '.join(txn.fraud_patterns)}")
        else:
            logger.info("   No high-risk transactions found in the last 30 days")
    
    async def _demonstrate_user_preferences(self, sdk: FraudDetectionSdk):
        """Demonstrate user preferences management"""
        logger.info("\n⚙️ User Preferences Management")
        logger.info("-" * 35)
        
        # Update user preferences
        preferences = UserPreferences(
            UserId="demo_user_001",
            NotificationsEnabled=True,
            RiskThreshold=0.6,
            PreferredLanguage="en",
            Timezone="America/New_York",
            BiometricAuthEnabled=True,
            AutoLogoutMinutes=15
        )
        
        result = await sdk.update_user_preferences_async(preferences)
        if result:
            logger.info("✅ User preferences updated successfully")
            logger.info(f"   Risk Threshold: {preferences.risk_threshold}")
            logger.info(f"   Notifications: {'Enabled' if preferences.notifications_enabled else 'Disabled'}")
            logger.info(f"   Biometric Auth: {'Enabled' if preferences.biometric_auth_enabled else 'Disabled'}")
            logger.info(f"   Auto Logout: {preferences.auto_logout_minutes} minutes")
        else:
            logger.info("❌ Failed to update user preferences")
    
    async def _demonstrate_feedback_submission(self, sdk: FraudDetectionSdk):
        """Demonstrate feedback submission"""
        logger.info("\n📝 Feedback Submission")
        logger.info("-" * 25)
        
        # Submit feedback for a false positive
        feedback = FraudFeedback(
            TransactionId="txn_false_positive_001",
            UserId="demo_user_001",
            Label="false_positive",
            Comments="This was actually a legitimate business transaction with a known vendor",
            Confidence=0.9
        )
        
        result = await sdk.submit_feedback_async(feedback)
        if result:
            logger.info("✅ Feedback submitted successfully")
            logger.info(f"   Transaction ID: {feedback.transaction_id}")
            logger.info(f"   Label: {feedback.label}")
            logger.info(f"   Comments: {feedback.comments}")
            logger.info(f"   Confidence: {feedback.confidence}")
        else:
            logger.info("❌ Failed to submit feedback")
        
        # Submit feedback for a true positive
        feedback2 = FraudFeedback(
            TransactionId="txn_true_positive_001",
            UserId="demo_user_001",
            Label="true_positive",
            Comments="This was indeed a fraudulent transaction. Good catch!",
            Confidence=1.0
        )
        
        result2 = await sdk.submit_feedback_async(feedback2)
        if result2:
            logger.info(f"\n✅ Additional feedback submitted")
            logger.info(f"   Transaction ID: {feedback2.transaction_id}")
            logger.info(f"   Label: {feedback2.label}")
            logger.info(f"   Comments: {feedback2.comments}")


async def main():
    """Main function to run the integration example"""
    # You can change this URL to point to your fraud detection agent
    base_url = "http://localhost:5000"  # Default Flask development server
    
    example = FraudDetectionIntegrationExample(base_url)
    
    try:
        await example.run_comprehensive_example()
    except Exception as ex:
        logger.info(f"\n❌ Error running example: {ex}")
        logger.info("Make sure the fraud detection agent is running on the specified URL")


if __name__ == "__main__":
    asyncio.run(main())
