/**
 * UniversalShield - Scam Detector Engine
 */

class ScamDetector {
  static normalize(text) {
    // Removes hidden characters, extra spaces, and converts to lowercase
    return text.replace(/[\u200B-\u200D\uFEFF]/g, '').toLowerCase().trim();
  }

  static analyze(text) {
    const cleanText = this.normalize(text);
    let score = 0;
    let matches = [];

    // 1. Basic Pattern Matching
    for (const [category, patterns] of Object.entries(ScamPatterns)) {
      patterns.forEach(regex => {
        regex.lastIndex = 0;
        if (regex.test(cleanText)) {
          let weight = RiskWeights[category] || 10;
          
          // Gemini Prompt specific weights
          if (regex.source.includes('k[i1]ndl[y7]')) weight = 30;
          if (regex.source.includes('curr[e3]nt\s*l[o0]c[a4]t[i1][o0]n')) weight = 30;
          if (regex.source.includes('y[e3][a4]r[s5]\s*[o0]f\s*[e3]xp[e3]r[i1][e3]nc[e3]')) weight = 30;

          score += weight;
          matches.push(category);
        }
      });
    }

    // 2. Combo: Gmail + Recruiter/Principal Title (+40 points)
    const isRecruiterTitle = /r[e3]cru[i1]t[e3]r|pr[i1]nc[i1]p[a4]l/gi.test(cleanText);
    const hasGmailAddress = /gm[a4][i1]l\.c[o0]m/gi.test(cleanText);
    if (isRecruiterTitle && hasGmailAddress) {
      score += 40;
      matches.push('GMAIL_RECRUITER_COMBO');
    }

    // 3. Vague Physical Address (+30 points)
    // Matches "A: United States," or similar empty/placeholder addresses
    if (/a:\s*un[i1]t[e3]d\s*st[a4]t[e3][s5],?\s*$/gi.test(cleanText) || /a:\s*,/gi.test(cleanText)) {
      score += 30;
      matches.push('VAGUE_ADDRESS');
    }

    return {
      riskScore: Math.min(score, 100),
      riskLevel: score >= 50 ? 'scam' : (score >= 30 ? 'suspicious' : 'safe'),
      matchedPatterns: matches,
      isScam: score >= 50,
      isSuspicious: score >= 30 && score < 50,
      recommendations: score >= 50 ? ['🚨 UNIVERSAL SHIELD: BOT DETECTED', 'Report this message to LinkedIn'] : 
                      (score >= 30 ? ['⚠️ Review carefully before responding', 'Verify sender\'s profile'] : []),
      categories: matches
    };
  }

  // Compatibility method for existing content.js calls
  analyzeMessage(text) {
    return ScamDetector.analyze(text);
  }

  getCategoryName(category) {
    const names = {
      RESUME_SCAMS: '📝 CV/Resume Scam',
      URGENCY_WHATSAPP: '📱 WhatsApp/Urgency',
      PAYMENT_CRYPTO: '💰 Payment/Crypto'
    };
    return names[category] || category;
  }
}

// Export for use in content script
if (typeof module !== 'undefined' && module.exports) {
  module.exports = ScamDetector;
}
