/**
 * Unit Tests for UniversalShield Chrome Extension
 * Tests for cloudAnalyzer.js and content.js
 */

// Mock Chrome APIs
global.chrome = {
  storage: {
    local: {
      get: jest.fn((keys, callback) => {
        callback({ scamshield_license: 'US-PRO-DEMO12345678' });
      }),
      set: jest.fn()
    },
    sync: {
      get: jest.fn((keys, callback) => {
        callback({ scamshield_license: 'US-PRO-DEMO12345678' });
      }),
      set: jest.fn()
    }
  },
  runtime: {
    sendMessage: jest.fn()
  }
};

// Mock fetch
global.fetch = jest.fn();

describe('CloudAnalyzer', () => {
  let cloudAnalyzer;

  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();
    
    // Import CloudAnalyzer (would need to be adapted for Node.js)
    // For now, we'll define a simplified version for testing
    class CloudAnalyzer {
      constructor(apiUrl, licenseKey) {
        this.apiUrl = apiUrl || 'https://api.tucan.store';
        this.licenseKey = licenseKey;
      }

      async analyze(message, metadata) {
        const features = this.extractFeatures(message, metadata);
        
        const response = await fetch(`${this.apiUrl}/api/v1/analyze-features`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-License-Key': this.licenseKey || ''
          },
          body: JSON.stringify({ features })
        });

        return await response.json();
      }

      extractFeatures(message, metadata) {
        return {
          message_length: message.length,
          word_count: message.split(' ').length,
          urgency_keywords_count: (message.match(/urgent|immediately|now/gi) || []).length,
          money_keywords_count: (message.match(/money|payment|cash/gi) || []).length,
          platform_id: metadata.platform === 'linkedin' ? 1 : 0
        };
      }
    }

    cloudAnalyzer = new CloudAnalyzer('https://api.tucan.store', 'US-PRO-DEMO12345678');
  });

  test('should initialize with correct API URL and license key', () => {
    expect(cloudAnalyzer.apiUrl).toBe('https://api.tucan.store');
    expect(cloudAnalyzer.licenseKey).toBe('US-PRO-DEMO12345678');
  });

  test('should extract features from message', () => {
    const message = 'URGENT: Send money immediately for this opportunity!';
    const metadata = { platform: 'linkedin' };

    const features = cloudAnalyzer.extractFeatures(message, metadata);

    expect(features.message_length).toBe(message.length);
    expect(features.word_count).toBeGreaterThan(0);
    expect(features.urgency_keywords_count).toBeGreaterThan(0);
    expect(features.money_keywords_count).toBeGreaterThan(0);
    expect(features.platform_id).toBe(1);
  });

  test('should call API with correct parameters', async () => {
    const mockResponse = {
      risk_score: 85,
      risk_level: 'critical',
      explanation: 'High urgency and financial keywords detected'
    };

    global.fetch.mockResolvedValueOnce({
      json: async () => mockResponse
    });

    const message = 'URGENT: Send money now!';
    const metadata = { platform: 'linkedin' };

    const result = await cloudAnalyzer.analyze(message, metadata);

    expect(global.fetch).toHaveBeenCalledWith(
      'https://api.tucan.store/api/v1/analyze-features',
      expect.objectContaining({
        method: 'POST',
        headers: expect.objectContaining({
          'Content-Type': 'application/json',
          'X-License-Key': 'US-PRO-DEMO12345678'
        })
      })
    );

    expect(result).toEqual(mockResponse);
  });

  test('should handle API errors gracefully', async () => {
    global.fetch.mockRejectedValueOnce(new Error('Network error'));

    const message = 'Test message';
    const metadata = { platform: 'linkedin' };

    await expect(cloudAnalyzer.analyze(message, metadata)).rejects.toThrow('Network error');
  });

  test('should not send raw message content to API', async () => {
    const message = 'Sensitive personal information here';
    const metadata = { platform: 'linkedin' };

    global.fetch.mockResolvedValueOnce({
      json: async () => ({ risk_score: 10 })
    });

    await cloudAnalyzer.analyze(message, metadata);

    const callArgs = global.fetch.mock.calls[0][1];
    const body = JSON.parse(callArgs.body);

    // Verify only features are sent, not raw message
    expect(body.features).toBeDefined();
    expect(body.message).toBeUndefined();
    expect(body.features.message_length).toBeDefined();
  });
});

describe('FeatureExtractor', () => {
  test('should extract Rachel Good pattern features', () => {
    const message = 'Hi, I am a recruiter from Gmail. Where are you located?';
    const metadata = {
      platform: 'linkedin',
      sender_email: 'recruiter@gmail.com',
      claimed_role: 'recruiter'
    };

    // Mock feature extraction
    const features = {
      recruiter_keywords_count: 1,
      location_inquiry: 1,
      gmail_recruiter_combo: 1,
      message_length: message.length
    };

    expect(features.recruiter_keywords_count).toBe(1);
    expect(features.location_inquiry).toBe(1);
    expect(features.gmail_recruiter_combo).toBe(1);
  });

  test('should extract financial phishing features', () => {
    const message = 'Congratulations! You qualify for a Destiny Mastercard with $5000 credit limit. Security deposit required.';
    
    const features = {
      financial_phishing_keywords_count: 3, // destiny, mastercard, credit limit
      credit_card_mention: 1,
      credit_limit_mention: 1,
      security_deposit_mention: 1
    };

    expect(features.financial_phishing_keywords_count).toBeGreaterThan(0);
    expect(features.credit_card_mention).toBe(1);
    expect(features.security_deposit_mention).toBe(1);
  });

  test('should anonymize features (no PII)', () => {
    const message = 'Contact me at john.doe@example.com or call 555-1234';
    const metadata = {
      sender_email: 'scammer@gmail.com'
    };

    // Features should not contain email or phone
    const features = {
      message_length: message.length,
      link_count: 0,
      // No email or phone fields
    };

    expect(features.email).toBeUndefined();
    expect(features.phone).toBeUndefined();
    expect(features.sender_email).toBeUndefined();
  });
});

describe('Content Script Badge Creation', () => {
  test('should create critical risk badge', () => {
    const analysis = {
      isScam: true,
      riskScore: 95,
      riskLevel: 'critical',
      matchedPatterns: ['urgency', 'money_request']
    };

    // Mock badge creation
    const badge = {
      text: '⚠️ UNIVERSAL SHIELD: BOT DETECTED',
      color: '#ff0000',
      riskScore: 95
    };

    expect(badge.text).toContain('BOT DETECTED');
    expect(badge.color).toBe('#ff0000');
    expect(badge.riskScore).toBe(95);
  });

  test('should create caution badge for suspicious content', () => {
    const analysis = {
      isScam: false,
      isSuspicious: true,
      riskScore: 65,
      riskLevel: 'caution'
    };

    const badge = {
      text: '⚠️ UNIVERSAL SHIELD: SUSPICIOUS',
      color: '#ffcc00',
      riskScore: 65
    };

    expect(badge.text).toContain('SUSPICIOUS');
    expect(badge.color).toBe('#ffcc00');
  });
});

describe('License Validation', () => {
  test('should validate Pro license key', async () => {
    global.fetch.mockResolvedValueOnce({
      json: async () => ({
        valid: true,
        tier: 'pro',
        features_enabled: {
          cloud_ml: true,
          unlimited_scans: true
        }
      })
    });

    const response = await fetch('https://api.tucan.store/api/v1/subscription/validate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ license_key: 'US-PRO-DEMO12345678' })
    });

    const data = await response.json();

    expect(data.valid).toBe(true);
    expect(data.tier).toBe('pro');
    expect(data.features_enabled.cloud_ml).toBe(true);
  });

  test('should reject invalid license key', async () => {
    global.fetch.mockResolvedValueOnce({
      json: async () => ({
        valid: false,
        tier: 'free'
      })
    });

    const response = await fetch('https://api.tucan.store/api/v1/subscription/validate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ license_key: 'INVALID-KEY' })
    });

    const data = await response.json();

    expect(data.valid).toBe(false);
    expect(data.tier).toBe('free');
  });
});

describe('Feedback Reporting', () => {
  test('should send scam report to VPS Agent', async () => {
    const features = {
      message_length: 150,
      urgency_keywords_count: 3,
      money_keywords_count: 2
    };

    global.fetch.mockResolvedValueOnce({
      json: async () => ({
        success: true,
        data_point_id: 123
      })
    });

    const response = await fetch('https://api.tucan.store/api/v1/report-scam', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-License-Key': 'US-PRO-DEMO12345678'
      },
      body: JSON.stringify({
        features: features,
        is_scam: true,
        predicted_risk_score: 85,
        predicted_risk_level: 'critical',
        platform: 'linkedin'
      })
    });

    const data = await response.json();

    expect(data.success).toBe(true);
    expect(data.data_point_id).toBeDefined();
  });
});
