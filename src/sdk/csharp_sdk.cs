using System;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;

namespace ParadigmStore.FraudDetection
{
    public static class FraudDetection
    {
        private static string? _apiKey;
        private static readonly HttpClient _httpClient = new HttpClient();
        private static readonly string _baseUrl = "http://localhost:9001"; // Will be https://api.paradigmstore.com in production
        
        /// <summary>
        /// Initialize ParadigmStore Fraud Detection
        /// </summary>
        /// <param name="apiKey">Your API key</param>
        public static void Initialize(string apiKey)
        {
            _apiKey = apiKey ?? throw new ArgumentNullException(nameof(apiKey));
            _httpClient.DefaultRequestHeaders.Add("X-API-Key", apiKey);
        }
        
        /// <summary>
        /// Analyze transaction for fraud risk
        /// </summary>
        /// <param name="transaction">Transaction data</param>
        /// <returns>Fraud analysis result</returns>
        public static async Task<FraudResult> AnalyzeAsync(object transaction)
        {
            if (string.IsNullOrEmpty(_apiKey))
                throw new InvalidOperationException("FraudDetection not initialized. Call Initialize() first.");
            
            var json = JsonSerializer.Serialize(new { transaction, api_key = _apiKey });
            var content = new StringContent(json, Encoding.UTF8, "application/json");
            
            try
            {
                var response = await _httpClient.PostAsync($"{_baseUrl}/api/sdk/analyze", content);
                var responseJson = await response.Content.ReadAsStringAsync();
                
                var result = JsonSerializer.Deserialize<FraudResult>(responseJson) ?? new FraudResult();
                return result;
            }
            catch (Exception ex)
            {
                return new FraudResult
                {
                    Success = false,
                    Error = ex.Message,
                    RiskScore = 0.5,
                    Recommendation = "REVIEW"
                };
            }
        }
        
        /// <summary>
        /// Analyze transaction synchronously
        /// </summary>
        /// <param name="transaction">Transaction data</param>
        /// <returns>Fraud analysis result</returns>
        public static FraudResult Analyze(object transaction)
        {
            return AnalyzeAsync(transaction).GetAwaiter().GetResult();
        }
    }
    
    public class FraudResult
    {
        public double RiskScore { get; set; }
        public string Recommendation { get; set; } = "";
        public string Reasoning { get; set; } = "";
        public double ProcessingTimeMs { get; set; }
        public bool Success { get; set; } = true;
        public string Error { get; set; } = "";
        public string AnalysisId { get; set; } = "";
        public string Agent { get; set; } = "";
        public string Version { get; set; } = "";
    }
}
