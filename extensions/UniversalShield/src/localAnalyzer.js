/**
 * Local Analyzer - FREE Tier
 * 100% local analysis - ZERO data sent to any server
 * Privacy guarantee: Everything happens in the browser
 */

class LocalAnalyzer {
  constructor() {
    this.urgencyKeywords = [
      'urgent', 'immediately', 'now', 'today', 'asap', 'hurry',
      'limited time', 'expires', 'act now', 'don\'t miss',
      'last chance', 'ending soon', 'quick', 'fast'
    ];
    
    this.moneyKeywords = [
      'money', 'cash', 'payment', 'bank', 'account', 'wire',
      'transfer', 'deposit', 'credit card', 'ssn', 'social security',
      'bitcoin', 'crypto', 'investment', 'profit', 'earn', 'income',
      'salary', 'pay', 'fee', 'charge', 'refund', 'prize', 'lottery',
      'million', 'thousand', 'dollars'
    ];
    
    this.credentialKeywords = [
      'password', 'login', 'verify', 'confirm', 'account',
      'username', 'credentials', 'security', 'suspended',
      'locked', 'verify identity', 'click here', 'sign in'
    ];
    
    this.dangerousExtensions = [
      'exe', 'bat', 'cmd', 'com', 'scr', 'vbs', 'js',
      'jar', 'msi', 'app', 'dmg', 'pkg'
    ];
  }
  
  analyze(message, metadata) {
    const behavioral = this.analyzeBehavior(message, metadata);
    const linguistic = this.analyzeLinguistic(message);
    const social = this.analyzeSocial(metadata);
    
    const riskScore = this.calculateRisk(behavioral, linguistic, social);
    
    return {
      risk_score: riskScore,
      risk_level: this.getRiskLevel(riskScore),
      explanation: this.generateExplanation(behavioral, linguistic, social),
      context_signals: { behavioral, linguistic, social },
      source: 'local',
      tier: 'free'
    };
  }
  
  analyzeBehavior(message, metadata) {
    const messageLower = message.toLowerCase();
    
    return {
      platform: metadata.platform || 'unknown',
      action_requested: this.detectAction(messageLower),
      file_type: metadata.fileType,
      file_risk: this.getFileRisk(metadata.fileType),
      link_count: (message.match(/https?:\/\//g) || []).length,
      suspicious_links: this.hasSuspiciousLinks(message),
      urgency_level: this.calculateUrgency(messageLower),
      requests_credentials: this.requestsCredentials(messageLower),
      requests_money: this.requestsMoney(messageLower)
    };
  }
  
  analyzeLinguistic(message) {
    const messageLower = message.toLowerCase();
    
    return {
      message_length: message.length,
      urgency_keywords_count: this.countKeywords(messageLower, this.urgencyKeywords),
      money_keywords_count: this.countKeywords(messageLower, this.moneyKeywords),
      credential_keywords_count: this.countKeywords(messageLower, this.credentialKeywords),
      excessive_punctuation: (message.match(/[!?]{2,}/g) || []).length > 2,
      all_caps_ratio: this.calculateCapsRatio(message),
      exclamation_count: (message.match(/!/g) || []).length
    };
  }
  
  analyzeSocial(metadata) {
    const accountAge = metadata.accountAge || 0;
    const connectionDegree = metadata.connectionDegree || 3;
    
    return {
      account_age_days: accountAge,
      account_age_risk: this.getAccountAgeRisk(accountAge),
      connection_degree: connectionDegree,
      connection_risk: this.getConnectionRisk(connectionDegree),
      previous_interactions: metadata.previousInteractions || 0,
      trust_score: this.calculateTrustScore(metadata)
    };
  }
  
  calculateRisk(behavioral, linguistic, social) {
    let risk = 0;
    
    // Behavioral risk
    if (behavioral.file_risk > 0.8) risk += 30;
    else if (behavioral.file_risk > 0.5) risk += 15;
    
    if (behavioral.action_requested === 'download') risk += 25;
    if (behavioral.action_requested === 'transfer_money') risk += 25;
    if (behavioral.action_requested === 'provide_credentials') risk += 25;
    
    if (behavioral.urgency_level > 0.7) risk += 20;
    else if (behavioral.urgency_level > 0.4) risk += 10;
    
    if (behavioral.requests_credentials) risk += 25;
    if (behavioral.requests_money) risk += 20;
    if (behavioral.suspicious_links) risk += 15;
    
    // Social risk
    if (social.account_age_risk > 0.8) risk += 20;
    else if (social.account_age_risk > 0.5) risk += 10;
    
    if (social.connection_risk > 0.7) risk += 15;
    if (social.previous_interactions === 0) risk += 10;
    if (social.trust_score < 0.3) risk += 15;
    
    // Linguistic risk
    if (linguistic.urgency_keywords_count > 3) risk += 15;
    else if (linguistic.urgency_keywords_count > 1) risk += 8;
    
    if (linguistic.money_keywords_count > 2) risk += 12;
    if (linguistic.credential_keywords_count > 2) risk += 15;
    if (linguistic.excessive_punctuation) risk += 10;
    if (linguistic.all_caps_ratio > 0.3) risk += 10;
    
    // Contextual combinations (intelligence)
    if (behavioral.action_requested === 'download' && 
        behavioral.file_risk > 0.8 && 
        social.account_age_days < 7) {
      risk += 20;
    }
    
    if (behavioral.requests_credentials && 
        behavioral.urgency_level > 0.6 && 
        social.previous_interactions === 0) {
      risk += 25;
    }
    
    if (behavioral.requests_money && 
        social.connection_degree > 2 && 
        social.previous_interactions === 0) {
      risk += 20;
    }
    
    return Math.min(risk, 100);
  }
  
  getRiskLevel(score) {
    if (score < 30) return 'safe';
    if (score < 70) return 'caution';
    return 'critical';
  }
  
  generateExplanation(behavioral, linguistic, social) {
    const reasons = [];
    
    if (behavioral.file_risk > 0.8) {
      reasons.push(`Dangerous file type detected (${behavioral.file_type})`);
    }
    
    if (behavioral.urgency_level > 0.7) {
      reasons.push('High urgency language detected');
    }
    
    if (social.account_age_days < 7) {
      reasons.push(`Very new account (${social.account_age_days} days old)`);
    } else if (social.account_age_days < 30) {
      reasons.push(`New account (${social.account_age_days} days old)`);
    }
    
    if (social.connection_degree > 2) {
      reasons.push('No direct connection to sender');
    }
    
    if (behavioral.requests_credentials) {
      reasons.push('Requests login credentials or personal information');
    }
    
    if (behavioral.requests_money) {
      reasons.push('Requests money transfer or payment');
    }
    
    if (social.previous_interactions === 0) {
      reasons.push('First time contact from this sender');
    }
    
    if (linguistic.excessive_punctuation) {
      reasons.push('Excessive punctuation (spam indicator)');
    }
    
    if (behavioral.suspicious_links) {
      reasons.push('Contains suspicious or shortened links');
    }
    
    if (reasons.length === 0) {
      return 'No significant risk factors detected.';
    }
    
    return reasons.join(' • ');
  }
  
  // Helper methods
  
  detectAction(message) {
    if (/download|install|run|execute/.test(message)) return 'download';
    if (/send money|wire|transfer|pay|deposit/.test(message)) return 'transfer_money';
    if (/password|login|verify|confirm identity/.test(message)) return 'provide_credentials';
    if (/click|visit|go to/.test(message)) return 'click_link';
    return 'none';
  }
  
  getFileRisk(fileType) {
    if (!fileType) return 0.0;
    const ext = fileType.toLowerCase();
    if (this.dangerousExtensions.includes(ext)) return 1.0;
    if (['pdf', 'doc', 'docx', 'txt', 'jpg', 'png'].includes(ext)) return 0.1;
    return 0.5;
  }
  
  hasSuspiciousLinks(message) {
    const urls = message.match(/https?:\/\/[^\s]+/g) || [];
    const suspicious = ['bit.ly', 'tinyurl', 'goo.gl', 'verify', 'secure', 
                       'account', 'login', '.tk', '.ml', '.ga', '.cf'];
    
    return urls.some(url => 
      suspicious.some(indicator => url.toLowerCase().includes(indicator))
    );
  }
  
  calculateUrgency(message) {
    const count = this.countKeywords(message, this.urgencyKeywords);
    return Math.min(count / 5.0, 1.0);
  }
  
  requestsCredentials(message) {
    return this.countKeywords(message, this.credentialKeywords) >= 2;
  }
  
  requestsMoney(message) {
    const moneyCount = this.countKeywords(message, this.moneyKeywords);
    const hasTransferWords = /send|transfer|wire|pay|deposit/.test(message);
    return moneyCount >= 2 && hasTransferWords;
  }
  
  getAccountAgeRisk(ageDays) {
    if (ageDays < 7) return 1.0;
    if (ageDays < 30) return 0.7;
    if (ageDays < 90) return 0.4;
    return 0.1;
  }
  
  getConnectionRisk(degree) {
    if (degree >= 3) return 0.8;
    if (degree === 2) return 0.4;
    return 0.1;
  }
  
  calculateTrustScore(metadata) {
    let score = 0.5;
    
    const accountAge = metadata.accountAge || 0;
    if (accountAge > 365) score += 0.3;
    else if (accountAge > 90) score += 0.1;
    
    const interactions = metadata.previousInteractions || 0;
    if (interactions > 10) score += 0.2;
    else if (interactions > 0) score += 0.1;
    
    const connection = metadata.connectionDegree || 3;
    if (connection === 1) score += 0.2;
    
    return Math.min(score, 1.0);
  }
  
  countKeywords(text, keywords) {
    let count = 0;
    for (const keyword of keywords) {
      if (text.includes(keyword)) count++;
    }
    return count;
  }
  
  calculateCapsRatio(message) {
    const letters = message.match(/[a-zA-Z]/g) || [];
    if (letters.length === 0) return 0;
    
    const caps = message.match(/[A-Z]/g) || [];
    return caps.length / letters.length;
  }
}

// Export for use in extension
if (typeof module !== 'undefined' && module.exports) {
  module.exports = LocalAnalyzer;
}
