"""
Example: Python/Django Integration
Simple fraud detection integration for any Python application
"""

# Step 1: Install the package
# pip install paradigmstore-fraud-detection

# Step 2: Initialize in your main.py or settings.py
import paradigmstore_fraud_detection as fraud_detection

# Initialize with your API key
fraud_detection.initialize("your-api-key-here")

# Step 3: Use anywhere in your application
def process_payment(request):
    transaction = {
        'amount': request.POST['amount'],
        'user_id': request.user.id,
        'merchant': 'Your Store Name',
        'timestamp': datetime.now().isoformat()
    }
    
    # Analyze for fraud
    result = fraud_detection.analyze(transaction)
    
    if result['recommendation'] == 'DENY':
        return JsonResponse({'error': 'Transaction blocked for security'}, status=403)
    elif result['recommendation'] == 'REVIEW':
        # Flag for manual review
        flag_for_review(transaction, result)
    
    # Process payment normally
    return process_normal_payment(transaction)

# Async version
async def process_payment_async(request):
    transaction = {
        'amount': request.POST['amount'],
        'user_id': request.user.id,
        'merchant': 'Your Store Name'
    }
    
    # Async fraud analysis
    result = await fraud_detection.analyze_async(transaction)
    
    # Handle result...
    return handle_fraud_result(result)
