using System;
using System.Collections.Generic;
using System.Text.Json.Serialization;

namespace ParadigmFraudDetectionSdk.Models
{
    /// <summary>
    /// Configuration options for the Fraud Detection SDK
    /// </summary>
    public class FraudDetectionSdkOptions
    {
        [JsonPropertyName("baseUrl")]
        public string BaseUrl { get; set; } = string.Empty;

        [JsonPropertyName("apiKey")]
        public string? ApiKey { get; set; }

        [JsonPropertyName("timeout")]
        public double Timeout { get; set; } = 30.0;

        [JsonPropertyName("environment")]
        public string Environment { get; set; } = "Production";

        [JsonPropertyName("applicationName")]
        public string? ApplicationName { get; set; }

        [JsonPropertyName("applicationVersion")]
        public string? ApplicationVersion { get; set; }
    }

    /// <summary>
    /// Request for fraud detection chat
    /// </summary>
    public class MobileChatRequest
    {
        [JsonPropertyName("message")]
        public string Message { get; set; } = string.Empty;

        [JsonPropertyName("conversationId")]
        public string? ConversationId { get; set; }

        [JsonPropertyName("sessionId")]
        public string? SessionId { get; set; }

        [JsonPropertyName("transactionContext")]
        public TransactionContext? TransactionContext { get; set; }

        [JsonPropertyName("location")]
        public LocationInfo? Location { get; set; }

        [JsonPropertyName("deviceInfo")]
        public DeviceInfo? DeviceInfo { get; set; }

        [JsonPropertyName("metadata")]
        public Dictionary<string, object>? Metadata { get; set; }
    }

    /// <summary>
    /// Request for transaction risk assessment
    /// </summary>
    public class MobileTransactionRequest
    {
        [JsonPropertyName("amount")]
        public decimal Amount { get; set; }

        [JsonPropertyName("merchantName")]
        public string MerchantName { get; set; } = string.Empty;

        [JsonPropertyName("location")]
        public string Location { get; set; } = string.Empty;

        [JsonPropertyName("transactionTime")]
        public DateTime TransactionTime { get; set; } = DateTime.UtcNow;

        [JsonPropertyName("paymentMethod")]
        public string PaymentMethod { get; set; } = string.Empty;

        [JsonPropertyName("deviceInfo")]
        public DeviceInfo? DeviceInfo { get; set; }

        [JsonPropertyName("merchantCategory")]
        public string? MerchantCategory { get; set; }

        [JsonPropertyName("transactionType")]
        public string? TransactionType { get; set; }

        [JsonPropertyName("currency")]
        public string? Currency { get; set; }

        [JsonPropertyName("cardLastFour")]
        public string? CardLastFour { get; set; }

        [JsonPropertyName("isRecurring")]
        public bool IsRecurring { get; set; }

        [JsonPropertyName("metadata")]
        public Dictionary<string, object>? Metadata { get; set; }
    }

    /// <summary>
    /// Request for counterfactual analysis
    /// </summary>
    public class MobileCounterfactualRequest
    {
        [JsonPropertyName("transactionId")]
        public string TransactionId { get; set; } = string.Empty;

        [JsonPropertyName("targetRiskThreshold")]
        public double TargetRiskThreshold { get; set; }

        [JsonPropertyName("factors")]
        public List<string> Factors { get; set; } = new();

        [JsonPropertyName("maxRecommendations")]
        public int MaxRecommendations { get; set; } = 5;

        [JsonPropertyName("includeExplanations")]
        public bool IncludeExplanations { get; set; } = true;
    }

    /// <summary>
    /// Response from fraud detection API
    /// </summary>
    public class MobileFraudResponse
    {
        [JsonPropertyName("message")]
        public string Message { get; set; } = string.Empty;

        [JsonPropertyName("riskScore")]
        public double? RiskScore { get; set; }

        [JsonPropertyName("riskLevel")]
        public string? RiskLevel { get; set; }

        [JsonPropertyName("recommendations")]
        public List<string> Recommendations { get; set; } = new();

        [JsonPropertyName("conversationId")]
        public string? ConversationId { get; set; }

        [JsonPropertyName("canCopyShare")]
        public bool CanCopyShare { get; set; }

        [JsonPropertyName("detectedPatterns")]
        public List<string>? DetectedPatterns { get; set; }

        [JsonPropertyName("confidence")]
        public double? Confidence { get; set; }

        [JsonPropertyName("suggestedActions")]
        public List<SuggestedAction>? SuggestedActions { get; set; }

        [JsonPropertyName("context")]
        public Dictionary<string, object>? Context { get; set; }
    }

    /// <summary>
    /// Counterfactual analysis response
    /// </summary>
    public class CounterfactualResponse
    {
        [JsonPropertyName("originalRiskScore")]
        public double OriginalRiskScore { get; set; }

        [JsonPropertyName("targetThreshold")]
        public double TargetThreshold { get; set; }

        [JsonPropertyName("canAchieveTarget")]
        public bool CanAchieveTarget { get; set; }

        [JsonPropertyName("bestAchievableRiskScore")]
        public double BestAchievableRiskScore { get; set; }

        [JsonPropertyName("confidenceLevel")]
        public double ConfidenceLevel { get; set; }

        [JsonPropertyName("detailedExplanation")]
        public string DetailedExplanation { get; set; } = string.Empty;

        [JsonPropertyName("recommendations")]
        public List<MobileRecommendation> Recommendations { get; set; } = new();

        [JsonPropertyName("marginToSafe")]
        public double? MarginToSafe { get; set; }

        [JsonPropertyName("mostEffectiveChange")]
        public ParameterChange? MostEffectiveChange { get; set; }
    }

    /// <summary>
    /// Mobile-specific recommendation
    /// </summary>
    public class MobileRecommendation
    {
        [JsonPropertyName("change")]
        public string Change { get; set; } = string.Empty;

        [JsonPropertyName("expectedRiskScore")]
        public double ExpectedRiskScore { get; set; }

        [JsonPropertyName("explanation")]
        public string Explanation { get; set; } = string.Empty;

        [JsonPropertyName("impactLevel")]
        public string? ImpactLevel { get; set; }

        [JsonPropertyName("feasibility")]
        public string? Feasibility { get; set; }
    }

    /// <summary>
    /// Parameter change suggestion
    /// </summary>
    public class ParameterChange
    {
        [JsonPropertyName("parameterName")]
        public string ParameterName { get; set; } = string.Empty;

        [JsonPropertyName("currentValue")]
        public object? CurrentValue { get; set; }

        [JsonPropertyName("suggestedValue")]
        public object? SuggestedValue { get; set; }

        [JsonPropertyName("explanation")]
        public string Explanation { get; set; } = string.Empty;

        [JsonPropertyName("impact")]
        public double Impact { get; set; }
    }

    /// <summary>
    /// Suggested action for user
    /// </summary>
    public class SuggestedAction
    {
        [JsonPropertyName("actionType")]
        public string ActionType { get; set; } = string.Empty;

        [JsonPropertyName("description")]
        public string Description { get; set; } = string.Empty;

        [JsonPropertyName("priority")]
        public string Priority { get; set; } = string.Empty;

        [JsonPropertyName("canAutomate")]
        public bool CanAutomate { get; set; }

        [JsonPropertyName("parameters")]
        public Dictionary<string, object>? Parameters { get; set; }
    }

    /// <summary>
    /// Transaction context information
    /// </summary>
    public class TransactionContext
    {
        [JsonPropertyName("amount")]
        public decimal Amount { get; set; }

        [JsonPropertyName("merchantName")]
        public string MerchantName { get; set; } = string.Empty;

        [JsonPropertyName("location")]
        public string Location { get; set; } = string.Empty;

        [JsonPropertyName("timestamp")]
        public DateTime? Timestamp { get; set; }

        [JsonPropertyName("paymentMethod")]
        public string? PaymentMethod { get; set; }

        [JsonPropertyName("transactionId")]
        public string? TransactionId { get; set; }

        [JsonPropertyName("currency")]
        public string? Currency { get; set; }
    }

    /// <summary>
    /// Location information
    /// </summary>
    public class LocationInfo
    {
        [JsonPropertyName("latitude")]
        public double? Latitude { get; set; }

        [JsonPropertyName("longitude")]
        public double? Longitude { get; set; }

        [JsonPropertyName("city")]
        public string? City { get; set; }

        [JsonPropertyName("state")]
        public string? State { get; set; }

        [JsonPropertyName("country")]
        public string? Country { get; set; }

        [JsonPropertyName("postalCode")]
        public string? PostalCode { get; set; }

        [JsonPropertyName("accuracy")]
        public double? Accuracy { get; set; }

        [JsonPropertyName("timestamp")]
        public DateTime? Timestamp { get; set; }
    }

    /// <summary>
    /// Device information
    /// </summary>
    public class DeviceInfo
    {
        [JsonPropertyName("deviceId")]
        public string DeviceId { get; set; } = string.Empty;

        [JsonPropertyName("deviceType")]
        public string DeviceType { get; set; } = string.Empty;

        [JsonPropertyName("osVersion")]
        public string OsVersion { get; set; } = string.Empty;

        [JsonPropertyName("appVersion")]
        public string AppVersion { get; set; } = string.Empty;

        [JsonPropertyName("screenResolution")]
        public string? ScreenResolution { get; set; }

        [JsonPropertyName("timezone")]
        public string? Timezone { get; set; }

        [JsonPropertyName("language")]
        public string? Language { get; set; }

        [JsonPropertyName("carrier")]
        public string? Carrier { get; set; }

        [JsonPropertyName("networkType")]
        public string? NetworkType { get; set; }

        [JsonPropertyName("isJailbroken")]
        public bool? IsJailbroken { get; set; }

        [JsonPropertyName("isEmulator")]
        public bool? IsEmulator { get; set; }

        [JsonPropertyName("fingerprint")]
        public string? Fingerprint { get; set; }
    }

    /// <summary>
    /// User information
    /// </summary>
    public class UserInfo
    {
        [JsonPropertyName("userId")]
        public string UserId { get; set; } = string.Empty;

        [JsonPropertyName("username")]
        public string Username { get; set; } = string.Empty;

        [JsonPropertyName("name")]
        public string Name { get; set; } = string.Empty;

        [JsonPropertyName("email")]
        public string? Email { get; set; }

        [JsonPropertyName("roles")]
        public List<string> Roles { get; set; } = new();

        [JsonPropertyName("claims")]
        public Dictionary<string, string> Claims { get; set; } = new();

        [JsonPropertyName("preferredLanguage")]
        public string? PreferredLanguage { get; set; }
    }

    /// <summary>
    /// Login request
    /// </summary>
    public class LoginRequest
    {
        [JsonPropertyName("username")]
        public string Username { get; set; } = string.Empty;

        [JsonPropertyName("password")]
        public string Password { get; set; } = string.Empty;

        [JsonPropertyName("rememberMe")]
        public bool RememberMe { get; set; }

        [JsonPropertyName("deviceInfo")]
        public DeviceInfo? DeviceInfo { get; set; }
    }

    /// <summary>
    /// Token response
    /// </summary>
    public class TokenResponse
    {
        [JsonPropertyName("accessToken")]
        public string AccessToken { get; set; } = string.Empty;

        [JsonPropertyName("refreshToken")]
        public string RefreshToken { get; set; } = string.Empty;

        [JsonPropertyName("expiresIn")]
        public int ExpiresIn { get; set; }

        [JsonPropertyName("tokenType")]
        public string TokenType { get; set; } = "Bearer";
    }

    /// <summary>
    /// Authentication result
    /// </summary>
    public class AuthenticationResult
    {
        [JsonPropertyName("isSuccess")]
        public bool IsSuccess { get; set; }

        [JsonPropertyName("tokenResponse")]
        public TokenResponse? TokenResponse { get; set; }

        [JsonPropertyName("errorMessage")]
        public string? ErrorMessage { get; set; }

        [JsonPropertyName("errorCode")]
        public string? ErrorCode { get; set; }
    }

    /// <summary>
    /// Fraud feedback
    /// </summary>
    public class FraudFeedback
    {
        [JsonPropertyName("transactionId")]
        public string TransactionId { get; set; } = string.Empty;

        [JsonPropertyName("userId")]
        public string UserId { get; set; } = string.Empty;

        [JsonPropertyName("label")]
        public string Label { get; set; } = string.Empty;

        [JsonPropertyName("timestamp")]
        public DateTime Timestamp { get; set; } = DateTime.UtcNow;

        [JsonPropertyName("comments")]
        public string? Comments { get; set; }

        [JsonPropertyName("confidence")]
        public double? Confidence { get; set; }
    }

    /// <summary>
    /// Fraud history request
    /// </summary>
    public class FraudHistoryRequest
    {
        [JsonPropertyName("startDate")]
        public DateTime? StartDate { get; set; }

        [JsonPropertyName("endDate")]
        public DateTime? EndDate { get; set; }

        [JsonPropertyName("maxItems")]
        public int? MaxItems { get; set; }

        [JsonPropertyName("page")]
        public int? Page { get; set; }

        [JsonPropertyName("riskLevelFilter")]
        public string? RiskLevelFilter { get; set; }

        [JsonPropertyName("transactionTypeFilter")]
        public string? TransactionTypeFilter { get; set; }
    }

    /// <summary>
    /// Fraud history response
    /// </summary>
    public class FraudHistoryResponse
    {
        [JsonPropertyName("transactions")]
        public List<FraudHistoryItem> Transactions { get; set; } = new();

        [JsonPropertyName("totalCount")]
        public int TotalCount { get; set; }

        [JsonPropertyName("page")]
        public int Page { get; set; }

        [JsonPropertyName("pageSize")]
        public int PageSize { get; set; }

        [JsonPropertyName("hasMore")]
        public bool HasMore { get; set; }
    }

    /// <summary>
    /// Fraud history item
    /// </summary>
    public class FraudHistoryItem
    {
        [JsonPropertyName("transactionId")]
        public string TransactionId { get; set; } = string.Empty;

        [JsonPropertyName("timestamp")]
        public DateTime Timestamp { get; set; }

        [JsonPropertyName("amount")]
        public decimal Amount { get; set; }

        [JsonPropertyName("merchantName")]
        public string MerchantName { get; set; } = string.Empty;

        [JsonPropertyName("riskScore")]
        public double RiskScore { get; set; }

        [JsonPropertyName("riskLevel")]
        public string RiskLevel { get; set; } = string.Empty;

        [JsonPropertyName("status")]
        public string Status { get; set; } = string.Empty;

        [JsonPropertyName("fraudPatterns")]
        public List<string> FraudPatterns { get; set; } = new();
    }

    /// <summary>
    /// User preferences
    /// </summary>
    public class UserPreferences
    {
        [JsonPropertyName("userId")]
        public string UserId { get; set; } = string.Empty;

        [JsonPropertyName("notificationsEnabled")]
        public bool NotificationsEnabled { get; set; } = true;

        [JsonPropertyName("riskThreshold")]
        public double RiskThreshold { get; set; } = 0.7;

        [JsonPropertyName("preferredLanguage")]
        public string PreferredLanguage { get; set; } = "en";

        [JsonPropertyName("timezone")]
        public string Timezone { get; set; } = "UTC";

        [JsonPropertyName("biometricAuthEnabled")]
        public bool BiometricAuthEnabled { get; set; } = false;

        [JsonPropertyName("autoLogoutMinutes")]
        public int AutoLogoutMinutes { get; set; } = 30;
    }

    /// <summary>
    /// Health status
    /// </summary>
    public class HealthStatus
    {
        [JsonPropertyName("status")]
        public string Status { get; set; } = string.Empty;

        [JsonPropertyName("version")]
        public string Version { get; set; } = string.Empty;

        [JsonPropertyName("timestamp")]
        public DateTime Timestamp { get; set; } = DateTime.UtcNow;

        [JsonPropertyName("services")]
        public Dictionary<string, string> Services { get; set; } = new();
    }

    /// <summary>
    /// Fraud risk analysis result
    /// </summary>
    public class FraudRiskAnalysis
    {
        [JsonPropertyName("requestId")]
        public string RequestId { get; set; } = string.Empty;

        [JsonPropertyName("riskScore")]
        public double RiskScore { get; set; }

        [JsonPropertyName("recommendedAction")]
        public string RecommendedAction { get; set; } = string.Empty;

        [JsonPropertyName("shouldBlock")]
        public bool ShouldBlock { get; set; }

        [JsonPropertyName("blockReason")]
        public string? BlockReason { get; set; }

        [JsonPropertyName("analysisTimestamp")]
        public DateTime AnalysisTimestamp { get; set; } = DateTime.UtcNow;
    }
}
