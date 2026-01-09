/**
 * Cloud Analyzer - PRO Tier
 * Enhanced ML analysis with anonymized features only
 * Privacy guarantee: NEVER sends raw message content
 */

class CloudAnalyzer {
  constructor(apiUrl, licenseKey) {
    this.apiUrl = apiUrl || 'https://api.universalshield.dev';
    this.licenseKey = licenseKey;
    this.featureExtractor = new FeatureExtractor();
  }
  
  async analyze(message, metadata) {
    try {
      // Step 1: Extract anonymized features LOCALLY
      const features = this.featureExtractor.extract(message, metadata);
      
      // Step 2: Send ONLY features to API (never raw message)
      const response = await fetch(`${this.apiUrl}/api/v1/analyze-features`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-License-Key': this.licenseKey || ''
        },
        body: JSON.stringify({ features })
      });
      
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      
      const result = await response.json();
      
      return {
        risk_score: result.risk_score,
        risk_level: result.risk_level,
        explanation: result.explanation,
        source: 'cloud',
        tier: result.tier,
        scans_remaining: result.scans_remaining
      };
    } catch (error) {
      console.error('Cloud analysis failed:', error);
      // Fallback to local analysis
      const localAnalyzer = new LocalAnalyzer();
      return localAnalyzer.analyze(message, metadata);
    }
  }
}

class FeatureExtractor {
  constructor() {
    this.urgencyKeywords = [
      'urgent', 'immediately', 'now', 'today', 'asap', 'hurry',
      'limited time', 'expires', 'act now', 'don\'t miss'
    ];
    
    this.moneyKeywords = [
      'money', 'cash', 'payment', 'bank', 'account', 'wire',
      'transfer', 'deposit', 'bitcoin', 'crypto', 'investment',
      'profit', 'earn', 'income', 'fee', 'prize', 'lottery'
    ];
    
    this.credentialKeywords = [
      'password', 'login', 'verify', 'confirm', 'account',
      'username', 'credentials', 'security', 'suspended'
    ];
  }
  
  extract(message, metadata) {
    const messageLower = message.toLowerCase();
    
    // Returns ONLY numerical features - NEVER raw text
    return {
      // Message structure
      message_length: message.length,
      word_count: message.split(/\s+/).length,
      sentence_count: message.split(/[.!?]+/).length,
      avg_word_length: this.calculateAvgWordLength(message),
      
      // Keyword density
      urgency_keywords_count: this.countKeywords(messageLower, this.urgencyKeywords),
      money_keywords_count: this.countKeywords(messageLower, this.moneyKeywords),
      credential_keywords_count: this.countKeywords(messageLower, this.credentialKeywords),
      
      // Links and attachments
      link_count: (message.match(/https?:\/\//g) || []).length,
      has_shortened_url: this.hasShortenedUrl(message) ? 1 : 0,
      file_attachment: metadata.hasAttachment ? 1 : 0,
      file_extension_risk: this.getExtensionRisk(metadata.fileType),
      
      // Linguistic features
      exclamation_count: (message.match(/!/g) || []).length,
      question_count: (message.match(/\?/g) || []).length,
      caps_ratio: this.calculateCapsRatio(message),
      number_count: (message.match(/\d+/g) || []).length,
      currency_symbol_count: (message.match(/[$€£]/g) || []).length,
      
      // Social context (anonymized)
      sender_account_age_days: metadata.accountAge || 0,
      connection_degree: metadata.connectionDegree || 3,
      previous_interactions: Math.min(metadata.previousInteractions || 0, 100),
      
      // Platform and context (categorical IDs)
      platform_id: this.platformToId(metadata.platform),
      context_type_id: this.contextToId(metadata.claimedRole),
      
      // Behavioral flags (binary)
      requests_download: this.requestsDownload(messageLower) ? 1 : 0,
      requests_payment: this.requestsPayment(messageLower) ? 1 : 0,
      requests_credentials: this.requestsCredentials(messageLower) ? 1 : 0,
      has_urgency: this.countKeywords(messageLower, this.urgencyKeywords) > 0 ? 1 : 0
    };
  }
  
  calculateAvgWordLength(message) {
    const words = message.split(/\s+/).filter(w => w.length > 0);
    if (words.length === 0) return 0;
    return words.reduce((sum, word) => sum + word.length, 0) / words.length;
  }
  
  countKeywords(text, keywords) {
    let count = 0;
    for (const keyword of keywords) {
      if (text.includes(keyword)) count++;
    }
    return count;
  }
  
  hasShortenedUrl(message) {
    const shorteners = ['bit.ly', 'tinyurl', 'goo.gl', 't.co', 'ow.ly'];
    return shorteners.some(s => message.toLowerCase().includes(s));
  }
  
  getExtensionRisk(fileType) {
    if (!fileType) return 0.0;
    
    const dangerous = ['exe', 'bat', 'cmd', 'scr', 'vbs', 'js', 'jar', 'msi'];
    const safe = ['pdf', 'doc', 'docx', 'txt', 'jpg', 'png'];
    
    const ext = fileType.toLowerCase();
    if (dangerous.includes(ext)) return 1.0;
    if (safe.includes(ext)) return 0.1;
    return 0.5;
  }
  
  calculateCapsRatio(message) {
    const letters = message.match(/[a-zA-Z]/g) || [];
    if (letters.length === 0) return 0;
    const caps = message.match(/[A-Z]/g) || [];
    return caps.length / letters.length;
  }
  
  platformToId(platform) {
    const map = { linkedin: 1, gmail: 2, outlook: 3 };
    return map[platform] || 0;
  }
  
  contextToId(context) {
    const map = {
      recruiter: 1, investor: 2, friend: 3, coworker: 4,
      support: 5, delivery_service: 6, professional: 7
    };
    return map[context] || 0;
  }
  
  requestsDownload(message) {
    return /download|install|run|execute|open file/.test(message);
  }
  
  requestsPayment(message) {
    return /send money|wire|transfer|pay|deposit|bank details/.test(message);
  }
  
  requestsCredentials(message) {
    return this.countKeywords(message, this.credentialKeywords) >= 2;
  }
}

// Export for use in extension
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { CloudAnalyzer, FeatureExtractor };
}
