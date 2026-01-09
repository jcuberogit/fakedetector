# 🛡️ Universal Fraud Detection SDK

**Cross-Platform Fraud Detection SDK with Python Core and C# Wrapper**

## 🎯 **What It Does**

This SDK provides **universal fraud detection capabilities** across multiple platforms:

- **🐍 Python Core**: High-performance fraud detection engine
- **🔷 C# Wrapper**: Seamless integration with .NET applications
- **📱 Universal**: Works on any platform that supports Python or C#
- **🔄 HTTP Interception**: Automatically analyzes all HTTP requests
- **🤖 AI-Powered**: Advanced ML models for fraud detection

## 🔥 **Key Features**

- **🔄 Universal HTTP Interception** - Monitors every API call automatically
- **🚫 Real-time Blocking** - Stops high-risk transactions before they happen  
- **📊 Fraud Analytics** - Detailed risk scoring and pattern analysis
- **🔐 Zero Code Changes** - Drop-in integration with existing apps
- **📱 Cross-Platform** - Works on iOS, Android, Windows, macOS, Linux
- **⚡ Offline Support** - Queues analysis when network is unavailable
- **🤖 AI Integration** - OpenAI-powered conversational fraud analysis
- **📈 ML Models** - XGBoost, Neural Networks, Graph Neural Networks

## 📦 **Installation**

### Python Installation
```bash
pip install paradigm-fraud-detection-sdk
```

### C# Installation
```bash
dotnet add package ParadigmFraudDetectionSdk
```

## 🚀 **Quick Start**

### Python Usage

```python
import asyncio
from sdk import FraudDetectionSdk, FraudDetectionSdkOptions, MobileChatRequest

async def main():
    # Initialize SDK
    options = FraudDetectionSdkOptions(
        BaseUrl="https://fraudapi.paradigmstore.com",
        Environment="Production"
    )
    
    async with FraudDetectionSdk(options) as sdk:
        # Send chat message for fraud analysis
        request = MobileChatRequest(
            Message="Is this transaction safe?",
            TransactionContext={
                "amount": 1000.0,
                "merchant": "Online Store"
            }
        )
        
        response = await sdk.chat_async(request)
        print(f"Risk Score: {response.risk_score}")
        print(f"Recommendations: {response.recommendations}")

asyncio.run(main())
```

### C# Usage

```csharp
using ParadigmFraudDetectionSdk;
using ParadigmFraudDetectionSdk.Models;

// Initialize SDK
var options = new FraudDetectionSdkOptions
{
    BaseUrl = "https://fraudapi.paradigmstore.com",
    Environment = "Production"
};

using var sdk = new FraudDetectionSdkWrapper(options);
await sdk.InitializeAsync();

// Send chat message for fraud analysis
var request = new MobileChatRequest
{
    Message = "Is this transaction safe?",
    TransactionContext = new TransactionContext
    {
        Amount = 1000.0m,
        MerchantName = "Online Store"
    }
};

var response = await sdk.ChatAsync(request);
Console.WriteLine($"Risk Score: {response.RiskScore}");
Console.WriteLine($"Recommendations: {string.Join(", ", response.Recommendations)}");
```

## 🔥 **HTTP Interception (Zero Code Changes)**

### Python HTTP Interception

```python
import aiohttp
from sdk import UniversalHttpInterceptor, FraudDetectionInterceptor, FraudDetectionSdkOptions

# Create interceptor
options = FraudDetectionSdkOptions(BaseUrl="https://fraudapi.paradigmstore.com")
interceptor = FraudDetectionInterceptor(options, auth_handler, logger)
universal_interceptor = UniversalHttpInterceptor(interceptor)

# Wrap your HTTP client
async def make_request(url, method="GET", headers=None, body=None):
    # Intercept request
    analysis = await universal_interceptor.intercept_request(method, url, headers or {}, body)
    
    if analysis and analysis.get("blocked"):
        return {
            "status_code": analysis["status_code"],
            "error": analysis["error"]
        }
    
    # Make actual request
    async with aiohttp.ClientSession() as session:
        async with session.request(method, url, headers=headers, data=body) as response:
            # Intercept response
            await universal_interceptor.intercept_response(
                analysis.get("request_id", ""),
                response.status,
                dict(response.headers),
                await response.text()
            )
            return await response.json()
```

### C# HTTP Interception

```csharp
// Add to Program.cs or Startup.cs
builder.Services.AddFraudDetectionSdk(options =>
{
    options.BaseUrl = "https://fraudapi.paradigmstore.com";
    options.Environment = "Production";
});

// Add interceptor to HttpClient
builder.Services.AddHttpClient<IBankingService, BankingService>()
    .AddFraudDetectionInterceptor(serviceProvider.GetRequiredService<FraudDetectionSdkWrapper>());

// Your existing code works unchanged!
public class BankingService : IBankingService
{
    private readonly HttpClient _client;
    
    public BankingService(HttpClient client)
    {
        _client = client; // Automatically intercepted!
    }
    
    public async Task<AccountBalance> GetBalanceAsync()
    {
        // This request is automatically analyzed for fraud
        var response = await _client.GetAsync("/api/account/balance");
        return await response.Content.ReadFromJsonAsync<AccountBalance>();
    }
}
```

## 🎯 **Advanced Features**

### Transaction Risk Assessment

```python
from sdk import MobileTransactionRequest, DeviceInfo

# Check transaction risk
request = MobileTransactionRequest(
    Amount=5000.0,
    MerchantName="Suspicious Store",
    Location="Unknown Location",
    PaymentMethod="Credit Card",
    DeviceInfo=DeviceInfo(
        DeviceId="device_123",
        DeviceType="Mobile",
        OsVersion="iOS 15.0",
        AppVersion="1.0.0"
    )
)

response = await sdk.check_transaction_risk_async(request)
if response.risk_score > 0.7:
    print("High risk transaction detected!")
    print(f"Recommendations: {response.recommendations}")
```

### Counterfactual Analysis

```python
from sdk import MobileCounterfactualRequest

# Get counterfactual analysis
request = MobileCounterfactualRequest(
    TransactionId="txn_123",
    TargetRiskThreshold=0.3,
    Factors=["amount", "location", "merchant"],
    MaxRecommendations=5
)

response = await sdk.get_counterfactual_analysis_async(request)
print(f"Original Risk: {response.original_risk_score}")
print(f"Best Achievable: {response.best_achievable_risk_score}")

for recommendation in response.recommendations:
    print(f"Change: {recommendation.change}")
    print(f"Expected Risk: {recommendation.expected_risk_score}")
    print(f"Explanation: {recommendation.explanation}")
```

### Fraud History and Analytics

```python
from sdk import FraudHistoryRequest, FraudFeedback

# Get fraud history
history_request = FraudHistoryRequest(
    StartDate=datetime.now() - timedelta(days=30),
    MaxItems=50,
    RiskLevelFilter="High"
)

history = await sdk.get_fraud_history_async(history_request)
print(f"Found {history.total_count} high-risk transactions")

# Submit feedback
feedback = FraudFeedback(
    TransactionId="txn_123",
    UserId="user_456",
    Label="false_positive",
    Comments="This was actually a legitimate transaction"
)

await sdk.submit_feedback_async(feedback)
```

## 🔧 **Configuration**

### Python Configuration

```python
from sdk import FraudDetectionSdkOptions, RetryPolicyOptions, OfflineSyncOptions

options = FraudDetectionSdkOptions(
    BaseUrl="https://fraudapi.paradigmstore.com",
    Environment="Production",
    Timeout=30.0,
    RetryPolicy=RetryPolicyOptions(
        MaxRetries=3,
        BaseDelay=1.0,
        BackoffMultiplier=2.0
    ),
    OfflineSync=OfflineSyncOptions(
        Enabled=True,
        SyncInterval=300.0,  # 5 minutes
        MaxQueueSize=1000
    )
)
```

### C# Configuration

```csharp
var options = new FraudDetectionSdkOptions
{
    BaseUrl = "https://fraudapi.paradigmstore.com",
    Environment = "Production",
    Timeout = 30.0,
    ApplicationName = "MyBankingApp",
    ApplicationVersion = "1.0.0"
};
```

## 🧪 **Testing**

### Python Testing

```python
from sdk import FraudDetectionSdkBuilder

# Use test environment
sdk = (FraudDetectionSdkBuilder()
    .with_base_url("https://test-fraudapi.paradigmstore.com")
    .with_environment("test")
    .build())

async with sdk:
    # Test authentication
    login_result = await sdk.login_async(LoginRequest(
        Username="testuser@example.com",
        Password="TestPassword123!"
    ))
    
    assert login_result.is_success
    
    # Test chat
    response = await sdk.chat_async(MobileChatRequest(
        Message="Test message"
    ))
    
    assert response.message.startswith("Mock response")
```

### C# Testing

```csharp
[Test]
public async Task TestFraudDetection()
{
    var options = new FraudDetectionSdkOptions
    {
        BaseUrl = "https://test-fraudapi.paradigmstore.com",
        Environment = "test"
    };
    
    using var sdk = new FraudDetectionSdkWrapper(options);
    await sdk.InitializeAsync();
    
    // Test authentication
    var loginResult = await sdk.LoginAsync(new LoginRequest
    {
        Username = "testuser@example.com",
        Password = "TestPassword123!"
    });
    
    Assert.IsTrue(loginResult.IsSuccess);
    
    // Test chat
    var response = await sdk.ChatAsync(new MobileChatRequest
    {
        Message = "Test message"
    });
    
    Assert.IsTrue(response.Message.StartsWith("Mock response"));
}
```

## 📊 **Performance**

- **Response Time**: < 100ms for risk assessment
- **Throughput**: 1000+ requests per second
- **Memory Usage**: < 50MB base footprint
- **CPU Usage**: < 5% during normal operation
- **Network**: Minimal bandwidth usage with intelligent caching

## 🔒 **Security**

- **🔐 JWT Authentication** - Secure token-based authentication
- **🛡️ Certificate Pinning** - Optional SSL certificate validation
- **🔒 Encrypted Storage** - Secure local data storage
- **🚫 PII Redaction** - Automatic sensitive data protection
- **🔍 Audit Logging** - Comprehensive activity tracking

## 🌍 **Platform Support**

| Platform | Python | C# | Status |
|----------|--------|----|---------| 
| Windows | ✅ | ✅ | Fully Supported |
| macOS | ✅ | ✅ | Fully Supported |
| Linux | ✅ | ❌ | Python Only |
| iOS | ✅ | ✅ | Via Xamarin/.NET MAUI |
| Android | ✅ | ✅ | Via Xamarin/.NET MAUI |
| Web | ✅ | ✅ | Via Blazor/ASP.NET |

## 📚 **API Reference**

### Core Methods

- `chat_async(request)` - AI-powered fraud analysis chat
- `check_transaction_risk_async(request)` - Transaction risk assessment
- `get_counterfactual_analysis_async(request)` - What-if analysis
- `submit_feedback_async(feedback)` - User feedback submission
- `get_fraud_history_async(request)` - Fraud history retrieval
- `intercept_request_async(method, url, headers, body)` - HTTP interception

### Authentication Methods

- `login_async(login_request)` - User authentication
- `logout_async()` - User logout
- `is_authenticated_async()` - Authentication status check
- `get_current_user_async()` - Current user information

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 **License**

MIT License - see LICENSE file for details.

## 🆘 **Support**

- **Documentation**: [docs.paradigmstore.com](https://docs.paradigmstore.com)
- **Issues**: [GitHub Issues](https://github.com/paradigmstore/fraud-detection-sdk/issues)
- **Email**: support@paradigmstore.com
- **Discord**: [ParadigmStore Community](https://discord.gg/paradigmstore)

---

**Built with ❤️ by the ParadigmStore Team**
