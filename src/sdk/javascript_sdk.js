const axios = require('axios');

class FraudDetection {
    constructor() {
        this.apiKey = null;
        this.baseUrl = 'http://localhost:9001'; // Will be https://api.paradigmstore.com in production
    }
    
    /**
     * Initialize ParadigmStore Fraud Detection
     * @param {string} apiKey - Your API key
     */
    init(apiKey) {
        if (!apiKey) {
            throw new Error('API key is required');
        }
        this.apiKey = apiKey;
    }
    
    /**
     * Analyze transaction for fraud risk
     * @param {object} transaction - Transaction data
     * @returns {Promise<object>} Fraud analysis result
     */
    async analyze(transaction) {
        if (!this.apiKey) {
            throw new Error('FraudDetection not initialized. Call init() first.');
        }
        
        try {
            const response = await axios.post(`${this.baseUrl}/api/sdk/analyze`, {
                transaction,
                api_key: this.apiKey
            }, {
                headers: {
                    'Content-Type': 'application/json',
                    'X-API-Key': this.apiKey
                }
            });
            
            return response.data;
        } catch (error) {
            return {
                success: false,
                error: error.message,
                risk_score: 0.5,
                recommendation: 'REVIEW'
            };
        }
    }
}

// Export singleton instance
module.exports = new FraudDetection();
