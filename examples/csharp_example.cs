// Example: C#/.NET/MAUI Integration
// Simple fraud detection integration for any .NET application

// Step 1: Install the package
// Install-Package ParadigmStore.FraudDetection

// Step 2: Initialize in Program.cs or Startup.cs
using ParadigmStore.FraudDetection;

// Initialize with your API key
FraudDetection.Initialize("your-api-key-here");

// Step 3: Use anywhere in your application
public class PaymentController : ControllerBase
{
    [HttpPost("process-payment")]
    public async Task<IActionResult> ProcessPayment([FromBody] PaymentRequest request)
    {
        var transaction = new
        {
            amount = request.Amount,
            user_id = User.Identity.Name,
            merchant = "Your Store Name",
            timestamp = DateTime.UtcNow.ToString("O")
        };
        
        // Analyze for fraud
        var result = await FraudDetection.AnalyzeAsync(transaction);
        
        if (result.Recommendation == "DENY")
        {
            return BadRequest(new { error = "Transaction blocked for security" });
        }
        else if (result.Recommendation == "REVIEW")
        {
            // Flag for manual review
            await FlagForReview(transaction, result);
        }
        
        // Process payment normally
        return Ok(await ProcessNormalPayment(transaction));
    }
}

// MAUI/Mobile example
public partial class PaymentPage : ContentPage
{
    private async void OnPayButtonClicked(object sender, EventArgs e)
    {
        var transaction = new
        {
            amount = decimal.Parse(AmountEntry.Text),
            user_id = Preferences.Get("user_id", ""),
            merchant = "Mobile Store"
        };
        
        // Quick fraud check
        var result = await FraudDetection.AnalyzeAsync(transaction);
        
        if (result.Recommendation == "APPROVE")
        {
            await DisplayAlert("Success", "Payment approved!", "OK");
            await ProcessPayment(transaction);
        }
        else
        {
            await DisplayAlert("Security Alert", 
                "Transaction requires additional verification", "OK");
        }
    }
}
