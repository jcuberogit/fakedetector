using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Diagnostics;
using System.IO;
using System.Runtime.InteropServices;

namespace ParadigmFraudDetectionSdk
{
    /// <summary>
    /// C# wrapper for the Python Universal Fraud Detection SDK
    /// Provides seamless integration with existing C# applications
    /// </summary>
    public class FraudDetectionSdkWrapper : IDisposable
    {
        private readonly string _pythonExecutable;
        private readonly string _sdkPath;
        private readonly FraudDetectionSdkOptions _options;
        private Process _pythonProcess;
        private bool _disposed = false;

        /// <summary>
        /// Event fired when Python process outputs data
        /// </summary>
        public event EventHandler<string>? PythonOutputReceived;

        /// <summary>
        /// Event fired when Python process encounters an error
        /// </summary>
        public event EventHandler<string>? PythonErrorReceived;

        public FraudDetectionSdkWrapper(FraudDetectionSdkOptions options)
        {
            _options = options ?? throw new ArgumentNullException(nameof(options));
            _pythonExecutable = FindPythonExecutable();
            _sdkPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "sdk");
            
            if (!Directory.Exists(_sdkPath))
            {
                throw new DirectoryNotFoundException($"SDK path not found: {_sdkPath}");
            }
        }

        /// <summary>
        /// Initialize the Python SDK
        /// </summary>
        public async Task InitializeAsync()
        {
            try
            {
                var initScript = CreateInitializationScript();
                await ExecutePythonScriptAsync(initScript);
            }
            catch (Exception ex)
            {
                throw new InvalidOperationException($"Failed to initialize Python SDK: {ex.Message}", ex);
            }
        }

        /// <summary>
        /// Authenticate user with credentials
        /// </summary>
        public async Task<AuthenticationResult> LoginAsync(LoginRequest loginRequest)
        {
            var script = $@"
import sys
import json
from sdk import FraudDetectionSdk, FraudDetectionSdkOptions, LoginRequest

# Initialize SDK
options = FraudDetectionSdkOptions(BaseUrl='{_options.BaseUrl}', Environment='{_options.Environment}')
sdk = FraudDetectionSdk(options)
await sdk.initialize()

# Login
login_req = LoginRequest(Username='{loginRequest.Username}', Password='{loginRequest.Password}')
result = await sdk.login_async(login_req)

print(json.dumps(result.dict(by_alias=True)))
";

            var result = await ExecutePythonScriptAsync(script);
            return JsonSerializer.Deserialize<AuthenticationResult>(result);
        }

        /// <summary>
        /// Logout and revoke tokens
        /// </summary>
        public async Task<bool> LogoutAsync()
        {
            var script = $@"
import sys
import json
from sdk import FraudDetectionSdk, FraudDetectionSdkOptions

# Initialize SDK
options = FraudDetectionSdkOptions(BaseUrl='{_options.BaseUrl}', Environment='{_options.Environment}')
sdk = FraudDetectionSdk(options)
await sdk.initialize()

# Logout
result = await sdk.logout_async()
print(json.dumps(result))
";

            var result = await ExecutePythonScriptAsync(script);
            return JsonSerializer.Deserialize<bool>(result);
        }

        /// <summary>
        /// Check if user is currently authenticated
        /// </summary>
        public async Task<bool> IsAuthenticatedAsync()
        {
            var script = $@"
import sys
import json
from sdk import FraudDetectionSdk, FraudDetectionSdkOptions

# Initialize SDK
options = FraudDetectionSdkOptions(BaseUrl='{_options.BaseUrl}', Environment='{_options.Environment}')
sdk = FraudDetectionSdk(options)
await sdk.initialize()

# Check authentication
result = await sdk.is_authenticated_async()
print(json.dumps(result))
";

            var result = await ExecutePythonScriptAsync(script);
            return JsonSerializer.Deserialize<bool>(result);
        }

        /// <summary>
        /// Send chat message for fraud analysis
        /// </summary>
        public async Task<MobileFraudResponse> ChatAsync(MobileChatRequest request)
        {
            var requestJson = JsonSerializer.Serialize(request, new JsonSerializerOptions
            {
                PropertyNamingPolicy = JsonNamingPolicy.CamelCase
            });

            var script = $@"
import sys
import json
from sdk import FraudDetectionSdk, FraudDetectionSdkOptions, MobileChatRequest

# Initialize SDK
options = FraudDetectionSdkOptions(BaseUrl='{_options.BaseUrl}', Environment='{_options.Environment}')
sdk = FraudDetectionSdk(options)
await sdk.initialize()

# Parse request
request_data = json.loads('{requestJson}')
chat_req = MobileChatRequest(**request_data)

# Send chat
response = await sdk.chat_async(chat_req)
print(json.dumps(response.dict(by_alias=True)))
";

            var result = await ExecutePythonScriptAsync(script);
            return JsonSerializer.Deserialize<MobileFraudResponse>(result);
        }

        /// <summary>
        /// Check transaction risk
        /// </summary>
        public async Task<MobileFraudResponse> CheckTransactionRiskAsync(MobileTransactionRequest request)
        {
            var requestJson = JsonSerializer.Serialize(request, new JsonSerializerOptions
            {
                PropertyNamingPolicy = JsonNamingPolicy.CamelCase
            });

            var script = $@"
import sys
import json
from sdk import FraudDetectionSdk, FraudDetectionSdkOptions, MobileTransactionRequest

# Initialize SDK
options = FraudDetectionSdkOptions(BaseUrl='{_options.BaseUrl}', Environment='{_options.Environment}')
sdk = FraudDetectionSdk(options)
await sdk.initialize()

# Parse request
request_data = json.loads('{requestJson}')
txn_req = MobileTransactionRequest(**request_data)

# Check risk
response = await sdk.check_transaction_risk_async(txn_req)
print(json.dumps(response.dict(by_alias=True)))
";

            var result = await ExecutePythonScriptAsync(script);
            return JsonSerializer.Deserialize<MobileFraudResponse>(result);
        }

        /// <summary>
        /// Get counterfactual analysis for transaction
        /// </summary>
        public async Task<CounterfactualResponse> GetCounterfactualAnalysisAsync(MobileCounterfactualRequest request)
        {
            var requestJson = JsonSerializer.Serialize(request, new JsonSerializerOptions
            {
                PropertyNamingPolicy = JsonNamingPolicy.CamelCase
            });

            var script = $@"
import sys
import json
from sdk import FraudDetectionSdk, FraudDetectionSdkOptions, MobileCounterfactualRequest

# Initialize SDK
options = FraudDetectionSdkOptions(BaseUrl='{_options.BaseUrl}', Environment='{_options.Environment}')
sdk = FraudDetectionSdk(options)
await sdk.initialize()

# Parse request
request_data = json.loads('{requestJson}')
cf_req = MobileCounterfactualRequest(**request_data)

# Get counterfactual analysis
response = await sdk.get_counterfactual_analysis_async(cf_req)
print(json.dumps(response.dict(by_alias=True)))
";

            var result = await ExecutePythonScriptAsync(script);
            return JsonSerializer.Deserialize<CounterfactualResponse>(result);
        }

        /// <summary>
        /// Submit user feedback on fraud detection
        /// </summary>
        public async Task<bool> SubmitFeedbackAsync(FraudFeedback feedback)
        {
            var feedbackJson = JsonSerializer.Serialize(feedback, new JsonSerializerOptions
            {
                PropertyNamingPolicy = JsonNamingPolicy.CamelCase
            });

            var script = $@"
import sys
import json
from sdk import FraudDetectionSdk, FraudDetectionSdkOptions, FraudFeedback

# Initialize SDK
options = FraudDetectionSdkOptions(BaseUrl='{_options.BaseUrl}', Environment='{_options.Environment}')
sdk = FraudDetectionSdk(options)
await sdk.initialize()

# Parse feedback
feedback_data = json.loads('{feedbackJson}')
feedback = FraudFeedback(**feedback_data)

# Submit feedback
result = await sdk.submit_feedback_async(feedback)
print(json.dumps(result))
";

            var result = await ExecutePythonScriptAsync(script);
            return JsonSerializer.Deserialize<bool>(result);
        }

        /// <summary>
        /// Get user's fraud history
        /// </summary>
        public async Task<FraudHistoryResponse> GetFraudHistoryAsync(FraudHistoryRequest request)
        {
            var requestJson = JsonSerializer.Serialize(request, new JsonSerializerOptions
            {
                PropertyNamingPolicy = JsonNamingPolicy.CamelCase
            });

            var script = $@"
import sys
import json
from sdk import FraudDetectionSdk, FraudDetectionSdkOptions, FraudHistoryRequest

# Initialize SDK
options = FraudDetectionSdkOptions(BaseUrl='{_options.BaseUrl}', Environment='{_options.Environment}')
sdk = FraudDetectionSdk(options)
await sdk.initialize()

# Parse request
request_data = json.loads('{requestJson}')
history_req = FraudHistoryRequest(**request_data)

# Get fraud history
response = await sdk.get_fraud_history_async(history_req)
print(json.dumps(response.dict(by_alias=True)))
";

            var result = await ExecutePythonScriptAsync(script);
            return JsonSerializer.Deserialize<FraudHistoryResponse>(result);
        }

        /// <summary>
        /// Update user preferences
        /// </summary>
        public async Task<bool> UpdateUserPreferencesAsync(UserPreferences preferences)
        {
            var preferencesJson = JsonSerializer.Serialize(preferences, new JsonSerializerOptions
            {
                PropertyNamingPolicy = JsonNamingPolicy.CamelCase
            });

            var script = $@"
import sys
import json
from sdk import FraudDetectionSdk, FraudDetectionSdkOptions, UserPreferences

# Initialize SDK
options = FraudDetectionSdkOptions(BaseUrl='{_options.BaseUrl}', Environment='{_options.Environment}')
sdk = FraudDetectionSdk(options)
await sdk.initialize()

# Parse preferences
preferences_data = json.loads('{preferencesJson}')
preferences = UserPreferences(**preferences_data)

# Update preferences
result = await sdk.update_user_preferences_async(preferences)
print(json.dumps(result))
";

            var result = await ExecutePythonScriptAsync(script);
            return JsonSerializer.Deserialize<bool>(result);
        }

        /// <summary>
        /// Get API health status
        /// </summary>
        public async Task<HealthStatus> GetHealthAsync()
        {
            var script = $@"
import sys
import json
from sdk import FraudDetectionSdk, FraudDetectionSdkOptions

# Initialize SDK
options = FraudDetectionSdkOptions(BaseUrl='{_options.BaseUrl}', Environment='{_options.Environment}')
sdk = FraudDetectionSdk(options)
await sdk.initialize()

# Get health
response = await sdk.get_health_async()
print(json.dumps(response.dict(by_alias=True)))
";

            var result = await ExecutePythonScriptAsync(script);
            return JsonSerializer.Deserialize<HealthStatus>(result);
        }

        /// <summary>
        /// Intercept HTTP request for fraud analysis
        /// </summary>
        public async Task<FraudRiskAnalysis> InterceptRequestAsync(string method, string url, Dictionary<string, string> headers, string? body = null)
        {
            var headersJson = JsonSerializer.Serialize(headers);
            var bodyJson = body != null ? JsonSerializer.Serialize(body) : "null";

            var script = $@"
import sys
import json
from sdk import FraudDetectionSdk, FraudDetectionSdkOptions

# Initialize SDK
options = FraudDetectionSdkOptions(BaseUrl='{_options.BaseUrl}', Environment='{_options.Environment}')
sdk = FraudDetectionSdk(options)
await sdk.initialize()

# Intercept request
headers = json.loads('{headersJson}')
body = json.loads('{bodyJson}') if '{bodyJson}' != 'null' else None

result = await sdk.intercept_request_async('{method}', '{url}', headers, body)
print(json.dumps(result))
";

            var result = await ExecutePythonScriptAsync(script);
            return JsonSerializer.Deserialize<FraudRiskAnalysis>(result);
        }

        /// <summary>
        /// Execute Python script and return result
        /// </summary>
        private async Task<string> ExecutePythonScriptAsync(string script)
        {
            var tempFile = Path.GetTempFileName();
            try
            {
                await File.WriteAllTextAsync(tempFile, script);

                var startInfo = new ProcessStartInfo
                {
                    FileName = _pythonExecutable,
                    Arguments = tempFile,
                    WorkingDirectory = _sdkPath,
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    CreateNoWindow = true
                };

                using var process = new Process { StartInfo = startInfo };
                process.Start();

                var output = await process.StandardOutput.ReadToEndAsync();
                var error = await process.StandardError.ReadToEndAsync();

                await process.WaitForExitAsync();

                if (process.ExitCode != 0)
                {
                    throw new InvalidOperationException($"Python script failed: {error}");
                }

                PythonOutputReceived?.Invoke(this, output);
                if (!string.IsNullOrEmpty(error))
                {
                    PythonErrorReceived?.Invoke(this, error);
                }

                return output.Trim();
            }
            finally
            {
                if (File.Exists(tempFile))
                {
                    File.Delete(tempFile);
                }
            }
        }

        /// <summary>
        /// Create initialization script for Python SDK
        /// </summary>
        private string CreateInitializationScript()
        {
            return $@"
import sys
import json
from sdk import FraudDetectionSdk, FraudDetectionSdkOptions

# Initialize SDK
options = FraudDetectionSdkOptions(BaseUrl='{_options.BaseUrl}', Environment='{_options.Environment}')
sdk = FraudDetectionSdk(options)
await sdk.initialize()

print('SDK initialized successfully')
";
        }

        /// <summary>
        /// Find Python executable
        /// </summary>
        private string FindPythonExecutable()
        {
            var possiblePaths = new[]
            {
                "python",
                "python3",
                "python.exe",
                "python3.exe",
                Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFiles), "Python39", "python.exe"),
                Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFilesX86), "Python39", "python.exe"),
                Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFiles), "Python310", "python.exe"),
                Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFilesX86), "Python310", "python.exe"),
                Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFiles), "Python311", "python.exe"),
                Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFilesX86), "Python311", "python.exe")
            };

            foreach (var path in possiblePaths)
            {
                try
                {
                    var startInfo = new ProcessStartInfo
                    {
                        FileName = path,
                        Arguments = "--version",
                        UseShellExecute = false,
                        RedirectStandardOutput = true,
                        CreateNoWindow = true
                    };

                    using var process = Process.Start(startInfo);
                    if (process != null)
                    {
                        process.WaitForExit();
                        if (process.ExitCode == 0)
                        {
                            return path;
                        }
                    }
                }
                catch
                {
                    // Continue to next path
                }
            }

            throw new InvalidOperationException("Python executable not found. Please install Python 3.9 or later.");
        }

        /// <summary>
        /// Dispose resources
        /// </summary>
        public void Dispose()
        {
            if (!_disposed)
            {
                _pythonProcess?.Dispose();
                _disposed = true;
            }
        }
    }

    /// <summary>
    /// Extension methods for easy SDK integration
    /// </summary>
    public static class FraudDetectionSdkExtensions
    {
        /// <summary>
        /// Add fraud detection SDK to service collection
        /// </summary>
        public static IServiceCollection AddFraudDetectionSdk(
            this IServiceCollection services,
            Action<FraudDetectionSdkOptions> configureOptions)
        {
            var options = new FraudDetectionSdkOptions();
            configureOptions(options);
            
            services.AddSingleton<FraudDetectionSdkWrapper>(provider =>
                new FraudDetectionSdkWrapper(options));
            
            return services;
        }

        /// <summary>
        /// Add fraud detection interceptor to HttpClient
        /// </summary>
        public static IHttpClientBuilder AddFraudDetectionInterceptor(
            this IHttpClientBuilder builder,
            FraudDetectionSdkWrapper sdkWrapper)
        {
            return builder.AddHttpMessageHandler(provider =>
                new FraudDetectionHttpMessageHandler(sdkWrapper));
        }
    }

    /// <summary>
    /// HTTP message handler that integrates with fraud detection SDK
    /// </summary>
    public class FraudDetectionHttpMessageHandler : DelegatingHandler
    {
        private readonly FraudDetectionSdkWrapper _sdkWrapper;

        public FraudDetectionHttpMessageHandler(FraudDetectionSdkWrapper sdkWrapper)
        {
            _sdkWrapper = sdkWrapper ?? throw new ArgumentNullException(nameof(sdkWrapper));
        }

        protected override async Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken cancellationToken)
        {
            try
            {
                // Intercept request for fraud analysis
                var headers = request.Headers.ToDictionary(h => h.Key, h => string.Join(",", h.Value));
                var body = request.Content != null ? await request.Content.ReadAsStringAsync() : null;

                var analysis = await _sdkWrapper.InterceptRequestAsync(
                    request.Method.Method,
                    request.RequestUri?.ToString() ?? "",
                    headers,
                    body);

                // Block high-risk requests
                if (analysis.ShouldBlock)
                {
                    return new HttpResponseMessage(HttpStatusCode.Forbidden)
                    {
                        Content = new StringContent(JsonSerializer.Serialize(new
                        {
                            error = "Request blocked due to fraud risk",
                            riskScore = analysis.RiskScore,
                            reason = analysis.BlockReason
                        }), Encoding.UTF8, "application/json")
                    };
                }

                // Send the original request
                var response = await base.SendAsync(request, cancellationToken);

                // Intercept response for additional analysis
                var responseHeaders = response.Headers.ToDictionary(h => h.Key, h => string.Join(",", h.Value));
                var responseBody = response.Content != null ? await response.Content.ReadAsStringAsync() : null;

                await _sdkWrapper.InterceptResponseAsync(
                    analysis.RequestId,
                    (int)response.StatusCode,
                    responseHeaders,
                    responseBody);

                return response;
            }
            catch (Exception ex)
            {
                // Continue with original request on error (fail-open for availability)
                return await base.SendAsync(request, cancellationToken);
            }
        }
    }
}
