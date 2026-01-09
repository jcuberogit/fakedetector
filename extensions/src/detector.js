/**
 * LinkedIn ScamShield - Scam Detector Engine
 * 100% Open Source - MIT License
 */

class ScamDetector {
  constructor() {
    this.patterns = ScamPatterns;
    this.weights = RiskWeights;
  }

  /**
   * Analyze a message for scam indicators
   * @param {string} messageText - The message content to analyze
   * @param {Object} senderProfile - Optional sender profile data
   * @returns {Object} Analysis result with risk score and details
   */
  analyzeMessage(messageText, senderProfile = null) {
    const text = messageText.toLowerCase();
    const results = {
      riskScore: 0,
      riskLevel: 'safe',
      matchedPatterns: [],
      categories: [],
      recommendations: []
    };

    // Check each pattern category
    for (const [category, patterns] of Object.entries(this.patterns)) {
      const matches = this.findMatches(text, patterns);
      if (matches.length > 0) {
        const weight = this.weights[category] || 0.5;
        const categoryScore = Math.min(matches.length * weight * 0.2, weight);
        results.riskScore += categoryScore;
        results.matchedPatterns.push(...matches);
        results.categories.push(category);
      }
    }

    // Analyze sender profile if available
    if (senderProfile) {
      const profileRisk = this.analyzeProfile(senderProfile);
      results.riskScore += profileRisk.score;
      if (profileRisk.flags.length > 0) {
        results.categories.push('profileRedFlags');
        results.matchedPatterns.push(...profileRisk.flags);
      }
    }

    // Normalize score to 0-100
    results.riskScore = Math.min(Math.round(results.riskScore * 100), 100);

    // Determine risk level
    if (results.riskScore >= 70) {
      results.riskLevel = 'scam';
      results.recommendations.push('🚨 High probability scam - Do not respond');
      results.recommendations.push('Report this message to LinkedIn');
    } else if (results.riskScore >= 40) {
      results.riskLevel = 'suspicious';
      results.recommendations.push('⚠️ Review carefully before responding');
      results.recommendations.push('Verify sender\'s profile and company');
    } else {
      results.riskLevel = 'safe';
    }

    return results;
  }

  /**
   * Find matching patterns in text
   */
  findMatches(text, patterns) {
    const matches = [];
    for (const pattern of patterns) {
      if (text.includes(pattern.toLowerCase())) {
        matches.push(pattern);
      }
    }
    return matches;
  }

  /**
   * Analyze sender profile for red flags
   */
  analyzeProfile(profile) {
    const result = { score: 0, flags: [] };

    // New account (less than 30 days)
    if (profile.accountAge && profile.accountAge < 30) {
      result.score += 0.3;
      result.flags.push('New account (< 30 days)');
    }

    // Low connection count
    if (profile.connections && profile.connections < 50) {
      result.score += 0.2;
      result.flags.push('Low connections (< 50)');
    }

    // No profile photo or default photo
    if (!profile.hasPhoto || profile.isDefaultPhoto) {
      result.score += 0.2;
      result.flags.push('No profile photo');
    }

    // No work history
    if (!profile.hasWorkHistory) {
      result.score += 0.2;
      result.flags.push('No work history');
    }

    // Generic job title
    const genericTitles = ['recruiter', 'hr specialist', 'talent acquisition', 'career coach'];
    if (profile.title && genericTitles.some(t => profile.title.toLowerCase().includes(t))) {
      result.score += 0.1;
      result.flags.push('Generic recruiter title');
    }

    return result;
  }

  /**
   * Quick check if message contains any scam patterns
   */
  quickCheck(messageText) {
    const text = messageText.toLowerCase();
    
    // Check high-priority patterns first
    const highPriority = [
      ...this.patterns.paymentRedFlags,
      ...this.patterns.cvScams.slice(0, 10),
      ...this.patterns.phishingIndicators
    ];

    for (const pattern of highPriority) {
      if (text.includes(pattern.toLowerCase())) {
        return true;
      }
    }
    return false;
  }

  /**
   * Get human-readable category name
   */
  getCategoryName(category) {
    const names = {
      cvScams: '📝 CV/Resume Scam',
      fakeJobOffers: '💼 Fake Job Offer',
      urgencyTactics: '⏰ Urgency Tactics',
      paymentRedFlags: '💰 Payment Request',
      botPatterns: '🤖 Bot Pattern',
      phishingIndicators: '🎣 Phishing Attempt',
      spanishPatterns: '🌎 Scam (Spanish)',
      suspiciousDomains: '🔗 Suspicious Link',
      profileRedFlags: '👤 Profile Red Flags'
    };
    return names[category] || category;
  }
}

// Export for use in content script
if (typeof module !== 'undefined' && module.exports) {
  module.exports = ScamDetector;
}
