// Example: JavaScript/Node.js/React Integration
// Simple fraud detection integration for any JavaScript application

// Step 1: Install the package
// npm install @paradigmstore/fraud-detection

// Step 2: Initialize in your main app file
const FraudDetection = require('@paradigmstore/fraud-detection');
// or: import FraudDetection from '@paradigmstore/fraud-detection';

// Initialize with your API key
FraudDetection.init('your-api-key-here');

// Step 3: Node.js/Express example
app.post('/api/process-payment', async (req, res) => {
    const transaction = {
        amount: req.body.amount,
        user_id: req.user.id,
        merchant: 'Your Store Name',
        timestamp: new Date().toISOString()
    };
    
    // Analyze for fraud
    const result = await FraudDetection.analyze(transaction);
    
    if (result.recommendation === 'DENY') {
        return res.status(403).json({ error: 'Transaction blocked for security' });
    } else if (result.recommendation === 'REVIEW') {
        // Flag for manual review
        await flagForReview(transaction, result);
    }
    
    // Process payment normally
    const payment = await processNormalPayment(transaction);
    res.json(payment);
});

// React component example
import React, { useState } from 'react';
import FraudDetection from '@paradigmstore/fraud-detection';

// Initialize once in your App.js
FraudDetection.init('your-api-key-here');

function PaymentForm() {
    const [amount, setAmount] = useState('');
    const [loading, setLoading] = useState(false);
    
    const handlePayment = async (e) => {
        e.preventDefault();
        setLoading(true);
        
        const transaction = {
            amount: parseFloat(amount),
            user_id: userId,
            merchant: 'React Store'
        };
        
        try {
            // Quick fraud check
            const result = await FraudDetection.analyze(transaction);
            
            if (result.recommendation === 'APPROVE') {
                await processPayment(transaction);
                alert('Payment successful!');
            } else {
                alert('Transaction requires additional verification');
            }
        } catch (error) {
            console.error('Fraud check failed:', error);
        } finally {
            setLoading(false);
        }
    };
    
    return (
        <form onSubmit={handlePayment}>
            <input 
                type="number" 
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                placeholder="Amount"
                required
            />
            <button type="submit" disabled={loading}>
                {loading ? 'Checking...' : 'Pay Now'}
            </button>
        </form>
    );
}
